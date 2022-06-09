# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass


@dataclass
class Group:
    group_id: str = ""
    title: str = ""
    description: str = ""
    platforms: list = None
    rules_ids: list = None
    sub_groups: list = None

    def as_dict(self):
        if not self.sub_groups:
            return {
                "group_id": self.group_id,
                "title": self.title,
                "description": self.description,
                "platforms": self.platforms,
                "rules_ids": self.rules_ids,
                "sub_groups": None,
            }
        return {
            "group_id": self.group_id,
            "title": self.title,
            "description": self.description,
            "platforms": self.platforms,
            "rules_ids": self.rules_ids,
            "sub_groups": [sub_group.as_dict() for sub_group in self.sub_groups],
        }
