from .data_structures.data_structures import Remediation, Rule
from .description_parser import DescriptionParser
from .namespaces import NAMESPACES


class RuleParser():
    def __init__(self):
        self.description_parser = DescriptionParser()

    @staticmethod
    def _get_references(rule):
        references = []
        for referenc in rule.findall(".//xccdf:reference", NAMESPACES):
            ref = {
                "href": referenc.get("href"),
                "text": referenc.text,
            }
            references.append(ref)
        return references

    @staticmethod
    def _get_identifiers(rule):
        identifiers = []
        for identifier in rule.findall(".//xccdf:ident", NAMESPACES):
            ident = {
                "system": identifier.get("system"),
                "text": identifier.text,
            }
            identifiers.append(ident)
        return identifiers

    @staticmethod
    def _get_warnings(rule):
        warnings = []
        for warning in rule.findall(".//xccdf:warning", NAMESPACES):
            warnings.append(warning.text)
        return warnings

    @staticmethod
    def _get_remediations(rule):
        output = []
        for fix in rule.findall(".//xccdf:fix", NAMESPACES):
            fix_dict = {
                "remediation_id": fix.get("id"),
                "system": fix.get("system"),
                "complexity": fix.get("complexity", ""),
                "disruption": fix.get("disruption", ""),
                "strategy": fix.get("strategy", ""),
                "fix": fix.text,
            }
            output.append(Remediation(**fix_dict))
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
            "description": self.description_parser.get_full_description(rule),
            "references": self._get_references(rule),
            "identifiers": self._get_identifiers(rule),
            "warnings": self._get_warnings(rule),
            "remediations": self._get_remediations(rule),
            "multi_check": self._get_multi_check(rule),
        }

        title = rule.find(".//xccdf:title", NAMESPACES)
        if title is not None:
            rule_dict["title"] = title.text

        rationale = rule.find(".//xccdf:rationale", NAMESPACES)
        if rationale is not None:
            rule_dict["rationale"] = rationale.text

        platforms = rule.findall(".//xccdf:platform", NAMESPACES)
        rule_dict["platforms"] = []
        if platforms is not None:
            for platform in platforms:
                rule_dict["platforms"].append(platform.get("idref"))

        check_content_refs_dict = self._get_check_content_refs_dict(rule)
        rule_dict["oval_definition_id"] = check_content_refs_dict.get("oval", "")

        return Rule(**rule_dict)
