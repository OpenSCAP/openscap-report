# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

class MissingOVALResult(Exception):
    """Raised when OVAL results are missing in the report"""


class MissingProcessableRules(Exception):
    """Raised when processable rules are missing in the report"""


class ExceptionNoCPEApplicabilityLanguage(Exception):
    """Raise when there is no CPE Applicability Language platform specification"""


class NotSupportedReportingFormat(Exception):
    """Raise when the given input isn't a valid ARF report or XCCDF report"""
