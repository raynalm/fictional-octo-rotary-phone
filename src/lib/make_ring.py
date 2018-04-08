import heapq as hq

from lib.config import LEADER, WHITE, BLACK


color = dict()


def make_ring(node):
    """
    main method for leader node to create a ring from a graph
    Creates the virtual ring and initiates a broadcast of the ring
    for other nodes to get it
    """
    assert(node.role == LEADER)

    # build a virtual ring
    for n in node.graph:
        color[n] = WHITE
    color[node.my_id] = BLACK
    ring = make_ring_dfs(node, node.my_id)

    # compute routes for the virtual ring
    ring = [
        get_path(node.graph, ring[i], ring[i+1]) for i in range(len(ring)-1)
    ] + [get_path(node.graph, ring[-1], ring[0])]

    print(ring)
    # get own right and left routes
    node.route_right = next(l for l in ring if l[0] == node.my_id)[1:]
    node.route_left = [l[::-1] for l in ring if l[-1] == node.my_id][0][1:]

    # get list of all nodes in the network
    # and split ring in left side and right side
    node.all_nodes = [l[0] for l in ring]
    i = node.all_nodes.index(node.my_id)
    node.all_nodes = node.all_nodes[i:] + node.all_nodes[:i]
    node.nodes_right = node.all_nodes[:len(node.all_nodes)//2]
    node.nodes_left = node.all_nodes[len(node.all_nodes)//2:]

    # spread the ring informations to all other nodes on the network
    node.ring_received = True
    node.nb_broadcast_msg_recv = 0
    for v in node.neighbors_ids:
        node.send_msg(ring, v)


def make_ring_dfs(node, u):
    """
    recursively builds a ring from a graph using the spanning tree.
    DFS approach with vertex coloring to keep it simple
    """
    result = [u]
    for v in node.graph[u]:                    # for all neighbors
        if color[v] == WHITE:                  # if neighbor is white
            color[v] = BLACK                   # paint it black
            result += make_ring_dfs(node, v)   # and call recursively on it
    return result


def get_path(edges, start, end):
    """
    Returns the shortest path between two nodes using Dijkstra's algorithm
    """
    q = [(0, start, [start])]
    hq.heapify(q)
    while len(q) > 0:
        d, u, path = hq.heappop(q)
        for v in edges[u]:
            if v == end:
                return path + [v]
            hq.heappush(q, (d+1, v, path + [v]))
