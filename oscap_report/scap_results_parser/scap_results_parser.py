import logging
from pathlib import Path

from lxml import etree

from .data_structures.data_structures import Group, Remediation, Report, Rule
from .cpe_tree_builder import CpeTreeBulder
from .exceptions import MissingOVALResult
from .namespaces import NAMESPACES
from .oval_definition_parser.oval_definition_parser import OVALDefinitionParser

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

    def _insert_rules_results(self):
        rules_results = self.test_results.findall('.//xccdf:rule-result', NAMESPACES)
        for rule_result in rules_results:
            rule_id = rule_result.get('idref')
            self.rules[rule_id].time = rule_result.get('time')
            self.rules[rule_id].result = rule_result.find('.//xccdf:result', NAMESPACES).text

            message = rule_result.find('.//xccdf:message', NAMESPACES)
            if message is not None:
                self.rules[rule_id].message = message.text

    @staticmethod
    def _get_references(rule):
        references = []
        for referenc in rule.findall(".//xccdf:reference", NAMESPACES):
            ref = {}
            ref["href"] = referenc.get("href")
            ref["text"] = referenc.text
            references.append(ref)
        return references

    @staticmethod
    def _get_identifiers(rule):
        identifiers = []
        for identifier in rule.findall(".//xccdf:ident", NAMESPACES):
            ident = {}
            ident["system"] = identifier.get("system")
            ident["text"] = identifier.text
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
            fix_dict = {}
            fix_dict["remediation_id"] = fix.get("id")
            fix_dict["system"] = fix.get("system")
            fix_dict["complexity"] = fix.get("complexity", "")
            fix_dict["disruption"] = fix.get("disruption", "")
            fix_dict["strategy"] = fix.get("strategy", "")
            fix_dict["fix"] = fix.text
            output.append(Remediation(**fix_dict))
        return output

    @staticmethod
    def _get_multi_check(rule):
        for check in rule.findall(".//xccdf:check", NAMESPACES):
            if check.get("multi-check") == "true":
                return True
        return False

    @staticmethod
    def _get_full_description(rule):
        description = rule.find(".//xccdf:description", NAMESPACES)
        if description is None:
            return None
        str_description = etree.tostring(description).decode()
        start_tag_description = str_description.find(">") + 1
        end_tag_description = str_description.rfind("</")
        return str_description[start_tag_description:end_tag_description].replace("html:", "")

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
            "description": self._get_full_description(rule),
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

        self.rules[rule_id] = Rule(**rule_dict)

    def _insert_oval_and_cpe_trees(self):
        try:
            oval_parser = OVALDefinitionParser(self.root)
            oval_trees = oval_parser.get_oval_trees()
            oval_cpe_trees = oval_parser.get_oval_cpe_trees()
            cpe_tree_builder = CpeTreeBulder(
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
                group_dict["description"] = self._get_full_description(item)

            if "platform" in item.tag:
                group_dict["platforms"].append(item.get("idref"))

            if "Rule" in item.tag:
                group_dict["rules_ids"].append(item.get("id"))
                self.process_rule(item)
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
                self.process_rule(rule)

    def parse_report(self):
        self.profile = self.get_profile_info()
        logging.debug(self.profile)
        self.process_groups_or_rules()
        self._insert_rules_results()
        self._insert_oval_and_cpe_trees()
        self._debug_show_rules()
        self.profile.rules = self.rules
        return self.profile
