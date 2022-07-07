# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
from pathlib import Path

from lxml import etree

from .cpe_tree_builder import CpeTreeBuilder
from .data_structures import Group, Report
from .exceptions import MissingOVALResult
from .namespaces import NAMESPACES
from .parsers import FullTextParser, OVALDefinitionParser, RuleParser

SCHEMAS_DIR = Path(__file__).parent / "schemas"


class SCAPResultsParser():  # pylint: disable=R0902
    def __init__(self, data):
        self.root = etree.XML(data)
        self.arf_schemas_path = 'arf/1.1/asset-reporting-format_1.1.0.xsd'
        if not self.validate(self.arf_schemas_path):
            logging.warning("This file is not valid ARF report!")
        else:
            logging.info("The file is valid ARF report")
        self.test_results = self.root.find('.//xccdf:TestResult', NAMESPACES)
        self.ref_values = self._get_ref_values()
        self.rule_parser = RuleParser(self.ref_values)
        self.description_parser = FullTextParser(self.ref_values)
        self.profile = None
        self.rules = {}
        self.groups = {}
        self.rule_to_grup_id = {}
        self.group_to_platforms = {}

    def validate(self, xsd_path):
        xsd_path = str(SCHEMAS_DIR / xsd_path)
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        return xmlschema.validate(self.root)

    def _get_ref_values(self):
        ref_values = {}
        for ref_value in self.root.findall('.//xccdf:set-value', NAMESPACES):
            ref_values[ref_value.get("idref")] = ref_value.text
        return ref_values

    def _get_cpe_platforms(self):
        cpe_platforms = []
        for platform in self.test_results.findall('.//xccdf:platform', NAMESPACES):
            cpe_platforms.append(platform.get('idref'))
        return cpe_platforms

    def get_profile_info(self):
        report_dict = {}

        report_dict["title"] = self.test_results.find('.//xccdf:title', NAMESPACES).text
        report_dict["identity"] = self.test_results.find('.//xccdf:identity', NAMESPACES).text

        profile_name = self.test_results.find('.//xccdf:profile', NAMESPACES)
        if profile_name is not None:
            report_dict["profile_name"] = profile_name.get("idref")

        report_dict["target"] = self.test_results.find('.//xccdf:target', NAMESPACES).text

        platform = self.root.find('.//xccdf:platform', NAMESPACES)
        if platform is not None:
            report_dict["platform"] = platform.get('idref')

        report_dict["cpe_platforms"] = self._get_cpe_platforms()

        target_facts = self.test_results.find('.//xccdf:target-facts', NAMESPACES)
        report_dict["scanner"] = target_facts.find(
            ".//xccdf:fact[@name='urn:xccdf:fact:scanner:name']", NAMESPACES).text

        report_dict["scanner_version"] = target_facts.find(
            ".//xccdf:fact[@name='urn:xccdf:fact:scanner:version']", NAMESPACES).text

        benchmark = self.test_results.find('.//xccdf:benchmark', NAMESPACES)
        report_dict["benchmark_url"] = benchmark.get("href")
        report_dict["benchmark_id"] = benchmark.get("id")
        report_dict["benchmark_version"] = self.test_results.get("version")

        report_dict["start_time"] = self.test_results.get("start-time")
        report_dict["end_time"] = self.test_results.get("end-time")

        report_dict["test_system"] = self.test_results.get("test-system")

        score = self.test_results.find(".//xccdf:score", NAMESPACES)
        report_dict["score"] = float(score.text)
        report_dict["score_max"] = float(score.get("maximum"))
        return Report(**report_dict)

    def _debug_show_rules(self):
        for rule_id, rule in self.rules.items():
            logging.debug(rule_id)
            logging.debug(rule)

    def _improve_result_of_remedied_rule(self, rule_id):
        remediation_error_code = None
        check_engine_result = None
        remediation_error_code_prefix = "Fix execution completed and returned:"
        check_engine_result_prefix = "Checking engine returns:"

        for message in self.rules[rule_id].messages:
            if message.startswith(remediation_error_code_prefix):
                error_code = message.replace(remediation_error_code_prefix, "")
                remediation_error_code = int(error_code)

            index = message.find(check_engine_result_prefix)
            if index:
                check_engine_result = message[index:]

        if check_engine_result is not None and "fail" in check_engine_result:
            self.rules[rule_id].result = "fix unsuccessful"

        if remediation_error_code is not None and remediation_error_code > 0:
            self.rules[rule_id].result = "fix failed"

    def _insert_rules_results(self):
        rules_results = self.test_results.findall('.//xccdf:rule-result', NAMESPACES)
        for rule_result in rules_results:
            rule_id = rule_result.get('idref')
            self.rules[rule_id].time = rule_result.get('time')
            self.rules[rule_id].result = rule_result.find('.//xccdf:result', NAMESPACES).text

            messages = rule_result.findall('.//xccdf:message', NAMESPACES)
            if messages is not None:
                self.rules[rule_id].messages = []
                for message in messages:
                    self.rules[rule_id].messages.append(message.text)
                self._improve_result_of_remedied_rule(rule_id)

            if "fix" in self.rules[rule_id].result:
                message = (
                    "The OVAL graph of the rule as it was displayed before the fix was performed."
                )
                self.rules[rule_id].messages.append(message)

    def _insert_oval_and_cpe_trees(self):
        try:
            oval_parser = OVALDefinitionParser(self.root)
            oval_trees = oval_parser.get_oval_trees()
            oval_cpe_trees = oval_parser.get_oval_cpe_trees()
            cpe_tree_builder = CpeTreeBuilder(
                self.rule_to_grup_id,
                self.group_to_platforms,
                self.profile.platform
            )
            for rule in self.rules.values():
                if rule.oval_definition_id in oval_trees:
                    rule.oval_tree = oval_trees[rule.oval_definition_id]
                rule.cpe_tree = cpe_tree_builder.build_cpe_tree(rule, oval_cpe_trees)
        except MissingOVALResult:
            logging.warning("Not found OVAL results!")

    def get_group(self, group, platforms=None):
        if platforms is None:
            platforms = []
        group_dict = {
            "platforms": [],
            "rules_ids": [],
            "sub_groups": [],
            "group_id": group.get("id"),
        }

        for item in group.iterchildren():
            if "title" in item.tag:
                group_dict["title"] = item.text

            if "description" in item.tag:
                group_dict["description"] = self.description_parser.get_full_description(item)

            if "platform" in item.tag:
                group_dict["platforms"].append(item.get("idref"))

            if "Rule" in item.tag:
                group_dict["rules_ids"].append(item.get("id"))
                rule = self.rule_parser.process_rule(item)
                self.rules[rule.rule_id] = rule
                self.rule_to_grup_id[item.get("id")] = group_dict.get("group_id")

            if "Group" in item.tag:
                group_dict["sub_groups"].append(self.get_group(item, group_dict.get("platforms")))

        platforms_of_group = list(set(group_dict.get("platforms")) | set(platforms))
        self.group_to_platforms[group_dict.get("group_id")] = platforms_of_group
        return Group(**group_dict)

    def process_groups_or_rules(self):
        group = self.root.find(".//xccdf:Group", NAMESPACES)
        benchmark = self.root.find(".//xccdf:Benchmark", NAMESPACES)
        if group is not None and benchmark is not None:
            for item in benchmark:
                if "Group" in item.tag:
                    self.groups[item.get("id")] = self.get_group(item)
        else:
            for rule in self.root.findall(".//xccdf:Rule", NAMESPACES):
                rule = self.rule_parser.process_rule(rule)
                self.rules[rule.rule_id] = rule

    def parse_report(self):
        self.profile = self.get_profile_info()
        logging.debug(self.profile)
        self.process_groups_or_rules()
        self._insert_rules_results()
        self._insert_oval_and_cpe_trees()
        self._debug_show_rules()
        self.profile.rules = self.rules
        return self.profile
