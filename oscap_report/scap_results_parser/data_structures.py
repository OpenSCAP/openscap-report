import json
import logging
from dataclasses import dataclass

from .exceptions import MissingProcessableRules


@dataclass
class Report:  # pylint: disable=R0902
    title: str = ""
    identity: str = ""
    profile_name: str = ""
    target: str = ""
    cpe_platforms: str = ""
    scanner: str = ""
    scanner_version: str = ""
    benchmark_url: str = ""
    benchmark_id: str = ""
    benchmark_version: str = ""
    start_time: str = ""
    end_time: str = ""
    test_system: str = ""
    score: float = 0.0
    score_max: float = 0.0
    rules: dict = None

    def as_dict(self):
        return {
            "title": self.title,
            "profile_name": self.profile_name,
            "target": self.target,
            "identit": self.identity,
            "cpe_platforms": self.cpe_platforms,
            "scanner": self.scanner,
            "scanner_version": self.scanner_version,
            "benchmark_url": self.benchmark_url,
            "benchmark_id": self.benchmark_id,
            "benchmark_version": self.benchmark_version,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "test_system": self.test_system,
            "score": self.score,
            "score_max": self.score_max,
            "rules": self.rules,
        }

    def get_rule_results_stats(self):
        results_stats = {
            "fail": len(list(
                filter(lambda rule: rule.result.lower() == "fail", self.rules.values()))),
            "pass": len(list(
                filter(lambda rule: rule.result.lower() == "pass", self.rules.values()))),
            "unknown_error": len(list(
                filter(lambda rule:
                       rule.result.lower() in ("error", "unknown"), self.rules.values()))),
        }
        not_ignored_rules = len(list(
            filter(
                lambda rule: rule.result.lower() not in ("notselected", "notapplicable"),
                self.rules.values()
            )))
        if not_ignored_rules == 0:
            raise MissingProcessableRules("There are no applicable or selected rules.")
        percent_per_rule = 100 / not_ignored_rules
        results_stats["other"] = not_ignored_rules - results_stats["fail"] - results_stats['pass']
        results_stats["fail_percent"] = results_stats["fail"] * percent_per_rule
        results_stats["pass_percent"] = results_stats["pass"] * percent_per_rule
        results_stats["other_percent"] = results_stats["other"] * percent_per_rule
        results_stats["sum_of_rules"] = not_ignored_rules
        return results_stats

    def get_severity_of_failed_rules_stats(self):
        failed_rules = self.get_failed_rules()
        count_of_failed_rules = len(failed_rules)
        if count_of_failed_rules == 0:
            raise MissingProcessableRules("There are no failed rules!")
        percent_per_rule = 100 / count_of_failed_rules
        severity_stats = {
            "low": sum(map(lambda rule: rule.severity.lower() == "low", failed_rules)),
            "medium": sum(map(lambda rule: rule.severity.lower() == "medium", failed_rules)),
            "high": sum(map(lambda rule: rule.severity.lower() == "high", failed_rules)),
            "unknown": sum(map(lambda rule: rule.severity.lower() == "unknown", failed_rules)),
        }
        severity_stats["low_percent"] = severity_stats["low"] * percent_per_rule
        severity_stats["medium_percent"] = severity_stats["medium"] * percent_per_rule
        severity_stats["high_percent"] = severity_stats["high"] * percent_per_rule
        severity_stats["unknown_percent"] = severity_stats["unknown"] * percent_per_rule
        severity_stats["sum_of_filed_rules"] = len(failed_rules)
        return severity_stats

    def get_failed_rules(self):
        return list(filter(lambda rule: rule.result.lower() == "fail", self.rules.values()))


@dataclass
class OvalObject():
    object_id: str = ""
    flag: str = ""
    object_type: str = ""
    object_data: dict = None

    def as_dict(self):
        return {
            "object_id": self.object_id,
            "flag": self.flag,
            "object_type": self.object_type,
            "object_data": self.object_data,
        }


@dataclass
class OvalTest():
    test_id: str = ""
    test_type: str = ""
    comment: str = ""
    oval_object: OvalObject = None

    def as_dict(self):
        return {
            "test_id": self.test_id,
            "test_type": self.test_type,
            "comment": self.comment,
            "oval_object": self.oval_object.as_dict(),
        }


@dataclass
class OvalNode:  # pylint: disable=R0902
    node_id: str
    node_type: str
    value: str
    negation: bool = False
    comment: str = ""
    tag: str = ""
    children: list = None
    test_info: OvalTest = None

    def as_dict(self):
        if not self.children:
            return {
                'node_id': self.node_id,
                'node_type': self.node_type,
                'value': self.value,
                'negation': self.negation,
                'comment': self.comment,
                'tag': self.tag,
                'test_info': self.test_info.as_dict(),
                'children': None
            }
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'value': self.value,
            'negation': self.negation,
            'comment': self.comment,
            'tag': self.tag,
            'test_info': None,
            'children': [child.as_dict() for child in self.children]
        }

    def as_json(self):
        return json.dumps(self.as_dict())

    def log_oval_tree(self, level=0):
        out = ""
        if self.node_type != "value":
            out = "  " * level + self.node_type + " = " + self.value
        else:
            out = "  " * level + self.node_id + " = " + self.value
        logging.info(out)
        if self.children is not None:
            for child in self.children:
                child.log_oval_tree(level + 1)


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
    platform: str = ""
    oval_definition_id: str = ""
    message: str = ""
    remediations: list = None
    oval_tree: OvalNode = None

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
            "platform": self.platform,
            "oval_definition_id": self.oval_definition_id,
            "message": self.message,
            "remediations": self.remediations,
            "oval_tree": self.oval_tree,
        }


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
        if self.system == "urn:xccdf:fix:script:sh":
            return "Shell script"
        if self.system == "urn:xccdf:fix:script:ansible":
            return "Ansible snippet"
        if self.system == "urn:xccdf:fix:script:puppet":
            return "Puppet snippet"
        if self.system == "urn:redhat:anaconda:pre":
            return "Anaconda snippet"
        if self.system == "urn:xccdf:fix:script:kubernetes":
            return "Kubernetes snippet"
        return self.system
