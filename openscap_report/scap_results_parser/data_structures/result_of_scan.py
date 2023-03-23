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
    "score",
    "score_max",
]


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
    score: float = 0.0
    score_max: float = 0.0

    def as_dict(self):
        return asdict(self)
