import sys
import random

from lib.config import RANDOM_START, RANDOM_END
from lib.pika_node import PikaNode


def run_pika_node(my_id):
    """
    Instanciates a PikaNode and launches it
    Args:
        my_id: int, the identifier of the node.
               if my_id is None, then a random number is picked
    """
    if my_id is None:
        rng = random.SystemRandom()
        my_id = rng.randrange(RANDOM_START, RANDOM_END)
    node = PikaNode(my_id)
    node.launch()


if __name__ == "__main__":
    my_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_pika_node(my_id)
