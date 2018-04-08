#!/usr/bin/env python3

import pika
import json
# import sys

from lib.config import QUEUE_PREFIX, MAIN_Q, MAIN_LAUNCHER
from lib.config import ANSWER, REFLUX, FLUX, YES, ID, NEIGHBORS
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
        Class constructor.
        Args:
            my_id: int, the identifier of the node
        """
        self.my_id = my_id
        self.out_queue = {MAIN_LAUNCHER: MAIN_Q}
        self.in_queue = QUEUE_PREFIX + str(self.my_id) + "__main_q"

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
# _______________________ LAUNCH NODE _____________________________________

    def launch(self):
        """
        Main method. Sets up the network, launches yoyo algorithm, etc ....
        """
        # initialize connection
        self.init_connection()

        # send id to main launcher, and modify in case it is used
        self.declare_to_main_launcher()

        # receive list of neighbors' ids from main launcher
        self.receive_neighbors_ids()
        self.declare_neighbors_queues()

        # elect a leader
        self.elect_leader()

        # use shout protocol so the leader can gather all the graph's info
        shout(self)

        # leader creates a virtual ring, and sends routing infos to others
        if self.role == LEADER:
            self.graph = {int(k): self.graph[k] for k in self.graph}
            make_ring(self)
        else:
            self.ring_received = False

        # get the virtual ring created by the leader
        self.recv_msg(self.broadcast_callback)

        print(self.route_left)
        print(self.route_right)

        # enter main loop
        self.main_loop()


# _________________________________________________________________________
# _______________________ SEND MESSAGE ____________________________________

    def send_msg(self, msg, receiver_id):
        """
        Sends the message msg to 'receiver_id'.
        """
        queue_name = self.out_queue[receiver_id]
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(msg)
        )


# _________________________________________________________________________
# _______________________ RECEIVE MESSAGE _________________________________

    def recv_msg(self, callback):
        """
        Starts consuming messages on own queue using 'callback'
        """
        self.channel.basic_consume(
            callback,
            queue=self.in_queue,
            no_ack=False
        )
        self.channel.start_consuming()

# _________________________________________________________________________
# _______________________ NETWORK INITIALIZATION __________________________

    def declare_to_main_launcher(self):
        """
        Declare queues to communicate with the main launcher
        Sends my_id to the main launcher
        """
        self.channel.queue_declare(queue=self.out_queue[MAIN_LAUNCHER])
        self.channel.queue_declare(queue=self.in_queue)

        # send id to main launcher
        self.send_msg(self.my_id, MAIN_LAUNCHER)

    def receive_neighbors_ids(self):
        """
        Receives ids from one's neighbors in the network.
        """
        self.recv_msg(self.init_network_callback)

    def declare_neighbors_queues(self):
        """
        Declares all the queues needed to communicate with the neighbors
        """
        for v in self.neighbors_ids:
            q_name = QUEUE_PREFIX + str(v) + "__"
            self.channel.queue_declare(queue=q_name)
            self.out_queue[v] = q_name

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
        self.exit_program()

# _____________________________________________________________________________
# _______________________ CALLBACKS ___________________________________________

    def init_network_callback(self, ch, method, properties, body):
        """
        Callback for consuming main launcher answer.
        Stores neighbors' ids, and eventually modifies my_id
        """
        self.channel.basic_ack(method.delivery_tag)
        msg = json.loads(body)
        self.my_id = msg[ID]
        print("ID : %s" % self.my_id)
        self.in_queue = QUEUE_PREFIX + str(self.my_id) + "__"
        self.channel.queue_declare(self.in_queue)
        self.neighbors_ids = msg[NEIGHBORS]
        print("NEIGHBORS : %s" % self.neighbors_ids)
        self.channel.stop_consuming()

    def yoyo_recv_id_callback(self, ch, method_frame, properties, body):
        """
        yo_yo specific callback. Stores the candidate's id received in a dict.
        """
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        sender, packet = json.loads(body)
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
        if packet == NO:
            self.edges_to_flip += [sender]
        self.yes_no_received[sender] = packet
        if prune_or_not == PRUNE_OUR_LINK:
            self.edges[sender] = PRUNED
        self.channel.stop_consuming()

    def shout_callback(self, ch, method_frame, properties, body):
        """
        shout protocol specific callback. Depending on th type of message
        (ANSWER, FLUW OR REFLUX), adapts its behavior.
        shout protocol allows to send all graph informations to the leader
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
                        self.send_msg([FLUX, self.my_id, None], v)
                    else:
                        self.send_msg([ANSWER, self.my_id, YES], v)
            else:  # not first FLUX recv
                self.send_msg([ANSWER, self.my_id, NO], sender)

        # reflux
        elif p_type == REFLUX:
            for k in packet:
                self.reflux[int(k)] = packet[k]
            self.wait_answer_from.remove(sender)

        if not self.wait_answer_from:
            if self.role != LEADER:
                self.send_msg(
                    [REFLUX, self.my_id, self.reflux], self.where_to_reflux
                )
            self.channel.stop_consuming()

    def broadcast_callback(self, ch, method_frame, properties, body):
        """
        Callback used to broadcast the virtual ring around the nodes
        """
        if not self.ring_received:
            ring = json.loads(body)
            # get own right and left routes
            self.route_right = [l for l in ring if l[0] == self.my_id][0][1:]
            self.route_left = [l[::-1] for l in ring if l[-1] == self.my_id][0][1:]  # noqa: E501
            # spread info to neighbors
            for v in self.neighbors_ids:
                self.send_msg(ring, v)
            self.nb_broadcast_msg_recv = 1
            self.ring_received = True
        else:

            self.nb_broadcast_msg_recv += 1
            if self.nb_broadcast_msg_recv == len(self.neighbors_ids):
                self.channel.stop_consuming()

# _____________________________________________________________________________
# _______________________ EXIT PROGRAM ________________________________________

    def exit_program(self):
        self.channel.queue_delete(queue=self.in_queue)
        self.connection.close()
