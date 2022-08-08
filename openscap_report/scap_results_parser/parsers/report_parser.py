# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import Report
from ..namespaces import NAMESPACES


class ReportParser:
    def __init__(self, root, test_results):
        self.root = root
        self.test_results = test_results

    def _get_cpe_platforms(self):
        return [
            platform.get('idref')
            for platform in self.test_results.findall('.//xccdf:platform', NAMESPACES)
        ]

    def get_report(self):
        target_facts = self.test_results.find('.//xccdf:target-facts', NAMESPACES)
        score = self.test_results.find(".//xccdf:score", NAMESPACES)
        benchmark = self.test_results.find('.//xccdf:benchmark', NAMESPACES)

        report_dict = {
            "title": self.test_results.find('.//xccdf:title', NAMESPACES).text,
            "identity": self.test_results.find('.//xccdf:identity', NAMESPACES).text,
            "cpe_platforms": self._get_cpe_platforms(),
            "target": self.test_results.find('.//xccdf:target', NAMESPACES).text,
            "benchmark_version": self.test_results.get("version"),
            "start_time": self.test_results.get("start-time"),
            "end_time": self.test_results.get("end-time"),
            "test_system": self.test_results.get("test-system"),
            "score": float(score.text),
            "score_max": float(score.get("maximum")),
            "benchmark_url": benchmark.get("href"),
            "benchmark_id": benchmark.get("id"),
            "scanner": target_facts.find(
                ".//xccdf:fact[@name='urn:xccdf:fact:scanner:name']", NAMESPACES).text,
            "scanner_version": target_facts.find(
                ".//xccdf:fact[@name='urn:xccdf:fact:scanner:version']", NAMESPACES).text,
        }

        profile_name = self.test_results.find('.//xccdf:profile', NAMESPACES)
        if profile_name is not None:
            report_dict["profile_name"] = profile_name.get("idref")

        platform = self.root.find('.//xccdf:platform', NAMESPACES)
        if platform is not None:
            report_dict["platform"] = platform.get('idref')

        return Report(**report_dict)
