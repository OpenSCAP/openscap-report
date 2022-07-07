# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass


@dataclass
class OvalObject():
    object_id: str = ""
    flag: str = ""
    object_type: str = ""
    object_data: dict = None

    def as_dict(self):
        return asdict(self)
