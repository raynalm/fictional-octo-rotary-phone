#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika
import json
import sys
import select
import time
import base64

from lib.config import *
from lib.constants import *

from lib.yo_yo import yo_yo
from lib.shout import shout
from lib.make_ring import make_ring
from lib.utils import console_print

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
            PIKA_CONNECTION_PARAMETERS
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

        # enter main loop
        self.main_loop()


# _________________________________________________________________________
# _______________________ SEND MESSAGE ____________________________________

    def send_msg(self, msg, receiver_id):
        """
        Sends the message msg to 'receiver_id'.
        """
        queue_name = self.out_queue[receiver_id]
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(msg)
            )
        except:
            console_print("Error while attempting to send a message\n"
                          "Exiting.")
            self.exit_program()

# _________________________________________________________________________
# _______________________ RECEIVE MESSAGE _________________________________

    def recv_msg(self, callback):
        """
        Starts consuming messages on own queue using 'callback'
        """
        try:
            self.channel.basic_consume(
                callback,
                queue=self.in_queue,
                no_ack=False
            )
            self.channel.start_consuming()
        except:
            console_print("Error while attempting to receive a message\n"
                          "Exiting.")
            self.exit_program()
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
        self.in_main_loop = True
        while self.in_main_loop:
            try:
                # check if user issued a command
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    self.process_cmd()
                self.get_msg_non_blocking()
                time.sleep(0.1)
            except:
                self.in_main_loop = False
        self.exit_program()

    def process_cmd(self):
        cmd = raw_input()
        if not cmd:
            pass
        elif cmd == QUIT:
            self.exit_program()
        elif cmd.split()[0] == SEND_MSG:
            self.ring_send_msg(cmd)
        elif cmd == LIST_NODES:
            print(
                "Available nodes : {0}".format(
                    ', '.join({str(e) for e in self.all_nodes})
                )
            )
        elif cmd.split()[0] == ASK_FILE:
            self.ring_ask_file(cmd)
        elif cmd == HELP:
            self.display_help()

    def display_help(self):
        console_print("Commmands :\n'%s' -> lists network's nodes\n"
                      "'%s recv_id msg' -> sends a message\n"
                      "'%s' -> display help\n"
                      "'%s recv_id filename' -> request a file"
                      % (LIST_NODES, SEND_MSG, HELP, ASK_FILE))

    def get_msg_non_blocking(self):
        try:
            m_frame, header_frame, body = self.channel.basic_get(self.in_queue)
            if m_frame:
                self.channel.basic_ack(m_frame.delivery_tag)
                msg = json.loads(body)
                if msg[ROUTE]:
                    self.route_msg(msg)
                elif int(msg[RECEIVER]) == self.my_id:
                    self.open_msg(msg)
                else:
                    if msg[DIRECTION] == LEFT:
                        msg[ROUTE] = self.route_left[1:]
                    else:
                        msg[ROUTE] = self.route_right[1:]
                        self.send_msg(msg, self.route_right[0])
            # else -> no message on the queue
        except pika.exceptions.ChannelClosed:
            self.exit_program()

# _____________________________________________________________________________
# _______________________ RING METHODS ________________________________________

    def send_on_ring(self, msg_type, msg_body, recv_id, filename=None, direction=RIGHT):
        route = self.route_right if direction == RIGHT else self.route_left
        packet = {
            TYPE: msg_type,
            BODY: msg_body,
            RECEIVER: recv_id,
            DIRECTION: direction,
            ROUTE: route[1:],
            SENDER: self.my_id,
            FILENAME: filename
        }
        self.send_msg(packet, route[0])

    def ring_send_msg(self, cmd):
        cmd_spl = cmd.split()
        if len(cmd_spl) < 3 or int(cmd_spl[1]) not in self.all_nodes:
            console_print("Send a message syntax : '%s recv_id msg'\n"
                          "For instance, '%s 471 hello mister 471"
                          % (SEND_MSG, SEND_MSG))
        else:
            self.send_on_ring(
                RING_MSG,
                cmd[cmd.index(cmd_spl[2]):],
                cmd_spl[1]
            )

    def ring_ask_file(self, cmd):
        cmd_spl = cmd.split()
        if len(cmd_spl) < 3 or int(cmd_spl[1]) not in self.all_nodes:
            console_print("ask a file syntax : '%s recv_id filename'\n"
                          "For instance, '%s 471 new_file.txt'"
                          % (ASK_FILE, ASK_FILE))
        else:
            self.send_on_ring(
                RING_ASK_FILE,
                cmd[cmd.index(cmd_spl[2]):],
                cmd_spl[1]
            )

    def route_msg(self, msg):
        assert(msg[ROUTE] != [])
        recv_id = int(msg[ROUTE][0])
        msg[ROUTE] = msg[ROUTE][1:]
        self.send_msg(msg, recv_id)

    def open_msg(self, msg):
        if msg[TYPE] == RING_MSG:
            console_print(
                "[%s] %s" % (msg[SENDER], msg[BODY])
            )
        elif msg[TYPE] == RING_FILE:
            if msg[FILENAME] == NO_SUCH_FILE:
                console_print("Invalid filename")
            else:
                f = open(msg[FILENAME], 'wb')
                f.write(base64.b64decode(msg[BODY]))
                f.close()
                console_print("%s copy successful" % msg[FILENAME])
        elif msg[TYPE] == RING_ASK_FILE:
            self.ring_send_file(msg[BODY], msg[SENDER])

    def ring_send_file(self, filename, recv_id, direction=RIGHT):
        try:
            f = open(filename, 'rb')
        except IOError:
            filename = NO_SUCH_FILE
        route = self.route_right if direction == RIGHT else self.route_left
        packet = {
                TYPE: RING_FILE,
                DIRECTION: direction,
                ROUTE: route[1:],
                RECEIVER: recv_id,
                SENDER: self.my_id,
                BODY: base64.b64encode(f.read())
                if filename != NO_SUCH_FILE else None,
                FILENAME: filename
        }
        self.send_msg(packet, route[0])

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
        self.to_close_on_exit = self.in_queue
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

            # get list of all nodes in the network
            self.all_nodes = [l[0] for l in ring if l[0] != self.my_id]

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
        self.channel.queue_delete(self.to_close_on_exit)
        self.channel.close()
        self.connection.close()
        console_print("bye")
        sys.exit()
