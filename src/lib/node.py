#!/usr/bin/env python3

import pika
import json
from .config import *


# NODE __________ ______________________________________________________
class Node:
    def __init__(self, my_id):
        """
        Args:
            my_id: int, the identifier of the node
        """
        self.__id = my_id
        self.init_connection()


    def init_connection(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = connection.channel()
        print("Connection initialized")



    def launch(self):
        self.declare_to_main_launcher()


    def declare_to_main_launcher(self):
        # send id to main launcher
        self.channel.queue_declare(queue = INIT_QUEUE_NAME)
        msg = json.dumps(self.__id)
        self.channel.basic_publish(
            exchange = '',
            routing_key = INIT_QUEUE_NAME,
            body = msg
        )
        # get an answer from main launcher
        self.channel.basic_consume(
            self.init_callback,
            queue = INIT_QUEUE_NAME,
            no_ack = True
        )

    def init_callback(self, ch, method, properties, body):
        self.__p_neighbors = json.loads(body)
        self.channel.stop_consuming()
