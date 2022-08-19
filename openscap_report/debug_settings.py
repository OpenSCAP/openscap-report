# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass


@dataclass
class DebugSetting():
    no_minify: bool = False
    options_require_debug_script: tuple = (
        "BUTTON-SHOW-ALL-RULES",
        "BUTTON-SHOW-ALL-RULES-AND-OVAL-TEST-DETAILS"
    )
    include_debug_script: bool = False
    button_show_all_rules: bool = False
    use_online_css: bool = False
    button_show_all_rules_and_oval_test_details: bool = False

    def set_no_minify(self, val):
        self.no_minify = val

    def set_button_show_all_rules(self, val):
        self.button_show_all_rules = val

    def set_use_online_css(self, val):
        self.use_online_css = val

    def set_button_show_all_rules_and_oval_test_details(self, val):
        self.button_show_all_rules_and_oval_test_details = val

    def update_settings_with_debug_flags(self, debug_flags):
        flags = {
            "NO-MINIFY": self.set_no_minify,
            "BUTTON-SHOW-ALL-RULES": self.set_button_show_all_rules,
            "ONLINE-CSS": self.set_use_online_css,
            "BUTTON-SHOW-ALL-RULES-AND-OVAL-TEST-DETAILS":
                self.set_button_show_all_rules_and_oval_test_details,
        }

        for flag in debug_flags:
            if flag in self.options_require_debug_script:
                self.include_debug_script = True
            if flag in flags:
                flags[flag](True)
