/* eslint-env jquery */

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
String.prototype.asId = function(prefix) {
    var id = this.replace(/ /ug, "-").toLowerCase();
    return prefix + id;
};

// Search engine of rules
function search_rule(self) { // eslint-disable-line no-unused-vars
    var value = self.val().toLowerCase();
    $("#rule-table tbody[rule-id]").filter(function () { // eslint-disable-line array-callback-return
        var is_matched_title = $(this).attr("title").toLowerCase().includes(value);
        var is_matched_rule_id = $(this).attr("rule-id").toLowerCase().includes(value);
        var result_of_rule = $(this).attr("result").asId('result-');
        var severity_of_rule = $(this).attr("severity").asId('severity-');
        var advance_option = (FILTER_TABLE[result_of_rule]) && (FILTER_TABLE[severity_of_rule]);

        $(this).toggle((is_matched_title || is_matched_rule_id) && advance_option);
    });
}

// Filter by result, Severity
function toggle_rules(filter_by, result) { // eslint-disable-line no-unused-vars
    FILTER_TABLE[filter_by + '-' + result] = !(FILTER_TABLE[filter_by + '-' + result]);
    search_rule($("input#input-search-rule"));
}

function show_advanced_options(self) { // eslint-disable-line no-unused-vars
    self.toggleClass('pf-m-expanded');
    self.children().attr('class', (self.children().attr('class') == 'fas fa-caret-right') ? 'fas fa-caret-down' : 'fas fa-caret-right');
    self.parent().parent().children('.pf-c-accordion__expanded-content').toggleClass('pf-m-expanded').toggle();
}


function toggle_OVAL_operator(self) { // eslint-disable-line no-unused-vars
    self.parent().parent().toggleClass('pf-m-expanded');
    self.parent().parent().children('ul').children().toggle();
}

function show_OVAL_details(self, info_id) { // eslint-disable-line no-unused-vars
    self.parent().children(info_id).toggleClass('pf-m-expanded').toggle();
    self.text((self.text() == 'Show test details') ? 'Hide test details' : 'Show test details');
    self.attr('aria-label', (self.attr('aria-label') == 'Show test details') ? 'Hide test details' : 'Show test details');
}

function show_evaluation_characteristics(self) { // eslint-disable-line no-unused-vars
    self.toggleClass('pf-m-expanded');
    self.parent().parent().children('.pf-c-accordion__expanded-content').toggleClass('pf-m-expanded').toggle();
}

function show_rule_detail(self, rule_id) { // eslint-disable-line no-unused-vars
    self.toggleClass('pf-m-expanded');
    self.parent().parent().parent().children('.pf-c-table__expandable-row').toggleClass('pf-m-expanded');
    generate_oval_tree(self, "div #oval_tree_of_rule_" + rule_id);
    generate_oval_tree(self, "div #cpe_tree_of_rule_" + rule_id);
}

const NEGATION_COLOR = { 'pf-m-green': 'pf-m-red', 'pf-m-red': 'pf-m-green', '': '' };
const NEGATION_ICON = { 'fa-check': 'fa-times', 'pf-m-red': 'fa-check', 'fa-question-circle': 'fa-question-circle' };
const COLOR_TRANSLATION = { 'pf-m-green': '--pf-global--success-color--200', 'pf-m-red': '--pf-global--danger-color--200', '': '' };

var tree_content = '';
function generate_oval_tree(self, searched_div) {
    var div_with_tree = self.parent().parent().parent().find(searched_div);
    var data = div_with_tree.attr("data");
    if (data === undefined) {
        return;
    }
    var tree_data = JSON.parse(data);
    tree_content = '<div class="pf-c-tree-view pf-m-guides pf-m-no-background"><ul class="pf-c-tree-view__list" role="tree">';
    if (div_with_tree.attr("is_rendered") == 'false' && tree_data != undefined) {
        render_OVAL_tree(tree_data);
        tree_content += '<\/ul><\/div>';
        div_with_tree.append(tree_content);
        div_with_tree.attr("is_rendered", 'true');
    }
}

function render_OVAL_tree(root) {
    if (root.node_type != 'value') {
        tree_content += '<li class="pf-c-tree-view__list-item pf-m-expanded" role="treeitem" aria-expanded="true" tabindex="0">';
        render_OVAL_operator(root);
    }
    if (root.children) {
        tree_content += '<ul class="pf-c-tree-view__list" role="group">';

        for (const child of root.children) {
            if (child.node_type == "value") {
                render_OVAL_test(child);
            } else {
                render_OVAL_tree(child);
            }
        }
        tree_content += '<\/ul>';
    }
    if (root.node_type != 'value') {
        tree_content += '<\/li>';
    }
}

function render_OVAL_test(node) {
    tree_content +=
        '<li class="pf-c-tree-view__list-item" role="treeitem" tabindex="-1">' +
            '<div class="pf-c-tree-view__content">' +
                '<div class="pf-c-tree-view__node" tabindex="0">' +
                    '<div class="pf-c-tree-view__node-container">' +
                        '<div class="pf-c-tree-view__node-content">' +
                            '<span class="pf-c-tree-view__node-text">'; // Start span
    var color = '';
    var icon = 'fa-question-circle';
    if (node.value == 'true') {
        color = 'pf-m-green';
        icon = 'fa-check';
    } else if (node.value == 'false') {
        color = 'pf-m-red';
        icon = 'fa-times';
    }

    if (node.negation) {
        tree_content +=
            '<span style="color: var(' + COLOR_TRANSLATION[NEGATION_COLOR[color]] + ')">' +
                '<span class="pf-c-label__icon">' +
                    '<i class="fas fa-fw ' + NEGATION_ICON[icon] + '" aria-hidden="true"><\/i>' +
                '<\/span>' +
                '<b> NOT <\/b>' +
            '<\/span>';
    }

    tree_content += '<span style="color: var(' + COLOR_TRANSLATION[color] + ');">';
    if (!node.negation) {
        tree_content +=
            '<span class="pf-c-label__icon">' +
                '<i class="fas fa-fw ' + icon + '" aria-hidden="true"><\/i>' +
            '<\/span>';
    }
    var test_id = node.node_id.replace("oval:ssg-", "").replace(":tst:1", "");
    tree_content +=
        '<b> ' + test_id + '<\/b>' +
        '<\/span>' +
        '<span class="pf-c-label ' + color + '">' +
            '<span class="pf-c-label__content"> ' + node.tag + '<\/span>' +
        '<\/span>' +
        '<span class="pf-c-label ' + color + '">' +
            '<span class="pf-c-label__content">' +
                '<span class="pf-c-label__icon">' +
                    '<i class="fas fa-fw ' + icon + '" aria-hidden="true"><\/i>' +
                '<\/span>' +
                node.value +
            '<\/span>' +
        '<\/span>' +
    '<\/span>'; // End span
    var info_id = 'info_of_test_' + test_id.replace(/[\.:_\-]/ug, "");
    tree_content +=
        '<button ' +
            'class="pf-c-button pf-m-inline pf-m-link" onClick="show_OVAL_details($(this), \'div #' + info_id + '\');" ' +
            'type="button" ' +
            'aria-label="Show test details">Show test details<\/button>' +
            '<div id="' + info_id + '" class="pf-c-accordion__expanded-content" style="display: none;" aria-label="OVAL test info">' +
                '<div class="pf-c-accordion__expanded-content-body">';
    insert_OVAL_test_info(node);
    tree_content += '<\/div><\/div><\/div><\/div><\/div><\/div><\/li>';
}

function render_OVAL_operator(node) {
    tree_content +=
        '<div class="pf-c-tree-view__content">' +
            '<button ' +
                'class="pf-c-tree-view__node" ' +
                'onClick="toggle_OVAL_operator($(this));" ' +
                'title="Onclick shows or hides child nodes of the OVAL tree.">' +
                '<div class="pf-c-tree-view__node-container">' +
                    '<div class="pf-c-tree-view__node-toggle">' +
                        '<span class="pf-c-tree-view__node-toggle-icon">' +
                            '<i class="fas fa-angle-right" aria-hidden="true"><\/i>' +
                        '<\/span>' +
                    '<\/div>' +
                '<div class="pf-c-tree-view__node-content">' +
                    '<span class="pf-c-tree-view__node-text">';
    var color = '';
    var icon = 'fa-question-circle';
    if (node.value == 'true') {
        color = 'pf-m-green';
        icon = 'fa-check';
    } else if (node.value == 'false') {
        color = 'pf-m-red';
        icon = 'fa-times';
    }

    if (node.negation) {
        tree_content +=
            '<span style="color: var(' + COLOR_TRANSLATION[NEGATION_COLOR[color]] + ')">' +
                '<span class="pf-c-label__icon">' +
                    '<i class="fas fa-fw ' + NEGATION_ICON[icon] + '" aria-hidden="true"><\/i>' +
                '<\/span>' +
                '<b> NOT <\/b>' +
            '<\/span>';
    }
    tree_content += '<span style="color: var(' + COLOR_TRANSLATION[color] + ');">';
    if (!node.negation) {
        tree_content +=
            '<span class="pf-c-label__icon">' +
                '<i class="fas fa-fw ' + icon + '" aria-hidden="true"><\/i>' +
            '<\/span>';
    }
    tree_content +=
        '<b>' + node.node_type + '<\/b>' +
        '<\/span>' +
        '<span class="pf-c-label ' + color + '">' +
            '<span class="pf-c-label__content">' + node.tag + '<\/span>' +
        '<\/span>' +
        '<span class="pf-c-label ' + color + '">' +
            '<span class="pf-c-label__content">' +
                '<span class="pf-c-label__icon">' +
                    '<i class="fas fa-fw ' + icon + '" aria-hidden="true"><\/i>' +
                '<\/span>' +
                node.value +
            '<\/span>' +
        '<\/span>' +
        '<\/span><\/div><\/div><\/button><\/div>';
}

function insert_OVAL_test_info(node) {
    tree_content +=
        '<span class="pf-c-label pf-m-blue">' +
            '<span class="pf-c-label__content">' +
                node.test_info.comment +
            '<\/span>' +
        '<\/span>' +
        '<span class="pf-c-label">' +
            '<span class="pf-c-label__content">' +
                node.test_info.test_id +
            '<\/span>' +
        '<\/span>';

    if (node.test_info.oval_object) {

        if (node.test_info.oval_object.flag == "complete") {
            tree_content += '<p>Following items have been found on the system:<\/p>';
        } else {
            tree_content +=
                '<p>No items have been found conforming to the following objects:<br>Object <b>' +
                node.test_info.oval_object.object_id +
                '<\/b> of type <b>' + node.test_info.oval_object.object_type + '<\/b><\/p>';
        }
        tree_content +=
            '<div  style="width: 0; min-width: 100em; overflow-x: auto;">' +
                '<table class="pf-c-table pf-m-compact pf-m-grid-md" style="table-layout:auto;" role="grid">' +
                    '<thead>' + // Start thead
                        '<tr role="row">';
        var objects = [];
        for (const object of node.test_info.oval_object.object_data) {
            objects.push(filter_object(object, node));
        }
        for (const item of get_header_items(objects)) {
            tree_content += '<th role="columnheader" scope="col">';
            tree_content += format_header_item(item) + '<\/th>';
        }

        tree_content +=
            '<\/tr><\/thead>' + // End thead
            '<tbody role="rowgroup">';
        for (const row of objects) {
            tree_content += '<tr role="row">';
            for (const key in row) {
                tree_content += '<td role="cell" data-label="' + key + '">' + row[key] + '<\/td>';
            }
            tree_content += '<\/tr>';
        }
        tree_content += '<\/tbody><\/table><\/div>';
    }
}

function get_header_items(objects) {
    var out = [];
    for (const object of objects) {
        for (const key in object) {
            if (!out.includes(key)) {
                out.push(key);
            }
        }
    }
    return out;
}

function format_header_item(str) {
    var text = remove_uuid(str);
    var text_with_spaces = text.replace("_", " ");
    return text_with_spaces.charAt(0).toUpperCase() + text_with_spaces.slice(1);
}

function remove_uuid(str) {
    var index_special_char = str.indexOf('@');
    var text = str.substring(0, index_special_char != -1 ? index_special_char : str.length);
    return text;
}

function filter_permissions(object) {
    var permission = {
        'uread': null,
        'uwrite': null,
        'uexec': null,
        'gread': null,
        'gwrite': null,
        'gexec': null,
        'oread': null,
        'owrite': null,
        'oexec': null
    };
    var new_object = {};
    Object.keys(object).forEach(key => {
        if (key in permission) {
            permission[key] = object[key];
        } else {
            new_object[key] = object[key];
        }
    });
    for (const key in permission) {
        if (permission[key] === null) {
            return object;
        }
    }
    var out = '<code>';
    Object.keys(permission).forEach(key => {
        if (permission[key] == 'true') {
            switch (key.substring(1, key.length)) {
                case 'read':
                    out += "r";
                    break;
                case 'write':
                    out += "w";
                    break;
                case 'exec':
                    out += "x";
                    break;
                default:
                    // pass
                    break;
            }
        } else {
            out += "-";
        }
    });
    out += '<\/code>';
    new_object['permission'] = out;
    return new_object;
}

function filter_object(object, node) {
    if (node.test_info.oval_object.object_type == 'textfilecontent54_object') {
        if ("filepath" in object && "text" in object) {
            return {
                "filepath": object["filepath"],
                "content": object["text"]
            };
        }
    }
    return filter_permissions(object);
}