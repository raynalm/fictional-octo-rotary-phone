#!/usr/bin/env python3

from lib.config import YES, NO, LEADER, FLUX


def shout(node):
    node.reflux = {node.my_id: list(node.neighbors_ids)}
    if node.role == LEADER:
        node.shout_answer = NO
        node.wait_answer_from = [e for e in node.neighbors_ids]
        for v in node.neighbors_ids:
            node.send_msg([FLUX, node.my_id, None], v, True)
        node.recv_msg(node.shout_callback)
        node.graph = dict(node.reflux)
    else:
        node.wait_answer_from = []
        node.shout_answer = YES
        node.recv_msg(node.shout_callback)
