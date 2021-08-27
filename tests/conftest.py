import os
import tempfile
from glob import glob
from pathlib import Path

import pytest


@pytest.fixture()
def remove_generated_file():
    # Removes all files in /tmp which name starts with oscap-report-tests_*
    yield
    pattern = str(Path(tempfile.gettempdir()) / "oscap-report-tests_*")
    for item in glob(pattern):
        if not os.path.isdir(item):
            os.remove(item)
