from lxml import etree

from .namespaces import NAMESPACES


class DescriptionParser():
    @staticmethod
    def get_full_description(item):
        description = item.find(".//xccdf:description", NAMESPACES)
        if description is None:
            return None
        str_description = etree.tostring(description).decode()
        start_tag_description = str_description.find(">") + 1
        end_tag_description = str_description.rfind("</")
        return str_description[start_tag_description:end_tag_description].replace("html:", "")
