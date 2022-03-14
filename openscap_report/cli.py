import argparse
import logging
from dataclasses import dataclass
from sys import exit as sys_exit
from sys import stdin, stdout

from lxml.etree import XMLSyntaxError

from . import __version__
from .html_report import ReportGenerator
from .old_html_report_style import OldOSCAPReportGenerator
from .scap_results_parser import SCAPResultsParser

DESCRIPTION = ("Generate a HTML (JSON, PDF?, Printable HTML, etc) document (HTML report)"
               " from an ARF (or XCCDF file) containing results of oscap scan. Unless"
               " the --output option is specified it will be written to standard output.")
LOG_LEVES_DESCRIPTION = (
    "LOG LEVELS:\n"
    "\tDEBUG - Detailed information, typically of interest only when diagnosing problems.\n"
    "\tINFO - Confirmation that things are working as expected.\n"
    "\tWARING -  An indication that something unexpected happened, or indicative of"
    " some problem in the near future. The software is still working as expected.\n"
    "\tERROR - Due to a more serious problem, the software has not been able to perform "
    "some function.\n"
    "\tCRITICAL - A serious error, indicating that the program itself may be unable "
    "to continue running.\n"
)
DEBUG_FLAGS_DESCRIPTION = (
    "DEBUG FLAGS:\n"
    "\tNO-MINIFY - The HTML report is not minified.\n"
    "\tBUTTON-SHOW-ALL-RULES - Adds the button that shows all rules."
)

MASSAGE_FORMAT = '%(levelname)s: %(message)s'
EXPECTED_ERRORS = (XMLSyntaxError, )
EXIT_FAILURE_CODE = 1
EXIT_SUCCESS_CODE = 0


class CommandLineAPI():  # pylint: disable=R0902
    def __init__(self):
        self.arguments = self._parse_arguments()
        self.log_file = self.arguments.log_file
        self.log_level = self.arguments.log_level
        self.debug_flags = self.arguments.debug
        self._setup_logging()
        logging.debug("Args: %s", self.arguments)
        self.report_file = self.arguments.FILE
        self.output_file = self.arguments.output
        self.output_format = self.arguments.format.upper()
        self.debug_setting = DebugSetting()

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            prog="oscap-report",
            formatter_class=argparse.RawTextHelpFormatter,
            description=DESCRIPTION,
            add_help=False,
        )
        self._prepare_arguments(parser)
        return parser.parse_args()

    @staticmethod
    def _prepare_arguments(parser):
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
            help="ARF file, stdin if not provided.")
        parser.add_argument(
            "-o",
            "--output",
            action="store",
            type=argparse.FileType("wb+", 0),
            default=stdout,
            help="write the report to this file instead of standard output.")
        parser.add_argument(
            "--log-file",
            action="store",
            default=None,
            help="if not provided - stderr.")
        parser.add_argument(
            "--log-level",
            action="store",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help=(
                "creates LOG_FILE file with log information depending on LOG_LEVEL."
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
            choices=["NO-MINIFY", "BUTTON-SHOW-ALL-RULES"],
            help=f"{DEBUG_FLAGS_DESCRIPTION}"
        )

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


@dataclass
class DebugSetting():
    no_minify: bool = False
    options_require_debug_script: tuple = ("BUTTON-SHOW-ALL-RULES", )
    include_debug_script: bool = False
    button_show_all_rules: bool = False

    def update_settings_with_debug_flags(self, debug_flags):
        for flag in debug_flags:
            if flag in self.options_require_debug_script:
                self.include_debug_script = True
            if flag == "NO-MINIFY":
                self.no_minify = True
            if flag == "BUTTON-SHOW-ALL-RULES":
                self.button_show_all_rules = True


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
