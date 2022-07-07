# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from .data_structures import OvalNode


class CpeTreeBuilder:
    def __init__(self, rule_to_grup_id, group_to_platforms, profile_platform):
        self.rule_to_grup_id = rule_to_grup_id
        self.group_to_platforms = group_to_platforms
        self.profile_platform = profile_platform

    @staticmethod
    def _build_rule_platforms(rule, oval_cpe_trees):
        tmp_rule_cpe_tree = OvalNode(
            node_id="Rule_platforms",
            node_type="OR",
            tag="CPE platforms of rule",
            value="",
            children=[]
        )
        for platform in rule.platforms:
            if platform in oval_cpe_trees:
                tmp_rule_cpe_tree.children.append(oval_cpe_trees[platform])
        tmp_rule_cpe_tree.value = tmp_rule_cpe_tree.evaluate_tree()
        return tmp_rule_cpe_tree

    def _build_group_platforms(self, rule, oval_cpe_trees):
        tmp_groups_cpe_tree = OvalNode(
            node_id="Groups_platforms",
            node_type="AND",
            value="",
            tag="CPE platforms of groups",
            children=[]
        )
        if rule.rule_id not in self.rule_to_grup_id:
            tmp_groups_cpe_tree.value = tmp_groups_cpe_tree.evaluate_tree()
            return tmp_groups_cpe_tree

        rule_group = self.rule_to_grup_id[rule.rule_id]
        for platform in self.group_to_platforms[rule_group]:
            if platform in oval_cpe_trees:
                tmp_groups_cpe_tree.children.append(oval_cpe_trees[platform])
        tmp_groups_cpe_tree.value = tmp_groups_cpe_tree.evaluate_tree()
        return tmp_groups_cpe_tree

    def build_cpe_tree(self, rule, oval_cpe_trees):
        cpe_tree = None
        tmp_rule_cpe_tree = self._build_rule_platforms(rule, oval_cpe_trees)
        tmp_groups_cpe_tree = self._build_group_platforms(rule, oval_cpe_trees)

        tmp_profile_cpe_tree = OvalNode(
            node_id="Profile_platforms",
            node_type="AND",
            value="",
            tag="CPE platforms of profile",
            children=[]
        )
        if tmp_rule_cpe_tree.value is not None:
            tmp_profile_cpe_tree.children.append(tmp_rule_cpe_tree)
        if tmp_groups_cpe_tree.value is not None:
            tmp_profile_cpe_tree.children.append(tmp_groups_cpe_tree)

        if self.profile_platform in oval_cpe_trees:
            tmp_profile_cpe_tree.children.append(oval_cpe_trees[self.profile_platform])
        tmp_profile_cpe_tree.value = tmp_profile_cpe_tree.evaluate_tree()

        if tmp_profile_cpe_tree.value is not None:
            cpe_tree = tmp_profile_cpe_tree
        return cpe_tree
