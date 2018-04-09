#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika

"""
This file contains all constants, along with configuration variables
"""

USE_LOCALLY = True
if USE_LOCALLY:
    PIKA_CONNECTION_PARAMETERS = pika.ConnectionParameters(host='localhost')
else:
    HOST_URL = '42.42.42.42'
    CREDENTIALS = ('user', 'pass')
    PIKA_PORT = 5672
    PIKA_CONNECTION_PARAMETERS = pika.ConnectionParameters(
        HOST_URL,
        PIKA_PORT,
        '/',
        CREDENTIALS
    )


RANDOM_START = 8
RANDOM_END = 1000
DEFAULT_MATRIX_SIZE = 3
DEFAULT_SPARSENESS = 0.35

MAIN_LAUNCHER = "main_launcher"
MAIN_Q = "pika_main_launcher_q"
QUEUE_PREFIX = "pika_q_pr_"
ID = "ID"
NEIGHBORS = "NEIGHBORS"
SELECT_TIMEOUT = 0.2

KEYS = "KEYS"
HASH = "HASH"
PUB_KEY = "PUB_KEY"
DIRECTION = "DIRECTION"
ROUTE = "ROUTE"
RECEIVER = "RECEIVER"
BODY = "BODY"
TYPE = "TYPE"
RING_MSG = "RING_MSG"
SENDER = "SENDER"
RING_ASK_FILE = "RING_ASK_FILE"
RING_FILE = "RING_FILE"
FILENAME = "FILENAME"
NO_SUCH_FILE = "NO SUCH FILE"
# COMMAND MACROS ______________________________________________________
QUIT = "/q"
SEND_MSG = "/s"
LIST_NODES = "/l"
HELP = "/h"
ASK_FILE = "/ask_file"

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
