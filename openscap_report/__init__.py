# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from os import path

from pkg_resources import DistributionNotFound, get_distribution

DISTRIBUTION_NAME = "openscap-report"
try:
    distribution = get_distribution(DISTRIBUTION_NAME)
except DistributionNotFound:
    __version__ = f"Version is unavailable. Please install {DISTRIBUTION_NAME}!"
else:
    __version__ = distribution.version
