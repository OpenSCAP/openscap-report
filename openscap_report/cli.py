# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
from sys import exit as sys_exit
from sys import stdin, stdout

from lxml.etree import XMLSyntaxError

from . import __version__
from .debug_settings import DebugSetting
from .html_report import ReportGenerator
from .old_html_report_style import OldOSCAPReportGenerator
from .scap_results_parser import SCAPResultsParser

DESCRIPTION = ("Generates an HTML report from an ARF (or XCCDF Result) file with results of "
               "a SCAP-compatible utility scan. Unless the --output option is specified "
               "the report will be written to the standard output.")
LOG_LEVES_DESCRIPTION = (
    "LOG LEVELS:\n"
    "\tDEBUG - Detailed information, typically of interest only for diagnosing problems.\n"
    "\tINFO - A confirmation that things are working as expected.\n"
    "\tWARING -  An indication that something unexpected happened, or a signal of"
    " a possible problem in the future. The software is still working as expected.\n"
    "\tERROR - Due to a more serious problems, the software has not been able to perform "
    "its function to the full extent.\n"
    "\tCRITICAL - A serious error, indicating that the program itself may be unable "
    "to continue operating.\n"
)
DEBUG_FLAGS_DESCRIPTION = (
    "DEBUG FLAGS:\n"
    "\tNO-MINIFY - The HTML report will not be minified.\n"
    "\tBUTTON-SHOW-ALL-RULES - Adds a button to the HTML report for expanding all rules.\n"
    "\tONLINE-CSS - Use the latest online version of Patternfly CSS/JS in the HTML report\n"
    "\tBUTTON-SHOW-ALL-RULES-AND-OVAL-TEST-DETAILS - "
    "Adds a button to the HTML report for expanding all rules and all OVAL test details."
)

MASSAGE_FORMAT = '%(levelname)s: %(message)s'
EXPECTED_ERRORS = (XMLSyntaxError, )
EXIT_FAILURE_CODE = 1
EXIT_SUCCESS_CODE = 0


def prepare_parser():
    parser = argparse.ArgumentParser(
        prog="oscap-report",
        formatter_class=argparse.RawTextHelpFormatter,
        description=DESCRIPTION,
        add_help=False,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="Show program's version number and exit.")
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit.')
    parser.add_argument(
        'FILE',
        type=argparse.FileType("r"),
        nargs='?',
        default=stdin,
        help="ARF (XCCDF) file or stdin if not provided.")
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        type=argparse.FileType("wb+", 0),
        default=stdout,
        help="write the report to a file instead of the standard output.")
    parser.add_argument(
        "--log-file",
        action="store",
        default=None,
        help="write the log to a file instead of stderr.")
    parser.add_argument(
        "--log-level",
        action="store",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=(
            "write debug information to the log up to the LOG_LEVEL."
            f"\n{LOG_LEVES_DESCRIPTION}")
    )
    parser.add_argument(
        "-f",
        "--format",
        action="store",
        default="HTML",
        choices=["HTML", "OLD-STYLE-HTML"],
        help="FORMAT: %(choices)s (default: %(default)s)."
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store",
        nargs='+',
        default=[""],
        choices=[
            "NO-MINIFY",
            "BUTTON-SHOW-ALL-RULES",
            "ONLINE-CSS",
            "BUTTON-SHOW-ALL-RULES-AND-OVAL-TEST-DETAILS"
        ],
        help=(
            "extra HTML generation options for debugging"
            f"{DEBUG_FLAGS_DESCRIPTION}")
    )
    return parser


class CommandLineAPI():  # pylint: disable=R0902
    def __init__(self):
        self.arguments = prepare_parser().parse_args()
        self.log_file = self.arguments.log_file
        self.log_level = self.arguments.log_level
        self.debug_flags = self.arguments.debug
        self._setup_logging()
        logging.debug("Args: %s", self.arguments)
        self.report_file = self.arguments.FILE
        self.output_file = self.arguments.output
        self.output_format = self.arguments.format.upper()
        self.debug_setting = DebugSetting()

    def _setup_logging(self):
        logging.basicConfig(
            format=MASSAGE_FORMAT,
            filename=self.log_file,
            filemode='w',
            level=self.log_level.upper()
        )

    def generate_report(self, report_parser):
        logging.info("Generate report")
        if self.output_format == "OLD-STYLE-HTML":
            report_generator = OldOSCAPReportGenerator(report_parser)
            return report_generator.generate_html_report()
        report_generator = ReportGenerator(report_parser)

        self.debug_setting.update_settings_with_debug_flags(self.debug_flags)

        return report_generator.generate_html_report(self.debug_setting)

    def load_file(self):
        logging.info("Loading file: %s", self.report_file)
        return self.report_file.read().encode()

    def store_file(self, data):
        logging.info("Store report")
        if self.output_file.name == "<stdout>":
            logging.info("Output is stdout, converting bytes output to str")
            data = data.read().decode("utf-8")
        self.output_file.writelines(data)

    def close_files(self):
        logging.info("Close files")
        self.report_file.close()
        self.output_file.close()


def main():
    exit_code = EXIT_SUCCESS_CODE
    api = CommandLineAPI()
    arf_report = api.load_file()

    logging.info("Parse file")
    try:
        parser = SCAPResultsParser(arf_report)

        report = api.generate_report(parser)

        api.store_file(report)
    except EXPECTED_ERRORS as error:
        logging.fatal("%s", error)
        exit_code = EXIT_FAILURE_CODE
    api.close_files()
    sys_exit(exit_code)


if __name__ == '__main__':
    main()
