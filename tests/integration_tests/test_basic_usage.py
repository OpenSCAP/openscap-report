# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import subprocess

import pytest

# pylint: disable-msg=R0801
from ..constants import (PATH_TO_ARF,
                         PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO,
                         PATH_TO_ARF_SCANNED_ON_CONTAINER,
                         PATH_TO_ARF_WITH_MULTI_CHECK,
                         PATH_TO_ARF_WITH_OS_CPE_CHECK,
                         PATH_TO_ARF_WITHOUT_INFO,
                         PATH_TO_ARF_WITHOUT_SYSTEM_DATA,
                         PATH_TO_RULE_AND_CPE_CHECK_ARF,
                         PATH_TO_RULE_AND_CPE_CHECK_XCCDF,
                         PATH_TO_SIMPLE_RULE_FAIL_ARF,
                         PATH_TO_SIMPLE_RULE_FAIL_XCCDF,
                         PATH_TO_SIMPLE_RULE_PASS_ARF,
                         PATH_TO_SIMPLE_RULE_PASS_XCCDF, PATH_TO_XCCDF,
                         PATH_TO_XCCDF_WITH_MULTI_CHECK,
                         PATH_TO_XCCDF_WITHOUT_INFO,
                         PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA)

OSCAP_REPORT_COMMAND = "oscap-report"


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "file_path",
    [
        PATH_TO_ARF,
        PATH_TO_SIMPLE_RULE_FAIL_ARF,
        PATH_TO_SIMPLE_RULE_PASS_ARF,
        PATH_TO_RULE_AND_CPE_CHECK_ARF,
        PATH_TO_ARF_WITHOUT_INFO,
        PATH_TO_ARF_WITHOUT_SYSTEM_DATA,
        PATH_TO_ARF_WITH_MULTI_CHECK,
        PATH_TO_ARF_WITH_OS_CPE_CHECK,
        PATH_TO_ARF_SCANNED_ON_CONTAINER,
        PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO,
        PATH_TO_XCCDF,
        PATH_TO_SIMPLE_RULE_FAIL_XCCDF,
        PATH_TO_SIMPLE_RULE_PASS_XCCDF,
        PATH_TO_RULE_AND_CPE_CHECK_XCCDF,
        PATH_TO_XCCDF_WITHOUT_INFO,
        PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA,
        PATH_TO_XCCDF_WITH_MULTI_CHECK,
    ],
)
def test_oscap_report_basic_usage(file_path):
    command_stdout = subprocess.check_output([OSCAP_REPORT_COMMAND, str(file_path)])
    assert command_stdout.decode("utf-8").startswith("<!DOCTYPE html>")
