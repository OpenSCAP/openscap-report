# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import uuid

from ..data_structures import OvalObject, OvalTest
from ..namespaces import NAMESPACES

MAX_MESSAGE_LEN = 99


class InfoOfTest:
    def __init__(self, oval_report):
        self.oval_report = oval_report
        self.oval_definitions = self._get_oval_definitions()
        self.tests = self._get_tests()
        self.objects = self._get_objects_by_id()
        self.oval_system_characteristics = self._get_oval_system_characteristics()
        self.collected_objects = self._get_collected_objects_by_id()
        self.system_data = self._get_system_data_by_id()

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

    @staticmethod
    def get_key_of_xml_element(element):
        return element.tag[element.tag.index('}') + 1:] if '}' in element.tag else element.tag

    @staticmethod
    def _find_item_ref(object_):
        list_of_item_ref = [item.get('item_ref') for item in object_]
        return list(filter(None, list_of_item_ref))

    @staticmethod
    def _get_unique_key(key):
        return key + '@' + str(uuid.uuid4())

    def _get_unique_id_in_dict(self, object_, dict_):
        if self.get_key_of_xml_element(object_) in dict_:
            return self._get_unique_key(self.get_key_of_xml_element(object_))
        return self.get_key_of_xml_element(object_)

    def _get_collected_objects_info(self, xml_collected_object, xml_object):
        object_dict = {}
        object_dict["object_id"] = xml_collected_object.attrib.get('id')
        object_dict["flag"] = xml_collected_object.attrib.get('flag')
        object_dict["object_type"] = self.get_key_of_xml_element(xml_object)
        if len(xml_collected_object) == 0:
            object_dict["object_data"] = self._get_object_items(xml_object, xml_collected_object)
        else:
            item_refs = self._find_item_ref(xml_collected_object)
            items = []
            if item_refs:
                for item_id in item_refs:
                    items.append(self._get_item(item_id))
            else:
                items = self._get_object_items(xml_object, xml_collected_object)
            object_dict["object_data"] = items
        return OvalObject(**object_dict)

    def get_object(self, id_object):
        xml_object = self.objects.get(id_object)
        xml_collected_object = self.collected_objects.get(id_object)
        if xml_collected_object is not None:
            return self._get_collected_objects_info(xml_collected_object, xml_object)
        object_dict = {}
        object_dict["object_id"] = xml_object.attrib.get('id')
        object_dict["flag"] = "does not exist"
        object_dict["object_type"] = self.get_key_of_xml_element(xml_object)
        object_dict["object_data"] = self._get_object_items(xml_object, xml_collected_object)
        return OvalObject(**object_dict)

    def _get_object_items(self, xml_object, xml_collected_object):
        out = []
        for element in xml_object.iterchildren():
            id_in_dict = self._get_unique_id_in_dict(element, out)
            if element.text and element.text.strip():
                out.append({id_in_dict: element.text})
            else:
                out.append({id_in_dict: self._get_ref_var(element, xml_collected_object)})
        if len(out) > 1:
            return [dict(pair for dict_item in out for pair in dict_item.items())]
        return out

    def _get_ref_var(self, element, xml_collected_object):
        variable_value = ''
        if self._collected_object_is_not_none_and_contain_var_ref(
                element, xml_collected_object):
            var_id = element.attrib.get('var_ref')
            for item in xml_collected_object:
                if var_id == item.attrib.get('variable_id'):
                    variable_value += item.text
                elif self.get_key_of_xml_element(item) == 'message':
                    variable_value += self._complete_message(item, var_id) + '<br>'
        else:
            variable_value = 'no value'
        return variable_value

    @staticmethod
    def _complete_message(item, var_id):
        if len(item.text) == MAX_MESSAGE_LEN and var_id[:item.text.find('(')] in var_id:
            return f"{item.text[:item.text.find('(') + 1]}{var_id})"
        return item.text

    @staticmethod
    def _collected_object_is_not_none_and_contain_var_ref(element, collected_object):
        return collected_object is not None and 'var_ref' in element.attrib

    def _get_item(self, item_ref):
        item = self.system_data.get(item_ref)
        out = {}
        for element in item.iterchildren():
            if element.text and element.text.strip():
                out[self._get_unique_id_in_dict(element, out)] = element.text
        return out

    def get_test_info(self, test_id):
        test = self.tests[test_id]
        oval_object = None
        for item in self.tests[test_id]:
            object_id = item.attrib.get('object_ref')
            if object_id is not None:
                oval_object = self.get_object(object_id)

        return OvalTest(
            test_id=test_id,
            test_type=test.tag[test.tag.index('}') + 1:],
            comment=test.attrib.get('comment'),
            oval_object=oval_object,
        )
