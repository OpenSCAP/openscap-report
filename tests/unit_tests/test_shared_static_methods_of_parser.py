# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest
from lxml import etree

from openscap_report.scap_results_parser.parsers.shared_static_methods_of_parser import \
    SharedStaticMethodsOfParser


@pytest.mark.unit_test
@pytest.mark.parametrize("object_, dict_", [
    (etree.Element("xml_element"), {}),
    (etree.Element("xml_element"), {"xml_element": "value"}),
    (etree.Element("xml_element"), {"xml": "value"}),
    (etree.Element("{}xml_element"), {"xml_element": "value"}),
    (etree.Element("{NAME_SPACE}xml_element"), {"xml_element": "value"}),
])
def test_get_unique_id_in_dict(object_, dict_):
    unique_id = SharedStaticMethodsOfParser.get_unique_id_in_dict(object_, dict_)
    assert unique_id not in dict_.keys()


@pytest.mark.unit_test
@pytest.mark.parametrize("element, expect_key", [
    (etree.Element("xml_element"), "xml_element"),
    (etree.Element("{}xml_element"), "xml_element"),
    (etree.Element("{NAME_SPACE}xml_element"), "xml_element"),
])
def test_get_key_of_xml_element(element, expect_key):
    key_element = SharedStaticMethodsOfParser.get_key_of_xml_element(element)
    assert key_element == expect_key
