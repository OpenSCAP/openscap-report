# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from .shared_static_methods_of_parser import SharedStaticMethodsOfParser


class OVALEndpointInformation:

    def _parse_attributes(
        self, id_in_items_of_test_property, element, element_dict
    ):
        for key, value in element.attrib.items():
            key = key[key.find("}") + 1:]
            element_dict[f"{key}@{id_in_items_of_test_property}"] = value

    def _get_items(self, xml_test_property):
        items_of_test_property = {}
        for element in xml_test_property.iterchildren():
            id_in_items_of_test_property = (
                SharedStaticMethodsOfParser.get_unique_id_in_dict(
                    element, items_of_test_property
                )
            )

            element_dict = {}
            if element.text and element.text.strip():
                element_dict[f"{id_in_items_of_test_property}@text"] = element.text
            if element.attrib:
                self._parse_attributes(
                    id_in_items_of_test_property,
                    element,
                    element_dict
                )
            if len(element):
                element_dict = self._get_items(element)

            items_of_test_property[id_in_items_of_test_property] = element_dict
        return items_of_test_property
