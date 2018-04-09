#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika

"""
This file contains configuration variables
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

RANDOM_START = 1
RANDOM_END = 1000
DEFAULT_MATRIX_SIZE = 3
DEFAULT_SPARSENESS = 0.4
