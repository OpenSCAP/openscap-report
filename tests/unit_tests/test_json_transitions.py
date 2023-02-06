# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later


import pytest

from openscap_report.scap_results_parser.data_structures.json_transformation import (
    is_not_empty, rearrange_identifiers, rearrange_references,
    remove_empty_values, remove_not_selected_rules)


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "dictionary_json, result",
    [
        (
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "identifiers": [
                            {
                                "text": "CCE-90841-8",
                                "system": "random-link.com",
                            }
                        ],
                        "references": [
                            {
                                "text": "11",
                                "href": "idk-link.com",
                            }
                        ],
                    }
                }
            },
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "identifiers": [
                            {
                                "text": "CCE-90841-8",
                                "system": "random-link.com",
                            }
                        ],
                        "references": [
                            "11",
                        ],
                    }
                },
                "references": {"11": "idk-link.com"},
            },
        )
    ],
)
def test_rearrange_references(dictionary_json, result):
    rearrange_references(dictionary_json)
    assert dictionary_json == result


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "dictionary_json, result",
    [
        (
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "identifiers": [
                            {
                                "text": "CCE-90841-8",
                                "system": "random-link.com",
                            }
                        ],
                        "references": [
                            {
                                "text": "11",
                                "href": "idk-link.com",
                            }
                        ],
                    }
                }
            },
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "identifiers": ["CCE-90841-8"],
                        "references": [
                            {
                                "text": "11",
                                "href": "idk-link.com",
                            }
                        ],
                    }
                },
                "identifiers": {"CCE-90841-8": "random-link.com"},
            },
        )
    ],
)
def test_rearrange_identifiers(dictionary_json, result):
    rearrange_identifiers(dictionary_json)
    assert dictionary_json == result


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "val, result",
    [
        (None, False),
        ([], False),
        ({}, False),
        (1.3, True),
        (0.0, True),
        (-1.3, True),
        (["a", "b"], True),
        ({"a": "b", "c": "d"}, True),
    ],
)
def test_is_not_empty(val, result):
    assert is_not_empty(val) == result


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "dictionary_json, ids_of_selected_rules, result",
    [
        (
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                    "rule_a": {
                        "rule_id": "rule_a",
                        "result": "notselected",
                    },
                }
            },
            ["xccdf_org.ssgproject.content_rule_rpm_verify_hashes"],
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                }
            },
        ),
        (
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                    "rule_a": {
                        "rule_id": "rule_a",
                        "result": "notselected",
                    },
                }
            },
            [],
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                }
            },
        ),
        (
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                    "rule_a": {
                        "rule_id": "rule_a",
                        "result": "fail",
                    },
                }
            },
            ["xccdf_org.ssgproject.content_rule_rpm_verify_hashes"],
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                }
            },
        ),
        (
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                    "rule_a": {
                        "rule_id": "rule_a",
                        "result": "fail",
                    },
                }
            },
            ["xccdf_org.ssgproject.content_rule_rpm_verify_hashes", "rule_a"],
            {
                "rules": {
                    "xccdf_org.ssgproject.content_rule_rpm_verify_hashes": {
                        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
                        "result": "pass",
                    },
                    "rule_a": {
                        "rule_id": "rule_a",
                        "result": "fail",
                    },
                }
            },
        ),
    ],
)
def test_remove_not_selected_rules(dictionary_json, ids_of_selected_rules, result):
    remove_not_selected_rules(dictionary_json, ids_of_selected_rules)
    assert dictionary_json == result


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "dictionary, result",
    [
        ({"a": "", "b": {"c": ""}, "x": "x"}, {"x": "x"}),
        ({"a": "a", "b": "", "x": "x"}, {"a": "a", "x": "x"}),
        ({"a": [], "x": "x"}, {"x": "x"}),
        ({"a": {}, "x": "x"}, {"x": "x"}),
        ({"a": 3.14, "b": {}, "x": "x"}, {"a": 3.14, "x": "x"}),
        (
            {"a": "", "b": {"c": {"z": "y"}, "m": "o"}, "x": "x"},
            {"b": {"c": {"z": "y"}, "m": "o"}, "x": "x"},
        ),
    ],
)
def test_remove_empty_values(dictionary, result):
    assert remove_empty_values(dictionary) == result
