
// eslint-disable-next-line no-extend-native
String.prototype.asJqueryComplaintId = function() {
    return this.replace(/\./ug, "");
};

const NEGATION_COLOR = {
    'pf-m-green': 'pf-m-red',
    'pf-m-red': 'pf-m-green',
    '': ''
};
const NEGATION_ICON = {
    'fa-check': 'fa-times',
    'pf-m-red': 'fa-check',
    'fa-question-circle': 'fa-question-circle'
};
const COLOR_TRANSLATION = {
    'pf-m-green': '--pf-global--success-color--200',
    'pf-m-red': '--pf-global--danger-color--200',
    '': ''
};

window.addEventListener('load', () => {
    var selector = "table[id=rule-table] tbody[rule-id] button[id=show_hide_rule_detail_button]";
    var rule_buttons = document.querySelectorAll(selector);
    rule_buttons.forEach(item => {
        var rule_id = item.parentNode.parentNode.parentNode.getAttribute("rule-id").asJqueryComplaintId();
        generate_oval_tree(item, "oval_tree_of_rule_" + rule_id); // eslint-disable-line no-undef
        generate_oval_tree(item, "cpe_tree_of_rule_" + rule_id); // eslint-disable-line no-undef
    });
});


function toggle_OVAL_operator() { // eslint-disable-line no-unused-vars
    var operator_parent = this.parentNode.parentNode;
    operator_parent.classList.toggle('pf-m-expanded');
    var children_to_hide_or_show = get_child_of_element_with_selector(operator_parent, "ul"); // eslint-disable-line no-undef
    hide_or_show(children_to_hide_or_show); // eslint-disable-line no-undef
}

function show_OVAL_details(event) { // eslint-disable-line no-unused-vars
    var oval_details = get_child_of_element_with_selector( // eslint-disable-line no-undef
        event.currentTarget.param_this.parentNode,
        event.currentTarget.param_selector
    );
    oval_details.classList.toggle('pf-m-expanded')
    hide_or_show(oval_details); // eslint-disable-line no-undef
    event.currentTarget.param_this.textContent = self.textContent == 'Show test details' ? 'Hide test details' : 'Show test details';
    event.currentTarget.param_this.setAttribute('aria-label', event.currentTarget.param_this.textContent);
}


function generate_oval_tree(self, div_id_with_oval_graph_data) { // eslint-disable-line no-unused-vars
    var div_with_tree = self.parentNode.parentNode.parentNode.querySelector(`div[id=${div_id_with_oval_graph_data}]`);
    if (div_with_tree === null) {
        return;
    }
    var data = div_with_tree.getAttribute("data");
    var tree_data = JSON.parse(data);
    var tree_element = document.createElement("div");
    tree_element.className = "pf-c-tree-view pf-m-guides pf-m-no-background";
    var ul = document.createElement("ul");
    ul.className = "pf-c-tree-view__list";
    ul.setAttribute('role', "tree");
    tree_element.appendChild(ul);

    if (div_with_tree.getAttribute("is_rendered") === 'false' && tree_data !== undefined) {
        ul.appendChild(get_OVAL_tree_node(tree_data));
        div_with_tree.appendChild(tree_element);
        div_with_tree.setAttribute("is_rendered", 'true');
    }
}

function get_OVAL_tree_node(root) {
    if (root.node_type != 'value') {
        var root_node = get_OVAL_tree_operator_node(root);
        if (root.children) {
            var ul = document.createElement("ul");
            ul.className = "pf-c-tree-view__list";
            ul.setAttribute('role', "group");
            root_node.appendChild(ul);

            for (const child of root.children) {
                if (child.node_type == "value") {
                    ul.appendChild(render_OVAL_test(child));
                } else {
                    ul.appendChild(get_OVAL_tree_node(child));
                }
            }
        }
        return root_node;
    }
    return undefined;
}


function get_test_node() {
    var test_node = document.createElement("li");
    test_node.className = "pf-c-tree-view__list-item";
    test_node.setAttribute("role", "treeitem");
    test_node.setAttribute("tabindex", "-1");

    var content = document.createElement("div");
    content.className = "pf-c-tree-view__content";
    test_node.appendChild(content);

    var node = document.createElement("div");
    node.className = "pf-c-tree-view__node";
    node.setAttribute("tabindex", "0");
    content.appendChild(node);

    var node_container = document.createElement("div");
    node_container.className = "pf-c-tree-view__node-container";
    node.appendChild(node_container);

    var node_content = document.createElement("div");
    node_content.className = "pf-c-tree-view__node-content";
    node_container.appendChild(node_content);

    var node_text = document.createElement("span");
    node_text.className = "pf-c-tree-view__node-text";
    node_content.appendChild(node_text);
    return { test_node, node_content, node_text };
}


function render_OVAL_test(node_data) {
    var { test_node, node_content, node_text } = get_test_node();

    var color = '';
    var icon = 'fa-question-circle';
    if (node_data.value == 'true') {
        color = 'pf-m-green';
        icon = 'fa-check';
    } else if (node_data.value == 'false') {
        color = 'pf-m-red';
        icon = 'fa-times';
    }
    var node = null;
    if (node_data.negation) {
        node = get_node(COLOR_TRANSLATION[NEGATION_COLOR[color]]);
        node_text.appendChild(node);
        node.appendChild(get_icon_as_html(NEGATION_ICON[icon]));
        node.appendChild(get_bold_text("NOT"));
    } else {
        node = get_node(COLOR_TRANSLATION[color]);
        node_text.appendChild(node);
        node.appendChild(get_icon_as_html(icon));
    }

    var test_id = node_data.node_id.replace("oval:ssg-", "").replace(":tst:1", "");
    node.appendChild(get_bold_text(` ${test_id} `));
    node_text.appendChild(get_label(color, node_data.tag));
    node_text.appendChild(get_label(color, node_data.value, get_icon_as_html(icon)));


    var info_id = 'info_of_test_' + test_id.replace(/[\.:_\-]/ug, "");
    var button = document.createElement("button");
    button.className = "pf-c-button pf-m-inline pf-m-link";
    button.addEventListener("click", show_OVAL_details, false);
    button.param_this = button;
    button.param_selector = `[id=${info_id}]`;
    button.setAttribute("type", " button");
    button.setAttribute("aria-label", "Show test details");
    button.appendChild(document.createTextNode("Show test details"))
    node_content.appendChild(button);

    var div = document.createElement("div");
    div.className = "pf-c-tree-view__node-container";
    div.setAttribute("id", info_id);
    div.style.display = "none";
    div.setAttribute("aria-label", "OVAL test info");
    node_content.appendChild(div);

    div.appendChild(get_OVAL_test_info(node_data.test_info));

    return test_node;
}


function get_icon_as_html(icon) {
    var html_icon = document.createElement("span");
    html_icon.className = "pf-c-label__icon";

    var i = document.createElement("i");
    i.className = `fas fa-fw ${icon}`;
    i.setAttribute("aria-hidden", "true");
    html_icon.appendChild(i);
    return html_icon;
}

function get_node(color) {
    var node = document.createElement("span");
    node.style.cssText = "color:var(" + color + ")";
    return node;
}

function get_bold_text(text) {
    var b = document.createElement("b");
    b.appendChild(document.createTextNode(text));
    return b;
}

function get_label(color, text, icon = undefined) {
    var span = document.createElement("span");
    span.className = `pf-c-label ${color}`;

    var content = document.createElement("span");
    content.className = "pf-c-label__content"
    content.appendChild(document.createTextNode(text));
    if (icon !== undefined) {
        content.appendChild(icon);
    }
    span.appendChild(content);
    return span;
}

function get_operator_node() {
    var operator_node = document.createElement("li");
    operator_node.className = "pf-c-tree-view__list-item pf-m-expanded";
    operator_node.setAttribute("role", "treeitem");
    operator_node.setAttribute("aria-expanded", "true");
    operator_node.setAttribute("tabindex", "0");

    var content = document.createElement("div");
    content.className = "pf-c-tree-view__content";
    operator_node.appendChild(content);

    var button = document.createElement("button");
    button.className = "pf-c-tree-view__node";
    button.addEventListener("click", toggle_OVAL_operator);
    button.title = "Onclick shows or hides child nodes of the OVAL tree.";
    content.appendChild(button);

    var node_container = document.createElement("div");
    node_container.className = "pf-c-tree-view__node-container";
    button.appendChild(node_container);

    var node_toggle = document.createElement("div");
    node_toggle.className = "pf-c-tree-view__node-toggle";
    node_container.appendChild(node_toggle);

    var node_toggle_icon = document.createElement("span");
    node_toggle_icon.className = "pf-c-tree-view__node-toggle-icon";
    node_toggle.appendChild(node_toggle_icon);

    var icon = document.createElement("i");
    icon.className = "fas fa-angle-right";
    icon.setAttribute("aria-hidden", "true");
    node_toggle_icon.appendChild(icon);

    var node_content = document.createElement("div");
    node_content.className = "pf-c-tree-view__node-content";
    node_container.appendChild(node_content);

    var node_text = document.createElement("span");
    node_text.className = "pf-c-tree-view__node-text";
    node_content.appendChild(node_text);
    return { operator_node, node_text };

}

function get_OVAL_tree_operator_node(node_data) {
    var { operator_node, node_text } = get_operator_node();
    var color = '';
    var icon = 'fa-question-circle';
    if (node_data.value == 'true') {
        color = 'pf-m-green';
        icon = 'fa-check';
    } else if (node_data.value == 'false') {
        color = 'pf-m-red';
        icon = 'fa-times';
    }
    var node = null;
    if (node_data.negation) {
        node = get_node(COLOR_TRANSLATION[NEGATION_COLOR[color]]);
        node_text.appendChild(node);
        node.appendChild(get_icon_as_html(NEGATION_ICON[icon]));
        node.appendChild(get_bold_text("NOT"));
    } else {
        node = get_node(COLOR_TRANSLATION[color]);
        node_text.appendChild(node);
        node.appendChild(get_icon_as_html(icon));
    }
    node.appendChild(get_bold_text(` ${node_data.node_type} `));
    node_text.appendChild(get_label(color, node_data.tag));
    node_text.appendChild(get_label(color, node_data.value, get_icon_as_html(icon)));
    return operator_node;
}

function get_table_header(objects) {
    var table_thead = document.createElement("thead");
    table_thead.className = "pf-c-table pf-m-compact pf-m-grid-md";
    table_thead.cssText = "table-layout:auto;"
    table_thead.setAttribute("role", "grid");
    var row = document.createElement("tr");
    row.setAttribute("role", "row");
    table_thead.appendChild(row);

    for (const item of get_header_items(objects)) {
        var header_col = document.createElement("th");
        header_col.setAttribute("role", "columnheader");
        header_col.setAttribute("scope", "col");
        var header_col_text = document.createTextNode(format_header_item(item));
        header_col.appendChild(header_col_text);
        row.appendChild(header_col);
    }
    return table_thead;
}

function get_table_body(objects) {
    var tbody = document.createElement("tbody");
    tbody.setAttribute("role", "rowgroup");
    for (const object of objects) {
        var row = document.createElement("tr");
        row.setAttribute("role", "row");
        tbody.appendChild(row);
        for (const key in object) {
            var col = document.createElement("td");
            col.setAttribute("role", "cell");
            col.setAttribute("data-label", key);
            var col_text = document.createTextNode(object[key]);
            col.appendChild(col_text);
            row.appendChild(col);
        }
    }
    return tbody;
}

function get_info_paragraf(test_info) {
    var info_paragraf = document.createElement("p");
    var info_text = null;
    if (test_info.oval_object.flag == "complete") {
        info_text = document.createTextNode('Following items have been found on the system:');
        info_paragraf.appendChild(info_text);
    } else {
        info_text = document.createTextNode('No items have been found conforming to the following objects:');
        info_paragraf.appendChild(info_text);
        info_paragraf.appendChild(document.createElement("br"));

        var bold_text = document.createElement("b");
        bold_text.appendChild(document.createTextNode(test_info.oval_object.object_id))
        info_paragraf.appendChild(bold_text);
        info_paragraf.appendChild(document.createTextNode(" of type "));
        bold_text = document.createElement("b");
        bold_text.appendChild(document.createTextNode(test_info.oval_object.object_type));
        info_paragraf.appendChild(bold_text);
    }
    return info_paragraf;
}

function get_OVAL_test_info(test_info) {
    var div = document.createElement("div");
    div.className = "pf-c-accordion__expanded-content-body";
    div.appendChild(get_label("pf-m-blue", test_info.comment));
    div.appendChild(get_label("", test_info.test_id));

    if (test_info.oval_object === undefined) {
        // eslint-disable-next-line no-console
        console.error("Error: The test information has no oval objects.");
        return undefined;
    }
    div.appendChild(get_info_paragraf(test_info));
    var table_div = document.createElement("div");
    div.appendChild(table_div);
    table_div.cssText = "width: 0; min-width: 100em; overflow-x: auto;";
    var table = document.createElement("table");
    table_div.appendChild(table);

    var objects = [];
    for (const data of test_info.oval_object.object_data) {
        objects.push(filter_object(data, test_info.oval_object));
    }
    table.appendChild(get_table_header(objects));
    table.appendChild(get_table_body(objects));
    return div;
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

function filter_object(data, oval_object) {
    if (oval_object.object_type == 'textfilecontent54_object') {
        if ("filepath" in data && "text" in data) {
            return {
                "filepath": data["filepath"],
                "content": data["text"]
            };
        }
    }
    return filter_permissions(data);
}