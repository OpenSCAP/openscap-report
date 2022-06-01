# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

class MissingOVALResult(Exception):
    """Raised when OVAL results are missing in the report"""


class MissingProcessableRules(Exception):
    """Raised when processable rules are missing in the report"""
