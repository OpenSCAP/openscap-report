# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass

IDENTIFIER_JSON_KEYS = [
    "system",
    "text",
]


@dataclass
class Identifier:
    system: str
    text: str

    def as_dict(self):
        return asdict(self)
