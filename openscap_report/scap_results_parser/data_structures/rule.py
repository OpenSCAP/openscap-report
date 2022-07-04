# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass

from .oval_node import OvalNode


@dataclass
class Rule:  # pylint: disable=R0902
    rule_id: str = ""
    title: str = ""
    result: str = ""
    multi_check: bool = False
    time: str = ""
    severity: str = ""
    identifiers: list = None
    references: list = None
    description: str = ""
    rationale: str = ""
    warnings: list = None
    platforms: list = None
    oval_definition_id: str = ""
    message: str = ""
    remediations: list = None
    oval_tree: OvalNode = None
    cpe_tree: OvalNode = None

    def as_dict(self):
        return asdict(self)
