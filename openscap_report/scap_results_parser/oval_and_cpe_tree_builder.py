# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

from .data_structures import OvalNode
from .exceptions import MissingOVALResult
from .parsers import OVALDefinitionParser


class OVALAndCPETreeBuilder:
    def __init__(self, root, group_parser, profile_platform):
        self.profile_platform = profile_platform
        self.root = root
        self.group_parser = group_parser
        self.missing_oval_results = False
        try:
            self.oval_parser = OVALDefinitionParser(self.root)
            self.oval_trees = self.oval_parser.get_oval_trees()
            self.oval_cpe_trees = self.oval_parser.get_oval_cpe_trees()
        except MissingOVALResult:
            logging.warning("Not found OVAL results!")
            self.missing_oval_results = True

    def _insert_platforms_cpe_trees_to_rule_cpe_tree(self, rule, rule_cpe_tree):
        for platform in rule.platforms:
            if platform in self.oval_cpe_trees:
                rule_cpe_tree.children.append(self.oval_cpe_trees[platform])

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
            if platform in self.oval_cpe_trees:
                tmp_groups_cpe_tree.children.append(self.oval_cpe_trees[platform])
        tmp_groups_cpe_tree.value = tmp_groups_cpe_tree.evaluate_tree()
        return tmp_groups_cpe_tree

    def _get_cpe_tree_of_profile_platform(self):
        cpe_tree = self.oval_cpe_trees[self.profile_platform]
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
        if self.profile_platform in self.oval_cpe_trees:
            cpe_tree.children.append(self._get_cpe_tree_of_profile_platform())
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
            if rule.oval_definition_id in self.oval_trees:
                rule.oval_tree = self.oval_trees[rule.oval_definition_id]
            rule.cpe_tree = self.build_cpe_tree(rule)
