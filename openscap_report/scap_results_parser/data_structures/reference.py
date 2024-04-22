# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from openscap_report.dataclasses import asdict, dataclass
from typing import List

REFERENCE_JSON_KEYS = [
    "name",
    "href",
    "ref_ids",
]


@dataclass
class Reference:
    name: str
    href: str
    ref_ids: List[str]

    def as_dict(self):
        return asdict(self)
