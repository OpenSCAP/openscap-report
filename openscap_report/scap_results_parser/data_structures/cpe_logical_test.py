# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import List

from .cpe_result_eval import EMPTY_RESULT, OVAL_RESULT_TO_CPE_RESULT, CpeResult
from .oval_node import OvalNode

NEGATE_VALUE = {
    "true": "false",
    "false": "true",
    "error": "error",
}


@dataclass
class LogicalTest:
    node_type: str  # ref or logical tests
    value: str = ""
    oval_tree: OvalNode = None
    negation: bool = False
    children: List['LogicalTest'] = field(default_factory=list)

    def as_dict(self):
        return asdict(self)

    def _get_result_counts(self):
        result = Counter(EMPTY_RESULT)
        for child in self.children:
            value = None
            if child.node_type == "frac-ref":
                value = str(child.oval_tree.evaluate_tree())
            else:
                value = str(child.evaluate_tree())

            node_result = OVAL_RESULT_TO_CPE_RESULT.get(value, "error")
            if child.negation:
                node_result = NEGATE_VALUE[value]
            result[f"number_of_{node_result}"] += 1
        return result

    def _eval_operator(self, cpe_result):
        out_result = None
        if self.node_type.lower() == "or":
            out_result = cpe_result.eval_operator_or()
        elif self.node_type.lower() == "and":
            out_result = cpe_result.eval_operator_and()
        if out_result is not None:
            self.value = out_result
        return out_result

    def evaluate_tree(self):
        results_counts = self._get_result_counts()
        cpe_result = CpeResult(**results_counts)
        out_result = self._eval_operator(cpe_result)
        if self.negation:
            out_result = NEGATE_VALUE[out_result]
        return out_result
