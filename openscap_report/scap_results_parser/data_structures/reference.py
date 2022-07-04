# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import asdict, dataclass


@dataclass
class Reference:
    href: str
    text: str

    def as_dict(self):
        return asdict(self)
