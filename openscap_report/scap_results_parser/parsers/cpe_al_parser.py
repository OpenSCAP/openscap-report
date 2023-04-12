# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later
from ..data_structures import LogicalTest, Platform
from ..exceptions import ExceptionNoCPEApplicabilityLanguage
from ..namespaces import NAMESPACES
from .full_text_parser import FullTextParser

TEXT_TO_BOOL = {"true": True, "false": False, "": False}


class CPEApplicabilityLanguageParser:
    def __init__(self, root, oval_cpe_definitions):
        self.root = root
        self.platform_to_oval_cpe_id = self.get_platform_to_oval_cpe_id_dict()
        self.full_text_parser = FullTextParser({})
        self.oval_cpe_definitions = oval_cpe_definitions

    def get_platform_to_oval_cpe_id_dict(self):
        cpe_list = self.root.find(".//ds:component/cpe-dict:cpe-list", NAMESPACES)
        out = {}
        if cpe_list is None:
            return out
        for cpe_item in cpe_list:
            name = cpe_item.get("name")
            check = cpe_item.find(".//cpe-dict:check", NAMESPACES)
            oval_id = check.text if check is not None else name
            out[name] = oval_id
        return out

    def _get_cpe_platform_elements(self):
        cpe_platform_elements = {}
        platform_specification = self.root.find('.//cpe-lang:platform-specification', NAMESPACES)
        if platform_specification is None:
            raise ExceptionNoCPEApplicabilityLanguage
        for platform in platform_specification:
            platform_id = platform.get("id")
            cpe_platform_elements[platform_id] = platform
        return cpe_platform_elements

    def _get_oval_cpe_tree(self, platform_name, check_id_ref):
        oval_tree = None
        oval_cpe_id = None

        if platform_name in self.platform_to_oval_cpe_id:
            oval_cpe_id = self.platform_to_oval_cpe_id[platform_name]

        if check_id_ref is not None:
            oval_cpe_id = check_id_ref

        oval_cpe_definition = self.oval_cpe_definitions.get(oval_cpe_id, None)
        oval_tree = oval_cpe_definition.oval_tree if oval_cpe_definition is not None else None
        return oval_tree

    def get_logical_test(self, logical_test_el):
        operator = logical_test_el.get("operator")
        negation = logical_test_el.get("negate", "")
        logical_test = LogicalTest(operator, negation=TEXT_TO_BOOL[negation])
        for child_logical_test_el in logical_test_el:
            if "fact-ref" in child_logical_test_el.tag:
                platform_name = child_logical_test_el.get("name")
                check_id_ref = child_logical_test_el.get("id-ref")
                logical_test.children.append(
                    LogicalTest(
                        node_type="frac-ref",
                        value=platform_name if platform_name is not None else check_id_ref,
                        oval_tree=self._get_oval_cpe_tree(platform_name, check_id_ref))
                )
            if child_logical_test_el.get('operator') is not None:
                logical_test.children.append(self.get_logical_test(child_logical_test_el))
        return logical_test

    def get_cpe_platforms(self):
        out = {}
        for platform, platform_el in self._get_cpe_platform_elements().items():
            title_el = platform_el.find(".//cpe-lang:title", NAMESPACES)
            title_str = ""
            if title_el is not None:
                self.full_text_parser.get_full_description(title_el)
            logical_test_el = platform_el.find(".//cpe-lang:logical-test", NAMESPACES)

            out[platform] = Platform(
                platform_id=platform,
                logical_test=self.get_logical_test(logical_test_el),
                title=title_str
            )
        return out
