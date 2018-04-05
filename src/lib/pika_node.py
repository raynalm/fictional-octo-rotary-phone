#!/usr/bin/env python3

import pika
import json
import sys

from lib.config import QUEUE_PREFIX, MAIN_PUB, MAIN_PRIV, PUB_Q
from lib.config import ANSWER, REFLUX, FLUX, YES
from lib.config import NO, PRUNE_OUR_LINK, PRUNED, LEADER
from lib.yo_yo import yo_yo
from lib.shout import shout
from lib.make_ring import make_ring


# _________________________________________________________________________
# _______________________ PIKA NODE CLASS _________________________________
# _________________________________________________________________________


class PikaNode:
    def __init__(self, my_id):
        """
        Args:
            my_id: int, the identifier of the node
        """
        self.my_id = my_id
        self.in_queue = {MAIN_PUB: PUB_Q, MAIN_PRIV: PUB_Q+str(my_id)}
        self.out_queue = {MAIN_PUB: PUB_Q, MAIN_PRIV: PUB_Q+str(my_id)}
        self.excl_queue = dict()
        self.init_connection()

# _________________________________________________________________________
# _______________________ INIT CONNECTION _________________________________

    def init_connection(self):
        """
        Initializes the connection with Rabbitmq
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        print("Connection initialized")

# _________________________________________________________________________
# _______________________ SEND MESSAGE ____________________________________

    def send_msg(self, msg, receiver_id, on_excl_queue=False):
        """
        Sends the message msg to 'receiver_id'.
        """
        print("send %s to %s" % (msg, receiver_id))
        if on_excl_queue:
            queue_name = self.excl_queue[receiver_id]
        else:
            queue_name = self.out_queue[receiver_id]
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(msg)
        )


# _________________________________________________________________________
# _______________________ RECEIVE MESSAGE _________________________________

    def recv_msg(self, callback, sender_id=None):
        """
        Consumes a message sent by 'sender_id' by calling 'callback'
        """
        if sender_id is None:
            queue_name = self.excl_queue[self.my_id]
        else:
            queue_name = self.in_queue[sender_id]
        self.channel.basic_consume(
            callback,
            queue=queue_name,
            no_ack=False
        )
        self.channel.start_consuming()

# _________________________________________________________________________
# _______________________ LAUNCH NODE _____________________________________

    def launch(self):
        """
        Main method. Sets up the network, launches yoyo algorithm, etc ....
        """
        # send id to main launcher, and modify in case it is used
        self.declare_to_main_launcher()

        # receive list of neighbors' ids from main launcher
        self.receive_neighbors_ids()
        self.declare_neighbors_queues()

        # elect a leader
        try:
            self.elect_leader()
        except:
            e = sys.exc_info()[0]
            print("<p>Error: %s</p>" % e)
            self.main_loop()

        shout(self)
        if self.role == LEADER:
            self.graph = {int(k): self.graph[k] for k in self.graph}
            print(self.graph)
            make_ring(self)
            print(self.ring)

        # enter main loop
        self.main_loop()

# _________________________________________________________________________
# _______________________ NETWORK INITIALIZATION __________________________

    def declare_to_main_launcher(self):
        """
        Declare queues to communicate with the main launcher
        Sends my_id to the main launcher, receive it back (eventually modified)
        """
        self.channel.queue_declare(queue=self.in_queue[MAIN_PUB])
        self.channel.queue_declare(queue=self.in_queue[MAIN_PRIV])

        # send id to main launcher
        self.send_msg(self.my_id, MAIN_PUB)

        # get an answer from main launcher
        self.recv_msg(self.init_callback, MAIN_PRIV)

    def receive_neighbors_ids(self):
        """
        Receives ids from one's neighbors in the network.
        """
        self.recv_msg(self.store_neighbors_callback, MAIN_PRIV)

    def declare_neighbors_queues(self):
        """
        Declares all the queues needed to communicate with the neighbors
        """
        for v in self.neighbors_ids:
            # declare in_queues
            sstr = QUEUE_PREFIX + str(v) + "->" + str(self.my_id)
            self.channel.queue_declare(queue=sstr)
            self.in_queue[v] = sstr
            # declare out_queues
            sstr = QUEUE_PREFIX + str(self.my_id) + "->" + str(v)
            self.channel.queue_declare(queue=sstr)
            self.out_queue[v] = sstr
            # declare excl_queue
            sstr = QUEUE_PREFIX + str(v) + "__"
            self.channel.queue_declare(queue=sstr)
            self.excl_queue[v] = sstr
# _________________________________________________________________________
# _______________________ YO-YO ALGORITHM _________________________________

    def elect_leader(self):
        """
        Leader election, done with the yoyo algorithm
        """
        self.is_leader = yo_yo(self)
        print("I am%s the leader" % ("" if self.role == LEADER else " not"))


# _____________________________________________________________________________
# _______________________ MAIN LOOP ___________________________________________

    def main_loop(self):
        in_main_loop = True
        while in_main_loop:
            user_in = raw_input(">")
            if user_in == "/q":
                in_main_loop = False
                print("bye")
# _____________________________________________________________________________
# _______________________ CALLBACKS ___________________________________________

    def init_callback(self, ch, method_frame, properties, body):
        """
        Callback for consuming main launcher answer. Can reset my_id
        """
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        if self.my_id != json.loads(body):
            # if my_id was modified
            self.my_id = json.loads(body)
            self.in_queue[MAIN_PRIV] = PUB_Q+str(self.my_id)
        self.excl_queue[self.my_id] = QUEUE_PREFIX + str(self.my_id) + "__"
        self.channel.queue_declare(self.in_queue[MAIN_PRIV])
        self.channel.stop_consuming()

    def store_neighbors_callback(self, ch, method, properties, body):
        """
        Callback for consuming main launcher message. Stores neighbors' ids
        """
        self.channel.basic_ack(method.delivery_tag)
        self.neighbors_ids = json.loads(body)
        self.channel.stop_consuming()

    def yoyo_recv_id_callback(self, ch, method_frame, properties, body):
        """
        yo_yo specific callback. Stores the candidate's id received in a dict.
        """
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        sender, packet = json.loads(body)
        print("recv %s from %s" % (packet, sender))
        self.id_received[sender] = packet
        self.channel.stop_consuming()

    def oy_oy_callback(self, ch, method_frame, properties, body):
        """
        yo_yo specific callback. Stores the yes/no answer received, and
        processesthe pruning/not pruning request
        """
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        sender, packet, prune_or_not = json.loads(body)
        print("recv %s, %s from %s" % (packet, prune_or_not, sender))
        if packet == NO:
            self.edges_to_flip += [sender]
        self.yes_no_received[sender] = packet
        if prune_or_not == PRUNE_OUR_LINK:
            self.edges[sender] = PRUNED
        self.channel.stop_consuming()

    def shout_callback(self, ch, method_frame, properties, body):
        """

        """
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process message
        p_type, sender, packet = json.loads(body)
        # answer : if yes, wait for reflux ; if no, wait for nothing more
        if p_type == ANSWER:
            if packet == NO:
                self.wait_answer_from.remove(sender)
        # flux

        elif p_type == FLUX: # TODO -> case where only one neighbor or case where all say no # noqa
            if self.shout_answer == YES:  # if first FLUX recv
                self.where_to_reflux = sender
                self.shout_answer = NO
                for v in self.neighbors_ids:
                    if v != sender:
                        self.wait_answer_from += [v]
                        self.send_msg([FLUX, self.my_id, None], v, True)
                    else:
                        self.send_msg([ANSWER, self.my_id, YES], v, True)
            else:  # not first FLUX recv
                self.send_msg([ANSWER, self.my_id, NO], sender, True)

        # reflux
        elif p_type == REFLUX:
            for k in packet:
                self.reflux[int(k)] = packet[k]
            self.wait_answer_from.remove(sender)

        if not self.wait_answer_from:
            if self.role != LEADER:
                self.send_msg(
                    [REFLUX, self.my_id, self.reflux],
                    self.where_to_reflux,
                    True
                )
            self.channel.stop_consuming()
