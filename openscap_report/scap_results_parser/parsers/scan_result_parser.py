# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import ResultOfScan
from ..namespaces import NAMESPACES


class ScanResultParser:
    def __init__(self, test_results_el, root):
        self.root = root
        self.test_results_el = test_results_el
        self.benchmark_el = self.root.find(".//xccdf:benchmark", NAMESPACES)

    def _get_cpe_platforms(self):
        return [
            platform.get('idref')
            for platform in self.test_results_el.findall('.//xccdf:platform', NAMESPACES)
        ]

    def _get_text_of_element(self, element_path):
        element = self.test_results_el.find(element_path, NAMESPACES)
        if element is None:
            return ""
        return element.text

    def get_test_result(self):
        score_el = self.test_results_el.find(".//xccdf:score", NAMESPACES)

        scan_result_dict = {
            "title": self._get_text_of_element('.//xccdf:title'),
            "identity": self._get_text_of_element('.//xccdf:identity'),
            "cpe_platforms": self._get_cpe_platforms(),
            "target": self._get_text_of_element('.//xccdf:target'),
            "benchmark_version": self.test_results_el.get("version"),
            "start_time": self.test_results_el.get("start-time"),
            "end_time": self.test_results_el.get("end-time"),
            "test_system": self.test_results_el.get("test-system"),
            "score_system": score_el.get("system"),
            "score": float(score_el.text),
            "score_max": float(score_el.get("maximum")),
            "benchmark_url": self.benchmark_el.get("href"),
            "benchmark_id": self.benchmark_el.get("id"),
            "scanner": self._get_text_of_element(
                ".//xccdf:target-facts/xccdf:fact[@name='urn:xccdf:fact:scanner:name']"),
            "scanner_version": self._get_text_of_element(
                ".//xccdf:target-facts/xccdf:fact[@name='urn:xccdf:fact:scanner:version']"),
        }

        profile_name = self.test_results_el.find('.//xccdf:profile', NAMESPACES)
        if profile_name is not None:
            scan_result_dict["profile_id"] = profile_name.get("idref")

        return ResultOfScan(**scan_result_dict)
