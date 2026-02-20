from collections import deque

# Reading input file
def read_input(file):

    with open(file, 'r') as f:
        input_lines = f.readlines()
    
    num_colours = None
    adj = {}

    for line in input_lines:
        line = line.strip()

        # Ignoring lines with comments
        if not line or line.startswith("#"):
            continue

        # Reading the line where the number of colours
        if line.lower().startswith("colours"):
            num_colours = int(line.split("=")[1].strip())
            continue
        
        # Reading the list of edges
        edges = line.split(",")
        if len(edges) == 2:
            u = edges[0].strip()
            v = edges[1].strip()
            if u not in adj:
                adj[u] = set()
            if v not in adj:
                adj[v] = set()
            adj[u].add(v)
            adj[v].add(u)

    vertices = set(adj.keys())
    return num_colours, vertices, adj

# Checking consistency of the colour assignment
def validate_colour(u, colour, coloured_vertices, adj):
    for v in adj[u]:
        if v in coloured_vertices and coloured_vertices[v] == colour:
            return False
    return True

# MRV heuristic for variable selection
def MRV(coloured_vertices, vertices, domain, adj):
    # Looking for an uncoloured vertex, k = canditate for colouring
    k = [u for u in vertices if u not in coloured_vertices]

    # Selecting the vertex with the minimum remaining values in its domain 
    # With a tie-breaker based on the number of adjacent vertices
    return min(k, key=lambda u: (len(domain[u]), -len(adj[u])))

# LCV heuristic for value ordering
def LCV(u, coloured_vertices, domain, adj):
    def count_constraints(colour):
        cnt = 0
        for k in adj[u]:
            if k not in coloured_vertices and colour in domain[k]:
                cnt += 1
        return cnt

    return sorted(domain[u], key=count_constraints)

# Revise function for AC3
def revise(domain, X, Y):
    revised = False
    for colour in list(domain[X]):
        if all(c == colour for c in domain[X]):
            domain[X].remove(colour)
            revised = True
    return revised

# CSP with AC3
def AC3(domain, adj, arcs=None):
    if arcs is None:
        dq = deque()
        for u in adj:
            for v in adj[u]:
                dq.append((u, v))
    else:
        dq = deque(arcs)


# Backtracking search
def search(vertices, adj, coloured_vertices, num_colours, domain):
    # All vertices are coloured
    if len(coloured_vertices) == len(vertices):
        return coloured_vertices

    # Looking for an uncoloured vertex, k = canditate for colouring
    k = MRV(coloured_vertices, vertices, domain, adj)
    
    for colour in LCV(k, coloured_vertices, domain, adj):
        if validate_colour(k, colour, coloured_vertices, adj):
            coloured_vertices[k] = colour
            result = search(vertices, adj, coloured_vertices, num_colours, domain)
            if result is not None:
                return result
            del coloured_vertices[k]

    return None


def main():
    num_colours, vertices, adj = read_input('./inputs/input1.txt')

    # print("Number of colours:", num_colours)
    # print("Number of vertices:", len(vertices))
    # print("Number of edges:", sum(len(neighbors) for neighbors in adj.values())//2)

    # Initializing the domain for each vertex
    domain = {v: set(range(1, num_colours + 1)) for v in vertices}
    result = search(vertices, adj, {}, num_colours, domain)

if __name__ == "__main__":
    main()

