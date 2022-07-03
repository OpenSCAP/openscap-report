# Copyright 2022, Red Hat, Inc.
# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest

from openscap_report.scap_results_parser.data_structures import OvalNode

SAMPLE_OVAL_TREE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="true",
        ),
        OvalNode(
            node_id="3",
            node_type="value",
            value="false",
        ),
        OvalNode(
            node_id="4",
            node_type="or",
            value="",
            children=[
                OvalNode(
                    node_id="5",
                    node_type="value",
                    value="false",
                ),
                OvalNode(
                    node_id="6",
                    node_type="value",
                    value="true",
                ),
            ]
        )
    ]
)

OVAL_TREE_TRUE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="true",
        )
    ]
)

OVAL_TREE_FALSE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="false",
        ),
    ]
)

OVAL_TREE_NOTEVAL = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="noteval",
        )
    ]
)

OVAL_TREE_NOTAPPL = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="notappl",
        )
    ]
)

OVAL_TREE_NEGATION_FALSE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    negation=True,
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="false",
        )
    ]
)

OVAL_TREE_NEGATION_TURE = OvalNode(
    node_id="1",
    node_type="and",
    negation=True,
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="true",
        )
    ]
)

OVAL_TREE_NEGATION_NODE_FALSE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="false",
            negation=True,
        ),
    ]
)

OVAL_TREE_NEGATION_NODE_TRUE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="true",
            negation=True,
        ),
    ]
)

BIG_OVAL_TREE = OvalNode(
    node_id="1",
    node_type="and",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="false",
        ),
        OvalNode(
            node_id="3",
            node_type="xor",
            value="",
            children=[
                OvalNode(
                    node_id="4",
                    node_type="value",
                    value="true",
                ),
                OvalNode(
                    node_id="5",
                    node_type="one",
                    value="",
                    children=[
                        OvalNode(
                            node_id="6",
                            node_type="value",
                            value="noteval",
                        ),
                        OvalNode(
                            node_id="7",
                            node_type="value",
                            value="true",
                        ),
                        OvalNode(
                            node_id="8",
                            node_type="value",
                            value="notappl",
                        ),
                    ]
                ),
                OvalNode(
                    node_id="9",
                    node_type="value",
                    value="error",
                ),
            ]
        ),
        OvalNode(
            node_id="10",
            node_type="or",
            value="",
            children=[
                OvalNode(
                    node_id="11",
                    node_type="value",
                    value="unknown",
                ),
                OvalNode(
                    node_id="12",
                    node_type="value",
                    value="true",
                ),
            ]
        ),
    ]
)

NOT_EXIST_OPERATOR_OVAL_TREE = OvalNode(
    node_id="1",
    node_type="nand",
    value="",
    children=[
        OvalNode(
            node_id="2",
            node_type="value",
            value="true",
        ),
    ]
)


@pytest.mark.unit_test
@pytest.mark.parametrize("tree, result", [
    (SAMPLE_OVAL_TREE, "false"),
    (OVAL_TREE_FALSE, "false"),
    (OVAL_TREE_TRUE, "true"),
    (OVAL_TREE_NOTEVAL, "not evaluated"),
    (OVAL_TREE_NOTAPPL, "not applicable"),
    (OVAL_TREE_NEGATION_FALSE, "true"),
    (OVAL_TREE_NEGATION_TURE, "false"),
    (OVAL_TREE_NEGATION_NODE_TRUE, "false"),
    (OVAL_TREE_NEGATION_NODE_FALSE, "true"),
    (BIG_OVAL_TREE, "false"),
    (NOT_EXIST_OPERATOR_OVAL_TREE, None),
])
def test_oval_tree_evaluation(tree, result):
    assert tree.evaluate_tree() == result
