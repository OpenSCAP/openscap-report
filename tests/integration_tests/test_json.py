# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import json

import pytest
from jsonschema import validate

from openscap_report.debug_settings import DebugSetting
from openscap_report.report_generators.json import JSONReportGenerator
from tests.unit_tests.test_data_structure import get_parser, get_report

from ..constants import PATH_TO_ARF, PATH_TO_JSON_SCHEMA


@pytest.mark.integration_test
def test_json_structure_with_schema():
    json_schema = None
    with open(PATH_TO_JSON_SCHEMA, "r", encoding="utf-8") as schema_file:
        json_schema = json.load(schema_file)
    json_gen = JSONReportGenerator(get_parser(PATH_TO_ARF))
    json_data = json_gen.generate_report(DebugSetting()).read().decode("utf-8")
    validate(json.loads(json_data), json_schema)


@pytest.mark.integration_test
def test_json_count_of_rules():
    report = get_report()
    json_dict = report.as_dict_for_default_json()
    assert len(json_dict["rules"]) == 714
