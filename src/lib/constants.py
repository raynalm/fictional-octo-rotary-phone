#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file contains a lot of constants used though the program
"""


MAIN_LAUNCHER = "main_launcher"
MAIN_Q = "pika_main_launcher_q"
QUEUE_PREFIX = "pika_q_pr_"
ID = "ID"
NEIGHBORS = "NEIGHBORS"
SELECT_TIMEOUT = 0.2

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
