# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later
import logging
from io import BytesIO

from .report_generator import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    def __init__(self, parser):  # pylint: disable=W0231
        self.report = parser.parse_report()

    def generate_report(self, debug_setting):
        logging.fatal("JSON Format is not implemented!")
        return BytesIO("{}".encode())
