# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import argparse
import tempfile
from dataclasses import replace
from pathlib import Path

try:
    from functools import cache
except ImportError:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

from lxml import etree

from openscap_report.scap_results_parser import SCAPResultsParser
from openscap_report.scap_results_parser.data_structures import OvalDefinition
from openscap_report.scap_results_parser.namespaces import NAMESPACES
from openscap_report.scap_results_parser.parsers import (
    CPEApplicabilityLanguageParser, RuleParser)

from .constants import (PATH_TO_ARF,
                        PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO)
from .unit_tests.test_oval_tree_eval import OVAL_TREE_TRUE

PATH_TO_RESULT_FILE = Path(tempfile.gettempdir()) / "oscap-report-tests_result.html"


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


def get_cpe_al_parser(file_path=PATH_TO_ARF):
    root = get_root(file_path)
    return CPEApplicabilityLanguageParser(root, get_dummy_cpe_oval_definition())


def get_dummy_cpe_oval_definition():
    dummy_oval_definition = OvalDefinition(
        definition_id="dummy_oval_def",
        title="dummy OVAL definition",
        definition_class="compliance",
        oval_tree=OVAL_TREE_TRUE,
    )
    return {
        "oval:ssg-installed_env_is_a_machine:def:1": dummy_oval_definition,
        "oval:ssg-installed_env_has_chrony_package:def:1": dummy_oval_definition,
        "oval:ssg-installed_env_has_ntp_package:def:1": dummy_oval_definition,
        "oval:ssg-installed_env_has_gdm_package:def:1": dummy_oval_definition,
        "oval:ssg-installed_OS_is_fedora:def:1": dummy_oval_definition,
        "oval:ssg-installed_env_has_zipl_package:def:1": dummy_oval_definition,
        "oval:ssg-system_boot_mode_is_uefi:def:1": dummy_oval_definition,
    }


def get_fake_args():
    # pylint: disable=bad-option-value,R1732
    input_file = open(PATH_TO_ARF, "r", encoding="utf-8")
    output_file = open(PATH_TO_RESULT_FILE, "wb")
    return argparse.Namespace(
        FILE=input_file, output=output_file,
        log_file=None, log_level="WARNING", format="HTML",
        debug=[""],
    )
