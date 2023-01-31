# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

from .data_structures import OvalNode
from .exceptions import MissingOVALResult
from .namespaces import NAMESPACES
from .parsers import OVALDefinitionParser


class OVALAndCPETreeBuilder:  # pylint: disable=R0902
    def __init__(self, root, group_parser, profile_platforms):
        self.profile_platforms = profile_platforms
        self.root = root
        self.group_parser = group_parser
        self.missing_oval_results = False
        self.oval_definitions = {}
        self.oval_cpe_definitions = {}
        self.platform_to_oval_cpe_id = {}
        self.load_oval_definitions()

    def load_oval_definitions(self):
        try:
            self.platform_to_oval_cpe_id = self.get_platform_to_oval_cpe_id_dict()
            self.oval_definition_parser = OVALDefinitionParser(
                self.root, self.platform_to_oval_cpe_id
            )
            self.oval_definitions = self.oval_definition_parser.get_oval_definitions()
            self.oval_cpe_definitions = self.oval_definition_parser.get_oval_cpe_definitions()
        except MissingOVALResult as error:
            logging.warning("OVAL results \"%s\" not found!", error)
            if str(error) != "oval1":
                self.missing_oval_results = True

    def get_platform_to_oval_cpe_id_dict(self):
        cpe_list = self.root.find(".//ds:component/cpe-dict:cpe-list", NAMESPACES)
        out = {}
        if cpe_list is None:
            return out
        for cpe_item in cpe_list:
            name = cpe_item.get("name")
            check = cpe_item.find(".//cpe-dict:check", NAMESPACES)
            oval_id = check.text if check is not None else name
            out[name] = oval_id
        return out

    def _get_oval_tree_from_oval_cpe_definition(self, platform):
        cpe_oval_id = ""
        if platform in self.platform_to_oval_cpe_id:
            cpe_oval_id = self.platform_to_oval_cpe_id[platform]
        if cpe_oval_id in self.oval_cpe_definitions:
            return self.oval_cpe_definitions[cpe_oval_id].oval_tree
        logging.warning("There is no CPE check for the platform \"%s\".", platform)
        return None

    def _insert_platforms_cpe_trees_to_rule_cpe_tree(self, rule, rule_cpe_tree):
        for platform in rule.platforms:
            oval_tree = self._get_oval_tree_from_oval_cpe_definition(platform)
            if oval_tree is not None:
                rule_cpe_tree.children.append(oval_tree)

    def _build_rule_platforms(self, rule):
        tmp_rule_cpe_tree = OvalNode(
            node_id="Rule_platforms",
            node_type="OR",
            tag="CPE platforms of rule",
            value="",
            children=[]
        )
        if rule.platforms:
            self._insert_platforms_cpe_trees_to_rule_cpe_tree(
                rule,
                tmp_rule_cpe_tree
            )
        tmp_rule_cpe_tree.value = tmp_rule_cpe_tree.evaluate_tree()
        return tmp_rule_cpe_tree

    def _build_group_platforms(self, rule):
        tmp_groups_cpe_tree = OvalNode(
            node_id="Groups_platforms",
            node_type="AND",
            value="",
            tag="CPE platforms of groups",
            children=[]
        )
        if rule.rule_id not in self.group_parser.rule_to_grup_id:
            tmp_groups_cpe_tree.value = tmp_groups_cpe_tree.evaluate_tree()
            return tmp_groups_cpe_tree

        rule_group = self.group_parser.rule_to_grup_id[rule.rule_id]
        for platform in self.group_parser.group_to_platforms[rule_group]:
            oval_tree = self._get_oval_tree_from_oval_cpe_definition(platform)
            if oval_tree is not None:
                tmp_groups_cpe_tree.children.append(oval_tree)
        tmp_groups_cpe_tree.value = tmp_groups_cpe_tree.evaluate_tree()
        return tmp_groups_cpe_tree

    def _get_cpe_tree_of_profile_platform(self, profile_platform):
        cpe_tree = self.oval_cpe_definitions[profile_platform].oval_tree
        cpe_tree.tag = "CPE platforms of profile"
        return cpe_tree

    def _merge_cpe_trees_applicable_for_rule(self, rule_cpe_tree, groups_cpe_tree):
        cpe_tree = OvalNode(
            node_id="Platforms_applicable_for_rule",
            node_type="AND",
            value="",
            tag="CPE platforms applicable for rule",
            children=[]
        )
        if rule_cpe_tree.value is not None:
            cpe_tree.children.append(rule_cpe_tree)
        if groups_cpe_tree.value is not None:
            cpe_tree.children.append(groups_cpe_tree)

        skip_fedora = False
        for profile_platform in self.profile_platforms:
            if "fedora" in profile_platform and skip_fedora:
                continue
            if profile_platform in self.platform_to_oval_cpe_id:
                cpe_oval_id = self.platform_to_oval_cpe_id[profile_platform]
                cpe_tree.children.append(self._get_cpe_tree_of_profile_platform(cpe_oval_id))
            if "fedora" in profile_platform:
                skip_fedora = True
        return cpe_tree

    def build_cpe_tree(self, rule):
        rule_cpe_tree = self._build_rule_platforms(rule)
        groups_cpe_tree = self._build_group_platforms(rule)
        cpe_tree = self._merge_cpe_trees_applicable_for_rule(rule_cpe_tree, groups_cpe_tree)
        cpe_tree.value = cpe_tree.evaluate_tree()
        return cpe_tree if cpe_tree.value is not None else None

    def insert_oval_and_cpe_trees_to_rules(self, rules):
        if self.missing_oval_results:
            return

        for rule in rules.values():
            if rule.oval_definition_id in self.oval_definitions:
                rule.oval_definition = self.oval_definitions[rule.oval_definition_id]
            rule.cpe_tree = self.build_cpe_tree(rule)
