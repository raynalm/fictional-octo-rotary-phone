import heapq as hq

from lib.config import LEADER, WHITE, BLACK


colors = dict()


def make_ring(node):
    assert(node.role == LEADER)
    for n in node.graph:
        colors[n] = WHITE
    colors[node.my_id] = BLACK
    node.ring = make_ring_dfs(node, node.my_id)
    for i in range(len(node.ring)-1):
        print(shortest_path(node.graph, node.ring[i], node.ring[i+1]))
    print(shortest_path(node.graph, node.ring[-1], node.ring[0]))


def make_ring_dfs(node, u):
    result = [u]
    for v in node.graph[u]:
        if colors[v] == WHITE:
            colors[v] = BLACK
            result += make_ring_dfs(node, v)
    return result


def shortest_path(g, start, end):
    q = [(0, start, [start])]
    hq.heapify(q)
    while len(q) > 0:
        d, u, path = hq.heappop(q)
        for v in g[u]:
            if v == end:
                return path + [v]
            hq.heappush(q, (d+1, v, path + [v]))
