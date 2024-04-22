# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

DISTRIBUTION_NAME = "openscap-report"
try:
    from importlib.metadata import PackageNotFoundError, version
    try:
        __version__ = version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        __version__ = f"Version is unavailable. Please install {DISTRIBUTION_NAME}!"
except ImportError:
    import pkg_resources
    try:
        __version__ = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        __version__ = f"Version is unavailable. Please install {DISTRIBUTION_NAME}!"
