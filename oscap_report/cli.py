import argparse
import logging
from sys import stdin, stdout

from . import __version__
from .old_html_report_style.report_generator import ReportGenerator
from .scap_results_parser.scap_results_parser import SCAPResultsParser

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
MASSAGE_FORMAT = '%(levelname)s: %(message)s'


class CommandLineAPI():
    def __init__(self):
        self.arguments = self._parse_arguments()
        self.log_file = self.arguments.log_file
        self.log_level = self.arguments.log_level
        self._setup_logging()
        logging.debug("Args: %s", self.arguments)
        self.report_file = self.arguments.FILE
        self.output_file = self.arguments.output
        self.output_format = self.arguments.format.upper()

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
            type=argparse.FileType("w+"),
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
                "\n{}").format(LOG_LEVES_DESCRIPTION)
        )
        parser.add_argument(
            "-f",
            "--format",
            action="store",
            default="HTML",
            choices=["HTML"],
            help="FORMAT: %(choices)s (default: %(default)s)."
        )

    def _setup_logging(self):
        logging.basicConfig(
            format=MASSAGE_FORMAT,
            filename=self.log_file,
            filemode='w',
            level=self.log_level.upper()
        )

    @staticmethod
    def generate_report(report_parser):
        logging.info("Generate report")
        report_generator = ReportGenerator(report_parser)
        return report_generator.generate_html_report()

    def load_file(self):
        logging.info("Loading file: %s", self.report_file)
        return self.report_file.read().encode()

    def store_file(self, data):
        logging.info("Store report")
        self.output_file.write(data)

    def close_files(self):
        logging.info("Close files")
        self.report_file.close()
        self.output_file.close()


def main():
    api = CommandLineAPI()
    arf_report = api.load_file()

    logging.info("Parse file")
    parser = SCAPResultsParser(arf_report)

    report = api.generate_report(parser)

    api.store_file(report)
    api.close_files()


if __name__ == '__main__':
    main()
