
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
