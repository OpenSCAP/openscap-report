# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Union

from .oval_object import OvalObject
from .oval_state import OvalState
from .oval_variable import OvalVariable


@dataclass
class OvalTest:  # pylint: disable=R0902
    test_id: str
    check_existence: str = ""
    check: str = ""
    test_type: str = ""
    comment: str = ""
    oval_object: OvalObject = None
    oval_states: List[OvalState] = field(default_factory=list)
    referenced_oval_endpoints: Dict[
        str, Union[OvalObject, OvalState, OvalVariable]
    ] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)
