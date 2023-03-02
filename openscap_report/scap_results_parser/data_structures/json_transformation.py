# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later


def rearrange_references(dictionary_json):
    global_references = {}
    for rule in dictionary_json["rules"].values():
        new_rule_references = []
        for ref in rule["references"]:
            global_references[ref["text"]] = ref["href"]
            new_rule_references.append(ref["text"])
        rule["references"] = new_rule_references
    dictionary_json["references"] = global_references


def rearrange_identifiers(dictionary_json):
    global_identifiers = {}
    for rule in dictionary_json["rules"].values():
        new_rule_identifiers = []
        for ident in rule["identifiers"]:
            global_identifiers[ident["text"]] = ident["system"]
            new_rule_identifiers.append(ident["text"])
        rule["identifiers"] = new_rule_identifiers
    dictionary_json["identifiers"] = global_identifiers


def _get_dict_or_value(val):
    if isinstance(val, list):
        out = []
        for item in val:
            out.append(_get_dict_or_value(item))
        return out
    if isinstance(val, dict):
        return remove_empty_values(val)
    return val


def is_not_empty(val):
    if val is None:
        return False
    if isinstance(val, float):
        return True
    return len(val) > 0


def remove_empty_values(dictionary_json):
    out = {}
    for key, val in dictionary_json.items():
        clean_value = _get_dict_or_value(val)
        if is_not_empty(clean_value):
            out[key] = clean_value
    return out


def remove_not_selected_rules(dictionary_json, ids_of_selected_rules):
    selected_rules = {}
    for rule_id, rule in dictionary_json["rules"].items():
        if rule_id in ids_of_selected_rules or (
            rule["result"] != "notselected" and not is_not_empty(ids_of_selected_rules)
        ):
            selected_rules[rule_id] = rule
    dictionary_json["rules"] = selected_rules
