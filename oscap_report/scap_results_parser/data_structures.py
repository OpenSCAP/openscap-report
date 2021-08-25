from dataclasses import dataclass


@dataclass
class Report:  # pylint: disable=R0902
    title: str = ""
    identity: str = ""
    profile_name: str = ""
    target: str = ""
    cpe_platforms: str = ""
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
        return {
            "title": self.title,
            "profile_name": self.profile_name,
            "target": self.target,
            "identit": self.identity,
            "cpe_platforms": self.cpe_platforms,
            "scanner": self.scanner,
            "scanner_version": self.scanner_version,
            "benchmark_url": self.benchmark_url,
            "benchmark_id": self.benchmark_id,
            "benchmark_version": self.benchmark_version,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "test_system": self.test_system,
            "score": self.score,
            "score_max": self.score_max,
        }
