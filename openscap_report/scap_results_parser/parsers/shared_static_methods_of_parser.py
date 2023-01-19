# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import uuid


class SharedStaticMethodsOfParser:

    @staticmethod
    def get_unique_key(key):
        return f"{key}@{str(uuid.uuid4())}"

    @staticmethod
    def get_key_of_xml_element(element):
        return element.tag[element.tag.index('}') + 1:] if '}' in element.tag else element.tag

    @staticmethod
    def get_unique_id_in_dict(object_, dict_):
        if SharedStaticMethodsOfParser.get_key_of_xml_element(object_) in dict_:
            return SharedStaticMethodsOfParser.get_unique_key(
                SharedStaticMethodsOfParser.get_key_of_xml_element(object_)
            )
        return SharedStaticMethodsOfParser.get_key_of_xml_element(object_)
