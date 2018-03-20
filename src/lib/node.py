#!/usr/bin/env python3

import pika
import json
from .config import *


# NODE CLASS __________________________________________________________________
class Node:
    def __init__(self, my_id):
        """
        Args:
            my_id: int, the identifier of the node
        """
        self.__id = my_id
        self.init_connection()


    # INIT CONNECTION _________________________________________________________
    def init_connection(self):
        """
        Initializes the connection with Rabbitmq
        """
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.__channel = connection.channel()
        print("[%s]Connection initialized" % self.__id)


    # LAUNCH NODE _____________________________________________________________
    def launch(self):
        self.declare_to_main_launcher()


    def declare_to_main_launcher(self):
        # send id to main launcher
        self.__channel.queue_declare(queue = INIT_QUEUE_NAME)
        msg = json.dumps(self.__id)
        self.__channel.basic_publish(
            exchange = '',
            routing_key = INIT_QUEUE_NAME,
            body = msg,

        )

        # get an answer from main launcher
        answer_queue = INIT_QUEUE_NAME+str(self.__id)
        self.__channel.queue_declare(answer_queue)
        self.__channel.basic_consume(
            self.init_callback,
            queue = answer_queue,
            no_ack = True
        )
        self.__channel.start_consuming()

    def init_callback(self, ch, method, properties, body):
        new_id = json.loads(body)
        if new_id == self.__id:
            print("[%s]ID confirmed" % self.__id)
        else:
            print("Changed ID from %s to %s" % (self.__id, new_id))
            self.__id = new_id
        self.__channel.stop_consuming()
