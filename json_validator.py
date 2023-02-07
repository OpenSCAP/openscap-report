#!/usr/bin/env python3

# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import argparse
import json
import sys

from jsonschema import validate


def parse_args():
    parser = argparse.ArgumentParser(prog='JSON Schema validator')
    parser.add_argument("-s",
                        "--schema",
                        type=str,
                        default="./tests/json_schema_of_report.json",
                        help="Path to schema of JSON to validate."
                        )
    parser.add_argument('JSON',
                        type=argparse.FileType("r"),
                        nargs='?',
                        default=sys.stdin,
                        help="JSON file source. Default: stdin"
                        )
    return parser.parse_args()


def validate_json(schema_src, json_file):
    json_schema = None
    json_data = None

    with open(schema_src, "r", encoding="utf-8") as schema_file:
        json_schema = json.load(schema_file)

    json_data = json.load(json_file)
    json_file.close()

    validate(json_data, json_schema)


def main():
    args = parse_args()
    validate_json(args.schema, args.JSON)


if __name__ == "__main__":
    main()
