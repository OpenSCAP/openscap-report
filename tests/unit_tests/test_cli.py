# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import tempfile
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

from openscap_report.cli import CommandLineAPI
from openscap_report.scap_results_parser import (ARF_SCHEMAS_PATH,
                                                 SCAPResultsParser)

from ..test_utils import get_fake_args

PATH_TO_RESULT_FILE = Path(tempfile.gettempdir()) / "oscap-report-tests_result.html"


@pytest.mark.unit_test
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=get_fake_args())
def test_load_file(mock_args):  # pylint: disable=W0613
    api = CommandLineAPI()
    xml_report = api.load_file()
    parser = SCAPResultsParser(xml_report)
    assert parser.validate(ARF_SCHEMAS_PATH)
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
