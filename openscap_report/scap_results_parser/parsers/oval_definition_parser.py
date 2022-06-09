# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

from ..data_structures import OvalNode
from ..exceptions import MissingOVALResult
from ..namespaces import NAMESPACES
from .info_of_test_parser import InfoOfTest

STR_TO_BOOL = {'true': True, 'false': False}
STR_NEGATION_BOOL = {'true': 'false', 'false': 'true'}


class OVALDefinitionParser:
    def __init__(self, root):
        self.root = root
        self.oval_reports = self._get_oval_reports()
        logging.info(self.oval_reports)
        self.oval_results = self._get_oval_results("oval0")
        self.parser_info_of_test = InfoOfTest(self.oval_reports.get("oval0", None))
        self.oval_cpe_results = self._get_oval_results("oval1")
        self.parser_info_of_cpe_test = None
        if "oval1" in self.oval_reports:
            self.parser_info_of_cpe_test = InfoOfTest(self.oval_reports["oval1"])

    def _get_oval_reports(self):
        oval_reports = {}
        reports = self.root.find('.//arf:reports', NAMESPACES)
        if reports is None:
            raise MissingOVALResult

        for report in reports:
            report_id = report.get("id")
            if "oval" in report_id:
                oval_reports[report_id] = report
        return oval_reports

    def _get_oval_results(self, oval_id):
        oval_report = self.oval_reports.get(oval_id, None)
        if oval_report is None:
            return None
        return oval_report.find(
            ('.//XMLSchema:oval_results/XMLSchema:results/'
             'XMLSchema:system/XMLSchema:definitions'), NAMESPACES)

    def _get_oval_definitions(self):
        return self.root.find(
            './/arf:report-requests/arf:report-request/'
            'arf:content/scap:data-stream-collection/'
            'scap:component/oval-definitions:oval_definitions/'
            'oval-definitions:definitions', NAMESPACES)

    def _get_cpe_dict(self):
        cpe_list = self.root.find(".//ds:component/cpe-dict:cpe-list", NAMESPACES)
        cpe_dict = {}
        for cpe_item in cpe_list:
            name = cpe_item.get("name")
            check = cpe_item.find(".//cpe-dict:check", NAMESPACES)
            oval_id = name
            if check is not None:
                oval_id = check.text
            cpe_dict[name] = oval_id
        return cpe_dict

    def get_oval_trees(self):
        dict_of_oval_definitions = {}
        for definition in self.oval_results:
            id_definition = definition.get('definition_id')
            dict_of_oval_definitions[id_definition] = self._build_node(
                definition[0],
                "Definition",
                id_definition=id_definition
            )
        return self._fill_extend_definition(dict_of_oval_definitions)

    def get_oval_cpe_trees(self):
        dict_of_oval_definitions = {}
        if self.oval_cpe_results is None:
            return dict_of_oval_definitions

        for definition in self.oval_cpe_results:
            id_definition = definition.get('definition_id')
            dict_of_oval_definitions[id_definition] = self._build_node(
                definition[0],
                "CPE Definition",
                True,
                id_definition
            )
        oval_cpe_trees = self._fill_extend_definition(dict_of_oval_definitions)
        cpe_dict = self._get_cpe_dict()
        out = {}
        for value, oval_id in cpe_dict.items():
            if oval_id in oval_cpe_trees:
                out[value] = oval_cpe_trees[oval_id]
        return out

    @staticmethod
    def _get_negation(node):
        negation = False
        if node.get('negate') is not None:
            negation = STR_TO_BOOL[node.get('negate')]
        return negation

    @staticmethod
    def _get_result(negation, tree):
        """
            This  method  removes  the  negation of
            the result. Because negation is already
            included in the result in ARF file.
        """
        result = tree.get('result')
        if negation and result in ('true', 'false'):
            result = STR_NEGATION_BOOL[result]
        return result

    def _get_extend_definition_node(self, child):
        negation = self._get_negation(child)
        result_of_node = self._get_result(negation, child)
        return OvalNode(
            node_id=child.get('definition_ref'),
            node_type="extend_definition",
            value=result_of_node,
            negation=negation,
            comment=None,
            tag="Extend definition",
        )

    def _get_test_node(self, child, is_cpe=False):
        negation = self._get_negation(child)
        result_of_node = self._get_result(negation, child)
        test_id = child.get('test_ref')
        parser_of_test_info = self.parser_info_of_test
        if is_cpe:
            parser_of_test_info = self.parser_info_of_cpe_test
        return OvalNode(
            node_id=test_id,
            node_type="value",
            value=result_of_node,
            negation=negation,
            tag="Test",
            test_info=parser_of_test_info.get_test_info(test_id),
        )

    def _build_node(self, tree, tag, is_cpe=False, id_definition=None):
        negation = self._get_negation(tree)
        node = OvalNode(
            node_id=id_definition,
            node_type=tree.get('operator'),
            negation=negation,
            value=self._get_result(negation, tree),
            tag=tag,
            children=[],
        )
        for child in tree:
            if child.get('operator') is not None:
                node.children.append(self._build_node(child, "Criteria", is_cpe))
            else:
                if child.get('definition_ref') is not None:
                    node.children.append(self._get_extend_definition_node(child))
                else:
                    node.children.append(self._get_test_node(child, is_cpe))
        return node

    def _fill_extend_definition(self, dict_of_oval_definitions):
        out = {}
        for id_definition, definition in dict_of_oval_definitions.items():
            out[id_definition] = self._fill_extend_definition_help(
                definition, dict_of_oval_definitions)
        return out

    def _fill_extend_definition_help(self, node, dict_of_oval_definitions):
        out = OvalNode(
            node_id=node.node_id,
            node_type=node.node_type,
            negation=node.negation,
            value=node.value,
            tag=node.tag,
            children=[],
        )
        for child in node.children:
            if child.node_type in ("AND", "OR", "ONE", "XOR"):
                out.children.append(
                    self._fill_extend_definition_help(child, dict_of_oval_definitions))
            elif child.node_type == "extend_definition":
                out.children.append(
                    self._find_definition_by_id(child, dict_of_oval_definitions))
            else:
                out.children.append(child)
        return out

    def _find_definition_by_id(self, node, dict_of_oval_definitions):
        extend_definition_id = node.node_id
        dict_of_oval_definitions[extend_definition_id].negation = node.negation
        dict_of_oval_definitions[extend_definition_id].tag = node.tag
        return self._fill_extend_definition_help(
            dict_of_oval_definitions[extend_definition_id], dict_of_oval_definitions)
