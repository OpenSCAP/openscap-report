# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
from dataclasses import asdict, dataclass, field

from ..exceptions import MissingProcessableRules
from .group import Group
from .profile_info import ProfileInfo
from .result_of_scan import ResultOfScan
from .rule import Rule


@dataclass
class Report:
    profile_info: ProfileInfo = field(default_factory=ProfileInfo)
    scan_result: ResultOfScan = field(default_factory=ResultOfScan)
    rules: dict[str, Rule] = field(default_factory=dict)
    groups: dict[str, Group] = field(default_factory=dict)

    @staticmethod
    def default_json_filter(dictionary):
        allowed_keys = [
            "title",
            "profile_name",
            "cpe_platforms",
            "scanner",
            "benchmark_id",
            "score"
        ]
        return {key: value for (key, value) in dictionary if key in allowed_keys}

    def as_dict_for_default_json(self):
        return asdict(self, dict_factory=self.default_json_filter)

    def as_dict(self):
        return asdict(self)

    def get_selected_rules(self):
        if not self.profile_info.selected_rules_ids:
            return [
                (rule_id, rule)
                for rule_id, rule in self.rules.items()
                if rule.result != "notselected"
            ]
        return [
            (rule_id, self.rules[rule_id])
            for rule_id in self.profile_info.selected_rules_ids
        ]

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
