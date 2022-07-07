# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass

from .oval_node import OvalNode
from .remediation import Remediation


@dataclass
class Identifier:
    system: str
    text: str

    def as_dict(self):
        return asdict(self)


@dataclass
class Reference:
    href: str
    text: str

    def as_dict(self):
        return asdict(self)


@dataclass
class Rule:  # pylint: disable=R0902
    rule_id: str
    title: str = ""
    result: str = ""
    multi_check: bool = False
    time: str = ""
    severity: str = ""
    identifiers: list[Identifier] = None
    references: list[Reference] = None
    description: str = ""
    rationale: str = ""
    warnings: list[str] = None
    platforms: list[str] = None
    oval_definition_id: str = None
    messages: list[str] = None
    remediations: list[Remediation] = None
    oval_tree: OvalNode = None
    cpe_tree: OvalNode = None

    def as_dict(self):
        return asdict(self)
