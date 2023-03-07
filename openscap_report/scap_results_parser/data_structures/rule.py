# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import Dict, List

from .cpe_platform import Platform
from .identifier import Identifier
from .oval_definition import OvalDefinition
from .oval_node import OvalNode
from .reference import Reference
from .remediation import Remediation
from .warning import RuleWarning

RULE_JSON_KEYS = [
    "rule_id",
    "title",
    "result",
    "time",
    "severity",
    "weight",
    "identifiers",
    "references",
    "description",
    "rationale",
    "warnings",
    "platforms",
    "oval_definition_id",
    "messages",
    "remediations",
]


@dataclass
class Rule:  # pylint: disable=R0902
    rule_id: str
    title: str = ""
    result: str = ""
    multi_check: bool = False
    time: str = ""
    severity: str = ""
    weight: float = 0.0
    identifiers: List[Identifier] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    description: str = ""
    rationale: str = ""
    warnings: List[RuleWarning] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    oval_definition_id: str = None
    oval_reference: str = None
    oval_definition: OvalDefinition = None
    messages: List[str] = field(default_factory=list)
    remediations: List[Remediation] = field(default_factory=list)
    cpe_oval_dict: Dict[str, Dict[str, OvalNode]] = field(default_factory=dict)
    cpe_al: Dict[str, Dict[str, Platform]] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)
