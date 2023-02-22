# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from ..data_structures import OvalTest
from ..namespaces import NAMESPACES
from .oval_object_parser import OVALObjectParser
from .oval_state_parser import OVALStateParser

MAX_MESSAGE_LEN = 99


class OVALTestInfoParser:  # pylint: disable=R0902
    def __init__(self, oval_report):
        self.oval_report = oval_report
        self.oval_definitions = self._get_oval_definitions()
        self.tests = self._get_tests()
        self.objects = self._get_objects_by_id()
        self.states = self._get_states_by_id()
        self.oval_system_characteristics = self._get_oval_system_characteristics()
        self.collected_objects = self._get_collected_objects_by_id()
        self.system_data = self._get_system_data_by_id()
        self.states_parser = OVALStateParser(self.states)
        self.objects_parser = OVALObjectParser(
            self.objects,
            self.collected_objects,
            self.system_data
        )

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

    def _get_states_by_id(self):
        data = self.oval_definitions.find(
            ('.//oval-definitions:states'), NAMESPACES)
        return self._get_data_by_id(data)

    def get_test_info(self, test_id):
        test = self.tests[test_id]

        list_object_of_test = test.xpath('.//*[local-name()="object"]')
        list_state_of_test = test.xpath('.//*[local-name()="state"]')

        oval_object_el = list_object_of_test.pop() if list_object_of_test else None
        oval_state_el = list_state_of_test.pop() if list_state_of_test else None

        oval_object = None
        oval_state = None

        if oval_object_el is not None:
            oval_object = self.objects_parser.get_object(oval_object_el.get("object_ref", ""))

        if oval_state_el is not None:
            oval_state = self.states_parser.get_state(oval_state_el.get("state_ref", ""))

        return OvalTest(
            test_id=test_id,
            check_existence=test.attrib.get("check_existence", ""),
            check=test.attrib.get("check", ""),
            test_type=test.tag[test.tag.index('}') + 1:],
            comment=test.attrib.get("comment", ""),
            oval_object=oval_object,
            oval_state=oval_state,
        )
