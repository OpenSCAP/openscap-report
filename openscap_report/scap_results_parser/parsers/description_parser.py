from lxml import etree

from ..namespaces import NAMESPACES


class DescriptionParser():
    def __init__(self, ref_values):
        self.ref_values = ref_values

    def replace_sub_tag(self, tag):
        return self.ref_values.get(tag.get("idref"))

    @staticmethod
    def get_html_attributes_as_string(attributes):
        out = ""
        for key, value in attributes.items():
            out += f" {key}=\"{value}\""
        return out

    def get_html_tag_as_string(self, tag):
        tag_name = etree.QName(tag).localname
        tag_text = tag.text
        tag_attributes = self.get_html_attributes_as_string(tag.attrib)
        for child in tag:
            if tag_text is None:
                tag_text = ""
            if child.prefix == "html":
                tag_text += self.get_html_tag_as_string(child)
            if etree.QName(child).localname == "sub":
                tag_text += self.replace_sub_tag(child)
            tag_text += child.tail if child.tail is not None else ""
        if tag_text is not None:
            return f"<{tag_name}{tag_attributes}>{tag_text}</{tag_name}>"
        return f"<{tag_name}{tag_attributes}>"

    def get_full_description(self, rule):
        description = rule.find(".//xccdf:description", NAMESPACES)
        if description is None:
            return None
        str_description = description.text
        for child in description:
            if str_description is None:
                str_description = ""
            if child.prefix == "html":
                str_description += self.get_html_tag_as_string(child)
            if etree.QName(child).localname == "sub":
                str_description += self.replace_sub_tag(child)
            str_description += child.tail if child.tail is not None else ""
        return str_description
