# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later
from dataclasses import asdict, dataclass

WARNING_JSON_KEYS = [
    "text",
    "category",
]


@dataclass
class RuleWarning:
    text: str
    category: str = ""

    def as_dict(self):
        return asdict(self)
