# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass


@dataclass
class Group:
    group_id: str = ""
    title: str = ""
    description: str = ""
    platforms: list = None
    rules_ids: list = None
    sub_groups: list = None

    def as_dict(self):
        return asdict(self)
