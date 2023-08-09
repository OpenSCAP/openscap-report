# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import OvalState
from .shared_static_methods_of_parser import SharedStaticMethodsOfParser


class OVALStateParser:
    def __init__(self, states):
        self.states = states

    def get_state(self, state_id):
        xml_state = self.states[state_id]
        state_dict = {
            "state_id": xml_state.attrib.get("id"),
            "comment": xml_state.attrib.get("comment", ""),
            "state_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_state),
            "state_data": self._get_state_items(xml_state),
        }
        return OvalState(**state_dict)

    def _get_ref_var(self, var_id):
        # TODO: resolve reference to variable
        return var_id

    def _get_attributes(self, id_in_items_of_state, element, element_dict):
        for key, value in element.attrib.items():
            key = key[key.find('}') + 1:]
            if key == "var_ref":
                element_dict[f"{key}@{id_in_items_of_state}"] = self._get_ref_var(value)
            else:
                element_dict[f"{key}@{id_in_items_of_state}"] = value

    def _get_state_items(self, xml_state):
        items_of_state = {}
        for element in xml_state.iterchildren():
            id_in_items_of_state = SharedStaticMethodsOfParser.get_unique_id_in_dict(
                element, items_of_state
            )

            element_dict = {}
            if element.text and element.text.strip():
                element_dict[f"{id_in_items_of_state}@text"] = element.text
            if element.attrib:
                self._get_attributes(id_in_items_of_state, element, element_dict)

            items_of_state[id_in_items_of_state] = element_dict
        return items_of_state
