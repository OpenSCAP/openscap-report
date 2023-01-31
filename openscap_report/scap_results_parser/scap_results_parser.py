# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
from pathlib import Path

from lxml import etree

from .namespaces import NAMESPACES
from .oval_and_cpe_tree_builder import OVALAndCPETreeBuilder
from .parsers import GroupParser, ReportParser, RuleParser

SCHEMAS_DIR = Path(__file__).parent / "schemas"


class SCAPResultsParser():
    def __init__(self, data):
        self.root = etree.XML(data)
        self.arf_schemas_path = 'arf/1.1/asset-reporting-format_1.1.0.xsd'
        if not self.validate(self.arf_schemas_path):
            logging.warning("This file is not valid ARF report!")
        else:
            logging.info("The file is valid ARF report")
        self.ref_values = self._get_ref_values()

    def validate(self, xsd_path):
        xsd_path = str(SCHEMAS_DIR / xsd_path)
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        return xmlschema.validate(self.root)

    def _get_ref_values(self):
        return {
            ref_value.get("idref"): ref_value.text
            for ref_value in self.root.findall('.//xccdf:set-value', NAMESPACES)
        }

    @staticmethod
    def _debug_show_rules(rules):
        for rule_id, rule in rules.items():
            logging.debug(rule_id)
            logging.debug(rule)

    @staticmethod
    def _get_applicable_cpe_ids_for_machine(cpe_platforms_for_profile):
        return [
            cpe_id for cpe_id, applicable_for_machine in cpe_platforms_for_profile.items()
            if applicable_for_machine
        ]

    def _get_benchmark_element(self):
        benchmark_el = self.root.find(".//xccdf:Benchmark", NAMESPACES)
        if "Benchmark" in self.root.tag:
            benchmark_el = self.root
        return benchmark_el

    def parse_report(self):
        test_results_el = self.root.find('.//xccdf:TestResult', NAMESPACES)
        benchmark_el = self._get_benchmark_element()

        report_parser = ReportParser(self.root, test_results_el, benchmark_el)
        report = report_parser.get_report()
        logging.debug(report)

        group_parser = GroupParser(self.root, self.ref_values, benchmark_el)
        groups = group_parser.get_groups()

        rule_parser = RuleParser(self.root, test_results_el, self.ref_values)
        rules = rule_parser.get_rules()

        OVAL_and_CPE_tree_builder = OVALAndCPETreeBuilder(  # pylint: disable=C0103
            self.root, group_parser,
            self._get_applicable_cpe_ids_for_machine(report.profile_info.cpe_platforms_for_profile)
        )
        OVAL_and_CPE_tree_builder.insert_oval_and_cpe_trees_to_rules(rules)

        self._debug_show_rules(rules)
        report.rules = rules
        report.groups = groups
        return report
