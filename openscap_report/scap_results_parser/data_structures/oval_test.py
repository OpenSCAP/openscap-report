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
