# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from importlib.metadata import PackageNotFoundError, version
from os import path

DISTRIBUTION_NAME = "openscap-report"
try:
    __version__ = version(DISTRIBUTION_NAME)
except PackageNotFoundError:
    __version__ = f"Version is unavailable. Please install {DISTRIBUTION_NAME}!"
