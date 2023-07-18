# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass, field
from typing import List

SCAN_JSON_KEYS = [
    "title",
    "identity",
    "profile_id",
    "target",
    "cpe_platforms",
    "scanner",
    "scanner_version",
    "benchmark_url",
    "benchmark_id",
    "benchmark_version",
    "start_time",
    "end_time",
    "test_system",
    "score_system",
    "score",
    "score_max",
]

SCORE_COMPUTATION_EXPLANATIONS = {
    "urn:xccdf:scoring:default": (
        "The default model score computation algorithm simply computes a normalized weighted sum "
        "at each tree node, omitting Rules and Groups that are not selected, and Groups that have "
        "no selected Rules under them. (Visualization of Groups in report is not implemented yet.)"
    ),
    "urn:xccdf:scoring:flat": (
        "The flat model simply computes the sum of the weights for the Rules that passed "
        "as the score, and the sum of the weights of all the applicable Rules as "
        "the maximum possible score. This model is simple and easy to compute, "
        "but scores between different target systems may not be directly comparable "
        "because the maximum score can vary."
    ),
    "urn:xccdf:scoring:flat-unweighted": (
        "The flat unweighted model simply computes the sum of the Rules that passed as the score, "
        "and the sum of all the applicable Rules as the maximum possible score. This model is "
        "simple and easy to compute, but scores between different target systems may not be "
        "directly comparable because the maximum score can vary."
    ),
    "urn:xccdf:scoring:absolute": (
        "The absolute model gives a score of 1 only when all applicable rules "
        "in the benchmark pass. It is computed by applying the Flat Model "
        "and returning 1 if s==m, and 0 otherwise."
    )
}


@dataclass
class ResultOfScan:  # pylint: disable=R0902
    title: str = ""
    identity: str = ""
    profile_id: str = ""
    target: str = ""
    cpe_platforms: List[str] = field(default_factory=list)
    scanner: str = ""
    scanner_version: str = ""
    benchmark_url: str = ""
    benchmark_id: str = ""
    benchmark_version: str = ""
    start_time: str = ""
    end_time: str = ""
    test_system: str = ""
    score_system: str = ""
    score: float = 0.0
    score_max: float = 0.0

    def as_dict(self):
        return asdict(self)

    def get_explanation_of_score_computation(self):
        return SCORE_COMPUTATION_EXPLANATIONS[self.score_system]
