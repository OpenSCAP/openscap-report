# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

import pytest

from openscap_report.scap_results_parser import MissingProcessableRules
from openscap_report.scap_results_parser.data_structures import Remediation
from tests.unit_tests.test_scap_result_parser import get_parser

from ..constants import PATH_TO_ARF


def get_report():
    parser = get_parser(PATH_TO_ARF)
    return parser.parse_report()


def remove_all_rules_by_result(report, result=()):
    new_rules = {}
    for rule_id, rule in report.rules.items():
        if rule.result.lower() not in result:
            new_rules[rule_id] = rule
    report.rules = new_rules
    return report


def remove_all_rules_by_severity(report, severity=()):
    new_rules = {}
    for rule_id, rule in report.rules.items():
        if rule.severity.lower() not in severity:
            new_rules[rule_id] = rule
    report.rules = new_rules
    return report


@pytest.mark.unit_test
@pytest.mark.parametrize("to_remove, result", [
    (
        (),
        {"fail": 442, "pass": 191, "unknown_error": 0, "other": 69, "sum_of_rules": 702}
    ),
    (
        ("fail", "pass"),
        {"fail": 0, "pass": 0, "unknown_error": 0, "other": 69, "sum_of_rules": 69}
    ),
    (
        ("fail"),
        {"fail": 0, "pass": 191, "unknown_error": 0, "other": 69, "sum_of_rules": 260}
    ),
    (
        ("fail", "notchecked"),
        {"fail": 0, "pass": 191, "unknown_error": 0, "other": 0, "sum_of_rules": 191}
    ),
    (
        ("pass"),
        {"fail": 442, "pass": 0, "unknown_error": 0, "other": 69, "sum_of_rules": 511}
    ),
    (
        ("pass", "notchecked"),
        {"fail": 442, "pass": 0, "unknown_error": 0, "other": 0, "sum_of_rules": 442}
    ),
    (
        ("notchecked"),
        {"fail": 442, "pass": 191, "unknown_error": 0, "other": 0, "sum_of_rules": 633}
    ),
    (
        ("error", "unknown"),
        {"fail": 442, "pass": 191, "unknown_error": 0, "other": 69, "sum_of_rules": 702}
    ),
    (
        ("notselected", "notapplicable"),
        {"fail": 442, "pass": 191, "unknown_error": 0, "other": 69, "sum_of_rules": 702}
    ),
])
def test_report_rule_results_stats(to_remove, result):
    report = remove_all_rules_by_result(get_report(), to_remove)
    rule_results_stats = report.get_rule_results_stats()
    for key in result:
        assert result[key] == rule_results_stats[key]


@pytest.mark.unit_test
@pytest.mark.parametrize("to_remove", [
    ("fail", "pass", "notchecked", "error", "unknown", "error"),
    ("fail", "pass", "notchecked"),
])
def test_report_rule_results_stats_without_processable_rules(to_remove, caplog):
    report = remove_all_rules_by_result(get_report(), to_remove)
    caplog.set_level(logging.WARNING)
    report.get_rule_results_stats()
    assert 'There are no applicable or selected rules.' in caplog.text


@pytest.mark.unit_test
@pytest.mark.parametrize("to_remove, result", [
    (
        (),
        {"low": 33, "medium": 351, "high": 25, "unknown": 33, "sum_of_failed_rules": 442}
    ),
    (
        ("low"),
        {"low": 0, "medium": 351, "high": 25, "unknown": 33, "sum_of_failed_rules": 409}
    ),
    (
        ("medium"),
        {"low": 33, "medium": 0, "high": 25, "unknown": 33, "sum_of_failed_rules": 91}
    ),
    (
        ("high"),
        {"low": 33, "medium": 351, "high": 0, "unknown": 33, "sum_of_failed_rules": 417}
    ),
    (
        ("unknown"),
        {"low": 33, "medium": 351, "high": 25, "unknown": 0, "sum_of_failed_rules": 409}
    ),
    (
        ("low", "medium"),
        {"low": 0, "medium": 0, "high": 25, "unknown": 33, "sum_of_failed_rules": 58}
    ),
    (
        ("high", "unknown"),
        {"low": 33, "medium": 351, "high": 0, "unknown": 0, "sum_of_failed_rules": 384}
    ),
    (
        ("medium", "high"),
        {"low": 33, "medium": 0, "high": 0, "unknown": 33, "sum_of_failed_rules": 66}
    ),
    (
        ("low", "unknown"),
        {"low": 0, "medium": 351, "high": 25, "unknown": 0, "sum_of_failed_rules": 376}
    ),
    (
        ("low", "medium", "high"),
        {"low": 0, "medium": 0, "high": 0, "unknown": 33, "sum_of_failed_rules": 33}
    ),
    (
        ("low", "medium", "unknown"),
        {"low": 0, "medium": 0, "high": 25, "unknown": 0, "sum_of_failed_rules": 25}
    ),
    (
        ("low", "high", "unknown"),
        {"low": 0, "medium": 351, "high": 0, "unknown": 0, "sum_of_failed_rules": 351}
    ),
    (
        ("medium", "high", "unknown"),
        {"low": 33, "medium": 0, "high": 0, "unknown": 0, "sum_of_failed_rules": 33}
    ),
])
def test_report_severity_of_failed_rules_stats(to_remove, result):
    report = remove_all_rules_by_severity(get_report(), to_remove)
    severity_of_failed_rules_stats = report.get_severity_of_failed_rules_stats()
    for key in result:
        assert result[key] == severity_of_failed_rules_stats[key]


@pytest.mark.unit_test
def test_report_severity_of_failed_rules_without_any_rules():
    report = remove_all_rules_by_severity(get_report(), ("low", "medium", "high", "unknown"))
    with pytest.raises(MissingProcessableRules):
        assert report.get_severity_of_failed_rules_stats()


@pytest.mark.unit_test
def test_report_severity_of_failed_rules_stats_without_failed_rules():
    report = remove_all_rules_by_result(get_report(), ("fail"))
    with pytest.raises(MissingProcessableRules):
        assert report.get_severity_of_failed_rules_stats()


@pytest.mark.unit_test
@pytest.mark.parametrize("system, type_of_remediation", [
    ("Unknown_system", "script"),
    ("urn:xccdf:fix:script:sh", "Shell script"),
    ("urn:xccdf:fix:script:ansible", "Ansible snippet"),
    ("urn:xccdf:fix:script:puppet", "Puppet snippet"),
    ("urn:redhat:anaconda:pre", "Anaconda snippet"),
    ("urn:xccdf:fix:script:kubernetes", "Kubernetes snippet"),
    ("urn:redhat:osbuild:blueprint", "OSBuild Blueprint snippet"),
    ("urn:xccdf:fix:script:pejskoskript", "script"),
])
def test_remediation_type(system, type_of_remediation):
    remediation = Remediation(system=system)
    assert remediation.get_type() == type_of_remediation
