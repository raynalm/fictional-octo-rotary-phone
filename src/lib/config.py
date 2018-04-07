#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file contains all constants, along with configuration variables
"""

RANDOM_START = 8
RANDOM_END = 1000
DEFAULT_MATRIX_SIZE = 3
DEFAULT_SPARSENESS = 0.35

MAIN_LAUNCHER = "main_launcher"
MAIN_Q = "pika_main_launcher_q"
QUEUE_PREFIX = "pika_q_pr_"
ID = "ID"
NEIGHBORS = "NEIGHBORS"


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

# SHOUT ALGORITHM MACROS ______________________________________________________
ANSWER = "ANSWER"
FLUX = "FLUX"
REFLUX = "REFLUX"

# RING ALGORITHM MACROS _______________________________________________________
WHITE = "WHITE"
BLACK = "BLACK"
RIGHT = "RIGHT"
LEFT = "LEFT"
