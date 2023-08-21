# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
import uuid
from dataclasses import dataclass

from lxml.etree import Element

from ..data_structures import OvalNode
from ..exceptions import MissingOVALResult
from ..namespaces import NAMESPACES
from .oval_test_parser import OVALTestParser

STR_TO_BOOL = {'true': True, 'false': False}
STR_NEGATION_BOOL = {'true': 'false', 'false': 'true'}


@dataclass
class OVALReport:
    oval_report_id: str
    oval_report_element: Element
    oval_results_element: Element
    oval_test_parser: OVALTestParser


class OVALResultParser:
    def __init__(self, root, oval_var_id_to_value_id, ref_values):
        self.root = root
        self.oval_var_id_to_value_id = oval_var_id_to_value_id
        self.ref_values = ref_values
        self.oval_reports = self._get_oval_reports()
        logging.info(self.oval_reports)

    def _get_oval_reports(self):
        oval_reports = {}
        reports = self.root.find('.//arf:reports', NAMESPACES)
        if reports is None:
            raise MissingOVALResult("all_OVAL_results")

        for report_element in reports:
            report_id = report_element.get("id")
            if "oval" in report_id:
                oval_results = self._get_oval_results(report_element)
                oval_test_parser = OVALTestParser(
                    report_element, self.oval_var_id_to_value_id, self.ref_values
                )
                oval_reports[report_id] = OVALReport(
                    report_id,
                    report_element,
                    oval_results,
                    oval_test_parser
                )
        return oval_reports

    def _get_oval_results(self, oval_report):
        return oval_report.find(
            ('.//XMLSchema:oval_results/XMLSchema:results/'
             'XMLSchema:system/XMLSchema:definitions'), NAMESPACES)

    def get_oval_trees_by_oval_reports(self):
        dict_of_oval_reports = {}
        for report_id, report in self.oval_reports.items():
            dict_of_oval_results = {}
            for definition in report.oval_results_element:
                id_definition = definition.get('definition_id')
                criteria_result = definition[0]
                dict_of_oval_results[id_definition] = self._build_node(
                    criteria_result,
                    "Definition",
                    id_definition,
                    report_id
                )
            dict_of_oval_reports[report_id] = self._fill_extend_definition(dict_of_oval_results)
        return dict_of_oval_reports

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
            tag="Extend definition",
        )

    def _get_test_node(self, child, oval_report_id):
        negation = self._get_negation(child)
        result_of_node = self._get_result(negation, child)
        test_id = child.get('test_ref')
        oval_test_parser = self.oval_reports[oval_report_id].oval_test_parser
        return OvalNode(
            node_id=test_id,
            node_type="value",
            value=result_of_node,
            negation=negation,
            tag="Test",
            test_info=oval_test_parser.get_test_info(test_id),
        )

    def _build_node(self, tree, tag, id_definition, oval_report_id):
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
                node.children.append(
                    self._build_node(
                        child,
                        "Criteria",
                        f"no-id-criteria-{uuid.uuid4()}",
                        oval_report_id
                    )
                )
            else:
                if child.get('definition_ref') is not None:
                    node.children.append(self._get_extend_definition_node(child))
                else:
                    node.children.append(self._get_test_node(child, oval_report_id))
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
