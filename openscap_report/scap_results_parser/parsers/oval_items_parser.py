# Copyright 2024, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from .shared_static_methods_of_parser import SharedStaticMethodsOfParser
from ..data_structures import OVALItems
from ..namespaces import NAMESPACES

PROCURED_ITEMS_LIMIT = 100


class OVALItemsParser:
    def __init__(self, collected_objects, system_data):
        self.collected_objects = collected_objects
        self.system_data = system_data

    def _get_item(self, item_ref):
        item_el = self.system_data.get(item_ref)
        item_data = {}
        for child_el in item_el:
            if child_el.text and child_el.text.strip():
                key = SharedStaticMethodsOfParser.get_key_of_xml_element(child_el)
                item_data[key] = child_el.text
        return item_data

    def _get_items(self, references):
        items = []
        for reference_el in references:
            item_ref = reference_el.get("item_ref")
            item = self._get_item(item_ref)
            items.append(item)
        return items

    @staticmethod
    def _get_header(items):
        header = []
        for item in items:
            for key in item.keys():
                if key not in header:
                    header.append(key)
        return tuple(header)

    @staticmethod
    def _get_entries(header, items):
        entries = []
        for item in items:
            entry = []
            for key in header:
                entry.append(item.get(key, ""))
            entries.append(tuple(entry))
        return entries

    def get_oval_items(self, object_id):
        collected_object_el = self.collected_objects.get(object_id)
        if collected_object_el is None:
            return None
        references = collected_object_el.findall(
            "oval-characteristics:reference", NAMESPACES
        )
        if len(references) == 0:
            return None
        items = self._get_items(references)
        header = self._get_header(items)
        entries = self._get_entries(header, items)
        message = None
        len_entries = len(entries)
        if len_entries > PROCURED_ITEMS_LIMIT:
            entries = entries[:PROCURED_ITEMS_LIMIT]
            message = (
                f"Collected {len_entries} items, showing only first "
                f"{PROCURED_ITEMS_LIMIT} items")
        return OVALItems(header=header, entries=entries, message=message)
