# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import List

from .oval_node import OvalNode
from .oval_reference import OvalReference

OVAL_DEFINITION_JSON_KEYS = [
    "definition_id",
    "title",
    "description",
    "version",
]

OVAL_CLASS_DESCRIPTION = {
    "compliance": (
        "Compliance class describes OVAL Definitions that check to see if a system's state is "
        'compliant with a specific policy. An evaluation result of "true", for this class of OVAL '
        "Definitions, indicates that a system is compliant with the stated policy."
    ),
    "vulnerability": (
        "Vulnerability class describes OVAL Definitions that check to see if the system is in a "
        'vulnerable state. An evaluation result of "true", for this class of OVAL Definitions, '
        "indicates that the system is in a vulnerable state."
    ),
    "inventory": (
        "Inventory class describes OVAL Definitions that check to see if a piece of software is "
        'installed on a system. An evaluation result of "true", for this class of OVAL '
        "Definitions, indicates that the specified software is installed on the system."
    ),
    "patch": (
        "Patch class describes OVAL Definitions that check to see if a patch should be installed "
        'on a system. An evaluation result of "true", for this class of OVAL Definitions, '
        "indicates that the specified patch should be installed on the system."
    ),
}


@dataclass
class OvalDefinition:
    definition_id: str
    definition_class: str
    title: str
    description: str = ""
    version: str = ""
    references: List[OvalReference] = field(default_factory=list)
    oval_tree: OvalNode = None

    def as_dict(self):
        return asdict(self)

    def get_oval_class_description(self):
        return OVAL_CLASS_DESCRIPTION[self.definition_class]
