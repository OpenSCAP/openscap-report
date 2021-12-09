import pytest

from oscap_report.scap_results_parser.data_structures import Report, Rule
from oscap_report.scap_results_parser.scap_results_parser import \
    SCAPResultsParser

from ..constants import (PATH_TO_ARF, PATH_TO_ARF_WITH_MULTI_CHECK,
                         PATH_TO_ARF_WITHOUT_INFO,
                         PATH_TO_ARF_WITHOUT_SYSTEM_DATA,
                         PATH_TO_EMPTY_XML_FILE,
                         PATH_TO_RULE_AND_CPE_CHECK_ARF,
                         PATH_TO_RULE_AND_CPE_CHECK_XCCDF,
                         PATH_TO_SIMPLE_RULE_FAIL_ARF,
                         PATH_TO_SIMPLE_RULE_FAIL_XCCDF,
                         PATH_TO_SIMPLE_RULE_PASS_ARF,
                         PATH_TO_SIMPLE_RULE_PASS_XCCDF, PATH_TO_XCCDF,
                         PATH_TO_XCCDF_WITH_MULTI_CHECK,
                         PATH_TO_XCCDF_WITHOUT_INFO,
                         PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA)


def get_parser(file_path):
    xml_data = None
    with open(file_path, "r", encoding="utf-8") as xml_report:
        xml_data = xml_report.read().encode()
    return SCAPResultsParser(xml_data)


@pytest.mark.parametrize("file_path, result", [
    (PATH_TO_ARF, True),
    (PATH_TO_SIMPLE_RULE_PASS_ARF, True),
    (PATH_TO_SIMPLE_RULE_FAIL_ARF, True),
    (PATH_TO_RULE_AND_CPE_CHECK_ARF, True),
    (PATH_TO_ARF_WITHOUT_INFO, True),
    (PATH_TO_ARF_WITHOUT_SYSTEM_DATA, True),
    (PATH_TO_XCCDF, False),
    (PATH_TO_SIMPLE_RULE_PASS_XCCDF, False),
    (PATH_TO_SIMPLE_RULE_FAIL_XCCDF, False),
    (PATH_TO_RULE_AND_CPE_CHECK_XCCDF, False),
    (PATH_TO_XCCDF_WITHOUT_INFO, False),
    (PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA, False),
    (PATH_TO_EMPTY_XML_FILE, False),
])
def test_validation(file_path, result):
    parser = get_parser(file_path)
    assert parser.validate(parser.arf_schemas_path) == result


@pytest.mark.parametrize("file_path, number_of_cpe_platforms", [
    (PATH_TO_ARF, 13),
    (PATH_TO_XCCDF, 13),
    (PATH_TO_SIMPLE_RULE_PASS_ARF, 0),
    (PATH_TO_SIMPLE_RULE_FAIL_ARF, 0),
    (PATH_TO_ARF_WITHOUT_INFO, 0),
    (PATH_TO_ARF_WITHOUT_SYSTEM_DATA, 0),
    (PATH_TO_RULE_AND_CPE_CHECK_ARF, 1),
    (PATH_TO_SIMPLE_RULE_PASS_XCCDF, 0),
    (PATH_TO_SIMPLE_RULE_FAIL_XCCDF, 0),
    (PATH_TO_XCCDF_WITHOUT_INFO, 0),
    (PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA, 0),
    (PATH_TO_RULE_AND_CPE_CHECK_XCCDF, 1),
])
def test_get_profile_info(file_path, number_of_cpe_platforms):
    parser = get_parser(file_path)
    report = parser.get_profile_info()
    assert len(report.cpe_platforms) == number_of_cpe_platforms


@pytest.mark.parametrize("file_path, number_of_rules", [
    (PATH_TO_ARF, 714),
    (PATH_TO_XCCDF, 714),
    (PATH_TO_SIMPLE_RULE_PASS_ARF, 1),
    (PATH_TO_SIMPLE_RULE_FAIL_ARF, 1),
    (PATH_TO_ARF_WITHOUT_INFO, 1),
    (PATH_TO_ARF_WITHOUT_SYSTEM_DATA, 1),
    (PATH_TO_RULE_AND_CPE_CHECK_ARF, 3),
    (PATH_TO_SIMPLE_RULE_PASS_XCCDF, 1),
    (PATH_TO_SIMPLE_RULE_FAIL_XCCDF, 1),
    (PATH_TO_XCCDF_WITHOUT_INFO, 1),
    (PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA, 1),
    (PATH_TO_RULE_AND_CPE_CHECK_XCCDF, 3),
])
def test_get_info_about_rules_in_profile(file_path, number_of_rules):
    parser = get_parser(file_path)
    rules = parser.get_info_about_rules_in_profile()
    assert len(rules.keys()) == number_of_rules
    for rule in rules.values():
        assert isinstance(rule, Rule)


@pytest.mark.parametrize("file_path, contains_oval_tree", [
    (PATH_TO_ARF, True),
    (PATH_TO_XCCDF, False),
])
def test_parse_report(file_path, contains_oval_tree):
    parser = get_parser(file_path)
    report = parser.parse_report()
    assert isinstance(report, Report)
    assert report.profile_name is not None
    assert report.rules is not None
    rule_id = "xccdf_org.ssgproject.content_rule_accounts_passwords_pam_faillock_deny"
    assert isinstance(report.rules[rule_id], Rule)
    assert (report.rules[rule_id].oval_tree is not None) == contains_oval_tree


@pytest.mark.parametrize("file_path, contains_rules_some_multi_check_rule", [
    (PATH_TO_ARF, False),
    (PATH_TO_XCCDF, False),
    (PATH_TO_XCCDF_WITH_MULTI_CHECK, True),
    (PATH_TO_ARF_WITH_MULTI_CHECK, True),
])
def test_multi_check(file_path, contains_rules_some_multi_check_rule):
    parser = get_parser(file_path)
    rules = parser.get_info_about_rules_in_profile()
    result = False
    for rule in rules.values():
        if rule.multi_check:
            result = True
    assert result == contains_rules_some_multi_check_rule
