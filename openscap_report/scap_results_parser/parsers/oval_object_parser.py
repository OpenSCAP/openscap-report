# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from lxml.builder import E

from ..data_structures import OvalObject, OvalObjectMessage
from ..namespaces import NAMESPACES
from .shared_static_methods_of_parser import SharedStaticMethodsOfParser

MAX_MESSAGE_LEN = 99


class OVALObjectParser:
    def __init__(self, objects, collected_objects, system_data):
        self.objects = objects
        self.collected_objects = collected_objects
        self.system_data = system_data

    def _get_ref_var(self, var_id):
        # TODO: resolve reference to variable
        return var_id

    def _get_attributes(self, id_in_items_of_object, element, element_dict):
        for key, value in element.attrib.items():
            if key == "var_ref":
                element_dict[f"{key}@{id_in_items_of_object}"] = self._get_ref_var(value)
            else:
                element_dict[f"{key}@{id_in_items_of_object}"] = value

    def _get_object_items(self, xml_object):
        items_of_object = {}
        for element in xml_object:
            id_in_items_of_object = SharedStaticMethodsOfParser.get_unique_id_in_dict(
                element, items_of_object
            )
            element_dict = {}
            if element.text and element.text.strip():
                element_dict[f"{id_in_items_of_object}@text"] = element.text
            if element.attrib:
                self._get_attributes(id_in_items_of_object, element, element_dict)
            items_of_object[id_in_items_of_object] = element_dict
        return items_of_object

    def _get_oval_message(self, xml_collected_object):
        message = xml_collected_object.find(".//oval-characteristics:message", NAMESPACES)
        if message is not None:
            return OvalObjectMessage(message.get("level", ""), message.text)
        return None

    def _get_collected_object_xml(self, id_object):
        return self.collected_objects.get(id_object, E.xml("empty"))

    def get_object(self, id_object):
        xml_object = self.objects.get(id_object)
        object_dict = {
            "object_id": xml_object.get('id'),
            "comment": xml_object.get('comment'),
            "object_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_object),
            "object_data": self._get_object_items(xml_object),
        }
        xml_collected_object = self._get_collected_object_xml(id_object)

        message = self._get_oval_message(xml_collected_object)
        if message is not None:
            object_dict["message"] = message
        object_dict["flag"] = xml_collected_object.get('flag', '')
        return OvalObject(**object_dict)
