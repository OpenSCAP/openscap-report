import pytest
from lxml import etree

from openscap_report.scap_results_parser import SCAPResultsParser
from openscap_report.scap_results_parser.parsers import FullTextParser

from ..constants import (PATH_TO_ARF,
                         PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO)

REF_VALUES = {
    "id-1234": "text1",
    "1234": 'echo "nwm"'
}
FULL_TEXT_PARSER = FullTextParser(REF_VALUES)


@pytest.mark.unit_test
@pytest.mark.parametrize("tag, return_data", [
    (etree.Element("sub", idref="id-1234"), "text1"),
    (etree.Element("sub", idref="1234"), 'echo "nwm"'),
    (
        etree.Element("sub", idref="hello-ID"),
        "<span class='error-id-ref'>Sub tag reference does not exist: hello-ID</span>"
    ),
])
def test_replace_sub_tag(tag, return_data):
    assert FULL_TEXT_PARSER.replace_sub_tag(tag) == return_data


def get_report(src):
    with open(src, "r") as report_file:
        return SCAPResultsParser(report_file.read().encode()).parse_report()


BASIC_REPORT = get_report(PATH_TO_ARF)
REPORT_REPRODUCING_DANGLING_REFERENCE_TO = get_report(
    PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO
)


@pytest.mark.integration_test
@pytest.mark.parametrize("report, rule_id, expected_data", [
    (
        REPORT_REPRODUCING_DANGLING_REFERENCE_TO,
        "xccdf_org.ssgproject.content_rule_grub2_l1tf_argument",
        (
            "L1 Terminal Fault (L1TF) is a hardware vulnerability which allows unprivileged\n"
            "speculative access to data which is available in the Level 1 Data Cache when\n"
            "the page table entry isn&#x27;t present.\n\nSelect the appropriate mitigation by"
            " adding the argument\n<code>l1tf=<span class='error-id-ref'>"
            "Sub tag reference does not exist: dangling reference to !</span>"
            "</code> to the default\nGRUB 2 command line for the Linux operating system.\n"
            "Configure the default Grub2 kernel command line to contain "
            "l1tf=xccdf_value(var_l1tf_options) as follows:\n"
            "<pre># grub2-editenv - set &quot;$(grub2-editenv - list | grep kernelopts) "
            "l1tf=xccdf_value(var_l1tf_options)&quot;</pre>\n\nSince Linux Kernel 4.19 "
            "you can check the L1TF vulnerability state with the\n"
            "following command:\n<code>cat /sys/devices/system/cpu/vulnerabilities/l1tf</code>"
        )
    ),
    (
        BASIC_REPORT,
        "xccdf_org.ssgproject.content_rule_postfix_client_configure_mail_alias",
        (
            "Make sure that mails delivered to root user are forwarded to a monitored\n"
            "email address. Make sure that the address\nsystem.administrator@mail.mil is"
            " a valid email address\nreachable from the system in question. Use the following"
            " command to\nconfigure the alias:\n<pre>$ sudo echo &quot;root: "
            "system.administrator@mail.mil&quot; &gt;&gt; /etc/aliases\n$ sudo newaliases</pre>"
        )
    ),
    (
        REPORT_REPRODUCING_DANGLING_REFERENCE_TO,
        "xccdf_org.ssgproject.content_rule_postfix_client_configure_mail_alias",
        (
            "Make sure that mails delivered to root user are forwarded to a monitored\n"
            "email address. Make sure that the address\nsystem.administrator@mail.mil is"
            " a valid email address\nreachable from the system in question. Use the following"
            " command to\nconfigure the alias:\n<pre>$ sudo echo &quot;root: "
            "system.administrator@mail.mil&quot; &gt;&gt; /etc/aliases\n$ sudo newaliases</pre>"
        )
    ),
])
def test_parsing_of_text(report, rule_id, expected_data):
    print(repr(report.rules[rule_id].description))
    assert report.rules[rule_id].description == expected_data
