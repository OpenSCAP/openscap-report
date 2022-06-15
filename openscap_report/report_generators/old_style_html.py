# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from io import BytesIO
from pathlib import Path

from lxml import etree

from .report_generator import ReportGenerator

XSL_DIR = Path(__file__).parent / "xsl"


class OldStyleHTMLReportGenerator(ReportGenerator):
    def __init__(self, parser):  # pylint: disable=W0231
        self.xml_report = parser.root
        self.xslt_doc = etree.parse(str(XSL_DIR / "xccdf-report.xsl"))
        self.xslt_transformer = etree.XSLT(self.xslt_doc)

    def generate_report(self, debug_setting):
        html_report = self.xslt_transformer(self.xml_report)
        result_html = etree.tostring(
            html_report,
            xml_declaration=True,
            doctype="<!DOCTYPE html>",
            encoding="utf-8",
            standalone=False,
            with_tail=False,
            method="html",
            pretty_print=debug_setting.no_minify)
        return BytesIO(result_html)
