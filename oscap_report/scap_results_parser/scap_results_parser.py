import logging
from pathlib import Path

from lxml import etree

from .data_structures import OvalNode, Remediation, Report, Rule
from .exceptions import MissingOVALResult
from .namespaces import NAMESPACES
from .oval_definition_parser.oval_definition_parser import OVALDefinitionParser

SCHEMAS_DIR = Path(__file__).parent / "schemas"


class SCAPResultsParser():
    def __init__(self, data):
        self.root = etree.XML(data)
        self.arf_schemas_path = 'arf/1.1/asset-reporting-format_1.1.0.xsd'
        if not self.validate(self.arf_schemas_path):
            logging.warning("This file is not valid ARF report!")
        else:
            logging.info("The file is valid ARF report")
        self.test_results = self.root.find('.//xccdf:TestResult', NAMESPACES)
        self.profile = None
        self.rules = None

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
        report_dict["profile_name"] = self.test_results.find(
            './/xccdf:profile', NAMESPACES).get("idref")
        report_dict["target"] = self.test_results.find('.//xccdf:target', NAMESPACES).text
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

            check_content_ref = rule_result.find(".//xccdf:check-content-ref", NAMESPACES)
            if check_content_ref is not None:
                self.rules[rule_id].oval_definition_id = check_content_ref.get("name", "")

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
        str_description = etree.tostring(description).decode()
        start_tag_description = str_description.find(">") + 1
        end_tag_description = str_description.rfind("</")
        return str_description[start_tag_description:end_tag_description].replace("html:", "")

    def get_info_about_rules_in_profile(self):
        rules = {}
        for rule in self.root.findall(".//xccdf:Rule", NAMESPACES):
            rule_dict = {}
            rule_id = rule.get("id")
            rule_dict["rule_id"] = rule_id
            rule_dict["severity"] = rule.get("severity")
            rule_dict["title"] = rule.find(".//xccdf:title", NAMESPACES).text
            rule_dict["description"] = self._get_full_description(rule)
            rule_dict["references"] = self._get_references(rule)
            rule_dict["rationale"] = rule.find(".//xccdf:rationale", NAMESPACES).text

            platform = rule.find(".//xccdf:platform", NAMESPACES)
            if platform is not None:
                rule_dict["platform"] = platform.get("idref")

            rule_dict["identifiers"] = self._get_identifiers(rule)
            rule_dict["warnings"] = self._get_warnings(rule)
            rule_dict["remediations"] = self._get_remediations(rule)
            rule_dict["multi_check"] = self._get_multi_check(rule)
            rules[rule_id] = Rule(**rule_dict)
        return rules

    def _insert_oval(self):
        try:
            oval_parser = OVALDefinitionParser(self.root)
            oval_trees = oval_parser.get_oval_trees()
            oval_cpe_trees = oval_parser.get_oval_cpe_trees()
            for rule in self.rules.values():
                if rule.oval_definition_id in oval_trees:
                    rule.oval_tree = oval_trees[rule.oval_definition_id]
                if rule.platform in oval_cpe_trees:
                    if rule.oval_tree is None:
                        rule.oval_tree = oval_cpe_trees[rule.platform]
                    else:
                        self._add_oval_cpe_to_oval_tree(rule, oval_cpe_trees[rule.platform])
        except MissingOVALResult:
            logging.warning("Not found OVAL results!")

    @staticmethod
    def _add_oval_cpe_to_oval_tree(rule, oval_cpe_tree):
        logging.info(rule.oval_tree)
        oval_tree_result = rule.oval_tree.value
        oval_cpe_tree_result = oval_cpe_tree.value

        result = ""
        if oval_tree_result == "true" and oval_cpe_tree_result == "true":
            result = "true"
        elif oval_tree_result == "false" or oval_cpe_tree_result == "false":
            result = "false"
        else:
            result = "unknown"

        merged_oval_tree = OvalNode(
            node_id="{} and {}".format(rule.oval_tree.node_id, rule.platform),
            node_type="AND",
            value=result,
            tag="Rule definition and CPE definition",
            children=[rule.oval_tree, oval_cpe_tree])

        rule.oval_tree = merged_oval_tree

    def parse_report(self):
        self.profile = self.get_profile_info()
        logging.debug(self.profile)
        self.rules = self.get_info_about_rules_in_profile()
        self._insert_rules_results()
        self._insert_oval()
        self._debug_show_rules()
        self.profile.rules = self.rules
        return self.profile
