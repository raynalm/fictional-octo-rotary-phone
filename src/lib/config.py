#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.yo_yo import yo_yo
from lib.multishout import multishout


# contains all constants
PRINT_DEBUG = False

RANDOM_START = 8
RANDOM_END = 1000
DEFAULT_MATRIX_SIZE = 3
DEFAULT_SPARSENESS = 0.3
MSG_ID_OK = "message id is ok"
IN = 0
OUT = 1
SOURCE = 0
INTERMEDIATE = 1
SINK = 2

MAIN_PUB = "main_pub"
MAIN_PRIV = "main_priv"
PUB_Q = "q_pub_"
QUEUE_PREFIX = "q_pr_"

USE_YO_YO = True


def elect_leader(node):
    if USE_YO_YO:
        return yo_yo(node)
    else:
        return multishout(node)
