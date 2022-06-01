# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass

from .oval_object import OvalObject


@dataclass
class OvalTest():
    test_id: str = ""
    test_type: str = ""
    comment: str = ""
    oval_object: OvalObject = None

    def as_dict(self):
        return {
            "test_id": self.test_id,
            "test_type": self.test_type,
            "comment": self.comment,
            "oval_object": self.oval_object.as_dict(),
        }
