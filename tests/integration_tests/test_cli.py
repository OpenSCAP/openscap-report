# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import argparse
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

from openscap_report.cli import CommandLineAPI
from openscap_report.scap_results_parser import SCAPResultsParser

from ..constants import PATH_TO_ARF, PATH_TO_EMPTY_FILE

PATH_TO_RESULT_FILE = Path(tempfile.gettempdir()) / "oscap-report-tests_result.html"
OSCAP_REPORT_COMMAND = "oscap-report"
CAT_ARF_FILE = ["cat", str(PATH_TO_ARF)]


def get_fake_args():
    # pylint: disable=bad-option-value,R1732
    input_file = open(PATH_TO_ARF, "r", encoding="utf-8")
    output_file = open(PATH_TO_RESULT_FILE, "wb")
    return argparse.Namespace(
        FILE=input_file, output=output_file,
        log_file=None, log_level="WARNING", format="HTML",
        debug=[""],
    )


@pytest.mark.unit_test
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=get_fake_args())
def test_load_file(mock_args):  # pylint: disable=W0613
    api = CommandLineAPI()
    xml_report = api.load_file()
    parser = SCAPResultsParser(xml_report)
    assert parser.validate(parser.arf_schemas_path)
    api.close_files()


@pytest.mark.unit_test
@pytest.mark.usefixtures("remove_generated_file")
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=get_fake_args())
def test_store_file(mock_args):  # pylint: disable=W0613
    api = CommandLineAPI()
    data = BytesIO(b'<html><h1>TEST DATA</h1></html>')
    api.store_file(data)
    api.close_files()
    with open(PATH_TO_RESULT_FILE, "r", encoding="utf-8") as result_file:
        assert result_file.read() == data.getvalue().decode("utf-8")


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
