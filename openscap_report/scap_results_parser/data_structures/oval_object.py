# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import Dict


@dataclass
class OvalObjectMessage:
    level: str
    text: str


@dataclass
class OvalObject:
    object_id: str
    flag: str = ""
    message: OvalObjectMessage = None
    comment: str = ""
    object_type: str = ""
    object_data: Dict[str, str] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)
