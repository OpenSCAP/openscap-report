# Copyright 2024, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest
from lxml import etree

from openscap_report.scap_results_parser.namespaces import NAMESPACES
from openscap_report.scap_results_parser.parsers.oval_items_parser import OVALItemsParser


@pytest.fixture
def parser():
    sc_ns = NAMESPACES["oval-characteristics"]
    is_ns = NAMESPACES["ind-sys"]

    o1_id = "oval:example:obj:1"
    o2_id = "oval:example:obj:2"
    o3_id = "oval:example:obj:3"
    i1_id = "11117777"
    i2_id = "11117777"
    i3_id = "33339999"

    o1 = etree.Element(
        "{%s}object" % sc_ns, nsmap=NAMESPACES, id=o1_id, version="1",
        flag="complete")
    o1_r1 = etree.Element(
        "{%s}reference" % sc_ns, nsmap=NAMESPACES, item_ref=i1_id)
    o1.append(o1_r1)

    o2 = etree.Element(
        "{%s}object" % sc_ns, nsmap=NAMESPACES,  id=o2_id, version="1",
        flag="complete")
    o2_r1 = etree.Element(
        "{%s}reference" % sc_ns, nsmap=NAMESPACES, item_ref=i2_id)
    o2.append(o2_r1)
    o2_r2 = etree.Element(
        "{%s}reference" % sc_ns, nsmap=NAMESPACES, item_ref=i3_id)
    o2.append(o2_r2)

    o3 = etree.Element(
        "{%s}object" % sc_ns, nsmap=NAMESPACES,  id=o3_id, version="1",
        flag="does not exist")

    collected_objects = {
        o1_id: o1,
        o2_id: o2,
        o3_id: o3
    }

    i1 = etree.Element(
        "{%s}textfilecontent_item" % is_ns, nsmap=NAMESPACES, id=i1_id,
        status="exists")
    i1_filepath = etree.Element("{%s}filepath" % is_ns, nsmap=NAMESPACES)
    i1_filepath.text = "/var/cities"
    i1.append(i1_filepath)
    i1_text = etree.Element("{%s}text" % is_ns, nsmap=NAMESPACES)
    i1_text.text = "Paris"
    i1.append(i1_text)

    i2 = etree.Element(
        "{%s}textfilecontent_item" % is_ns, nsmap=NAMESPACES, id=i2_id,
        status="exists")
    i2_filepath = etree.Element("{%s}filepath" % is_ns, nsmap=NAMESPACES)
    i2_filepath.text = "/var/cities"
    i2.append(i2_filepath)
    i2_text = etree.Element("{%s}text" % is_ns, nsmap=NAMESPACES)
    i2_text.text = "London"
    i2.append(i2_text)

    i3 = etree.Element(
        "{%s}textfilecontent_item" % is_ns, nsmap=NAMESPACES, id=i3_id,
        status="exists")
    i3_filepath = etree.Element("{%s}filepath" % is_ns, nsmap=NAMESPACES)
    i3_filepath.text = "/var/cities"
    i3.append(i3_filepath)
    i3_text = etree.Element("{%s}text" % is_ns, nsmap=NAMESPACES)
    i3_text.text = "Prague"
    i3.append(i3_text)

    system_data = {
        i1_id: i1,
        i2_id: i2,
        i3_id: i3,
    }

    return OVALItemsParser(collected_objects, system_data)


@pytest.mark.unit_test
def test_oval_items_parser_single(parser):
    oi = parser.get_oval_items("oval:example:obj:1")
    assert oi is not None
    assert oi.header == ("filepath", "text")
    assert len(oi.entries) == 1
    assert oi.entries[0] == ("/var/cities", "London")


@pytest.mark.unit_test
def test_oval_items_parser_multiple(parser):
    oi = parser.get_oval_items("oval:example:obj:2")
    assert oi is not None
    assert oi.header == ("filepath", "text")
    assert len(oi.entries) == 2
    assert oi.entries[0] == ("/var/cities", "London")
    assert oi.entries[1] == ("/var/cities", "Prague")


@pytest.mark.unit_test
def test_oval_items_parser_dne(parser):
    oi = parser.get_oval_items("oval:example:obj:3")
    assert oi is None


@pytest.mark.unit_test
def test_oval_items_parser_wrong_object_id(parser):
    oi = parser.get_oval_items("oval:example:obj:666")
    assert oi is None
