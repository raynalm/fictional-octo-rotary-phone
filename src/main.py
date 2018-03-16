#!/usr/bin/env python

import sys
import pika
import json
from lib.config  import *
from lib.graph   import *

# MAIN LAUNCHER ________________________________________________________________
class MainLauncher:
    def __init__(self, n = DEFAULT_MATRIX_SIZE, s = 0):
        """
        Args:
            n: int, the number of nodes in the network
            s: int, the number of edges in the network
        """
        self.nb_nodes = n
        self.adj_matrix = adj_matrix(gen_graph(n, s))
        self.nodes_id = []


    def init_callback(ch, method, properties, body):
        """
        Called upon first com from node to main launcher.

        """
        new_node_id = json.loads(body)
        if new_node_id in self.nodes_id:
            # TODO -> create protocol for f***ers who play choosing same random
            print("2 f***ers are playing with randomness, I'm on strike. Bye")
            sys.exit()
        self.nodes_id += [new_node_id]
        if len(nodes_id) == self.nb_nodes:
            channel.stop_consuming()


    def launch_network(self):
        # init pika connection and channel
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        channel = connection.channel()
        # start a beautiful narrative with the user
        print("you can now run all nodes in new terminals by typing: "
              "./python run_node.\n You need to launch %s nodes in order "
              "to start.")

        # collect the id from all nodes in the network
        channel.queue_declare(queue = INIT_QUEUE_NAME)
        channel.basic_consume(
            init_callback,
            queue = INIT_QUEUE_NAME,
            no_ack = True         # TODO -> make sure no_ack is the good choice
        )
        channel.start_consuming()

        # now associate each id to a number
        # and communicate each node their neighbors' id
        for i, node_id in enumerate(self.nodes_id):
            queue_name = INIT_QUEUE_NAME + str(node_id)
            channel.queue_declare(queue = queue_name)
            msg = json.dumps(self.adj_matrix[i])
            channel.basic_publish(
                exchange = '',
                routing_key = queue_name,
                body = msg
            )
        print("All nodes have been communicated their neighbors' ids."
              "\nExiting")
        connection.close()
        sys.exit()
