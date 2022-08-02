# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import html
import logging

from lxml import etree

from ..namespaces import NAMESPACES


class FullTextParser():
    def __init__(self, ref_values):
        self.ref_values = ref_values

    def replace_sub_tag(self, tag):
        id_ref = tag.get("idref")
        if id_ref in self.ref_values:
            return self.ref_values.get(id_ref)
        error_msg = f"Sub tag reference does not exist: {id_ref}"
        logging.warning(error_msg)
        return f"<span class='error-id-ref'>{error_msg}</span>"

    @staticmethod
    def _get_html_attributes_as_string(attributes):
        out = ""
        for key, value in attributes.items():
            out += f" {key}=\"{value}\""
        return out

    def _get_tag_text(self, tag):
        if tag.prefix == "html":
            return self._get_html_tag_as_string(tag)
        if etree.QName(tag).localname == "sub":
            return self.replace_sub_tag(tag)
        return ""

    def _get_html_tag_as_string(self, tag):
        tag_name = etree.QName(tag).localname
        tag_text = "" if tag.text is None else html.escape(tag.text)
        tag_attributes = self._get_html_attributes_as_string(tag.attrib)
        for child in tag:
            tag_text += self._get_tag_text(child)
            tag_text += html.escape(child.tail) if child.tail is not None else ""
        if tag_text:
            return f"<{tag_name}{tag_attributes}>{tag_text}</{tag_name}>"
        return f"<{tag_name}{tag_attributes}>"

    def _get_element_as_string(self, element):
        text = "" if element.text is None else html.escape(element.text)
        for child in element:
            text += self._get_tag_text(child)
            text += html.escape(child.tail) if child.tail is not None else ""
        return text

    def get_full_description(self, rule):
        description = rule.find(".//xccdf:description", NAMESPACES)
        if description is None:
            return ""
        return self._get_element_as_string(description)

    def get_full_warning(self, warning):
        return self._get_element_as_string(warning)

    def get_full_rationale(self, rule):
        rationale = rule.find(".//xccdf:rationale", NAMESPACES)
        if rationale is None:
            return ""
        return self._get_element_as_string(rationale)
