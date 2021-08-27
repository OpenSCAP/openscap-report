import logging
from pathlib import Path

from lxml import etree

from .data_structures import Report
from .namespaces import NAMESPACES

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

    def parse_report(self):
        return self.get_profile_info()
