# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from .shared_static_methods_of_parser import SharedStaticMethodsOfParser


class OVALEndpointInformation:
    def __init__(self, oval_var_id_to_value_id, ref_values):
        self.oval_var_id_to_value_id = oval_var_id_to_value_id
        self.ref_values = ref_values

    def _get_oval_var_referenced_value(self, var_id, ids_of_oval_variable):
        value_id = self.oval_var_id_to_value_id.get(var_id, "")
        value = self.ref_values.get(value_id, var_id)
        if value == var_id:
            ids_of_oval_variable.append(var_id)
        return value

    def _parse_attributes(
        self, id_in_items_of_test_property, element, element_dict, ids_of_oval_variable
    ):
        for key, value in element.attrib.items():
            key = key[key.find("}") + 1:]
            if key == "var_ref":
                ref_value = self._get_oval_var_referenced_value(value, ids_of_oval_variable)
                if ref_value == value:
                    element_dict[f"{key}@{id_in_items_of_test_property}"] = ref_value
                else:
                    element_dict[f"value@{id_in_items_of_test_property}"] = ref_value
            else:
                element_dict[f"{key}@{id_in_items_of_test_property}"] = value

    def _get_items(self, xml_test_property):
        items_of_test_property = {}
        ids_of_oval_variable = []
        for element in xml_test_property.iterchildren():
            id_in_items_of_test_property = (
                SharedStaticMethodsOfParser.get_unique_id_in_dict(
                    element, items_of_test_property
                )
            )

            element_dict = {}
            if element.text and element.text.strip():
                element_dict[f"{id_in_items_of_test_property}@text"] = element.text
            if "var_ref" in id_in_items_of_test_property:
                element_dict[
                    f"value@{id_in_items_of_test_property}"
                ] = self._get_oval_var_referenced_value(
                    element.text, ids_of_oval_variable
                )
            if element.attrib:
                self._parse_attributes(
                    id_in_items_of_test_property,
                    element,
                    element_dict,
                    ids_of_oval_variable,
                )

            items_of_test_property[id_in_items_of_test_property] = element_dict
        # TODO: Insert OVAL Variables
        return items_of_test_property
