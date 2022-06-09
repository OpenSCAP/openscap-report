# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import json
import logging
from collections import Counter
from dataclasses import dataclass

from .oval_result_eval import (EMPTY_RESULT, FULL_RESULT_TO_SHORT_RESULT,
                               SHORT_RESULT_TO_FULL_RESULT, OvalResult)
from .oval_test import OvalTest


@dataclass
class OvalNode:  # pylint: disable=R0902
    node_id: str
    node_type: str
    value: str
    negation: bool = False
    comment: str = ""
    tag: str = ""
    children: list = None
    test_info: OvalTest = None

    def as_dict(self):
        if not self.children:
            return {
                'node_id': self.node_id,
                'node_type': self.node_type,
                'value': self.value,
                'negation': self.negation,
                'comment': self.comment,
                'tag': self.tag,
                'test_info': self.test_info.as_dict(),
                'children': None
            }
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'value': self.value,
            'negation': self.negation,
            'comment': self.comment,
            'tag': self.tag,
            'test_info': None,
            'children': [child.as_dict() for child in self.children]
        }

    def as_json(self):
        return json.dumps(self.as_dict())

    def log_oval_tree(self, level=0):
        out = ""
        negation_str = ""
        if self.negation:
            negation_str = "not "
        if self.node_type != "value":
            out = "  " * level + self.node_type + " = " + negation_str + self.value
        else:
            out = "  " * level + self.node_id + " = " + negation_str + self.value
        logging.info(out)
        if self.children is not None:
            for child in self.children:
                child.log_oval_tree(level + 1)

    def _get_result_counts(self):
        result = Counter(EMPTY_RESULT)
        for child in self.children:
            value = child.value
            if child.node_type != "value":
                value = str(child.evaluate_tree())

            node_result = FULL_RESULT_TO_SHORT_RESULT.get(value, value)

            key = f"number_of_{node_result}".replace(" ", "_")

            if child.value == "true" and child.negation:
                key = "number_of_false"
            elif child.value == "false" and child.negation:
                key = "number_of_true"

            result[key] += 1
        return result

    def _eval_operator(self, oval_result):
        out_result = None
        if self.node_type.lower() == "or":
            out_result = oval_result.eval_operator_or()
        elif self.node_type.lower() == "and":
            out_result = oval_result.eval_operator_and()
        elif self.node_type.lower() == "one":
            out_result = oval_result.eval_operator_one()
        elif self.node_type.lower() == "xor":
            out_result = oval_result.eval_operator_xor()
        return out_result

    def evaluate_tree(self):
        results_counts = self._get_result_counts()
        oval_result = OvalResult(**results_counts)
        out_result = None
        if oval_result.is_notapp_result():
            out_result = "notappl"
        else:
            out_result = self._eval_operator(oval_result)

        if out_result == "true" and self.negation:
            out_result = "false"
        elif out_result == "false" and self.negation:
            out_result = "true"

        return SHORT_RESULT_TO_FULL_RESULT.get(out_result, out_result)
