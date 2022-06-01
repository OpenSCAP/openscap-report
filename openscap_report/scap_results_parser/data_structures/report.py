# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
from dataclasses import dataclass

from ..exceptions import MissingProcessableRules


@dataclass
class Report:  # pylint: disable=R0902
    title: str = ""
    identity: str = ""
    profile_name: str = ""
    platform: str = ""
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
    groups: dict = None

    def as_dict(self):
        return {
            "title": self.title,
            "profile_name": self.profile_name,
            "platform": self.platform,
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
            "groups": self.groups,
        }

    def get_rule_results_stats(self):
        results_stats = {
            "fail": len(list(
                filter(lambda rule: rule.result.lower() == "fail", self.rules.values()))),
            "pass": len(list(
                filter(
                    lambda rule: rule.result.lower() in ("pass", "fixed"), self.rules.values()))),
            "unknown_error": len(list(
                filter(
                    lambda rule: rule.result.lower() in (
                        "error", "unknown", "fix unsuccessful", "fix failed"
                    ), self.rules.values()))),
        }
        not_ignored_rules = len(list(
            filter(
                lambda rule: rule.result.lower() not in ("notselected", "notapplicable"),
                self.rules.values()
            )))
        if not_ignored_rules == 0:
            not_ignored_rules = 1
            logging.warning("There are no applicable or selected rules.")
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
        severity_stats["sum_of_failed_rules"] = len(failed_rules)
        return severity_stats

    def get_failed_rules(self):
        return list(filter(lambda rule: rule.result.lower() == "fail", self.rules.values()))
