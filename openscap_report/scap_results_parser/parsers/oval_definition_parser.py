# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import OvalDefinition, OvalReference
from ..exceptions import MissingOVALResult
from ..namespaces import NAMESPACES
from .oval_result_parser import OVALResultParser


class OVALDefinitionParser:
    def __init__(self, root, oval_var_id_to_value_id, ref_values):
        self.root = root
        self.oval_result_parser = OVALResultParser(self.root, oval_var_id_to_value_id, ref_values)
        self.oval_trees_by_oval_reports = self.oval_result_parser.get_oval_trees_by_oval_reports()

        self.oval_reports = self.oval_result_parser.oval_reports
        self.oval_definitions = self._get_xml_elements_of_oval_definitions()

    def _get_xml_elements_of_oval_definitions(self):
        out = {}
        for oval, oval_report in self.oval_reports.items():
            out[oval] = oval_report.oval_report_element.find(
                './/oval-definitions:oval_definitions/oval-definitions:definitions', NAMESPACES)
        return out

    def _get_references(self, definition):
        references = []
        for ref in definition.findall('.//oval-definitions:reference', NAMESPACES):
            references.append(OvalReference(ref.get("source"), ref.get("ref_id")))
        return references

    def parse_oval_definition(self, definition_id, definition_class, definition):
        oval_definition_dict = {
            "definition_id": definition_id,
            "definition_class": definition_class,
            "title": definition.find('.//oval-definitions:title', NAMESPACES).text,
            "description": definition.find('.//oval-definitions:description', NAMESPACES).text,
            "version": definition.get("version"),
            "references": self._get_references(definition),
        }
        return OvalDefinition(**oval_definition_dict)

    def _get_oval_definitions(self, oval):
        if oval not in self.oval_definitions:
            raise MissingOVALResult(oval)

        definitions = {}
        dict_of_criteria = {}
        for definition in self.oval_definitions[oval]:
            definition_id = definition.get("id")
            definition_class = definition.get("class")
            oval_definition = self.parse_oval_definition(
                definition_id,
                definition_class,
                definition
            )
            criteria = definition.find('.//oval-definitions:criteria', NAMESPACES)
            dict_of_criteria[definition_id] = self._create_dict_from_criteria(criteria)
            definitions[definition_id] = oval_definition

        self._add_comments_to_oval_tree(dict_of_criteria, oval)
        self._add_oval_tree_to_definition(definitions, oval)
        return definitions

    def get_oval_definitions(self):
        oval_definitions_by_reports = {}
        for report_id in self.oval_trees_by_oval_reports:
            oval_definitions_by_reports[report_id] = self._get_oval_definitions(report_id)
        return oval_definitions_by_reports

    def _get_test_criteria(self, criterion):
        out = {"comment": criterion.get("comment")}
        if criterion.get('definition_ref'):
            out['extend_definition'] = criterion.get('definition_ref')
        else:
            out['value_id'] = criterion.get('test_ref')
        return out

    def _create_dict_from_criteria(self, criteria):
        criteria_dict = {
            "operator": criteria.get("operator", "AND"),
            "comment": criteria.get("comment"),
            "child_criteria": [],
        }
        for criterion in criteria:
            if criterion.get("operator") or "criteria" in criterion.tag:
                criteria_dict["child_criteria"].append(self._create_dict_from_criteria(criterion))
            else:
                criteria_dict["child_criteria"].append(self._get_test_criteria(criterion))
        return criteria_dict

    def _add_oval_tree_to_definition(self, definitions, oval_report_id):
        oval_tree_source = self.oval_trees_by_oval_reports.get(oval_report_id, {})
        for definition_id in definitions:
            self._set_oval_tree_to_definition(definitions, definition_id, oval_tree_source)

    def _set_oval_tree_to_definition(self, definitions, definition_id, oval_tree_source):
        if definition_id in oval_tree_source:
            oval_tree_source[definition_id].comment = definitions[definition_id].description
            definitions[definition_id].oval_tree = oval_tree_source[definition_id]

    @staticmethod
    def _get_criteria(criteria_id, criteria, criteria_dict):
        if criteria is None and criteria_id is not None:
            criteria = criteria_dict[criteria_id]
        return criteria

    @staticmethod
    def _set_comment_to_oval_tree(oval_tree, criteria):
        if not oval_tree.comment:
            oval_tree.comment = criteria.get("comment")

    def _fill_oval_tree_with_comments(self, oval_tree, criteria_id, criteria_dict, criteria=None):
        criteria = self._get_criteria(criteria_id, criteria, criteria_dict)
        self._set_comment_to_oval_tree(oval_tree, criteria)

        for criterion, oval_node in zip(criteria["child_criteria"], oval_tree.children):
            oval_node.comment = criterion.get("comment")
            if criterion.get('operator'):
                self._fill_oval_tree_with_comments(
                    oval_node, None, criteria_dict, criterion)
            if criterion.get("extend_definition"):
                self._fill_oval_tree_with_comments(
                    oval_node, criterion.get("extend_definition"), criteria_dict)

    def _add_comments_to_oval_tree(self, dict_of_criteria, oval_report_id):
        oval_tree_source = self.oval_trees_by_oval_reports.get(oval_report_id, {})
        for id_ in dict_of_criteria:

            if id_ not in oval_tree_source:
                continue

            oval_tree = oval_tree_source[id_]
            self._fill_oval_tree_with_comments(oval_tree, id_, dict_of_criteria)
