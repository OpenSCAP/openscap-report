# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import collections
from dataclasses import replace

from ..data_structures import Identifier, Reference, Rule, RuleWarning
from ..namespaces import NAMESPACES
from .full_text_parser import FullTextParser
from .remediation_parser import RemediationParser

# pylint: disable=line-too-long
KNOWN_REFERENCES = {
    "http://www.ssi.gouv.fr/administration/bonnes-pratiques/": "ANSSI",
    "https://public.cyber.mil/stigs/cci/": "CCI",
    "https://www.ccn-cert.cni.es/pdf/guias/series-ccn-stic/guias-de-acceso-publico-ccn-stic/6768-ccn-stic-610a22-perfilado-de-seguridad-red-hat-enterprise-linux-9-0/file.html": "CCN for RHEL 9",  # noqa: E501
    "https://www.cisecurity.org/controls/": "CIS",
    "https://www.cisecurity.org/benchmark/red_hat_linux/": "CIS for RHEL",
    "https://www.fbi.gov/file-repository/cjis-security-policy-v5_5_20160601-2-1.pdf": "CJIS",  # noqa: E501
    "http://www.cnss.gov/Assets/pdf/CNSSI-1253.pdf": "CNSS",
    "https://www.isaca.org/resources/cobit": "COBIT",
    "http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-171.pdf": "CUI",  # noqa: E501
    "https://www.gpo.gov/fdsys/pkg/CFR-2007-title45-vol1/pdf/CFR-2007-title45-vol1-chapA-subchapC.pdf": "HIPAA",  # noqa: E501
    "https://www.isa.org/products/ansi-isa-62443-3-3-99-03-03-2013-security-for-indu": "ISA-62443-2013",  # noqa: E501
    "https://www.isa.org/products/isa-62443-2-1-2009-security-for-industrial-automat": "ISA-62443-2009",  # noqa: E501
    "https://www.cyber.gov.au/acsc/view-all-content/ism": "ISM",
    "https://www.iso.org/standard/54534.html": "ISO 27001-2013",
    "https://www.nerc.com/pa/Stand/Standard%20Purpose%20Statement%20DL/US_Standard_One-Stop-Shop.xlsx": "NERC-CIP",  # noqa: E501
    "http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r4.pdf": "NIST 800-53",  # noqa: E501
    "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.04162018.pdf": "NIST CSF",  # noqa: E501
    "https://www.niap-ccevs.org/Profile/PP.cfm": "OSPP",
    "https://www.pcisecuritystandards.org/documents/PCI_DSS_v3-2-1.pdf": "PCI-DSS v3",  # noqa: E501
    "https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0.pdf": "PCI-DSS v4",  # noqa: E501
    "https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=application-servers": "SRG-APP",  # noqa: E501
    "https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=operating-systems%2Cgeneral-purpose-os": "SRG-OS",  # noqa: E501
    "https://public.cyber.mil/stigs/downloads/?_dl_facet_stigs=operating-systems%2Cunix-linux": "STIG ID",  # noqa: E501
    "https://public.cyber.mil/stigs/srg-stig-tools/": "STIG ref",
}
# pylint: enable=line-too-long


class RuleParser():
    def __init__(self, root, test_results, ref_values):
        self.root = root
        self.test_results = test_results
        self.full_text_parser = FullTextParser(ref_values)
        self.remediation_parser = RemediationParser(ref_values)
        self.to_select_rule_ids = set()
        self.to_deselect_rule_ids = set()

    @staticmethod
    def _get_references(rule):
        url_to_ref_ids = collections.defaultdict(list)
        for reference_el in rule.findall(".//xccdf:reference", NAMESPACES):
            url = reference_el.get("href")
            if url is None or url == "":
                url = "UNKNOWN"
            ref_id = reference_el.text
            url_to_ref_ids[url].append(ref_id)
        references = []
        for url, ref_ids in url_to_ref_ids.items():
            name = KNOWN_REFERENCES.get(url, url)
            references.append(Reference(name, url, sorted(ref_ids)))
        return sorted(references, key=lambda x: x.name)

    @staticmethod
    def _get_identifiers(rule):
        identifiers = []
        for identifier in rule.findall(".//xccdf:ident", NAMESPACES):
            identifiers.append(Identifier(identifier.get("system"), identifier.text))
        return identifiers

    def _get_warnings(self, rule):
        warnings = []
        for warning in rule.findall(".//xccdf:warning", NAMESPACES):
            warnings.append(
                RuleWarning(
                    self.full_text_parser.get_full_warning(warning),
                    warning.get("category")
                ))
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
        if check_content_refs is None:
            return check_content_refs_dict

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

        self._add_title(rule_dict, rule)
        self._add_platforms(rule_dict, rule)
        self._add_oval_definition_id(rule_dict, rule)
        return Rule(**rule_dict)

    @staticmethod
    def _add_title(rule_dict, rule):
        title = rule.find(".//xccdf:title", NAMESPACES)
        if title is not None:
            rule_dict["title"] = title.text

    @staticmethod
    def _add_platforms(rule_dict, rule):
        platforms = rule.findall(".//xccdf:platform", NAMESPACES)
        rule_dict["platforms"] = []
        if platforms is not None:
            for platform in platforms:
                rule_dict["platforms"].append(platform.get("idref"))

    def _add_oval_definition_id(self, rule_dict, rule):
        check_content_refs_dict = self._get_check_content_refs_dict(rule)
        rule_dict["oval_definition_id"] = check_content_refs_dict.get("oval")

    @staticmethod
    def _get_remediation_exit_code(message):
        remediation_exit_code_prefix = "Fix execution completed and returned:"
        if message.startswith(remediation_exit_code_prefix):
            exit_code = message.replace(remediation_exit_code_prefix, "")
            return int(exit_code)
        return None

    @staticmethod
    def _get_check_engine_result(message):
        check_engine_result_prefix = "Checking engine returns:"
        index = message.find(check_engine_result_prefix)
        return message[index:] if index > -1 else None

    @staticmethod
    def _evaluate_and_set_result(rule_id, rules, remediation_exit_code, check_engine_result):
        if check_engine_result is not None and "fail" in check_engine_result:
            rules[rule_id].result = "fix unsuccessful"

        if remediation_exit_code is not None and remediation_exit_code > 0:
            rules[rule_id].result = "fix failed"

    def _improve_result_of_remedied_rule(self, rule_id, rules):
        if not rules[rule_id].messages:
            return
        remediation_exit_code = None
        check_engine_result = None

        for message in rules[rule_id].messages:
            if remediation_exit_code is None:
                remediation_exit_code = self._get_remediation_exit_code(message)

            if check_engine_result is None:
                check_engine_result = self._get_check_engine_result(message)

        self._evaluate_and_set_result(rule_id, rules, remediation_exit_code, check_engine_result)

    @staticmethod
    def _add_message_about_oval(rule_id, rules):
        if "fix" in rules[rule_id].result:
            msg = "The OVAL graph of the rule as it was displayed before the fix was performed."
            rules[rule_id].messages.append(msg)

    @staticmethod
    def set_oval_definition_id_if_is_none(rule, check_name):
        if rule.oval_definition_id is None:
            rule.oval_definition_id = check_name

    @staticmethod
    def get_oval_check_href_name(rule_result_el):
        check_ref = rule_result_el.find('.//xccdf:check/xccdf:check-content-ref', NAMESPACES)
        if check_ref is None:
            return None, None
        return check_ref.get("href").lstrip("#"), check_ref.get("name")

    def _insert_rules_results(self, rules):
        rules_results = self.test_results.findall('.//xccdf:rule-result', NAMESPACES)
        for rule_result in rules_results:
            rule_id = rule_result.get('idref')
            rules[rule_id].time = rule_result.get('time')
            rules[rule_id].result = rule_result.find('.//xccdf:result', NAMESPACES).text
            rules[rule_id].weight = float(rule_result.get('weight'))

            rules[rule_id].oval_reference, check_name = self.get_oval_check_href_name(
                rule_result
            )
            self.set_oval_definition_id_if_is_none(rules[rule_id], check_name)

            messages = rule_result.findall('.//xccdf:message', NAMESPACES)
            if messages is not None:
                rules[rule_id].messages = []
                for message in messages:
                    rules[rule_id].messages.append(message.text)
                self._improve_result_of_remedied_rule(rule_id, rules)
            self._add_message_about_oval(rule_id, rules)

            if rules[rule_id].multi_check:
                self._create_new_multi_check_rule(rules, rule_id, check_name)

    def _create_new_multi_check_rule(self, rules, rule_id, check_name):
        self.to_deselect_rule_ids.add(rule_id)
        new_rule_id = f"{rule_id}-{check_name}"
        changes = {
            "rule_id": new_rule_id,
            "title": f"{rules[rule_id].title} ({check_name})",
            "oval_definition_id": check_name,
        }
        rules[new_rule_id] = replace(rules[rule_id], **changes)
        self.to_select_rule_ids.add(new_rule_id)

    def get_rules(self):
        rules = {}
        for rule_el in self.root.findall(".//xccdf:Rule", NAMESPACES):
            rule = self.process_rule(rule_el)
            rules[rule.rule_id] = rule
        self._insert_rules_results(rules)
        return rules
