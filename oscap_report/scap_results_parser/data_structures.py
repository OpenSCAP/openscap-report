from dataclasses import dataclass


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
        percent_per_rule = 100 / not_ignored_rules
        results_stats["other"] = not_ignored_rules - results_stats["fail"] - results_stats['pass']
        results_stats["fail_percent"] = results_stats["fail"] * percent_per_rule
        results_stats["pass_percent"] = results_stats["pass"] * percent_per_rule
        results_stats["other_percent"] = results_stats["other"] * percent_per_rule
        return results_stats

    def get_severity_of_failed_rules_stats(self):
        failed_rules = list(
            filter(lambda rule: rule.result.lower() == "fail", self.rules.values()))
        percent_per_rule = 100 / len(failed_rules)
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
        return severity_stats


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
