# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field

from .cpe_platform import Platform
from .identifier import Identifier
from .oval_definition import OvalDefinition
from .oval_node import OvalNode
from .reference import Reference
from .remediation import Remediation


@dataclass
class Rule:  # pylint: disable=R0902
    rule_id: str
    title: str = ""
    result: str = ""
    multi_check: bool = False
    time: str = ""
    severity: str = ""
    identifiers: list[Identifier] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    description: str = ""
    rationale: str = ""
    warnings: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    oval_definition_id: str = None
    oval_definition: OvalDefinition = None
    messages: list[str] = field(default_factory=list)
    remediations: list[Remediation] = field(default_factory=list)
    cpe_oval_dict: dict[str, dict[str, OvalNode]] = field(default_factory=dict)
    cpe_al: dict[str, dict[str, Platform]] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)
