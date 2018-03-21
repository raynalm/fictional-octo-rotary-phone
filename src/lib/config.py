#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yo_yo import yo_yo
from lib.multishout import multishout


# contains all constants
PRINT_DEBUG = False

INIT_QUEUE_NAME = "init_queue"
RANDOM_START = 8
RANDOM_END = 1000000000
DEFAULT_MATRIX_SIZE = 3
DEFAULT_SPARSENESS = 0.3
MSG_ID_OK = "message id is ok"
QUEUE_PREFIX = "q_pr_"
IN = 0
OUT = 1
SOURCE = 0
INTERMEDIATE = 1
SINK = 2


USE_YO_YO = True


def elect_leader(node):
    if USE_YO_YO:
        return yo_yo(node)
    else:
        return multishout(node)
