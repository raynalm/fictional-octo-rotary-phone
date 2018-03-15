#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pika
connection = pika.BlockingConnection()
channel = connection.channel()
channel.basic_publish(exchange='example',
                      routing_key='test',
                      body='Test Message')
connection.close()
