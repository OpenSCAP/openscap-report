# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
import sys
from sys import exit as sys_exit

from lxml.etree import XMLSyntaxError

from . import __version__
from .debug_settings import DebugSetting
from .report_generators import (HTMLReportGenerator,
                                JSONEverythingReportGenerator,
                                JSONReportGenerator,
                                OldStyleHTMLReportGenerator)
from .scap_results_parser import NotSupportedReportingFormat, SCAPResultsParser

DESCRIPTION = ("Generates an HTML report from an ARF (or XCCDF Result) file with results of "
               "a SCAP-compatible utility scan. Unless the --output option is specified "
               "the report will be written to the standard output.")
LOG_LEVELS_DESCRIPTION = """
LOG LEVELS:
    DEBUG - Detailed information, typically of interest only for diagnosing problems.

    INFO - A confirmation that things are working as expected.

    WARNING -  An indication that something unexpected happened, or a signal of a possible problem in the future. The software is still working as expected.

    ERROR - Due to a more serious problems, the software has not been able to perform its function to the full extent.

    CRITICAL - A serious error, indicating that the program itself may be unable to continue operating.
"""

DEBUG_FLAGS_DESCRIPTION = """
DEBUG FLAGS:
    NO-MINIFY - The HTML report will not be minified.

    BUTTON-SHOW-ALL-RULES - Adds a button to the HTML report for expanding all rules.

    ONLINE-CSS - Use the latest online version of Patternfly CSS/JS in the HTML report.

    BUTTON-SHOW-ALL-RULES-AND-OVAL-TEST-DETAILS - Adds a button to the HTML report for expanding all rules and all OVAL test details.
"""

MASSAGE_FORMAT = '%(levelname)s: %(message)s'
EXPECTED_ERRORS = (XMLSyntaxError, NotSupportedReportingFormat)
EXIT_FAILURE_CODE = 1
EXIT_SUCCESS_CODE = 0


class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        parts = []
        if action.nargs == 0:
            parts.extend(action.option_strings)
        else:
            default = action.dest.upper()
            args_string = self._format_args(action, default)
            options_string = ", ".join(action.option_strings)
            parts.append(f'{options_string} {args_string}')
        return ',  '.join(parts)


def prepare_parser():
    parser = argparse.ArgumentParser(
        prog="oscap-report",
        formatter_class=CustomHelpFormatter,
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
        default=sys.stdin,
        help="ARF (XCCDF) file or stdin if not provided.")
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        type=argparse.FileType("wb+", 0),
        default=sys.stdout,
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
            f"\n{LOG_LEVELS_DESCRIPTION}")
    )
    parser.add_argument(
        "-f",
        "--format",
        action="store",
        default="HTML",
        choices=["HTML", "OLD-STYLE-HTML", "JSON", "JSON-EVERYTHING"],
        help="FORMAT: %(choices)s"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store",
        nargs='+',
        default=[""],
        choices=[
            "NO-MINIFY",
            "ONLINE-CSS",
            "BUTTON-SHOW-ALL-RULES",
            "BUTTON-SHOW-ALL-RULES-AND-OVAL-TEST-DETAILS"
        ],
        help=(
            "extra HTML generation options for debugging."
            f"\n{DEBUG_FLAGS_DESCRIPTION}")
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

    def get_report_generator(self, report_parser):
        dict_of_report_generators = {
            "HTML": HTMLReportGenerator,
            "OLD-STYLE-HTML": OldStyleHTMLReportGenerator,
            "JSON": JSONReportGenerator,
            "JSON-EVERYTHING": JSONEverythingReportGenerator,
        }
        return dict_of_report_generators[self.output_format](report_parser)

    def generate_report(self, report_parser):
        logging.info("Generate report")
        report_generator = self.get_report_generator(report_parser)

        self.debug_setting.update_settings_with_debug_flags(self.debug_flags)

        return report_generator.generate_report(self.debug_setting)

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
