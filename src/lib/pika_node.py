#!/usr/bin/env python3

import pika
import json

from lib.config import QUEUE_PREFIX, INIT_QUEUE_NAME

# YO-YO ALGORITHM MACROS
IN = 0
OUT = 1

SOURCE = 0
INTERMEDIATE = 1
SINK = 2
PRUNED = 3
LEADER = 4

YES = 0
NO = 1


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

    def send_message(self, msg, queue_name, declare_queue=False):
        """
        Sends the message msg on the queue queue_name.
        Can also declare the queue.
        """
        if declare_queue:
            self.channel.declare_queue(queue_name)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(msg)
        )


# _________________________________________________________________________
# _______________________ RECEIVE MESSAGE _________________________________

    def recv_message(self, callback, queue_name, declare_queue=False):
        """
        Consumes a message on the queue 'queue_name' by calling 'callback'
        Can also declare the queue
        """
        if declare_queue:
            self.channel.declare_queue(queue_name)
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
        # elect_leader(self)

# _________________________________________________________________________
# _______________________ NETWORK INITIALIZATION __________________________

    def declare_to_main_launcher(self):
        """
        Sends my_id to the main launcher, receive it back (eventually modified)
        """
        # send id to main launcher
        self.channel.queue_declare(queue=INIT_QUEUE_NAME)
        self.send_message(INIT_QUEUE_NAME, self.my_id)

        # get an answer from main launcher
        self.answer_queue = INIT_QUEUE_NAME+str(self.my_id)
        self.recv_message(self.init_callback, self.answer_queue, True)

    def receive_neighbors_ids(self):
        """
        Receives ids from the neighbor in the network.
        """
        self.recv_message(self.store_neighbors_callback, self.answer_queue)

    def declare_neighbors_queues(self):
        """
        Declares all the queues needed to communicate with the neighbors
        """
        print(self.neighbors_ids)
        self.queues = dict()
        for v in self.neighbors_ids:
            if v > self.my_id:
                sstr = str(self.my_id)+str(v)
            else:
                sstr = str(v)+str(self.my_id)
            self.channel.queue_declare(QUEUE_PREFIX+sstr)
            self.queues[v] = QUEUE_PREFIX+sstr

# _________________________________________________________________________
# _______________________ YO-YO ALGORITHM _________________________________

    def elect_leader(self):
        """
        Leader election, done with the yoyo algorithm
        """
        self.is_leader = self.yo_yo()

    def yo_yo(self):
        """
        yoyo algorithm implementation
        """
        self.edges = dict()
        self.yo_yo_preprocess()
        self.do_yo_yo()
        return self.role == LEADER

    def yo_yo_preprocess(self):
        """
        Preprocessing phase of the yoyo algorithm
        """
        # logically orient edges
        for v in self.neighbors_ids:
            self.edges[v] = IN if v < self.my_id else OUT

        # determine initial role in the resulting DAG
        self.get_role()

    def get_role(self):
        if all([self.edges[v] == IN for v in self.edges]):
            self.role = SINK
        elif all([self.edges[v] == OUT for v in self.edges]):
            self.role = SOURCE
        else:
            self.role = INTERMEDIATE

    def do_yo_yo(self):
        """
        Main loop of the yoyo algorithm
        """
        # loop until pruned or leader
        while (self.role != PRUNED and self.role != LEADER):
            # yo- phase, then -yo (oy) phase
            self.yo_phase()
            self.oy_phase()

            # pruning
            self.yo_yo_prune()

    # YO- PHASE _______________________________________________________________
    def yo_phase(self):
        """
        YO- phase of the YO-YO algorithm
        """
        # gather ids from in edges (and include my_id for sources)
        self.id_received = {None: self.my_id}
        for v in self.in_edges():
            self.recv_message(self.yoyo_recv_id_callback, self.queues[v])

        # send smaller id received (or my_id if node is source) on out edges
        self.min_id_recv = min(self.id_received.values())
        for v in self.out_edges():
            self.send_message(self.queues[v], [self.my_id, self.min_id_recv])

    # -YO PHASE _______________________________________________________________

    def oy_phase(self):
        """
        -YO phase of the YO-YO algorithm
        """
        self.yes_no_received = dict()
        self.edges_to_flip = []
        if self.role == SINK:
            # send yes to nodes who sent smallest id, no to others
            for v in self.in_edges():
                if self.id_received[v] == self.min_id_recv:
                    self.send_message(self.queues[v], [self.my_id, YES])
                else:
                    self.send_message(self.queues[v], [self.my_id, NO])
                    self.edges_to_flip += [v]

        elif self.role == INTERMEDIATE:
            # gather answers from all out edges
            for v in self.out_edges():
                self.recv_message(self.oy_oy_callback, self.queues[v])

            # if all votes are YES, forward YES, otherwise forward NO
            if all(self.yes_no_received.values() == YES):
                # send YES to those who sent smallest id, NO to others
                for v in self.in_edges():
                    if self.id_received[v] == self.min_id_recv:
                        self.send_message(self.queues[v], [self.my_id, YES])
                    else:
                        self.send_message(self.queues[v], [self.my_id, NO])
                        self.edges_to_flip += [v]
            else:
                for v in self.in_edges():
                    self.send_message(self.queues[v], [self.my_id, NO])
                    self.edges_to_flip += [v]

        else:  # self.role == SOURCE
            for v in self.out_edges():
                self.recv_message(self.oy_oy_callback, self.queues[v])

        self.flip_edges()
        self.get_role()

    # PRUNING _________________________________________________________________
    def yo_yo_prune(self):
        pass

    # YO-YO UTILS _____________________________________________________________

    def out_edges(self):
        return [v for v in self.edges if self.edges[v] == OUT]

    def in_edges(self):
        return [v for v in self.edges if self.edges[v] == IN]

    def flip_edges(self):
        self.edges = {
            v: self.edges[v] if v not in self.to_flip else 1-self.edges[v]
            for v in self.edges
        }

# _____________________________________________________________________________
# _______________________ CALLBACKS ___________________________________________

    def init_callback(self, ch, method_frame, properties, body):
        """
        Callback for consuming main launcher answer. Can reset my_id
        """
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        self.my_id = json.loads(body)
        self.channel.stop_consuming()

    def store_neighbors_callback(self, ch, method, properties, body):
        """
        Callback for consuming main launcher message. Stores neighbors' ids
        """
        self.channel.basic_ack(method.delivery_tag)
        self.neighbors_ids = json.loads(body)
        self.channel.stop_consuming()

    def yoyo_recv_id_callback(self, ch, method_frame, properties, body):
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        sender, packet = json.loads(body)
        self.id_received[sender] = packet
        self.channel.stop_consuming()

    def oy_oy_callback(self, ch, method_frame, properties, body):
        # ack
        self.channel.basic_ack(method_frame.delivery_tag)
        # process answer and stop consuming
        sender, packet = json.loads(body)
        if packet == NO:
            self.to_flip += [sender]
        self.yes_no_received[sender] = packet
        self.channel.stop_consuming()
