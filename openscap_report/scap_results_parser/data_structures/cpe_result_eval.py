# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import NamedTuple

EMPTY_RESULT = {
    "number_of_error": 0,
    "number_of_true": 0,
    "number_of_false": 0,
}

OVAL_RESULT_TO_CPE_RESULT = {
    "true": "true",
    "false": "false",
    "error": "error",
    "unknown": "error",
    "noteval": "error",
    "notappl": "error",
    "None": "error",
}


class CpeResult(NamedTuple):
    number_of_true: int = 0
    number_of_false: int = 0
    number_of_error: int = 0

    def eval_operator_and(self):
        out_result = None
        false_eq_zero = self.number_of_false == 0
        true_eq_gt_one = self.number_of_true >= 1
        error_eq_zero = self.number_of_error == 0
        if true_eq_gt_one and false_eq_zero and error_eq_zero:
            out_result = "true"
        elif self.number_of_false >= 1:
            out_result = "false"
        # According to the table in the CPE specification,
        # there should be self.number_of_true >= 1, but
        # there isn't specified case for:
        # {"number_of_true": 0, "number_of_false": 0, "number_of_error": 1}
        elif self.number_of_true >= 0 and false_eq_zero and self.number_of_error >= 1:
            out_result = "error"
        return out_result

    def eval_operator_or(self):
        out_result = None
        true_eq_zero = self.number_of_true == 0
        false_ge_one = self.number_of_false >= 1
        error_eq_zero = self.number_of_error == 0
        if self.number_of_true >= 1:
            out_result = "true"
        elif true_eq_zero and false_ge_one and error_eq_zero:
            out_result = "false"
        # According to the table in the CPE specification,
        # there should be self.number_of_false >= 1, but
        # there isn't specified case for:
        # {"number_of_true": 0, "number_of_false": 0, "number_of_error": 1}
        elif true_eq_zero and self.number_of_false >= 0 and self.number_of_error >= 1:
            out_result = "error"
        return out_result
