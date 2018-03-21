#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# YO-YO ALGORITHM MACROS
IN = 0
OUT = 1
PRUNED = 2

SOURCE = 0
INTERMEDIATE = 1
SINK = 2
PRUNED = 3
LEADER = 4

YES = 0
NO = 1

PRUNE_OUR_LINK = 0
DONT_PRUNE_OUR_LINK = 1


# _________________________________________________________________________
# _______________________ YO-YO ALGORITHM _________________________________
# _________________________________________________________________________


def yo_yo(node):
    """
    yoyo algorithm implementation
    """
    node.edges = dict()
    yo_yo_preprocess(node)
    node.do_yo_yo(node)
    return node.role == LEADER


def yo_yo_preprocess(node):
    """
    Preprocessing phase of the yoyo algorithm
    """
    # logically orient edges
    for v in node.neighbors_ids:
        node.edges[v] = IN if v < node.my_id else OUT
    # determine initial role in the resulting DAG
    node.get_role()


def do_yo_yo(node):
    """
    Main loop of the yoyo algorithm
    """
    # loop until pruned or leader
    while (node.role != PRUNED and node.role != LEADER):
        # yo- phase, then -yo (oy) phase
        node.yo_phase()
        node.oy_phase()


# YO- PHASE _____________________________________________________________
def yo_phase(node):
    """
    YO- phase of the YO-YO algorithm
    """
    # gather ids from in edges (and include my_id for sources)
    node.id_received = {None: node.my_id}
    for v in node.in_edges():
        node.recv_message(node.yoyo_recv_id_callback, node.queues[v])

    # send smaller id received (or my_id if node is source) on out edges
    node.min_id_recv = min(node.id_received.values())
    for v in node.out_edges():
        node.send_message(node.queues[v], [node.my_id, node.min_id_recv])


# -YO PHASE _______________________________________________________________
def oy_phase(node):
    """
    -YO phase of the YO-YO algorithm
    """
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
                node.send_msg(node.queues[v], [node.my_id, YES, prune_or_not])
            else:
                node.send_msg(node.queues[v], [node.my_id, NO, prune_or_not])
                node.edges_to_flip += [v]

    elif node.role == INTERMEDIATE:
        # gather answers from all out edges
        for v in node.out_edges():
            node.recv_message(node.oy_oy_callback, node.queues[v])

        # node could have become a leaf after receiving answers
        if is_leaf(node):
            prune_or_not = PRUNE_OUR_LINK
            node.role = PRUNED
            for v in in_edges(node):
                node.send_msg(node.queues[v], YES, prune_or_not)
                node.edges[v] = PRUNED

        # if all votes are YES
        if all(node.yes_no_received.values() == YES):
            # send YES to those who sent smallest id, NO to others
            # prune all but one of those who sent a particular id
            for v in node.in_edges():
                # determine if link should be pruned or not
                if node.id_received[v] in ids_already_sent:
                    prune_or_not = PRUNE_OUR_LINK
                else:
                    prune_or_not = DONT_PRUNE_OUR_LINK
                    ids_already_sent.add(node.id_received[v])
                # should I yes or should I no ? (ok, easy one)
                if node.id_received[v] == node.min_id_recv:
                    node.send_msg(node.queues[v], [node.my_id, YES, prune_or_not])   # noqa
                else:
                    node.send_msg(node.queues[v], [node.my_id, NO, prune_or_not])    # noqa
                    node.edges_to_flip += [v]
        else:
            # at least one upcoming vote was no : send no to everyone, the best
            # candidate is not upstream. Enjoy the moment to do some pruning.
            for v in node.in_edges():
                if node.id_received[v] in ids_already_sent:
                    prune_or_not = PRUNE_OUR_LINK
                else:
                    prune_or_not = DONT_PRUNE_OUR_LINK
                node.send_msg(node.queues[v], [node.my_id, NO, prune_or_not])
                node.edges_to_flip += [v]

    else:  # node.role == SOURCE
        # gather answers from all out_edges
        for v in node.out_edges():
            node.recv_msg(node.oy_oy_callback, node.queues[v])

    node.flip_edges()


# YO-YO UTILS _____________________________________________________________

def active_edges(node):
    return [v for v in node.edges if node.edges[v] != PRUNED]


def out_edges(node):
    return (v for v in node.active_edges() if node.edges[v] == OUT)


def in_edges(node):
    return (v for v in node.active_edges() if node.edges[v] == IN)


def flip_edges(node):
    node.edges = {
        v: node.edges[v] if v not in node.to_flip else 1-node.edges[v]
        for v in node.edges
    }
    # flipping the edges can modify one's role. reaffect
    get_role(node)


def is_sink(node):
    return not any(node.edges.values() == OUT)


def is_leaf(node):
    return (len(node.in_edges()) == 1) and (len(node.out_edges()) == 0)


def get_role(node):
    """
    Determines own role in the DAG : source, intermediate, sink, pruned, leader
    """
    if not active_edges(node):
        node.role = LEADER if node.role == SOURCE else PRUNED
    elif all(active_edges(node).values() == IN):
        node.role = SINK
    elif all(active_edges(node).values == OUT):
        node.role = SOURCE
    else:
        node.role = INTERMEDIATE
