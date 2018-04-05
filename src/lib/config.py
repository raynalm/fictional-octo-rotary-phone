#!/usr/bin/env python3
# -*- coding: utf-8 -*-



# contains all constants
PRINT_DEBUG = False

RANDOM_START = 8
RANDOM_END = 1000
DEFAULT_MATRIX_SIZE = 3
DEFAULT_SPARSENESS = 0.3
MSG_ID_OK = "message id is ok"

MAIN_PUB = "main_pub"
MAIN_PRIV = "main_priv"
PUB_Q = "q_pub_"
QUEUE_PREFIX = "q_pr_"

USE_YO_YO = True

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
