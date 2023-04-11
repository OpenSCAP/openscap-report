# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import subprocess
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from openscap_report.cli import CommandLineAPI
from openscap_report.scap_results_parser import SCAPResultsParser

from ..constants import PATH_TO_ARF, PATH_TO_EMPTY_FILE
from ..test_utils import get_fake_args

PATH_TO_RESULT_FILE = Path(tempfile.gettempdir()) / "oscap-report-tests_result.html"
OSCAP_REPORT_COMMAND = "oscap-report"
CAT_ARF_FILE = ["cat", str(PATH_TO_ARF)]


@pytest.mark.integration_test
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=get_fake_args())
def test_generate_report(mock_args):  # pylint: disable=W0613
    data = None
    api = CommandLineAPI()
    with open(PATH_TO_ARF, "r", encoding="utf-8") as arf_report:
        parser = SCAPResultsParser(arf_report.read().encode())
        data = api.generate_report(parser)
    assert data.read().decode("utf-8").startswith("<!DOCTYPE html>")


@pytest.mark.integration_test
@pytest.mark.usefixtures("remove_generated_file")
def test_command_with_input_from_stdin_and_output_to_stdout():
    command_stdout = None
    with subprocess.Popen(CAT_ARF_FILE, stdout=subprocess.PIPE) as cat_command:
        command_stdout = subprocess.check_output(OSCAP_REPORT_COMMAND, stdin=cat_command.stdout)
    assert command_stdout.decode("utf-8").startswith("<!DOCTYPE html>")


@pytest.mark.integration_test
@pytest.mark.usefixtures("remove_generated_file")
@pytest.mark.parametrize("arguments, expected_start_string", [
    (
        [],
        '<!DOCTYPE html><html lang="en" class="pf-m-redhat-font">'
    ),
    (
        ["-f", "HTML"],
        '<!DOCTYPE html><html lang="en" class="pf-m-redhat-font">'
    ),
    (
        ["-f", "OLD-STYLE-HTML"],
        '<!DOCTYPE html>\n<html lang="en">'
    ),
    (
        ["-f", "JSON"],
        "{"
    )
])
def test_command_with_different_formats(arguments, expected_start_string):
    command_stdout = None
    with subprocess.Popen(CAT_ARF_FILE, stdout=subprocess.PIPE) as cat_command:
        command_stdout = subprocess.check_output(
            [OSCAP_REPORT_COMMAND, *arguments], stdin=cat_command.stdout)
    assert command_stdout.decode("utf-8").startswith(expected_start_string)


@pytest.mark.integration_test
@pytest.mark.usefixtures("remove_generated_file")
def test_command_with_input_from_file_and_output_to_stdout():
    command_stdout = subprocess.check_output([OSCAP_REPORT_COMMAND, str(PATH_TO_ARF)])
    assert command_stdout.decode("utf-8").startswith("<!DOCTYPE html>")


@pytest.mark.integration_test
@pytest.mark.usefixtures("remove_generated_file")
def test_command_with_input_from_stdin_and_output_to_file():
    command_stdout = None
    arguments = ["-o", str(PATH_TO_RESULT_FILE)]
    with subprocess.Popen(CAT_ARF_FILE, stdout=subprocess.PIPE) as cat_command:
        command_stdout = subprocess.check_output(
            [OSCAP_REPORT_COMMAND, *arguments], stdin=cat_command.stdout)
    assert not command_stdout.decode("utf-8")
    with open(PATH_TO_RESULT_FILE, "r", encoding="utf-8") as result_file:
        assert result_file.read().startswith("<!DOCTYPE html>")


@pytest.mark.integration_test
@pytest.mark.usefixtures("remove_generated_file")
def test_command_with_input_from_file_and_output_to_file():
    arguments = [str(PATH_TO_ARF), "-o", str(PATH_TO_RESULT_FILE)]
    command_stdout = subprocess.check_output([OSCAP_REPORT_COMMAND, *arguments])
    assert not command_stdout.decode("utf-8")
    with open(PATH_TO_RESULT_FILE, "r", encoding="utf-8") as result_file:
        assert result_file.read().startswith("<!DOCTYPE html>")


@pytest.mark.integration_test
@pytest.mark.usefixtures("remove_generated_file")
def test_logging_to_file():
    log_file_path = Path(tempfile.gettempdir()) / "oscap-report-tests_log-file.log"
    command = [
        OSCAP_REPORT_COMMAND,
        str(PATH_TO_ARF),
        "--log-level", "DEBUG",
        "--log-file", str(log_file_path)
    ]
    command_stdout = subprocess.check_output(command)
    assert command_stdout.decode("utf-8").startswith("<!DOCTYPE html>")
    with open(log_file_path, "r", encoding="utf-8") as result_file:
        assert result_file.read().startswith("DEBUG:")


@pytest.mark.integration_test
def test_command_with_empty_input_file():
    arguments = [str(PATH_TO_EMPTY_FILE)]
    with subprocess.Popen([OSCAP_REPORT_COMMAND, *arguments], stderr=subprocess.PIPE) as command:
        command.wait()
        assert command.returncode == 1
        std_err = command.stderr.read().decode("utf-8")
        assert std_err.startswith("CRITICAL:")
        assert "empty" in std_err


@pytest.mark.integration_test
def test_command_with_empty_stdin():
    cat_command_args = ["cat", str(PATH_TO_EMPTY_FILE)]
    with subprocess.Popen(cat_command_args, stdout=subprocess.PIPE) as cat_command:
        with subprocess.Popen(
                OSCAP_REPORT_COMMAND,
                stdin=cat_command.stdout,
                stderr=subprocess.PIPE) as command:
            command.wait()
            assert command.returncode == 1
            std_err = command.stderr.read().decode("utf-8")
            assert std_err.startswith("CRITICAL:")
            assert "empty" in std_err
