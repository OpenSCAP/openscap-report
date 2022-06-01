# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass


@dataclass
class Remediation:
    remediation_id: str = ""
    system: str = ""
    complexity: str = ""
    disruption: str = ""
    strategy: str = ""
    fix: str = ""

    def as_dict(self):
        return {
            "remediation_id": self.remediation_id,
            "system": self.system,
            "complexity": self.complexity,
            "disruption": self.disruption,
            "strategy": self.strategy,
            "fix": self.fix,
        }

    def get_type(self):
        script_types = {
            "urn:xccdf:fix:script:sh": "Shell script",
            "urn:xccdf:fix:script:ansible": "Ansible snippet",
            "urn:xccdf:fix:script:puppet": "Puppet snippet",
            "urn:redhat:anaconda:pre": "Anaconda snippet",
            "urn:xccdf:fix:script:kubernetes": "Kubernetes snippet",
            "urn:redhat:osbuild:blueprint": "OSBuild Blueprint snippet",
        }
        return script_types.get(self.system, "script")
