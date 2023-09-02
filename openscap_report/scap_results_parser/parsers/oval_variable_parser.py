# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import OvalVariable
from .oval_endpoint_information_parser import OVALEndpointInformation
from .shared_static_methods_of_parser import SharedStaticMethodsOfParser


class OVALVariableParser(OVALEndpointInformation):
    def __init__(self, variables, oval_var_id_to_value_id, ref_values):
        self.oval_var_id_to_value_id = oval_var_id_to_value_id
        self.ref_values = ref_values
        self.variables = variables

    def get_variable(self, variable_id):
        xml_variable = self.variables[variable_id]
        variable_dict = {
            "variable_id": xml_variable.attrib.get("id"),
            "comment": xml_variable.attrib.get("comment", ""),
            "variable_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_variable),
            "variable_data": self._get_items(xml_variable),
        }

        if variable_dict["variable_type"] == "external_variable":
            variable_dict["variable_data"] = {
                "external_variable": {
                    "value": self.ref_values.get(
                        self.oval_var_id_to_value_id.get(variable_id, ""),
                        "not found"
                    )
                }
            }
        return OvalVariable(**variable_dict)
