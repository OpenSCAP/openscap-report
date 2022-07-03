# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest

from openscap_report.scap_results_parser import SCAPResultsParser
from openscap_report.scap_results_parser.data_structures import Report, Rule

from ..constants import (PATH_TO_ARF, PATH_TO_ARF_SCANNED_ON_CONTAINER,
                         PATH_TO_ARF_WITH_MULTI_CHECK,
                         PATH_TO_ARF_WITH_OS_CPE_CHECK,
                         PATH_TO_ARF_WITHOUT_INFO,
                         PATH_TO_ARF_WITHOUT_SYSTEM_DATA,
                         PATH_TO_EMPTY_XML_FILE, PATH_TO_REMEDIATIONS_SCRIPTS,
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


@pytest.mark.unit_test
@pytest.mark.parametrize("file_path, result", [
    (PATH_TO_ARF, True),
    (PATH_TO_SIMPLE_RULE_PASS_ARF, True),
    (PATH_TO_SIMPLE_RULE_FAIL_ARF, True),
    (PATH_TO_RULE_AND_CPE_CHECK_ARF, True),
    (PATH_TO_ARF_WITHOUT_INFO, True),
    (PATH_TO_ARF_WITHOUT_SYSTEM_DATA, True),
    (PATH_TO_ARF_SCANNED_ON_CONTAINER, True),
    (PATH_TO_ARF_WITH_OS_CPE_CHECK, True),
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


@pytest.mark.unit_test
@pytest.mark.parametrize("file_path, number_of_cpe_platforms, os_cpe_platform", [
    (PATH_TO_ARF, 13, "cpe:/o:fedoraproject:fedora:32"),
    (PATH_TO_XCCDF, 13, "cpe:/o:fedoraproject:fedora:32"),
    (PATH_TO_SIMPLE_RULE_PASS_ARF, 0, ""),
    (PATH_TO_SIMPLE_RULE_FAIL_ARF, 0, ""),
    (PATH_TO_ARF_WITHOUT_INFO, 0, ""),
    (PATH_TO_ARF_WITHOUT_SYSTEM_DATA, 0, ""),
    (PATH_TO_ARF_SCANNED_ON_CONTAINER, 6, "cpe:/o:fedoraproject:fedora:35"),
    (PATH_TO_RULE_AND_CPE_CHECK_ARF, 1, "cpe:/o:example:applicable:5"),
    (PATH_TO_ARF_WITH_OS_CPE_CHECK, 0, "cpe:/o:fedoraproject:fedora:1"),
    (PATH_TO_SIMPLE_RULE_PASS_XCCDF, 0, ""),
    (PATH_TO_SIMPLE_RULE_FAIL_XCCDF, 0, ""),
    (PATH_TO_XCCDF_WITHOUT_INFO, 0, ""),
    (PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA, 0, ""),
    (PATH_TO_RULE_AND_CPE_CHECK_XCCDF, 1, "cpe:/o:example:applicable:5"),
])
def test_get_profile_info(file_path, number_of_cpe_platforms, os_cpe_platform):
    parser = get_parser(file_path)
    report = parser.get_profile_info()
    assert len(report.cpe_platforms) == number_of_cpe_platforms
    assert report.platform == os_cpe_platform


@pytest.mark.unit_test
@pytest.mark.parametrize("file_path, number_of_rules", [
    (PATH_TO_ARF, 714),
    (PATH_TO_XCCDF, 714),
    (PATH_TO_ARF_SCANNED_ON_CONTAINER, 121),
    (PATH_TO_SIMPLE_RULE_PASS_ARF, 1),
    (PATH_TO_SIMPLE_RULE_FAIL_ARF, 1),
    (PATH_TO_ARF_WITHOUT_INFO, 1),
    (PATH_TO_ARF_WITHOUT_SYSTEM_DATA, 1),
    (PATH_TO_ARF_WITH_OS_CPE_CHECK, 1),
    (PATH_TO_RULE_AND_CPE_CHECK_ARF, 3),
    (PATH_TO_SIMPLE_RULE_PASS_XCCDF, 1),
    (PATH_TO_SIMPLE_RULE_FAIL_XCCDF, 1),
    (PATH_TO_XCCDF_WITHOUT_INFO, 1),
    (PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA, 1),
    (PATH_TO_RULE_AND_CPE_CHECK_XCCDF, 3),
])
def test_get_info_about_rules_in_profile(file_path, number_of_rules):
    parser = get_parser(file_path)
    parser.process_groups_or_rules()
    assert len(parser.rules.keys()) == number_of_rules
    for rule in parser.rules.values():
        assert isinstance(rule, Rule)


@pytest.mark.unit_test
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


@pytest.mark.unit_test
@pytest.mark.parametrize("file_path, contains_rules_some_multi_check_rule", [
    (PATH_TO_ARF, False),
    (PATH_TO_XCCDF, False),
    (PATH_TO_XCCDF_WITH_MULTI_CHECK, True),
    (PATH_TO_ARF_WITH_MULTI_CHECK, True),
])
def test_multi_check(file_path, contains_rules_some_multi_check_rule):
    parser = get_parser(file_path)
    parser.process_groups_or_rules()
    result = False
    for rule in parser.rules.values():
        if rule.multi_check:
            result = True
    assert result == contains_rules_some_multi_check_rule


@pytest.mark.unit_test
@pytest.mark.parametrize("rule, result", [
    (
        "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
        "Prefer installation of 64-bit operating systems when the CPU supports it."
    ),
    (
        "xccdf_org.ssgproject.content_rule_dconf_gnome_screensaver_lock_enabled",
        (
            "\nTo activate locking of the screensaver in the GNOME3 desktop"
            " when it is activated,\nadd or set <code>lock-enabled</code>"
            " to <code>true</code> in\n<code>/etc/dconf/db/local.d/00-security-settings</code>."
            " For example:\n<pre>[org/gnome/desktop/screensaver]\nlock-enabled=true\n</pre>\n"
            "Once the settings have been added, add a lock to\n"
            "<code>/etc/dconf/db/local.d/locks/00-security-settings-lock</code> "
            "to prevent user modification.\nFor example:\n"
            "<pre>/org/gnome/desktop/screensaver/lock-enabled</pre>\n"
            "After the settings have been set, run <code>dconf update</code>."
        )
    ),
    (
        "xccdf_org.ssgproject.content_rule_auditd_data_retention_action_mail_acct",
        (
            "The <code>auditd</code> service can be configured to send email to\n"
            "a designated account in certain situations. Add or correct the following line\n"
            "in <code>/etc/audit/auditd.conf</code> to ensure that administrators are notified\n"
            "via email for those situations:\n<pre>action_mail_acct = root</pre>"
        )
    ),
    (
        "xccdf_org.ssgproject.content_rule_chronyd_specify_remote_server",
        (
            "<code>Chrony</code> is a daemon which implements"
            " the Network Time Protocol (NTP). It is designed to\n"
            "synchronize system clocks across a variety of systems and"
            " use a source that is highly\naccurate. More information on"
            " <code>chrony</code> can be found at\n\n    "
            "<a href=\"http://chrony.tuxfamily.org/\">http://chrony.tuxfamily.org/</a>.\n"
            "<code>Chrony</code> can be configured to be a client and/or a server.\n"
            "Add or edit server or pool lines to <code>/etc/chrony.conf</code> as appropriate:\n"
            "<pre>server &lt;remote-server&gt;</pre>\nMultiple servers may be configured."
        )
    ),
])
def test_description(rule, result):
    parser = get_parser(PATH_TO_ARF)
    parser.process_groups_or_rules()
    assert parser.rules[rule].description == result


@pytest.mark.unit_test
@pytest.mark.parametrize("rule, result", [
    (
        "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
        (
            "Use of a 64-bit operating system offers a few advantages, "
            "like a larger address space range for\nAddress Space Layout"
            " Randomization (ASLR) and systematic presence of No eXecute"
            " and Execute Disable (NX/XD) protection bits."
        )
    ),
    (
        "xccdf_org.ssgproject.content_rule_dconf_gnome_screensaver_lock_enabled",
        (
            "A session lock is a temporary action taken when a user stops work and"
            " moves away from the immediate physical vicinity\nof the information "
            "system but does not want to logout because of the temporary nature of the absense."
        )
    ),
    (
        "xccdf_org.ssgproject.content_rule_auditd_data_retention_action_mail_acct",
        (
            "Email sent to the root account is typically aliased to the\n"
            "administrators of the system, who can take appropriate action."
        )
    ),
    (
        "xccdf_org.ssgproject.content_rule_sudoers_explicit_command_args",
        (
            "Any argument can modify quite significantly the behavior of a"
            " program, whether regarding the\nrealized operation (read, write, delete, etc.)"
            " or accessed resources (path in a file system tree). To\navoid any possibility of"
            " misuse of a command by a user, the ambiguities must be removed at the\nlevel of its"
            " specification.\n\nFor example, on some systems, the kernel messages are only "
            "accessible by root.\nIf a user nevertheless must have the privileges to read them,"
            " the argument of the dmesg command has to be restricted\nin order to prevent "
            "the user from flushing the buffer through the -c option:\n"
            "<pre>\nuser ALL = dmesg &quot;&quot;\n</pre>"
        )
    )
])
def test_rationale(rule, result):
    parser = get_parser(PATH_TO_ARF)
    parser.process_groups_or_rules()
    assert parser.rules[rule].rationale == result


@pytest.mark.unit_test
@pytest.mark.parametrize("rule, result", [
    (
        "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
        ["There is no remediation besides installing a 64-bit operating system."]
    ),
    (
        "xccdf_org.ssgproject.content_rule_dconf_gnome_screensaver_lock_enabled",
        []
    ),
    (
        "xccdf_org.ssgproject.content_rule_auditd_data_retention_action_mail_acct",
        []
    ),
    (
        "xccdf_org.ssgproject.content_rule_sudoers_explicit_command_args",
        [
            (
                "This rule doesn&#x27;t come with a remediation, as absence of arguments in"
                " the user spec doesn&#x27;t mean that the command is intended to be executed "
                "with no arguments."
            ),
            (
                "The rule can produce false findings when an argument contains a"
                " comma - sudoers syntax allows comma escaping using backslash, but"
                " the check doesn&#x27;t support that. For example,"
                " <code>root ALL=(ALL) echo 1\\,2</code> allows root to execute"
                " <code>echo 1,2</code>, but the check would interpret it as two commands "
                "<code>echo 1\\</code> and <code>2</code>."
            )
        ]
    )
])
def test_warnings(rule, result):
    parser = get_parser(PATH_TO_ARF)
    parser.process_groups_or_rules()
    assert parser.rules[rule].warnings == result


@pytest.mark.unit_test
@pytest.mark.parametrize("rule, remediation_id, scripts", [
    (
        "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
        None,
        {}
    ),
    (
        "xccdf_org.ssgproject.content_rule_dconf_gnome_screensaver_lock_enabled",
        "dconf_gnome_screensaver_lock_enabled",
        {
            "urn:xccdf:fix:script:ansible": "dconf_gnome_screensaver_lock_enabled_ansible.txt",
            "urn:xccdf:fix:script:sh": "dconf_gnome_screensaver_lock_enabled_sh.txt"
        }
    ),
    (
        "xccdf_org.ssgproject.content_rule_auditd_data_retention_action_mail_acct",
        "auditd_data_retention_action_mail_acct",
        {
            "urn:xccdf:fix:script:sh": "auditd_data_retention_action_mail_acct_sh.txt",
            "urn:xccdf:fix:script:ansible": "auditd_data_retention_action_mail_acct_ansible.txt"
        }
    )
])
def test_remediations(rule, remediation_id, scripts):
    parser = get_parser(PATH_TO_ARF)
    parser.process_groups_or_rules()
    for remediation in parser.rules[rule].remediations:
        assert remediation.remediation_id == remediation_id
        assert remediation.system in scripts
        path = PATH_TO_REMEDIATIONS_SCRIPTS / str(scripts[remediation.system])
        with open(path, "r", encoding="utf-8") as script:
            data = script.read()
            assert data == remediation.fix
