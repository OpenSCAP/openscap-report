# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from lxml.builder import E

from ..data_structures import OvalObject, OvalObjectMessage
from ..namespaces import NAMESPACES
from .oval_endpoint_information_parser import OVALEndpointInformation
from .shared_static_methods_of_parser import SharedStaticMethodsOfParser


class OVALObjectParser(OVALEndpointInformation):
    def __init__(self, objects, collected_objects, system_data):
        self.objects = objects
        self.collected_objects = collected_objects
        self.system_data = system_data

    def _get_oval_message(self, xml_collected_object):
        message = xml_collected_object.find(
            ".//oval-characteristics:message", NAMESPACES
        )
        if message is not None:
            return OvalObjectMessage(message.get("level", ""), message.text)
        return None

    def _get_collected_object_xml(self, id_object):
        return self.collected_objects.get(id_object, E.xml("empty"))

    def get_object(self, id_object):
        xml_object = self.objects.get(id_object)
        object_dict = {
            "object_id": xml_object.get("id"),
            "comment": xml_object.get("comment", ""),
            "object_type": SharedStaticMethodsOfParser.get_key_of_xml_element(xml_object),
            "object_data": self._get_items(xml_object),
        }
        xml_collected_object = self._get_collected_object_xml(id_object)

        message = self._get_oval_message(xml_collected_object)
        if message is not None:
            object_dict["message"] = message
        object_dict["flag"] = xml_collected_object.get("flag", "")
        return OvalObject(**object_dict)
