# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import Report
from ..namespaces import NAMESPACES
from .profile_info_parser import ProfileInfoParser
from .scan_result_parser import ScanResultParser


class ReportParser:
    def __init__(self, root, test_results_el, benchmark_el):
        self.root = root
        self.test_results_el = test_results_el
        self.benchmark_el = benchmark_el
        self.profiles_info_elements = {
            profile.get("id"): profile
            for profile in self.root.findall('.//xccdf:Profile', NAMESPACES)
        }

    def get_report(self):
        scan_result_parser = ScanResultParser(self.test_results_el, self.root)
        scan_result = scan_result_parser.get_test_result()
        profile_info_parser = ProfileInfoParser(
            self.profiles_info_elements, scan_result.cpe_platforms, self.benchmark_el
        )
        profile_info = profile_info_parser.get_profile_info(scan_result.profile_id)
        return Report(scan_result=scan_result, profile_info=profile_info)
