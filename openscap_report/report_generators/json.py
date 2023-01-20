# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later
import json
import logging
from io import BytesIO

from .report_generator import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    def __init__(self, parser):
        super().__init__(parser)
        self.get_report_dict = None
        self.set_report_dictionary_source(self.report.as_dict_for_default_json)

    def set_report_dictionary_source(self, source):
        self.get_report_dict = source

    def generate_report(self, debug_setting):
        logging.warning("JSON Format is experimental output!")
        indent = "\t" if debug_setting.no_minify else None
        json_data = json.dumps(self.get_report_dict(), indent=indent)
        return BytesIO(json_data.encode())


class JSONEverythingReportGenerator(JSONReportGenerator):
    def __init__(self, parser):
        super().__init__(parser)
        self.set_report_dictionary_source(self.report.as_dict)
