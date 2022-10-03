# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field


@dataclass
class ProfileInfo:
    profile_id: str
    description: str
    title: str
    extends: str = None
    cpe_platforms_for_profile: dict[str, bool] = field(default_factory=dict)
    selected_rules_ids: list = field(default_factory=list)
    selected_groups_ids: list = field(default_factory=list)

    def as_dict(self):
        return asdict(self)
