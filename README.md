# The real fictional-octo-rotary-phone
## Environment
+ To run the project, the following packages/programs need to be installed :
  + Rabbitmq-server : `http://www.rabbitmq.com/download.html`
  + python3 : `https://www.python.org/downloads/`
  + python-pip3 : `https://docs.python.org/3/installing/index.html`. If you already have anaconda on your machine, you can use it to install the required python packages.
  + pika : `https://pypi.python.org/pypi/pika`
+ The easiest way to have those packages installed and ready to run on Ubuntu :
  + `sudo apt-get update`
  + `sudo apt-get install rabbitmq-server`
  + `sudo apt-get install python-pip`
  + `[sudo] pip install pika`
  + `[sudo] pip install graphviz`

## Usage
+ All config variables are in /src/lib/config.py
+ First, the main launcher needs to be launched.
  + To launch it, `python main.py [nb_nodes] [nb_edges]` in /src/
  + This program will generate a random connected graph. If no arguments are provided the default values will be given.
  + It will then wait for the right amount of PikaNodes to be launched.
  + There is a variable named 'DEFAULT_SPARSENESS' in the file 'config.py'. It sets the sparseness of the random graph. If its value is very low, the graph will be a tree. If it is 1, the graph will be fully connected.
+ To launch PikaNodes, you have two possibilities:
  + Open a lot of terminals, and launch `python run_node.py` in each of them
  + Or, if you are on linux and have gnome-terminal installed, you can launch the script 'python launch_multiple_nodes.py nb_nodes`

+ Then the main launcher will quit, and the nodes will be on their own.
  + They will first elect a leader using the Yo-Yo algorithm
  + Once a leader is elected, it gathers all the nodes informations using the shout protocol
  + Then it creates a ring, and 'broadcast' it to the other nodes.

+ At this point, the ring is implemented, and nodes can communicate. Commands are :
  + `/h` : help, display the possible commands.
  + `/l` : list all nodes ids on the network.
  + `/s 45 hello!` : sends the message 'hello!' to the node 45.
  + `/ask_file 45 a_file.txt` : requests node 45 to send the file 'a_file.txt'.
  + All those communications are handled on the ring, always in the same direction (but both directions have been implemented)
  + `/q` quits the program and closes the connections and channels. One can also exit the program with a simple Ctrl+C

+ The interface is very basic.

## Algorithms used
+ The purpose of the algorithms used is to prevent having any algorithm running in O(n^3). The multishout protocol (or wave) to perform a universal election runs in O(n^3), which is why the young 'Yo-Yo' algorithm was selected. All informations about it can be found in the document 'elections_in_dist_sys.pdf'. It is quite elegant, and has the advantage to run in O(m.log n), with n the number of nodes and m the number of edges. Its implementation is mainly in the file 'yoyo.py', except for a couple of callbacks which are in pika_node.py

+ Once a leader is elected, the shout protocol (or wave) is used for the leader to gather all required information about the networkk's graph. Since it is a shout with a single initiator, it runs in O(n^2). The implementation is in 'shout.py', and in 'pika_node.py'. A description of the shout protocol can be found in the document 'shout.pdf', along with reasons not to choose the multishout protocol.

+ To build a ring, the simplest method we thought of was retained. We build a spanning tree of the graph, and then the ring is the DFS path of this tree, where each node is represented only once. Then to calculate routes, the Dijkstra's algorithm was used. These two algorithm are in 'make_ring.py'. Once the ring is built, the ring's information is spread using the shout protocol again. Upon creating the ring, the leader draws the graph with its real edges in blue, and with the ring edges in red.

## What we like and what we would have liked to do
+ Nice : using elegant and efficient algorithms
+ Not nice : very poor interface, and clumsy main loop.
+ The whole structure is not fault tolerant, since it is designed to be a random graph network (in a star network, if the center node fails, then all fails). But it would have been nice anyway to do more in this direction, especially with more constraints on the graph (like a minimum degree of2 for each node)
+ A new version was on its way, where all communication was ciphered from end to end, but it could not be finished on time, so we provide the non ciphered version.

## Other
+ A small utility is included, to delete all rabbitmq queues when the program crashed. It was a very convenient script to run and purge the queues. It is located in /utils/, and can be run in this way : `sudo rabbitmqctl list_queues | python del_q.py` (rabbitmqctl needs to be installed though)