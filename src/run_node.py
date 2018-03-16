import sys
from lib.node import *
from random   import SystemRandom

def main(args):
    # first, you choose a random number
    # and communicate it to the server, it will be the node id
    my_id = SystemRandom(RANDOM_START, RANDOM_END)
    Node node = Node(my_id)
    node.launch



if __name__ == "__main__":
    main(sys.argv)
