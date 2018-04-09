#!/usr/bin/env python3

from lib.config import YES, NO, LEADER, FLUX
from lib.config import NEIGHBORS, KEYS


def shout(node):
    node.reflux = {
        NEIGHBORS: {node.my_id: list(node.neighbors_ids)},
        KEYS: {node.my_id: node.pub_key.exportKey()}
    }
    if node.role == LEADER:
        node.shout_answer = NO
        node.wait_answer_from = [e for e in node.neighbors_ids]
        for v in node.neighbors_ids:
            node.send_msg([FLUX, node.my_id, None], v)
        node.recv_msg(node.shout_callback)
        node.graph = dict(node.reflux[NEIGHBORS])
        node.keys = dict(node.reflux[KEYS])
    else:
        node.wait_answer_from = []
        node.shout_answer = YES
        node.recv_msg(node.shout_callback)
