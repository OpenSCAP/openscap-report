# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later
import json
import logging
from io import BytesIO

from .report_generator import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    def __init__(self, parser):  # pylint: disable=W0231
        self.report = parser.parse_report()

    def generate_report(self, debug_setting):
        logging.warning("JSON Format is experimental output!")

        indent = None
        if debug_setting.no_minify:
            indent = "\t"
        json_data = json.dumps(self.report.as_dict(), indent=indent)
        return BytesIO(json_data.encode())
