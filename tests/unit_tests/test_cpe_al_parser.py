# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest
from lxml import etree

from ..test_utils import get_cpe_al_parser


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "str_xml_element, evaluation_result",
    [
        (
            (
                '<cpe-lang:logical-test operator="AND" negate="false">'
                '     <cpe-lang:fact-ref name="cpe:/a:machine"/>'
                '</cpe-lang:logical-test>'
            ),
            "true",
        ),
        (
            (
                '<cpe-lang:logical-test operator="AND" negate="true">'
                '     <cpe-lang:fact-ref name="cpe:/a:machine"/>'
                '</cpe-lang:logical-test>'
            ),
            "false",
        ),
        (
            (
                '<cpe-lang:logical-test operator="AND" negate="false">'
                '     <cpe-lang:logical-test operator="OR" negate="false">'
                '         <cpe-lang:fact-ref name="cpe:/a:chrony"/>'
                '         <cpe-lang:fact-ref name="cpe:/a:ntp"/>'
                '     </cpe-lang:logical-test>'
                '     <cpe-lang:fact-ref name="cpe:/a:machine"/>'
                '</cpe-lang:logical-test>'
            ),
            "true",
        ),
        (
            (
                '<cpe-lang:logical-test operator="AND" negate="true">'
                '    <cpe-lang:logical-test operator="OR" negate="false">'
                '         <cpe-lang:logical-test operator="AND" negate="false">'
                '             <cpe-lang:fact-ref name="cpe:/o:fedoraproject:fedora:32"/>'
                '             <cpe-lang:fact-ref name="cpe:/a:gdm"/>'
                '         </cpe-lang:logical-test>'
                '         <cpe-lang:logical-test operator="AND" negate="false">'
                '             <cpe-lang:fact-ref name="cpe:/o:fedoraproject:fedora:32"/>'
                '             <cpe-lang:fact-ref name="cpe:/a:uefi"/>'
                '         </cpe-lang:logical-test>'
                '         <cpe-lang:logical-test operator="AND" negate="true">'
                '             <cpe-lang:fact-ref name="cpe:/a:zipl"/>'
                '             <cpe-lang:fact-ref name="cpe:/o:fedoraproject:fedora:32"/>'
                '         </cpe-lang:logical-test>'
                '     </cpe-lang:logical-test>'
                '</cpe-lang:logical-test>'
            ),
            "false",
        ),
        (
            (
                '<cpe-lang:logical-test operator="AND" negate="false">'
                '     <cpe-lang:check-fact-ref'
                ' system="http://oval.mitre.org/XMLSchema/oval-definitions-5"'
                ' href="ssg-rhel9-cpe-oval.xml"'
                ' id-ref="oval:ssg-installed_env_is_a_machine:def:1"/>'
                '</cpe-lang:logical-test>'
            ),
            "true",
        ),
        (
            (
                '<cpe-lang:logical-test operator="AND" negate="true">'
                '     <cpe-lang:check-fact-ref'
                ' system="http://oval.mitre.org/XMLSchema/oval-definitions-5"'
                ' href="ssg-rhel9-cpe-oval.xml"'
                ' id-ref="oval:ssg-installed_env_is_a_machine:def:1"/>'
                '</cpe-lang:logical-test>'
            ),
            "false",
        ),
        (
            (
                '<cpe-lang:logical-test operator="OR" negate="false">'
                '     <cpe-lang:check-fact-ref'
                ' system="http://oval.mitre.org/XMLSchema/oval-definitions-5"'
                ' href="ssg-rhel9-cpe-oval.xml"'
                ' id-ref="oval:ssg-installed_env_has_chrony_package:def:1"/>'
                '     <cpe-lang:check-fact-ref'
                ' system="http://oval.mitre.org/XMLSchema/oval-definitions-5"'
                ' href="ssg-rhel9-cpe-oval.xml"'
                ' id-ref="oval:ssg-installed_env_has_ntp_package:def:1"/>'
                '</cpe-lang:logical-test>'
            ),
            "true",
        ),
    ],
)
def test_get_logical_test(str_xml_element, evaluation_result):
    parser = get_cpe_al_parser()
    xml_element = etree.XML(
        f'<con xmlns:cpe-lang="http://cpe.mitre.org/language/2.0">{str_xml_element}</con>'
    )
    logical_test = parser.get_logical_test(xml_element[0])
    assert logical_test.evaluate_tree() == evaluation_result
