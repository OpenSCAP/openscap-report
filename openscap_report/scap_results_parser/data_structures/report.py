# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
from dataclasses import asdict, dataclass, field
from typing import Dict

from ..exceptions import MissingProcessableRules
from .group import GROUP_JSON_KEYS, Group
from .identifier import IDENTIFIER_JSON_KEYS
from .json_transformation import (rearrange_identifiers, rearrange_references,
                                  remove_empty_values,
                                  remove_not_selected_rules)
from .oval_definition import OVAL_DEFINITION_JSON_KEYS
from .profile_info import PROFILE_JSON_KEYS, ProfileInfo
from .reference import REFERENCE_JSON_KEYS
from .remediation import REMEDIATION_JSON_KEYS
from .result_of_scan import SCAN_JSON_KEYS, ResultOfScan
from .rule import RULE_JSON_KEYS, Rule
from .warning import WARNING_JSON_KEYS

JSON_REPORT_CONTENT = [
    "profile_info",
    "scan_result",
    "rules",
    *GROUP_JSON_KEYS,
    *IDENTIFIER_JSON_KEYS,
    *OVAL_DEFINITION_JSON_KEYS,
    *PROFILE_JSON_KEYS,
    *REFERENCE_JSON_KEYS,
    *REMEDIATION_JSON_KEYS,
    *RULE_JSON_KEYS,
    *SCAN_JSON_KEYS,
    *WARNING_JSON_KEYS,
]


@dataclass
class Report:
    profile_info: ProfileInfo = field(default_factory=ProfileInfo)
    scan_result: ResultOfScan = field(default_factory=ResultOfScan)
    rules: Dict[str, Rule] = field(default_factory=dict)
    groups: Dict[str, Group] = field(default_factory=dict)

    @staticmethod
    def default_json_filter(dictionary):
        return {key: value for (key, value) in dictionary if key in JSON_REPORT_CONTENT}

    def as_dict_for_default_json(self):
        json_dict = asdict(self, dict_factory=self.default_json_filter)
        remove_not_selected_rules(json_dict, self.profile_info.selected_rules_ids)
        rearrange_references(json_dict)
        rearrange_identifiers(json_dict)
        json_dict = remove_empty_values(json_dict)
        return json_dict

    def as_dict(self):
        return asdict(self)

    def get_selected_rules(self):
        if not self.profile_info.selected_rules_ids:
            return [
                (rule_id, rule)
                for rule_id, rule in self.rules.items()
                if rule.result != "notselected"
            ]
        out = []
        for rule_id in self.profile_info.selected_rules_ids:
            if rule_id in self.rules:
                out.append((rule_id, self.rules[rule_id]))
            else:
                logging.warning("Missing definition of selected rule: '%s'", rule_id)
        return out

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
