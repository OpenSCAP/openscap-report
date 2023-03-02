# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import replace
from functools import cache

from lxml import etree

from openscap_report.scap_results_parser import SCAPResultsParser
from openscap_report.scap_results_parser.namespaces import NAMESPACES
from openscap_report.scap_results_parser.parsers import RuleParser

from .constants import (PATH_TO_ARF,
                        PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO)


@cache
def get_xml_data(file_path):
    with open(file_path, "r", encoding="utf-8") as xml_report:
        return xml_report.read().encode()


def get_parser(file_path):
    xml_data = get_xml_data(file_path)
    return SCAPResultsParser(xml_data)


BASIC_REPORT = get_parser(PATH_TO_ARF).parse_report()


def get_report(file_path=None):
    if file_path is None:
        return replace(BASIC_REPORT)
    return get_parser(file_path).parse_report()


REPORT_REPRODUCING_DANGLING_REFERENCE_TO = get_report(
    PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO
)


def get_root(file_path):
    xml_data = get_xml_data(file_path)
    return etree.XML(xml_data)


def get_benchmark(root):
    benchmark_el = root.find(".//xccdf:Benchmark", NAMESPACES)
    if "Benchmark" in root.tag:
        return root
    return benchmark_el


def get_test_results(root):
    return root.find(".//xccdf:TestResult", NAMESPACES)


def get_ref_values(root):
    return {
        ref_value.get("idref"): ref_value.text
        for ref_value in root.findall(".//xccdf:set-value", NAMESPACES)
    }


DEFAULT_RULES = BASIC_REPORT.rules


def get_rules(file_path=None):
    if file_path is None:
        return DEFAULT_RULES.copy()
    root = get_root(file_path)
    test_results = get_test_results(root)
    ref_values = get_ref_values(root)
    rule_parser = RuleParser(root, test_results, ref_values)
    return rule_parser.get_rules()
