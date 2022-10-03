# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import re

from lxml.builder import E

from ..data_structures import ProfileInfo
from ..namespaces import NAMESPACES


class ProfileInfoParser:
    def __init__(self, profiles, results_of_cpe_platforms, benchmark_el):
        self.profiles = profiles
        self.results_of_cpe_platforms = results_of_cpe_platforms
        self.benchmark_el = benchmark_el

    def _selected_rules_and_groups_ids(self, selected_elements):
        groups_ids = []
        rules_ids = []
        for element in selected_elements:
            if element.get("selected") == "false":
                continue
            id_ = element.get("idref")
            if re.match("xccdf_[^_]+_group_.+", id_):
                groups_ids.append(id_)
            elif re.match("xccdf_[^_]+_rule_.+", id_):
                rules_ids.append(id_)
        return {"selected_rules_ids": rules_ids, "selected_groups_ids": groups_ids}

    def _get_cpe_platforms_for_profile(self):
        out = {}
        if self.benchmark_el is None:
            return out
        for element in self.benchmark_el.iterchildren():
            if element.tag.endswith("platform"):
                idref = element.get('idref')
                out[idref] = idref in self.results_of_cpe_platforms
        return out

    def get_profile_info(self, profile_id):
        profile_el = self.profiles.get(profile_id, E.xml("empty"))

        title = profile_el.find('.//xccdf:title', NAMESPACES)
        description = profile_el.find('.//xccdf:description', NAMESPACES)
        profile_info_dict = {
            "profile_id": profile_id,
            "title": title.text if title is not None else "",
            "description": description.text if description is not None else "",
            "extends": profile_el.get("extends", ""),
            "cpe_platforms_for_profile": self._get_cpe_platforms_for_profile()
        }
        selected_elements = profile_el.findall('.//xccdf:select', NAMESPACES)
        extend_profile_el = self.profiles.get(profile_info_dict["extends"], E.xml("empty"))
        selected_elements.extend(extend_profile_el.findall('.//xccdf:select', NAMESPACES))
        return ProfileInfo(
            **profile_info_dict, **self._selected_rules_and_groups_ids(selected_elements)
        )
