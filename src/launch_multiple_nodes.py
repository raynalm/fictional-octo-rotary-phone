import sys
import subprocess

DEFAULT_NB_NODES = 3


def main(argv):
    if len(argv) < 2:
        n = DEFAULT_NB_NODES
    else:
        n = int(argv[1])
    for i in range(n):
        subprocess.call(
            ["gnome-terminal", "-e", "python run_node.py"]
        )


if __name__ == "__main__":
    main(sys.argv)
