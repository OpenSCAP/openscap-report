# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import List

from .oval_object import OvalObject
from .oval_state import OvalState


@dataclass
class OvalTest:
    test_id: str
    check_existence: str = ""
    check: str = ""
    test_type: str = ""
    comment: str = ""
    oval_object: OvalObject = None
    oval_states: List[OvalState] = field(default_factory=list)

    def as_dict(self):
        return asdict(self)
