#!/usr/bin/env python3

import sys
import pika
import json
import random

from lib.config  import *
from lib.graph_gen   import *


# MAIN LAUNCHER CLASS _________________________________________________________

class MainLauncher:
    def __init__(self, n, s):
        """
        Args:
            n: int, the number of nodes in the network
            s: int, the number of edges in the network
        """
        self.__nb_nodes = n
        self.__adjacencies = gen_graph(n, s)
        self.__nodes_id = []


    # LAUNCH NETWORK __________________________________________________________
    def launch_network(self):
        """
        Launches the network
        """
        # initialize the connection
        self.init_connection()

        # start a beautiful narrative with the user
        print("you can now run all nodes in new terminals by typing: "
              "./python run_node.\n You need to launch %s nodes in order "
              "to start the network." % self.__nb_nodes)

        print("Starting to collect nodes ids ....")
        # collect the id from all nodes in the network
        self.collect_nodes_id()
        print("done")

        print("Sending to each node information about their neighbors ..")
        # send to each node the list of its neighbors
        self.send_neighbors()
        # job done, exiting
        self.exit_program()


    # INIT CONNECTION _________________________________________________________
    def init_connection(self):
        """
        Initializes Rabbitmq connection and creates a channel to receive the ids
        """
         # init pika connection and channel
        self.__connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.__channel = self.__connection.channel()
        self.__channel.queue_declare(INIT_QUEUE_NAME)


    # COLLECT NODES ID ________________________________________________________
    def collect_nodes_id(self):
        """
        Collects the identifiers from all nodes on the network
        """
        self.__channel.basic_consume(
            self.collect_nodes_id_callback,
            queue = INIT_QUEUE_NAME,
            no_ack = True
        )
        self.__channel.start_consuming()


    def collect_nodes_id_callback(self, ch, method_frame, header_frame, body):
        """
        Callback : collect one identifier and checks if it is unique
        """
        new_node_id = json.loads(body)
        if new_node_id in self.__nodes_id:
            new_node_id = self.choose_new_id()
        self.send_back_id(new_node_id)
        self.__nodes_id += [new_node_id]

        if len(self.__nodes_id) == self.__nb_nodes:
            self.__channel.stop_consuming()
        print_debug("Nodes so far : ")
        print_debug("%s" % self.__nodes_id)

    def send_back_id(self, node_id):
        send_queue = INIT_QUEUE_NAME+str(node_id)
        self.__channel.queue_declare(send_queue)
        msg = json.dumps(node_id)
        self.__channel.basic_publish(
            exchange = '',
            routing_key = send_queue,
            body = msg
        )

    def choose_new_id(self):
        """
        Generates a random number which is not in self.__nodes_id list
        already
        """
        rng = random.SystemRandom()
        new_id = rng.randrange(RANDOM_START, RANDOM_END)
        while new_id in self.__nodes_id:
            new_id = rng.randrange(RANDOM_START, RANDOM_END)
        return new_id

    # SEND NEIGHBORS __________________________________________________________
    def send_neighbors(self):
        for i, v in enumerate(self.__nodes_id):
            # get the list of neighbors' ids and json it
            neighbors = [self.__nodes_id[j] for j in self.__adjacencies[i]]
            msg = json.dumps(neighbors)
            # create a dedicated queue
            neighbors_queue = INIT_QUEUE_NAME+str(v)
            self.__channel.queue_declare(neighbors_queue)
            # send it all
            self.__channel.basic_publish(
                exchange = '',
                routing_key = neighbors_queue,
                body = msg
            )


    # EXIT PROGRAM ____________________________________________________________
    def exit_program(self):
        """
        Close the connection and exits
        """
        print("Exiting")
        self.__connection.close()
        sys.exit()



# MAIN ________________________________________________________________________

if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MATRIX_SIZE
    s = sys.argv[2] if len(sys.argv) > 2 else 0
    launcher = MainLauncher(n, s)
    launcher.launch_network()
