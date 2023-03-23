# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import OvalObject, OvalObjectMessage
from ..namespaces import NAMESPACES
from .shared_static_methods_of_parser import SharedStaticMethodsOfParser

MAX_MESSAGE_LEN = 99


class OVALObjectParser:
    def __init__(self, objects, collected_objects, system_data):
        self.objects = objects
        self.collected_objects = collected_objects
        self.system_data = system_data

    @staticmethod
    def _find_item_ref(object_):
        list_of_item_ref = [item.get('item_ref') for item in object_]
        return list(filter(None, list_of_item_ref))

    @staticmethod
    def _complete_message(item, var_id):
        if len(item.text) == MAX_MESSAGE_LEN and var_id[:item.text.find('(')] in var_id:
            return f"{item.text[:item.text.find('(') + 1]}{var_id})"
        return item.text

    def _get_ref_var(self, element, xml_collected_object):
        if xml_collected_object is None or 'var_ref' not in element.attrib:
            return 'no value'
        variable_values = []
        var_id = element.get('var_ref')
        for item in xml_collected_object:
            if var_id == item.get('variable_id'):
                variable_values.append(item.text)
            elif 'message' in SharedStaticMethodsOfParser.get_key_of_xml_element(item):
                variable_values.append(self._complete_message(item, var_id))
        return "\n".join(variable_values)

    def _get_object_items(self, xml_object, xml_collected_object):
        items_of_object = {}
        for element in xml_object:
            id_in_items_of_object = SharedStaticMethodsOfParser.get_unique_id_in_dict(
                element, items_of_object
            )
            if element.text and element.text.strip():
                items_of_object[id_in_items_of_object] = element.text
            else:
                items_of_object[id_in_items_of_object] = self._get_ref_var(
                    element, xml_collected_object
                )
        return items_of_object

    def _get_item(self, item_ref):
        item_el = self.system_data.get(item_ref)
        item = {}
        for element in item_el:
            if element.text and element.text.strip():
                key = SharedStaticMethodsOfParser.get_unique_id_in_dict(element, item)
                item[key] = element.text
        return item

    def _get_oval_message(self, xml_collected_object):
        message = xml_collected_object.find(".//oval-characteristics:message", NAMESPACES)
        if message is not None:
            return OvalObjectMessage(message.get("level", ""), message.text)
        return None

    def _get_collected_objects_info(self, xml_collected_object, xml_object):
        object_dict = {
            "object_id": xml_collected_object.get('id'),
            "flag": xml_collected_object.get('flag'),
            "object_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_object),
        }
        message = self._get_oval_message(xml_collected_object)
        if message is not None:
            object_dict["message"] = message

        if len(xml_collected_object) == 0:
            object_dict["object_data"] = [self._get_object_items(xml_object, xml_collected_object)]
        else:
            item_refs = self._find_item_ref(xml_collected_object)
            items = []
            if item_refs:
                for item_id in item_refs:
                    items.append(self._get_item(item_id))
            else:
                items.append(self._get_object_items(xml_object, xml_collected_object))
            object_dict["object_data"] = items
        return OvalObject(**object_dict)

    def get_object(self, id_object):
        xml_object = self.objects.get(id_object)
        xml_collected_object = self.collected_objects.get(id_object)
        if xml_collected_object is not None:
            return self._get_collected_objects_info(xml_collected_object, xml_object)
        object_dict = {
            "object_id": xml_object.get('id'),
            "flag": "does not exist",
            "object_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_object),
            "object_data": [self._get_object_items(xml_object, xml_collected_object)],
        }
        return OvalObject(**object_dict)
