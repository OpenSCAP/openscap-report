/*
 * Copyright 2022, Red Hat, Inc.
 * SPDX-License-Identifier: LGPL-2.1-or-later
 */

const FILTER_TABLE = {
    "result-pass": true,
    "result-fail": true,
    "result-notchecked": true,
    "result-notapplicable": true,
    "result-fixed": true,
    "result-error": true,
    "result-informational": true,
    "result-fix-failed": true,
    "result-fix-unsuccessful": true,
    "result-unknown": true,
    "severity-high": true,
    "severity-medium": true,
    "severity-low": true,
    "severity-unknown": true
};

// eslint-disable-next-line no-extend-native
String.prototype.asId = function (prefix) {
    return prefix + this.replace(/ /ug, "-").toLowerCase();
};

document.querySelector('main').addEventListener('scroll', () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
        show_next_rules();
    }
    document.getElementById('back-to-top-button').style.visibility = 'visible';
}, false);

function show_next_rules() {
    const next_five_rules = get_next_five_rules();
    next_five_rules.forEach(rule => {
        rule.classList.remove("hidden");
    });
}

let FIRST_HIDDEN_ELEMENT = document.querySelector("table[id=rule-table] tbody[rule-id].hidden");
function get_next_five_rules() {
    const next_five_rules = [];
    var count_five = 5;
    for(let i = 0; i <= count_five && FIRST_HIDDEN_ELEMENT !== null; i += 1) {
        next_five_rules.push(FIRST_HIDDEN_ELEMENT);
        FIRST_HIDDEN_ELEMENT = FIRST_HIDDEN_ELEMENT.nextSibling;
        if (!(FIRST_HIDDEN_ELEMENT instanceof HTMLElement) && FIRST_HIDDEN_ELEMENT !== null) {
            FIRST_HIDDEN_ELEMENT = FIRST_HIDDEN_ELEMENT.nextSibling;
        }
    }
   return next_five_rules;
}

function get_child_of_element_with_selector(element, selector) {
    return element.querySelector(":scope > ".concat(selector));
}

function hide_or_show(element) {
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}

// Search engine of rules
function search_rule(self) { // eslint-disable-line no-unused-vars
    const value = self.value.toLowerCase();
    const rules = document.querySelectorAll("table[id=rule-table] tbody[rule-id]");
    rules.forEach(function (rule) {
        const is_matched_title = rule.getAttribute("rule-title").toLowerCase().includes(value);
        const is_matched_rule_id = rule.getAttribute("rule-id").toLowerCase().includes(value);
        const result_of_rule = rule.getAttribute("result").asId('result-');
        const severity_of_rule = rule.getAttribute("severity").asId('severity-');
        const advance_option = (FILTER_TABLE[result_of_rule]) && (FILTER_TABLE[severity_of_rule]);
        if ((is_matched_title || is_matched_rule_id) && advance_option) {
            rule.style.display = "";
            rule.classList.remove("hidden")
        } else {
            rule.style.display = "none";
        }
    });
}

// Filter by result, Severity
function toggle_rules(filter_by, result) { // eslint-disable-line no-unused-vars
    FILTER_TABLE[filter_by + '-' + result] = !(FILTER_TABLE[filter_by + '-' + result]);
    search_rule(document.querySelector("input[id=input-search-rule]"));
}

function show_advanced_options(self) { // eslint-disable-line no-unused-vars
    self.classList.toggle('pf-m-expanded');
    self.firstChild.className = self.firstChild.className == 'fas fa-caret-right' ? 'fas fa-caret-down' : 'fas fa-caret-right';

    const element_to_show = get_child_of_element_with_selector(
        self.parentNode.parentNode,
        ".pf-c-accordion__expanded-content"
    );
    element_to_show.classList.toggle('pf-m-expanded');
    hide_or_show(element_to_show);
}

function show_evaluation_characteristics(self) { // eslint-disable-line no-unused-vars
    self.classList.toggle('pf-m-expanded');
    const div_to_show = get_child_of_element_with_selector(
        self.parentNode.parentNode,
        ".pf-c-accordion__expanded-content"
    );
    div_to_show.classList.toggle('pf-m-expanded');
    hide_or_show(div_to_show);
}

function show_rule_detail(self) { // eslint-disable-line no-unused-vars
    self.classList.toggle('pf-m-expanded');
    const element_to_show = get_child_of_element_with_selector(
        self.parentNode.parentNode.parentNode,
        ".pf-c-table__expandable-row"
    );
    element_to_show.classList.toggle('pf-m-expanded');
}

function show_rule_detail_after_click_on_rule_title(self) { // eslint-disable-line no-unused-vars
    show_rule_detail(self.parentElement.previousSibling.firstChild);
}

const selector = ".pf-c-clipboard-copy__text";
document.querySelectorAll("#copy").forEach(el => el.addEventListener('click', () => {
    const el_with_text = el.parentElement.parentElement.parentElement.querySelector(selector);
    navigator.clipboard.writeText(el_with_text.textContent);
}));

function clear_input(self) { // eslint-disable-line no-unused-vars
    self.previousSibling.value= "";
    search_rule(self.previousSibling);
}

document.querySelectorAll("#copy").forEach(el => el.appendChild(get_tooltip_copy_to_clipboard()));
function get_tooltip_copy_to_clipboard() { // eslint-disable-line no-unused-vars
    const div = document.createElement("div");

    const tooltip_div = div.cloneNode();
    tooltip_div.className = "pf-c-tooltip pf-m-top tooltip-box-top-side";
    tooltip_div.setAttribute("role", "tooltip");

    const tooltip_arrow_div = div.cloneNode();
    tooltip_arrow_div.className = "pf-c-tooltip__arrow";
    tooltip_div.appendChild(tooltip_arrow_div);

    const tooltip_content_div = div.cloneNode();
    tooltip_content_div.className = "pf-c-tooltip__content";
    tooltip_content_div.textContent = `Copied to clipboard.`;
    tooltip_div.appendChild(tooltip_content_div);
    return tooltip_div;
}

function toogle_deselect_button(self) { // eslint-disable-line no-unused-vars
    self.parentElement.parentElement.querySelectorAll('input[type="checkbox"]').forEach(e => {
        if (self.textContent == 'Deselect all' && e.checked) {
            e.onchange();
            e.checked = !e.checked;
        } else if (self.textContent == 'Select all' && !e.checked) {
            e.onchange();
            e.checked = !e.checked;
        }
    });
    self.textContent = self.textContent == 'Deselect all' ? 'Select all' : 'Deselect all';
}
