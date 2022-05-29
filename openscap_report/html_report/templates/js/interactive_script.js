
var FILTER_TABLE = {
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
    var id = this.replace(/ /ug, "-").toLowerCase();
    return prefix + id;
};

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
    var value = self.value.toLowerCase();
    var rules = document.querySelectorAll("table[id=rule-table] tbody[rule-id]");
    rules.forEach(function (rule) {
        var is_matched_title = rule.getAttribute("title").toLowerCase().includes(value);
        var is_matched_rule_id = rule.getAttribute("rule-id").toLowerCase().includes(value);
        var result_of_rule = rule.getAttribute("result").asId('result-');
        var severity_of_rule = rule.getAttribute("severity").asId('severity-');
        var advance_option = (FILTER_TABLE[result_of_rule]) && (FILTER_TABLE[severity_of_rule]);
        if ((is_matched_title || is_matched_rule_id) && advance_option) {
            rule.style.display = "";
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

    var element_to_show = get_child_of_element_with_selector(
        self.parentNode.parentNode,
        ".pf-c-accordion__expanded-content"
    );
    element_to_show.classList.toggle('pf-m-expanded');
    hide_or_show(element_to_show);
}

function show_evaluation_characteristics(self) { // eslint-disable-line no-unused-vars
    self.classList.toggle('pf-m-expanded');
    var div_to_show = get_child_of_element_with_selector(
        self.parentNode.parentNode,
        ".pf-c-accordion__expanded-content"
    );
    div_to_show.classList.toggle('pf-m-expanded');
    hide_or_show(div_to_show);
}

function show_rule_detail(self, rule_id) { // eslint-disable-line no-unused-vars
    self.classList.toggle('pf-m-expanded');
    var element_to_show = get_child_of_element_with_selector(
        self.parentNode.parentNode.parentNode,
        ".pf-c-table__expandable-row"
    );
    element_to_show.classList.toggle('pf-m-expanded');

    generate_oval_tree(self, "oval_tree_of_rule_" + rule_id); // eslint-disable-line no-undef
    generate_oval_tree(self, "cpe_tree_of_rule_" + rule_id); // eslint-disable-line no-undef
}