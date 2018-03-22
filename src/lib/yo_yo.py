#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# YO-YO ALGORITHM MACROS ______________________________________________________
# edges
IN = "IN"
OUT = "OUT"
PRUNED = "PRUNED"
# roles
SOURCE = "SOURCE"
INTERMEDIATE = "INTERMEDIATE"
SINK = "SINK"
LEADER = "LEADER"
# upstream answers
YES = "YES"
NO = "NO"
# pruning request
PRUNE_OUR_LINK = "PRUNE"
DONT_PRUNE_OUR_LINK = "NO_PRUNE"


# _____________________________________________________________________________
# _______________________ YO-YO ALGORITHM _____________________________________
# _____________________________________________________________________________


def yo_yo(node):
    """
    yoyo algorithm 'main'.
    The result is actually stored in node.role (leader or not)
    """
    node.edges = dict()
    yo_yo_preprocess(node)
    do_yo_yo(node)


def yo_yo_preprocess(node):
    """
    Preprocessing phase of the yoyo algorithm.
    Logically orients edges and initialize node's role
    """
    # logically orient edges
    for v in node.neighbors_ids:
        node.edges[v] = IN if v < node.my_id else OUT
    print_edges(node)
    # determine initial role in the resulting DAG
    get_role(node)


def do_yo_yo(node):
    """
    Main loop of the yoyo algorithm
    """
    print("[%s] start yoyo, my edges are %s" % (node.my_id, node.edges))
    # loop until pruned or leader
    while (node.role != PRUNED and node.role != LEADER):
        # yo- phase, then -yo (oy) phase
        yo_phase(node)
        oy_phase(node)


# YO- PHASE _____________________________________________________________
def yo_phase(node):
    """
    YO- phase of the YO-YO algorithm
    """
    print("[%s] start yo, role is %s" % (node.my_id, node.role))
    # gather ids from in edges (and include my_id for sources)
    node.id_received = {None: node.my_id}
    print("in_edges : %s" % (in_edges(node)))
    for v in in_edges(node):
        node.recv_msg(node.yoyo_recv_id_callback, v)
    print("here")
    # send smaller id received (or my_id if node is source) on out edges
    node.min_id_recv = min(node.id_received.values())
    for v in out_edges(node):
        node.send_msg([node.my_id, node.min_id_recv], v)


# -YO PHASE _______________________________________________________________
def oy_phase(node):
    """
    -YO phase of the YO-YO algorithm
    """
    print("[%s] start yo, role is %s" % (node.my_id, node.role))
    node.yes_no_received = dict()
    node.edges_to_flip = []
    ids_already_sent = set()

    if node.role == SINK:
        for v in in_edges(node):
            # determine if link should be pruned or not
            if is_leaf(node):
                prune_or_not = PRUNE_OUR_LINK
                node.role = PRUNED
                node.edges[v] = PRUNED
            elif node.id_received[v] in ids_already_sent:
                prune_or_not = PRUNE_OUR_LINK
                node.edges[v] = PRUNED
            else:
                prune_or_not = DONT_PRUNE_OUR_LINK
                ids_already_sent.add(node.id_received[v])

            # send yes/no and prune/not_prune on all in_edges
            if node.id_received[v] == node.min_id_recv:
                node.send_msg([node.my_id, YES, prune_or_not], v)
            else:
                node.send_msg([node.my_id, NO, prune_or_not], v)
                node.edges_to_flip += [v]

    elif node.role == INTERMEDIATE:
        # gather answers from all out edges
        for v in out_edges(node):
            node.recv_msg(node.oy_oy_callback, v)

        # node could have become a leaf after receiving answers
        if is_leaf(node):
            prune_or_not = PRUNE_OUR_LINK
            node.role = PRUNED
            for v in in_edges(node):
                node.send_msg([node.my_id, YES, prune_or_not], v)
                node.edges[v] = PRUNED

        # if all votes are YES
        if all([b == YES for b in node.yes_no_received.values()]):
            # send YES to those who sent smallest id, NO to others
            # prune all but one of those who sent a particular id
            for v in in_edges(node):
                # determine if link should be pruned or not
                if node.id_received[v] in ids_already_sent:
                    prune_or_not = PRUNE_OUR_LINK
                else:
                    prune_or_not = DONT_PRUNE_OUR_LINK
                    ids_already_sent.add(node.id_received[v])
                # should I yes or should I no ? (ok, easy one)
                if node.id_received[v] == node.min_id_recv:
                    node.send_msg([node.my_id, YES, prune_or_not], v)   # noqa
                else:
                    node.send_msg([node.my_id, NO, prune_or_not], v)    # noqa
                    node.edges_to_flip += [v]
        else:
            # at least one upcoming vote was no : send no to everyone, the best
            # candidate is not upstream. Enjoy the moment to do some pruning.
            for v in node.in_edges():
                if node.id_received[v] in ids_already_sent:
                    prune_or_not = PRUNE_OUR_LINK
                else:
                    prune_or_not = DONT_PRUNE_OUR_LINK
                node.send_msg([node.my_id, NO, prune_or_not], v)
                node.edges_to_flip += [v]

    else:  # node.role == SOURCE
        # gather answers from all out_edges
        for v in out_edges(node):
            node.recv_msg(node.oy_oy_callback, v)

    flip_edges(node)


# YO-YO UTILS _____________________________________________________________

def active_edges(node):
    """
    Returns the list of node's edges which have not been pruned yet
    """
    return [v for v in node.edges if node.edges[v] != PRUNED]


def out_edges(node):
    """
    Returns the list of node's out edges
    """
    return [v for v in active_edges(node) if node.edges[v] == OUT]


def in_edges(node):
    """
    Returns the list of node's in edges
    """
    return [v for v in active_edges(node) if node.edges[v] == IN]


def flip_edges(node):
    """
    Flips the logical orientation of node's edges which are in edges_to_flip
    """
    for v in node.edges:
        if v in node.edges_to_flip:
            node.edges[v] = "IN" if node.edges[v] == "OUT" else "OUT"
    # flipping the edges can modify one's role. reaffect
    get_role(node)


def is_sink(node):
    """
    Returns true iff node is a sink. This method does not check node.role,
    but actually checks edges to see if the node is currently a sink
    """
    return not any(node.edges.values() == OUT)


def is_leaf(node):
    """
    Returns true iff node is a sink with exactly one in edge
    """
    return (len(in_edges(node)) == 1) and (len(out_edges(node)) == 0)


def get_role(node):
    """
    Determines own role in the DAG : source, intermediate, sink, pruned, leader
    """
    if not active_edges(node):
        node.role = LEADER if node.role == SOURCE else PRUNED
    elif all([node.edges[e] == IN for e in active_edges(node)]):
        node.role = SINK
    elif all([node.edges[e] == OUT for e in active_edges(node)]):
        node.role = SOURCE
    else:
        node.role = INTERMEDIATE


def print_edges(node):
    """
    Utility printing oriented edges
    """
    for v in node.edges:
        if node.edges[v] == IN:
            print("%s <--- %s" % (node.my_id, v))
        elif node.edges[v] == OUT:
            print("%s ---> %s" % (node.my_id, v))
        else:
            print("%s -XX- %s" % (node.my_id, v))
