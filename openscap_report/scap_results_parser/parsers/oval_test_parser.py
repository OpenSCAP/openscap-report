# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import logging

from ..data_structures import OvalTest
from ..namespaces import NAMESPACES
from .oval_object_parser import OVALObjectParser
from .oval_state_parser import OVALStateParser
from .oval_variable_parser import OVALVariableParser


class OVALTestParser:  # pylint: disable=R0902
    def __init__(self, oval_report, oval_var_id_to_value_id, ref_values):
        self.oval_report = oval_report
        self.oval_definitions = self._get_oval_definitions()
        self.tests = self._get_tests()
        self.objects = self._get_objects_by_id()
        self.states = self._get_states_by_id()
        self.variables = self._get_variables_by_id()
        self.oval_system_characteristics = self._get_oval_system_characteristics()
        self.collected_objects = self._get_collected_objects_by_id()
        self.system_data = self._get_system_data_by_id()
        self.variable_parser = OVALVariableParser(
            self.variables,
            oval_var_id_to_value_id,
            ref_values
        )
        self.states_parser = OVALStateParser(self.states)
        self.objects_parser = OVALObjectParser(
            self.objects,
            self.collected_objects,
            self.system_data
        )

    def _get_oval_system_characteristics(self):
        return self.oval_report.find(
            ('.//XMLSchema:results/XMLSchema:system'
             '/oval-characteristics:oval_system_characteristics'), NAMESPACES)

    @staticmethod
    def _get_data_by_id(data):
        if data is None:
            return {}
        return {item.attrib.get('id'): item for item in data}

    def _get_collected_objects_by_id(self):
        data = self.oval_system_characteristics.find(
            './/oval-characteristics:collected_objects', NAMESPACES)
        return self._get_data_by_id(data)

    def _get_system_data_by_id(self):
        data = self.oval_system_characteristics.find(
            './/oval-characteristics:system_data', NAMESPACES)
        return self._get_data_by_id(data)

    def _get_oval_definitions(self):
        return self.oval_report.find(
            ('.//oval-definitions:oval_definitions'), NAMESPACES)

    def _get_tests(self):
        data = self.oval_definitions.find('.//oval-definitions:tests', NAMESPACES)
        return self._get_data_by_id(data)

    def _get_objects_by_id(self):
        data = self.oval_definitions.find(
            ('.//oval-definitions:objects'), NAMESPACES)
        return self._get_data_by_id(data)

    def _get_states_by_id(self):
        data = self.oval_definitions.find(
            ('.//oval-definitions:states'), NAMESPACES)
        return self._get_data_by_id(data)

    def _get_variables_by_id(self):
        data = self.oval_definitions.find(
            ('.//oval-definitions:variables'), NAMESPACES)
        return self._get_data_by_id(data)

    @staticmethod
    def _iter_over_data_and_get_references(dict_, out):
        for key, value in dict_.items():
            if isinstance(value, dict):
                OVALTestParser._iter_over_data_and_get_references(value, out)
            else:
                matches_key = ["object_reference", "var_ref", "object_ref", "filter"]
                matches_val = [":var:", ":obj:", ":ste:"]
                if any(s in key for s in matches_key) and any(s in value for s in matches_val):
                    out.append(value)

    def _resolve_reference(self, ref_id, new_ref, out):
        if ":var:" in ref_id:
            variable = self.variable_parser.get_variable(ref_id)
            self._iter_over_data_and_get_references(variable.variable_data, new_ref)
            out[ref_id] = variable
        elif ":obj:" in ref_id:
            object_ = self.objects_parser.get_object(ref_id)
            self._iter_over_data_and_get_references(object_.object_data, new_ref)
            out[ref_id] = object_
        elif ":ste:" in ref_id:
            state = self.states_parser.get_state(ref_id)
            self._iter_over_data_and_get_references(state.state_data, new_ref)
            out[ref_id] = state
        else:
            logging.warning(ref_id)

    def _get_referenced_endpoints(self, oval_object, oval_states):
        references = []
        object_data = oval_object.object_data if oval_object is not None else {}
        self._iter_over_data_and_get_references(object_data, references)
        for state in oval_states:
            self._iter_over_data_and_get_references(state.state_data, references)

        out = {}
        while len(references) != 0:
            ref = references.pop()
            self._resolve_reference(ref, references, out)
        return out

    def get_test_info(self, test_id):
        test = self.tests[test_id]

        list_object_of_test = test.xpath('.//*[local-name()="object"]')
        list_state_of_test = test.xpath('.//*[local-name()="state"]')

        oval_object_el = list_object_of_test.pop() if list_object_of_test else None

        oval_object = None
        oval_states = []

        if oval_object_el is not None:
            oval_object = self.objects_parser.get_object(oval_object_el.get("object_ref", ""))

        for oval_state_el in list_state_of_test:
            oval_states.append(self.states_parser.get_state(oval_state_el.get("state_ref", "")))

        referenced_oval_endpoints = self._get_referenced_endpoints(oval_object, oval_states)

        return OvalTest(
            test_id=test_id,
            check_existence=test.attrib.get("check_existence", ""),
            check=test.attrib.get("check", ""),
            test_type=test.tag[test.tag.index('}') + 1:],
            comment=test.attrib.get("comment", ""),
            oval_object=oval_object,
            oval_states=oval_states,
            referenced_oval_endpoints=referenced_oval_endpoints,
        )
