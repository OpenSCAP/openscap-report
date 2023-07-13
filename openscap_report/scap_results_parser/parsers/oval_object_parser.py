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

    def _get_object_items(self, xml_object):
        items_of_object = {}
        for element in xml_object:
            id_in_items_of_object = SharedStaticMethodsOfParser.get_unique_id_in_dict(
                element, items_of_object
            )
            if element.text and element.text.strip():
                items_of_object[id_in_items_of_object] = element.text
            else:
                items_of_object[id_in_items_of_object] = self._get_ref_var(element)
        return items_of_object

    def _get_item(self, item_ref):
        item_el = self.system_data.get(item_ref)
        item = {}
        for element in item_el:
            if element.text and element.text.strip():
                key = SharedStaticMethodsOfParser.get_unique_id_in_dict(element, item)
                item[key] = element.text
        return item

    def _get_oval_message(self, id_object):
        xml_collected_object = self.collected_objects.get(id_object, E.xml("empty"))
        message = xml_collected_object.find(".//oval-characteristics:message", NAMESPACES)
        if message is not None:
            return OvalObjectMessage(message.get("level", ""), message.text)
        return None

    def get_object(self, id_object):
        xml_object = self.objects.get(id_object)
        object_dict = {
            "object_id": xml_object.get('id'),
            "object_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_object),
            "object_data": [self._get_object_items(xml_object)],
        }
        message = self._get_oval_message(id_object)
        if message is not None:
            object_dict["message"] = message
        return OvalObject(**object_dict)
