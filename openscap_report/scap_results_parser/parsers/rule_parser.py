# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import Identifier, Reference, Rule
from ..namespaces import NAMESPACES
from .full_text_parser import FullTextParser
from .remediation_parser import RemediationParser


class RuleParser():
    def __init__(self, root, test_results, ref_values):
        self.root = root
        self.test_results = test_results
        self.full_text_parser = FullTextParser(ref_values)
        self.remediation_parser = RemediationParser(ref_values)

    @staticmethod
    def _get_references(rule):
        references = []
        for referenc in rule.findall(".//xccdf:reference", NAMESPACES):
            references.append(Reference(referenc.get("href"), referenc.text))
        return references

    @staticmethod
    def _get_identifiers(rule):
        identifiers = []
        for identifier in rule.findall(".//xccdf:ident", NAMESPACES):
            identifiers.append(Identifier(identifier.get("system"), identifier.text))
        return identifiers

    def _get_warnings(self, rule):
        warnings = []
        for warning in rule.findall(".//xccdf:warning", NAMESPACES):
            warnings.append(self.full_text_parser.get_full_warning(warning))
        return warnings

    def _get_remediations(self, rule):
        output = []
        for fix in rule.findall(".//xccdf:fix", NAMESPACES):
            remediation = self.remediation_parser.get_remediation(fix)
            output.append(remediation)
        return output

    @staticmethod
    def _get_multi_check(rule):
        for check in rule.findall(".//xccdf:check", NAMESPACES):
            if check.get("multi-check") == "true":
                return True
        return False

    @staticmethod
    def _get_check_content_refs_dict(rule):
        check_content_refs = rule.findall(".//xccdf:check-content-ref", NAMESPACES)
        check_content_refs_dict = {}
        if check_content_refs is not None:
            for check_ref in check_content_refs:
                name = check_ref.get("name", "")
                id_check = name[:name.find(":")]
                check_content_refs_dict[id_check] = name
        return check_content_refs_dict

    def process_rule(self, rule):
        rule_id = rule.get("id")

        rule_dict = {
            "rule_id": rule_id,
            "severity": rule.get("severity", "Unknown"),
            "description": self.full_text_parser.get_full_description_of_rule(rule),
            "references": self._get_references(rule),
            "identifiers": self._get_identifiers(rule),
            "warnings": self._get_warnings(rule),
            "remediations": self._get_remediations(rule),
            "multi_check": self._get_multi_check(rule),
            "rationale": self.full_text_parser.get_full_rationale(rule),
        }

        title = rule.find(".//xccdf:title", NAMESPACES)
        if title is not None:
            rule_dict["title"] = title.text

        platforms = rule.findall(".//xccdf:platform", NAMESPACES)
        rule_dict["platforms"] = []
        if platforms is not None:
            for platform in platforms:
                rule_dict["platforms"].append(platform.get("idref"))

        check_content_refs_dict = self._get_check_content_refs_dict(rule)
        rule_dict["oval_definition_id"] = check_content_refs_dict.get("oval", "")

        return Rule(**rule_dict)

    def _improve_result_of_remedied_rule(self, rule_id, rules):
        if not rules[rule_id].messages:
            return
        remediation_error_code = None
        check_engine_result = None
        remediation_error_code_prefix = "Fix execution completed and returned:"
        check_engine_result_prefix = "Checking engine returns:"

        for message in rules[rule_id].messages:
            if message.startswith(remediation_error_code_prefix):
                error_code = message.replace(remediation_error_code_prefix, "")
                remediation_error_code = int(error_code)

            index = message.find(check_engine_result_prefix)
            if index:
                check_engine_result = message[index:]

        if check_engine_result is not None and "fail" in check_engine_result:
            rules[rule_id].result = "fix unsuccessful"

        if remediation_error_code is not None and remediation_error_code > 0:
            rules[rule_id].result = "fix failed"

    def _insert_rules_results(self, rules):
        rules_results = self.test_results.findall('.//xccdf:rule-result', NAMESPACES)
        for rule_result in rules_results:
            rule_id = rule_result.get('idref')
            rules[rule_id].time = rule_result.get('time')
            rules[rule_id].result = rule_result.find('.//xccdf:result', NAMESPACES).text

            messages = rule_result.findall('.//xccdf:message', NAMESPACES)
            if messages is not None:
                rules[rule_id].messages = []
                for message in messages:
                    rules[rule_id].messages.append(message.text)
                self._improve_result_of_remedied_rule(rule_id, rules)

            if "fix" in rules[rule_id].result:
                message = (
                    "The OVAL graph of the rule as it was displayed before the fix was performed."
                )
                rules[rule_id].messages.append(message)

    def get_rules(self):
        rules = {}
        for rule in self.root.findall(".//xccdf:Rule", NAMESPACES):
            rule = self.process_rule(rule)
            rules[rule.rule_id] = rule
        self._insert_rules_results(rules)
        return rules
