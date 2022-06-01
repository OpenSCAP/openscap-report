/*
 * Copyright 2022, Red Hat, Inc.
 * SPDX-License-Identifier: LGPL-2.1-or-later
 */

function show_all_rules_details(self, expand_oval_test_details=false) { // eslint-disable-line no-unused-vars
    var other_button = get_other_button(self);
    if (other_button != undefined) {
        other_button.disabled = true;
    }
    self.disabled = true;
    const promises = []
    const selector = "table[id=rule-table] tbody[rule-id] button[id=show_hide_rule_detail_button]";
    const rule_buttons = document.querySelectorAll(selector);
    rule_buttons.forEach(function (item) {
        promises.push(new Promise(resolve => {
            setTimeout(() => {
            resolve(show_rule_detail_and_expand_oval_test_details(item, expand_oval_test_details)); // eslint-disable-line no-undef
            }, 0.001);
        }))
    });
    Promise.all(promises).then(() => {
        enable_and_change_text_of_button(self);
        if (other_button != undefined) {
            enable_and_change_text_of_button(other_button);
        }
    });
}

function enable_and_change_text_of_button(button) {
    if (button == undefined) {
        return;
    }
    button.disabled = false;
    if (button.textContent.includes("Show")) {
        button.textContent = button.textContent.replace("Show", "Hide");
    } else {
        button.textContent = button.textContent.replace("Hide", "Show");
    }
}


function show_rule_detail_and_expand_oval_test_details(item, expand_oval_test_details) {
    show_rule_detail(item); // eslint-disable-line no-undef
    if (expand_oval_test_details) {
        click_on_oval_test_details(item.parentNode.parentNode.parentNode);
    }
}


function click_on_oval_test_details(expanded_rule) {
    var selector = 'div[id^="info_of_test_"]';
    expanded_rule.querySelectorAll(selector).forEach(function (div) {
        if (div.style.display === "none") {
            var button = div.previousSibling;
            button.click();
        }
    });
}

function get_other_button(button) {
    if (button.getAttribute("id") == "show-all-rules-details") {
        return button.parentNode.parentNode.querySelector(`button[id=show-all-oval-test-details]`);
    }
    return button.parentNode.parentNode.querySelector(`button[id=show-all-rules-details]`);
}