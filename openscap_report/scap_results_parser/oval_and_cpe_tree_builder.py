# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

from .data_structures import LogicalTest, Platform
from .exceptions import ExceptionNoCPEApplicabilityLanguage, MissingOVALResult
from .parsers import CPEApplicabilityLanguageParser, OVALDefinitionParser


class OVALAndCPETreeBuilder:  # pylint: disable=R0902, R0913
    def __init__(self, root, group_parser, profile_platforms,
                 oval_definitions_and_results_sources, oval_var_id_to_value_id, ref_values):
        self.profile_platforms = profile_platforms
        self.root = root
        self.group_parser = group_parser
        self.oval_definitions_and_results_sources = oval_definitions_and_results_sources
        self.oval_var_id_to_value_id = oval_var_id_to_value_id
        self.ref_values = ref_values
        self.cpe_source = ""
        self.missing_oval_results = False
        self.cpe_al = True
        self.reports_with_oval_definitions = None
        self.platform_to_oval_cpe_id = {}
        self.cpe_platforms = {}
        self.dict_of_oval_cpe_definitions = {}
        self.load_oval_definitions()

    def load_oval_definitions(self):
        try:
            self.oval_definition_parser = OVALDefinitionParser(
                self.root, self.oval_var_id_to_value_id, self.ref_values
            )
            self.reports_with_oval_definitions = self.oval_definition_parser.get_oval_definitions()
            self._determine_cpe_source()
            self.dict_of_oval_cpe_definitions = self._get_dict_of_oval_cpe_definitions()
            self.cpe_al_parser = CPEApplicabilityLanguageParser(
                self.root, self.dict_of_oval_cpe_definitions
            )
            self.platform_to_oval_cpe_id = self.cpe_al_parser.platform_to_oval_cpe_id
            self._load_cpe_platforms()
        except MissingOVALResult as error:
            logging.warning((
                "The given input doesn't contain OVAL results (\"%s\"), "
                "OVAL details won't be shown in the report."), error)
            self.missing_oval_results = True

    def _determine_cpe_source(self):
        source_id = set(self.reports_with_oval_definitions.keys()).difference(
            self.oval_definitions_and_results_sources
        )
        if len(source_id) == 1:
            self.cpe_source = source_id.pop()

    def _get_dict_of_oval_cpe_definitions(self):
        if self.cpe_source in self.reports_with_oval_definitions:
            return self.reports_with_oval_definitions[self.cpe_source]
        logging.warning((
            "The given input does not contain a clear mapping of the OVAL definition used "
            "for CPE checks. The results of the OVAL definition in the CPE checks could "
            "be biased."
        ))
        all_oval_definition = {}
        for report in self.reports_with_oval_definitions.values():
            for id_definition, definition in report.items():
                if id_definition not in all_oval_definition:
                    all_oval_definition[id_definition] = definition
                else:
                    if definition.oval_tree.evaluate_tree() != "not evaluated":
                        all_oval_definition[id_definition] = definition
        return all_oval_definition

    def _get_oval_definition_of_cpe(self, platform):
        cpe_oval_id = self.platform_to_oval_cpe_id.get(platform)
        return self.dict_of_oval_cpe_definitions.get(cpe_oval_id)

    def _load_cpe_platforms(self):
        try:
            self.cpe_platforms = self.cpe_al_parser.get_cpe_platforms()
            for platform in self.profile_platforms:
                oval_definition = self._get_oval_definition_of_cpe(platform)
                if oval_definition is None:
                    logging.warning(
                        "Platform (\"%s\") doesn't exist, Platform won't be shown in the report.",
                        platform
                    )
                    continue
                self.cpe_platforms[platform] = Platform(
                    platform_id=platform,
                    logical_test=LogicalTest(
                        node_type="AND",
                        children=[LogicalTest(
                            node_type="frac-ref",
                            value=oval_definition.definition_id,
                            oval_tree=oval_definition.oval_tree
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
        if cpe_oval_id in self.dict_of_oval_cpe_definitions:
            return self.dict_of_oval_cpe_definitions[cpe_oval_id].oval_tree
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

    def get_oval_definition(self, rule):
        report = self.reports_with_oval_definitions.get(rule.oval_reference, None)
        if report is not None:
            return report.get(rule.oval_definition_id)
        oval_def = None
        for report in self.reports_with_oval_definitions.values():
            if oval_def is not None and rule.oval_definition_id in report:
                logging.warning(
                    ("The given input contains the duplicate results of "
                     "the OVAL definition (\"%s\")."),
                    rule.oval_definition_id
                )
            if rule.oval_definition_id in report:
                oval_def = report[rule.oval_definition_id]
        return oval_def

    def insert_oval_and_cpe_trees_to_rules(self, rules):
        if self.missing_oval_results:
            return

        for rule in rules.values():
            rule.oval_definition = self.get_oval_definition(rule)

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
