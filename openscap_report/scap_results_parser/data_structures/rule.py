# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass

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
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "result": self.result,
            "multi_check": self.multi_check,
            "time": self.time,
            "severity": self.severity,
            "identifiers": self.identifiers,
            "references": self.references,
            "description": self.description,
            "rationale": self.rationale,
            "warnings": self.warnings,
            "platforms": self.platforms,
            "oval_definition_id": self.oval_definition_id,
            "message": self.message,
            "remediations": self.remediations,
            "oval_tree": self.oval_tree.as_dict(),
            "cpe_tree": self.cpe_tree.as_dict(),
        }
