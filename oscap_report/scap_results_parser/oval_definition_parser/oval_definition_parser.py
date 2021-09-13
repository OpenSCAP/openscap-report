import logging

from ..data_structures import OvalNode
from ..exceptions import MissingOVALResult
from ..namespaces import NAMESPACES
from .info_of_test_parser import InfoOfTest

STR_TO_BOOL = {'true': True, 'false': False}
STR_NEGATION_BOOL = {'true': 'false', 'false': 'true'}


class OVALDefinitionParser:
    def __init__(self, root):
        self.dict_of_oval_tree_definitions = {}
        self.root = root
        self.oval_reports = self._get_oval_reports()
        logging.info(self.oval_reports)
        self.oval_results = self._get_oval_results("oval0")
        self.oval_cpe_results = self._get_oval_results("oval1")
        self.parser_info_of_test = InfoOfTest(self.oval_reports["oval0"])

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
        return self.oval_reports[oval_id].find(
            ('.//XMLSchema:oval_results/XMLSchema:results/'
             'XMLSchema:system/XMLSchema:definitions'), NAMESPACES)

    def _get_oval_definitions(self):
        return self.root.find(
            './/arf:report-requests/arf:report-request/'
            'arf:content/scap:data-stream-collection/'
            'scap:component/oval-definitions:oval_definitions/'
            'oval-definitions:definitions', NAMESPACES)

    def get_oval_trees(self):
        for definition in self.oval_results:
            id_definition = definition.get('definition_id')
            self.dict_of_oval_tree_definitions[id_definition] = self._build_node(
                definition[0],
                "Definition",
                id_definition
            )
        return self._fill_extend_definition()

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

    def _get_test_node(self, child):
        negation = self._get_negation(child)
        result_of_node = self._get_result(negation, child)
        test_id = child.get('test_ref')
        return OvalNode(
            node_id=test_id,
            node_type="value",
            value=result_of_node,
            negation=negation,
            tag="Test",
            test_info=self.parser_info_of_test.get_test_info(test_id),
        )

    def _build_node(self, tree, tag, id_definition=None):
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
                node.children.append(self._build_node(child, "Criteria"))
            else:
                if child.get('definition_ref') is not None:
                    node.children.append(self._get_extend_definition_node(child))
                else:
                    node.children.append(self._get_test_node(child))
        return node

    def _fill_extend_definition(self):
        out = {}
        for id_definition, definition in self.dict_of_oval_tree_definitions.items():
            out[id_definition] = self._fill_extend_definition_help(definition)
        return out

    def _fill_extend_definition_help(self, node):
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
                out.children.append(self._fill_extend_definition_help(child))
            elif child.node_type == "extend_definition":
                out.children.append(self._find_definition_by_id(child))
            else:
                out.children.append(child)
        return out

    def _find_definition_by_id(self, node):
        extend_definition_id = node.node_id
        self.dict_of_oval_tree_definitions[extend_definition_id].negation = node.negation
        self.dict_of_oval_tree_definitions[extend_definition_id].tag = node.tag
        return self._fill_extend_definition_help(
            self.dict_of_oval_tree_definitions[extend_definition_id])
