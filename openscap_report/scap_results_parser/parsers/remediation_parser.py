# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from lxml import etree

from ..data_structures import Remediation


class RemediationParser():
    def __init__(self, ref_values):
        self.ref_values = ref_values

    def replace_sub_tag(self, tag):
        return self.ref_values.get(tag.get("idref"))

    def _get_remediation_code(self, fix):
        str_fix = fix.text
        for child in fix:
            if str_fix is None:
                str_fix = ""
            if etree.QName(child).localname == "sub":
                str_fix += self.replace_sub_tag(child)
            str_fix += child.tail if child.tail is not None else ""
        return str_fix

    def get_remediation(self, fix):
        fix_dict = {
            "remediation_id": fix.get("id"),
            "system": fix.get("system"),
            "complexity": fix.get("complexity", ""),
            "disruption": fix.get("disruption", ""),
            "strategy": fix.get("strategy", ""),
            "fix": self._get_remediation_code(fix),
        }
        return Remediation(**fix_dict)
