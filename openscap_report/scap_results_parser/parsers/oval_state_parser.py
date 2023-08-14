# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import OvalState
from .oval_endpoint_information_parser import OVALEndpointInformation
from .shared_static_methods_of_parser import SharedStaticMethodsOfParser


class OVALStateParser(OVALEndpointInformation):
    def __init__(self, states):
        self.states = states

    def get_state(self, state_id):
        xml_state = self.states[state_id]
        state_dict = {
            "state_id": xml_state.attrib.get("id"),
            "comment": xml_state.attrib.get("comment", ""),
            "state_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_state),
            "state_data": self._get_items(xml_state),
        }
        return OvalState(**state_dict)
