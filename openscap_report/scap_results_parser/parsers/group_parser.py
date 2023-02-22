# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import re

from ..data_structures import Group
from ..namespaces import NAMESPACES
from .full_text_parser import FullTextParser


class GroupParser:
    def __init__(self, root, ref_values, benchmark_el):
        self.root = root
        self.benchmark_el = benchmark_el
        self.description_parser = FullTextParser(ref_values)
        self.rule_to_group_id = {}
        self.group_to_platforms = {}

    def insert_to_dict_group_to_platforms(self, group_dict, platforms):
        platforms_of_group = list(set(group_dict.get("platforms")) | set(platforms))
        self.group_to_platforms[group_dict.get("group_id")] = platforms_of_group

    @staticmethod
    def _set_title_to_group_dict(group_dict, item):
        group_dict["title"] = item.text

    def _set_description_to_group_dict(self, group_dict, item):
        group_dict["description"] = self.description_parser.get_full_description(item)

    @staticmethod
    def _append_platform_to_group_dict(group_dict, item):
        group_dict["platforms"].append(item.get("idref"))

    def _append_sub_group_to_group_dict(self, group_dict, item):
        group_dict["sub_groups"].append(self.get_group(item, group_dict.get("platforms")))

    def _append_rule_id_to_group_dict(self, group_dict, item):
        group_dict["rules_ids"].append(item.get("id"))
        self.rule_to_group_id[item.get("id")] = group_dict.get("group_id")

    def get_group(self, group_el, platforms=None):
        if platforms is None:
            platforms = []
        group_dict = {
            "platforms": [],
            "rules_ids": [],
            "sub_groups": [],
            "group_id": group_el.get("id"),
        }

        tag_to_function = {
            "title": self._set_title_to_group_dict,
            "description": self._set_description_to_group_dict,
            "platform": self._append_platform_to_group_dict,
            "Group": self._append_sub_group_to_group_dict,
            "Rule": self._append_rule_id_to_group_dict,
        }

        for item in group_el.iterchildren():
            tag_without_namespace_prefix = re.sub(r"{(.*?)}", "", item.tag)
            if tag_without_namespace_prefix in tag_to_function:
                tag_to_function[tag_without_namespace_prefix](group_dict, item)

        self.insert_to_dict_group_to_platforms(group_dict, platforms)
        return Group(**group_dict)

    def get_groups(self):
        groups = {}
        group_el = self.root.find(".//xccdf:Group", NAMESPACES)
        if group_el is None or self.benchmark_el is None:
            return groups

        for item in self.benchmark_el:
            if "Group" in item.tag:
                groups[item.get("id")] = self.get_group(item)
        return groups
