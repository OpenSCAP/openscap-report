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

    def _get_state_items(self, xml_state):
        out = {}
        for element in xml_state.iterchildren():
            id_in_dict = SharedStaticMethodsOfParser.get_unique_id_in_dict(element, out)
            if element.text and element.text.strip():
                out[id_in_dict] = element.text
            else:
                out[id_in_dict] = element.get("var_ref")

            operation = element.get("operation")
            if operation is not None:
                out["operation"] = operation
        return out
