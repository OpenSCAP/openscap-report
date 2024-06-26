# Copyright 2024, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from typing import List, Tuple

from openscap_report.dataclasses import asdict, dataclass, field


@dataclass
class OVALItems:
    header: Tuple[str] = field(default_factory=tuple)
    entries: List[Tuple[str]] = field(default_factory=list)
    message: str = None

    def as_dict(self):
        return asdict(self)
