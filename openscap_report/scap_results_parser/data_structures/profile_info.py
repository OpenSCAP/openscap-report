# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import Dict, List

PROFILE_JSON_KEYS = [
    "profile_id",
    "description",
    "title",
    "extends",
]


@dataclass
class ProfileInfo:
    profile_id: str
    description: str
    title: str
    extends: str = None
    cpe_platforms_for_profile: Dict[str, bool] = field(default_factory=dict)
    selected_rules_ids: List[str] = field(default_factory=list)
    selected_groups_ids: List[str] = field(default_factory=list)

    def as_dict(self):
        return asdict(self)

    def get_applicable_cpe_platforms_for_profile(self):
        return ", ".join(self.cpe_platforms_for_profile.keys())

    def get_cpe_platforms_that_satisfy_evaluation_target(self):
        return ", ".join(self.get_list_of_cpe_platforms_that_satisfy_evaluation_target())

    def get_list_of_cpe_platforms_that_satisfy_evaluation_target(self):
        return [
            cpe_id for cpe_id, is_satisfy in self.cpe_platforms_for_profile.items() if is_satisfy
        ]

    def deselect_rules(self, rule_ids):
        for rule_id in rule_ids:
            if rule_id in self.selected_rules_ids:
                self.selected_rules_ids.remove(rule_id)

    def select_rules(self, rule_ids):
        if len(self.selected_rules_ids) > 0:
            self.selected_rules_ids.extend(rule_ids)
