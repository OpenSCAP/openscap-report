from dataclasses import dataclass


@dataclass
class OvalObject():
    object_id: str = ""
    flag: str = ""
    object_type: str = ""
    object_data: dict = None

    def as_dict(self):
        return {
            "object_id": self.object_id,
            "flag": self.flag,
            "object_type": self.object_type,
            "object_data": self.object_data,
        }
