from lib.config  import *
from random import choice, randrange

def gen_graph(n, s = 0):
    """
    Builds a (somehow) random graph with n vertices and s edges.
    Args:
        n: int, the numbre of vertices
        s: int, the number of edges.
            If s is not specified, the default sparseness will be applied
    Returns:
        A dictionary {u: {v_1, ..., v_i}} representing the graph's edges
    """
    if s == 0:        # get the default sparseness if need be
        s = min(n-1, DEFAULT_SPARSENESS)
    print("n %s s %s" % (n, s))
    edges = {v: set() for v in range(n)}
    print(edges)
    # first we build the graph's spanning tree
    to_connect = {v for v in edges}
    print(to_connect)
    connected = set()
    v = choice(tuple(to_connect))
    to_connect.remove(v)
    connected.add(v)

    while to_connect: #is not empty
        u = choice(tuple(to_connect))
        v = choice(tuple(connected))
        edges[u].add(v)
        edges[v].add(u)
        to_connect.remove(u)
        connected.add(u)

    # now we need to add s-n+1 edges
    to_add = s-n+1
    while to_add > 0:
        #print(to_add)
        u, v = randrange(n), randrange(n)
        if u != v and v not in edges[u]:
            edges[u].add(v)
            edges[v].add(u)
            to_add -= 1

    return edges

def adj_matrix(edges):
    """
    Transforms a dictionary representation in an adjacency matrix
    Args:
        edges: dict, the edges
    Returns:
        m, the adjacency matrix
    """
    n = len(edges)
    return [[1 if j in edges[1] else 0 for j in range(n)] for i in range(n)]
