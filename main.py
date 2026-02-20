from collections import deque
import time

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
        if line.lower().startswith("colors") or line.lower().startswith("colours"):
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

# Removing inconsistent values for AC3
def remove(domain, X, Y):
    removed = False
    for colour in list(domain[X]):
        if all(c == colour for c in domain[Y]):
            domain[X].remove(colour)
            removed = True
    return removed

def remove(domain, X, Y):
    removed = False
    for colour in list(domain[X]):
        if not any(c != colour for c in domain[Y]):
            domain[X].remove(colour)
            removed = True
    return removed

# CSP with AC3
def AC3(domain, adj, arcs=None):
    # Deque with all arcs in the graph
    if arcs is None:
        dq = deque()
        for u in adj:
            for v in adj[u]:
                dq.append((u, v))
    else:
        dq = deque(arcs)

    while dq:
        (X, Y) = dq.popleft()

        if remove(domain, X, Y):
            if not domain[X]:
                return False
            for Z in adj[X]:
                if Z != Y:
                    dq.append((Z, X))
    return True

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

            # Saving the domain state for backtracking
            domains = {v: set(domain[v]) for v in vertices}
            # Changing the domain of k to the assigned colour
            domain[k] = {colour}
            # Check consistency with AC3
            arcs = [(neighbor, k) for neighbor in adj[k] if neighbor not in coloured_vertices]

            if AC3(domain, adj, arcs=arcs):
                result = search(vertices, adj, coloured_vertices, num_colours, domain)
                if result is not None:
                    return result

            # Backtracking
            domain.update(domains)
            del coloured_vertices[k]

    return None

def validate_solution(result, adj, num_colours, vertices):
    # Check all vertices are coloured
    if len(result) != len(vertices):
        return False

    # Check adjacency constraints
    for u in adj:
        for v in adj[u]:
            if result[u] == result[v]:
                return False

    # Check colour range
    for u, colour in result.items():
        if not (1 <= colour <= num_colours):
            return False

    return True


# Code runs here
def main(filename):

    start = time.time()
    print("(1)")
    print("Reading input...")
    num_colours, vertices, adj = read_input('./inputs/{}.txt'.format(filename))
    end = time.time()

    print("Input succesfully processed in {:.2f} seconds. Graph details:".format(end - start))
    print("-----------------------")
    print("Number of colours:", num_colours)
    print("Number of vertices:", len(vertices))
    print("Number of edges:", sum(len(neighbors) for neighbors in adj.values())//2)
    print("-----------------------\n")

    # Initializing the domain for each vertex
    print("(2)")
    print("Initializing domains...")
    start = time.time()
    domain = {v: set(range(1, num_colours + 1)) for v in vertices}
    end = time.time()
    print("Domains initialized in {:.2f} seconds.".format(end - start))

    print("\n(3)")
    print("Running AC3...")
    start = time.time()
    if not AC3(domain, adj):
        print("No solution found.")
        return
    end = time.time()
    print("AC3 completed in {:.2f} seconds.".format(end - start))

    print("\n(4)")
    print("Searching for a solution...")
    start = time.time()
    result = search(vertices, adj, {}, num_colours, domain)
    end = time.time()
    print("Search completed in {:.2f} seconds.".format(end - start))
    print("-----------------------")
    if result is not None:
        if validate_solution(result, adj, num_colours, vertices):
            print("Solution found:")
            if(len(vertices) <= 20):
                for vertex, colour in result.items():
                    print(f"Vertex {vertex}: Colour {colour}")
            else :
                print("Too many vertices to display. Showing first 20:")
                for i, (vertex, colour) in enumerate(result.items()):
                    if i >= 20:
                        break
                    print(f"Vertex {vertex}: Colour {colour}")
        else:
            print("INVALID solution found.")
    else:
        print("No solution found.")
    print("-----------------------")


if __name__ == "__main__":
    while(True):
        input_fine_name = input("Enter the input file name: ")
        if(input_fine_name.lower() == ""):
            print("Program terminated.")
            break
        main(input_fine_name)
