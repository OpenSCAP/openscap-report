# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest

from openscap_report.scap_results_parser.data_structures import (EMPTY_RESULT,
                                                                 OvalResult)

BAD_RESULT_COUNTS = {
    "number_of_true": -1,
    "number_of_false": -1,
    "number_of_error": -1,
    "number_of_unknown": -1,
    "number_of_noteval": -1,
    "number_of_notappl": -1
}

RESULT_COUNTS_1 = {
    "number_of_true": 3,
    "number_of_false": 3,
    "number_of_error": 3,
    "number_of_unknown": 0,
    "number_of_noteval": -1,
    "number_of_notappl": 3
}

RESULT_COUNTS_NOTAPPL = dict(**EMPTY_RESULT)
RESULT_COUNTS_NOTAPPL["number_of_notappl"] = 5

# AND cases
RESULT_COUNTS_AND_TRUE = {
    "number_of_true": 2,
    "number_of_false": 0,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_AND_FALSE = {
    "number_of_true": 2,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 1,
    "number_of_noteval": 1,
    "number_of_notappl": 1
}

RESULT_COUNTS_AND_ERROR = {
    "number_of_true": 1,
    "number_of_false": 0,
    "number_of_error": 3,
    "number_of_unknown": 1,
    "number_of_noteval": 1,
    "number_of_notappl": 1
}

RESULT_COUNTS_AND_UNKNOWN = {
    "number_of_true": 0,
    "number_of_false": 0,
    "number_of_error": 0,
    "number_of_unknown": 3,
    "number_of_noteval": 1,
    "number_of_notappl": 2
}

RESULT_COUNTS_AND_NOTEVAL = {
    "number_of_true": 2,
    "number_of_false": 0,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 3,
    "number_of_notappl": 2
}

# OR cases
RESULT_COUNTS_OR_TRUE = {
    "number_of_true": 2,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 2,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_OR_FALSE = {
    "number_of_true": 0,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_OR_ERROR = {
    "number_of_true": 0,
    "number_of_false": 2,
    "number_of_error": 3,
    "number_of_unknown": 1,
    "number_of_noteval": 1,
    "number_of_notappl": 1
}

RESULT_COUNTS_OR_UNKNOWN = {
    "number_of_true": 0,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 3,
    "number_of_noteval": 1,
    "number_of_notappl": 2
}

RESULT_COUNTS_OR_NOTEVAL = {
    "number_of_true": 0,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 3,
    "number_of_notappl": 3
}

# ONE cases
RESULT_COUNTS_ONE_TRUE = {
    "number_of_true": 1,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_ONE_FALSE = {
    "number_of_true": 2,
    "number_of_false": 2,
    "number_of_error": 3,
    "number_of_unknown": 5,
    "number_of_noteval": 2,
    "number_of_notappl": 1
}

RESULT_COUNTS_ONE_FALSE_1 = {
    "number_of_true": 0,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_ONE_ERROR = {
    "number_of_true": 1,
    "number_of_false": 2,
    "number_of_error": 3,
    "number_of_unknown": 1,
    "number_of_noteval": 1,
    "number_of_notappl": 1
}

RESULT_COUNTS_ONE_UNKNOWN = {
    "number_of_true": 1,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 3,
    "number_of_noteval": 4,
    "number_of_notappl": 2
}

RESULT_COUNTS_ONE_NOTEVAL = {
    "number_of_true": 1,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 3,
    "number_of_notappl": 6
}

# XOR cases
RESULT_COUNTS_XOR_TRUE = {
    "number_of_true": 7,
    "number_of_false": 5,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_XOR_FALSE = {
    "number_of_true": 8,
    "number_of_false": 5,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 0,
    "number_of_notappl": 1
}

RESULT_COUNTS_XOR_ERROR = {
    "number_of_true": 5,
    "number_of_false": 2,
    "number_of_error": 3,
    "number_of_unknown": 1,
    "number_of_noteval": 2,
    "number_of_notappl": 1
}

RESULT_COUNTS_XOR_UNKNOWN = {
    "number_of_true": 2,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 3,
    "number_of_noteval": 1,
    "number_of_notappl": 2
}

RESULT_COUNTS_XOR_NOTEVAL = {
    "number_of_true": 2,
    "number_of_false": 2,
    "number_of_error": 0,
    "number_of_unknown": 0,
    "number_of_noteval": 3,
    "number_of_notappl": 5
}


@pytest.mark.unit_test
@pytest.mark.parametrize("eval_function, result", [
    (OvalResult(**RESULT_COUNTS_NOTAPPL).is_notapp_result, True),

    (OvalResult(**BAD_RESULT_COUNTS).eval_operator_and, None),
    (OvalResult(**BAD_RESULT_COUNTS).eval_operator_one, None),
    (OvalResult(**BAD_RESULT_COUNTS).eval_operator_or, None),
    (OvalResult(**BAD_RESULT_COUNTS).eval_operator_xor, None),

    (OvalResult(**EMPTY_RESULT).eval_operator_and, None),
    (OvalResult(**EMPTY_RESULT).eval_operator_one, None),
    (OvalResult(**EMPTY_RESULT).eval_operator_or, None),
    (OvalResult(**EMPTY_RESULT).eval_operator_xor, "false"),

    (OvalResult(**RESULT_COUNTS_1).eval_operator_and, "false"),
    (OvalResult(**RESULT_COUNTS_1).eval_operator_one, None),
    (OvalResult(**RESULT_COUNTS_1).eval_operator_or, "true"),
    (OvalResult(**RESULT_COUNTS_1).eval_operator_xor, "error"),

    (OvalResult(**RESULT_COUNTS_AND_TRUE).eval_operator_and, "true"),
    (OvalResult(**RESULT_COUNTS_AND_FALSE).eval_operator_and, "false"),
    (OvalResult(**RESULT_COUNTS_AND_ERROR).eval_operator_and, "error"),
    (OvalResult(**RESULT_COUNTS_AND_UNKNOWN).eval_operator_and, "unknown"),
    (OvalResult(**RESULT_COUNTS_AND_NOTEVAL).eval_operator_and, "noteval"),

    (OvalResult(**RESULT_COUNTS_OR_TRUE).eval_operator_or, "true"),
    (OvalResult(**RESULT_COUNTS_OR_FALSE).eval_operator_or, "false"),
    (OvalResult(**RESULT_COUNTS_OR_ERROR).eval_operator_or, "error"),
    (OvalResult(**RESULT_COUNTS_OR_UNKNOWN).eval_operator_or, "unknown"),
    (OvalResult(**RESULT_COUNTS_OR_NOTEVAL).eval_operator_or, "noteval"),

    (OvalResult(**RESULT_COUNTS_ONE_TRUE).eval_operator_one, "true"),
    (OvalResult(**RESULT_COUNTS_ONE_FALSE).eval_operator_one, "false"),
    (OvalResult(**RESULT_COUNTS_ONE_FALSE_1).eval_operator_one, "false"),
    (OvalResult(**RESULT_COUNTS_ONE_ERROR).eval_operator_one, "error"),
    (OvalResult(**RESULT_COUNTS_ONE_UNKNOWN).eval_operator_one, "unknown"),
    (OvalResult(**RESULT_COUNTS_ONE_NOTEVAL).eval_operator_one, "noteval"),

    (OvalResult(**RESULT_COUNTS_XOR_TRUE).eval_operator_xor, "true"),
    (OvalResult(**RESULT_COUNTS_XOR_FALSE).eval_operator_xor, "false"),
    (OvalResult(**RESULT_COUNTS_XOR_ERROR).eval_operator_xor, "error"),
    (OvalResult(**RESULT_COUNTS_XOR_UNKNOWN).eval_operator_xor, "unknown"),
    (OvalResult(**RESULT_COUNTS_XOR_NOTEVAL).eval_operator_xor, "noteval"),
])
def test_evaluate_oval_result(eval_function, result):
    assert eval_function() is result
