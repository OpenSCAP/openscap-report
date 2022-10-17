
from dataclasses import asdict, dataclass, field

from .oval_node import OvalNode


@dataclass
class OvalDefinition:
    definition_id: str
    title: str
    description: str = ""
    version: str = ""
    references: list = field(default_factory=list)
    oval_tree: OvalNode = None

    def as_dict(self):
        return asdict(self)
