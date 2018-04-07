import heapq as hq

from lib.config import LEADER, WHITE, BLACK, RIGHT, LEFT


colors = dict()


def make_ring(node):
    """
    main method for leader node to create a ring from a graph
    """
    assert(node.role == LEADER)
    for n in node.graph:
        colors[n] = WHITE
    colors[node.my_id] = BLACK
    ring = make_ring_dfs(node, node.my_id)
    node.ring = [
        shortest_path(node.graph, ring[i], ring[i+1]) for i in range(len(ring)-1) # noqa
    ] + [shortest_path(node.graph, ring[-1], ring[0])]
    # print(node.ring)
    packet = make_ring_packet(node)
    for v in packet:
        print(packet[v])


def make_ring_dfs(node, u):
    """
    recursively builds a ring from a graph using the spanning tree.
    DFS approach with vertex coloring to make it simple
    """
    result = [u]
    for v in node.graph[u]:
        if colors[v] == WHITE:
            colors[v] = BLACK
            result += make_ring_dfs(node, v)
    return result


def shortest_path(g, start, end):
    """
    Returns the shortest path between two nodes using Dijkstra's algorithm
    """
    q = [(0, start, [start])]
    hq.heapify(q)
    while len(q) > 0:
        d, u, path = hq.heappop(q)
        for v in g[u]:
            if v == end:
                return path + [v]
            hq.heappush(q, (d+1, v, path + [v]))


def make_ring_packet(node):
    """
    Prepares a nice dictionary to broadcast so all nodes in the
    network can have the information they require about the virtual ring
    and routing.
    """
    packet = {v: dict() for v in node.graph}
    for v in node.graph:
        route_right = [l for l in node.ring if l[0] == v][0]
        route_left = [l[::-1] for l in node.ring if l[-1] == v][0]
        packet[v][RIGHT] = route_right
        packet[v][LEFT] = route_left
    return packet
