# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from pathlib import Path

PATH_TO_REMEDIATIONS_SCRIPTS = Path(__file__).parent / "test_data/remediations_scripts"

PATH_TO_EMPTY_XML_FILE = Path(__file__).parent / "test_data/empty.xml"
PATH_TO_EMPTY_FILE = Path(__file__).parent / "test_data/empty.txt"

PATH_TO_ARF = Path(__file__).parent / "test_data/arf-report.xml"
PATH_TO_SIMPLE_RULE_FAIL_ARF = Path(__file__).parent / "test_data/arf_simple_rule_fail.xml"
PATH_TO_SIMPLE_RULE_PASS_ARF = Path(__file__).parent / "test_data/arf_simple_rule_pass.xml"
PATH_TO_RULE_AND_CPE_CHECK_ARF = Path(__file__).parent / "test_data/arf_rule_and_cpe_check.xml"
PATH_TO_ARF_WITHOUT_INFO = Path(__file__).parent / "test_data/arf-with-removed-info.xml"
PATH_TO_ARF_WITHOUT_SYSTEM_DATA = Path(__file__).parent / "test_data/arf_no_system_data.xml"
PATH_TO_ARF_WITH_MULTI_CHECK = Path(__file__).parent / "test_data/arf_multi_check.xml"
PATH_TO_ARF_WITH_OS_CPE_CHECK = Path(__file__).parent / "test_data/arf_cpe_check_os_platform.xml"
PATH_TO_ARF_SCANNED_ON_CONTAINER = Path(__file__).parent / "test_data/arf-container.xml"
PATH_TO_ARF_REPRODUCING_DANGLING_REFERENCE_TO = (
    Path(__file__).parent / "test_data/arf-dangling-reference-to.xml"
)

PATH_TO_XCCDF = Path(__file__).parent / "test_data/xccdf-report.xml"
PATH_TO_SIMPLE_RULE_FAIL_XCCDF = Path(__file__).parent / "test_data/xccdf_simple_rule_fail.xml"
PATH_TO_SIMPLE_RULE_PASS_XCCDF = Path(__file__).parent / "test_data/xccdf_simple_rule_pass.xml"
PATH_TO_RULE_AND_CPE_CHECK_XCCDF = Path(__file__).parent / "test_data/xccdf_rule_and_cpe_check.xml"
PATH_TO_XCCDF_WITHOUT_INFO = Path(__file__).parent / "test_data/xccdf-with-removed-info.xml"
PATH_TO_XCCDF_WITHOUT_SYSTEM_DATA = Path(__file__).parent / "test_data/xccdf_no_system_data.xml"
PATH_TO_XCCDF_WITH_MULTI_CHECK = Path(__file__).parent / "test_data/xccdf_multi_check.xml"
