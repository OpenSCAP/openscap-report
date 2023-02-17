# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

from .data_structures import LogicalTest, Platform
from .exceptions import ExceptionNoCPEApplicabilityLanguage, MissingOVALResult
from .parsers import CPEApplicabilityLanguageParser, OVALDefinitionParser


class OVALAndCPETreeBuilder:  # pylint: disable=R0902
    def __init__(self, root, group_parser, profile_platforms):
        self.profile_platforms = profile_platforms
        self.root = root
        self.group_parser = group_parser
        self.missing_oval_results = False
        self.cpe_al = True
        self.oval_definitions = {}
        self.oval_cpe_definitions = {}
        self.platform_to_oval_cpe_id = {}
        self.cpe_platforms = {}
        self.load_oval_definitions()

    def load_oval_definitions(self):
        try:
            self.cpe_al_parser = CPEApplicabilityLanguageParser(self.root)
            self.platform_to_oval_cpe_id = self.cpe_al_parser.platform_to_oval_cpe_id
            self.oval_definition_parser = OVALDefinitionParser(
                self.root, self.platform_to_oval_cpe_id
            )
            self.oval_definitions = self.oval_definition_parser.get_oval_definitions()
            self.oval_cpe_definitions = self.oval_definition_parser.get_oval_cpe_definitions()
            self._load_cpe_platforms()
        except MissingOVALResult as error:
            logging.warning((
                "The given input doesn't contain OVAL results (\"%s\"),"
                " OVAL details won't be shown in the report."), error)
            if str(error) != "oval1":
                self.missing_oval_results = True

    def _load_cpe_platforms(self):
        try:
            self.cpe_platforms = self.cpe_al_parser.get_cpe_platforms(self.oval_cpe_definitions)
            for platform in self.profile_platforms:
                if platform in self.platform_to_oval_cpe_id:
                    cpe_oval_id = self.platform_to_oval_cpe_id[platform]
                    if cpe_oval_id in self.oval_cpe_definitions:
                        oval_tree = self.oval_cpe_definitions[cpe_oval_id].oval_tree
                        self.cpe_platforms[platform] = Platform(
                            platform_id=platform,
                            logical_test=LogicalTest(
                                node_type="AND",
                                children=[LogicalTest(
                                    node_type="frac-ref",
                                    value=cpe_oval_id,
                                    oval_tree=oval_tree
                                )],
                            ),
                            title="Profile platform",
                        )
            self._evaluate_all_cpe_platforms()
        except ExceptionNoCPEApplicabilityLanguage:
            self.cpe_al = False

    def _evaluate_all_cpe_platforms(self):
        for cpe_platform in self.cpe_platforms.values():
            cpe_platform.result = cpe_platform.logical_test.evaluate_tree()

    def _get_oval_tree_from_oval_cpe_definition(self, platform):
        cpe_oval_id = ""
        cpe_platform = platform.lstrip("#")
        if cpe_platform in self.platform_to_oval_cpe_id:
            cpe_oval_id = self.platform_to_oval_cpe_id[cpe_platform]
        if cpe_oval_id in self.oval_cpe_definitions:
            return self.oval_cpe_definitions[cpe_oval_id].oval_tree
        if cpe_platform in self.cpe_platforms:
            return None
        logging.warning("There is no CPE check for the platform \"%s\".", platform)
        return None

    def _get_cpe_al_platforms(self, platforms):
        out = {}
        for platform in platforms:
            cpe_platform = platform.lstrip("#")
            if cpe_platform in self.cpe_platforms:
                out[platform] = self.cpe_platforms[cpe_platform]
        return out

    def _get_cpe_oval_tree(self, platforms):
        out = {}
        for platform in platforms:
            oval_tree = self._get_oval_tree_from_oval_cpe_definition(platform)
            if oval_tree is not None:
                out[platform] = oval_tree
        return out

    @staticmethod
    def _remove_double_cpe_requirement(rule, group_platforms):
        for platform in rule.platforms:
            if platform in group_platforms:
                group_platforms.remove(platform)

    def insert_oval_and_cpe_trees_to_rules(self, rules):
        if self.missing_oval_results:
            return

        for rule in rules.values():
            if rule.oval_definition_id in self.oval_definitions:
                rule.oval_definition = self.oval_definitions[rule.oval_definition_id]
            rule_group = self.group_parser.rule_to_group_id.get(rule.rule_id, "")
            group_platforms = self.group_parser.group_to_platforms.get(rule_group, [])
            self._remove_double_cpe_requirement(rule, group_platforms)
            if not self.cpe_al:
                rule.cpe_oval_dict = {
                    "profile_platforms": self._get_cpe_oval_tree(self.profile_platforms),
                    "group_platforms": self._get_cpe_oval_tree(group_platforms),
                    "rule_platforms": self._get_cpe_oval_tree(rule.platforms),
                }
            else:
                rule.cpe_al = {
                    "profile_platforms": self._get_cpe_al_platforms(self.profile_platforms),
                    "group_platforms": self._get_cpe_al_platforms(group_platforms),
                    "rule_platforms": self._get_cpe_al_platforms(rule.platforms),
                }
