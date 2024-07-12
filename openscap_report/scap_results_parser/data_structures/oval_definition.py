# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import List

from openscap_report.dataclasses import asdict, dataclass, field

from .oval_node import OvalNode
from .oval_reference import OvalReference

OVAL_DEFINITION_JSON_KEYS = [
    "definition_id",
    "title",
    "description",
    "version",
]


@dataclass
class OvalDefinition:
    definition_id: str
    title: str
    description: str = ""
    version: str = ""
    references: List[OvalReference] = field(default_factory=list)
    oval_tree: OvalNode = None

    def as_dict(self):
        return asdict(self)
