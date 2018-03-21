#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pika
import json
import random

from lib.config import INIT_QUEUE_NAME, RANDOM_START, RANDOM_END
from lib.config import DEFAULT_MATRIX_SIZE
from lib.graph_gen import gen_graph


# _________________________________________________________________________
# _______________________ MAIN LAUNCHER CLASS _____________________________
# _________________________________________________________________________

class MainLauncher:
    def __init__(self, n, s):
        """
        Args:
            n: int, the number of nodes in the network
            s: int, the number of edges in the network
        """
        self.nb_nodes = n
        self.adjacencies = gen_graph(n, s)
        self.nodes_id = []

# _________________________________________________________________________
# _______________________ LAUNCH NETWORK___________________________________

    def launch_network(self):
        """
        Launches the network
        """
        # initialize the connection
        self.init_connection()

        # start a beautiful narrative with the user
        print("you can now run all nodes in new terminals by typing: "
              "./python run_node.\n You need to launch %s nodes in order "
              "to start the network." % self.nb_nodes)

        print("Starting to collect nodes ids ....")
        # collect the id from all nodes in the network
        self.collect_nodes_id()
        print("done")

        print("Sending to each node information about their neighbors ..")
        # send to each node the list of its neighbors
        self.send_neighbors()
        # job done, exiting
        self.exit_program()

# _________________________________________________________________________
# _______________________ INIT CONNECTION _________________________________

    def init_connection(self):
        """
        Initializes Rabbitmq connection and creates a channel to receives
        the ids from the PikaNodes
        """
        # init pika connection and channel
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        self.channel.queue_delete(queue=INIT_QUEUE_NAME)
        self.channel.queue_declare(queue=INIT_QUEUE_NAME)
        self.channel.confirm_delivery()

# _________________________________________________________________________
# _______________________ SEND MSG ________________________________________

    def send_msg(self, msg, queue_name=INIT_QUEUE_NAME):
        """
        Sends a message on a queue
        Args:
            msg: json str, the message to send
            queue_name: str, the queue to send it on
        """
        if not self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=msg
        ):                      # unhappy smiley because it's a failure case
            self.handle_msg_not_send(msg, queue_name)

    def handle_msg_not_send(self, msg, queue_name):
        print("Could not publish the message : <%s> "
              "on the queue : %s" % (msg, queue_name))
        self.exit_program()

# _________________________________________________________________________
# _______________________ COLLECT PIKA_NODES IDS __________________________

    def collect_nodes_id(self):
        """
        Collects the identifiers from all nodes on the network
        """
        for method_f, pr, body in self.channel.consume(INIT_QUEUE_NAME):
            # ack
            self.channel.basic_ack(method_f.delivery_tag)

            # reply
            node_id = json.loads(body)
            send_queue = INIT_QUEUE_NAME+str(node_id)
            if node_id in self.nodes_id:
                node_id = self.choose_new_id()
            self.channel.queue_declare(send_queue)
            self.send_msg(json.dumps(node_id), send_queue)

            # store
            self.nodes_id += [node_id]
            if len(self.nodes_id) == self.nb_nodes:
                break

    def choose_new_id(self):
        """
        Generates a random number which is not in self.nodes_id list
        already
        """
        rng = random.SystemRandom()
        new_id = rng.randrange(RANDOM_START, RANDOM_END)
        while new_id in self.nodes_id:
            new_id = rng.randrange(RANDOM_START, RANDOM_END)
        return new_id

# _________________________________________________________________________
# _______________________ SEND NEIGHBORS IDS ______________________________

    def send_neighbors(self):
        """
        Sends to each PikaNode in the network the list of its neighbors' id
        """
        for i, v in enumerate(self.nodes_id):
            # get the list of neighbors' ids
            neighbors = [self.nodes_id[j] for j in self.adjacencies[i]]

            # create a dedicated queue and send the list
            send_queue = INIT_QUEUE_NAME+str(v)
            self.channel.queue_declare(INIT_QUEUE_NAME+str(v))
            self.send_msg(json.dumps(neighbors), send_queue)

# _________________________________________________________________________
# _______________________ EXIT PROGRAM ____________________________________

    def exit_program(self):
        """
        Close the connection and exits
        """
        print("Exiting")
        self.connection.close()
        sys.exit()


# _________________________________________________________________________
# _______________________ MAIN ____________________________________________

if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MATRIX_SIZE
    s = sys.argv[2] if len(sys.argv) > 2 else 0
    launcher = MainLauncher(n, s)
    launcher.launch_network()
