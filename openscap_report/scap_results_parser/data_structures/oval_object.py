# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import Dict

from openscap_report.dataclasses import asdict, dataclass, field
from openscap_report.scap_results_parser.data_structures.oval_items import \
    OVALItems


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
    collected_items: OVALItems = None

    def as_dict(self):
        return asdict(self)
