#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import graphviz as gv

from random import choice, randrange
from lib.config import DEFAULT_SPARSENESS


def gen_graph(n, s):
    """
    Builds a (somehow) random graph with n vertices and s edges.
    Args:
        n: int, the numbre of vertices
        s: int, the number of edges.
            If s is not specified, the default sparseness will be applied
    Returns:
        A dictionary {u: {v_1, ..., v_i}} representing the graph's edges
    """
    # get the number of edges
    if s == 0:        # get the default sparseness if need be
        s = int(DEFAULT_SPARSENESS*n*(n-1)/2)
    else:             # get a reasonnable number of edges
        s = min(max(n-1, s), n*(n-1))
    print("Generating a random connected graph with"
          " %s vertices and %s edges", (n, s))
    edges = {v: set() for v in range(n)}
    # first we build the graph's spanning tree
    to_connect = {v for v in edges}
    connected = set()
    v = choice(tuple(to_connect))
    to_connect.remove(v)
    connected.add(v)

    while to_connect:   # is not empty
        u = choice(tuple(to_connect))
        v = choice(tuple(connected))
        edges[u].add(v)
        edges[v].add(u)
        to_connect.remove(u)
        connected.add(u)

    # now we need to add s-n+1 edges
    to_add = s-n+1
    while to_add > 0:
        u, v = randrange(n), randrange(n)
        if u != v and v not in edges[u]:
            edges[u].add(v)
            edges[v].add(u)
            to_add -= 1
    # to_graphviz(edges)
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


def to_graphviz(edges):
    """
    Draws a representation of the input graph using graphviz
    Args:
        m, a dictionary representing an unweighted undirected graph
    Return nothing
    """
    gg = gv.Graph(format="png")
    for u in edges:
        gg.node("%s" % u)

    for u in edges:
        for v in edges[u]:
            if u < v:
                gg.edge("%s" % u, "%s" % v)
    gg.render("graph", view=True)
