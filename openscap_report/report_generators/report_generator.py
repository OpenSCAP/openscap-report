# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from abc import ABC, abstractmethod


class ReportGenerator(ABC):
    @abstractmethod
    def __init__(self, parser):
        raise NotImplementedError

    @abstractmethod
    def generate_report(self, debug_setting):
        raise NotImplementedError
