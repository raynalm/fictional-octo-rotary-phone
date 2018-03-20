import sys
from lib.node import *
import random

def main(args):
    rng = random.SystemRandom()
    if len(args) == 1:
        my_id = rng.randrange(RANDOM_START, RANDOM_END)
    else:
        my_id = int(args[1])
    node = Node(my_id)
    node.launch()



if __name__ == "__main__":
    main(sys.argv)
