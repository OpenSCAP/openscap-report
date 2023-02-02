# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field

GROUP_JSON_KEYS = [
    "group_id",
    "title",
    "description",
    "platforms",
    "rules_ids",
    "sub_groups",
]


@dataclass
class Group:
    group_id: str
    title: str = ""
    description: str = ""
    platforms: list[str] = field(default_factory=list)
    rules_ids: list[str] = field(default_factory=list)
    sub_groups: list['Group'] = field(default_factory=list)

    def as_dict(self):
        return asdict(self)
