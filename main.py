from collections import deque
import time
import random

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

# Simple variable selection (no heuristic) - picks first uncolored vertex
def simple_select(coloured_vertices, vertices, domain, adj):
    for u in vertices:
        if u not in coloured_vertices:
            return u

# LCV heuristic for value ordering
def LCV(u, coloured_vertices, domain, adj):
    def count_constraints(colour):
        cnt = 0
        for k in adj[u]:
            if k not in coloured_vertices and colour in domain[k]:
                cnt += 1
        return cnt

    return sorted(domain[u], key=count_constraints)

# Simple value ordering (no heuristic) - returns domain as is
def simple_order(u, coloured_vertices, domain, adj):
    return list(domain[u])

# Removing inconsistent values for AC3
def remove(domain, X, Y):
    removed = False
    for colour in list(domain[X]):
        if all(c == colour for c in domain[Y]):
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

# Backtracking search - configurable heuristics and AC3
def search(vertices, adj, coloured_vertices, num_colours, domain,
           use_mrv=True, use_lcv=True, use_ac3=True):
    # All vertices are coloured
    if len(coloured_vertices) == len(vertices):
        return coloured_vertices

    # Looking for an uncoloured vertex, k = canditate for colouring
    if use_mrv:
        k = MRV(coloured_vertices, vertices, domain, adj)
    else:
        k = simple_select(coloured_vertices, vertices, domain, adj)

    # Ordering colours to try
    if use_lcv:
        colours = LCV(k, coloured_vertices, domain, adj)
    else:
        colours = simple_order(k, coloured_vertices, domain, adj)

    for colour in colours:
        if validate_colour(k, colour, coloured_vertices, adj):
            coloured_vertices[k] = colour

            # Saving the domain state for backtracking
            domains = {v: set(domain[v]) for v in vertices}
            # Changing the domain of k to the assigned colour
            domain[k] = {colour}

            proceed = True
            if use_ac3:
                # Check consistency with AC3
                arcs = [(neighbor, k) for neighbor in adj[k] if neighbor not in coloured_vertices]
                proceed = AC3(domain, adj, arcs=arcs)

            if proceed:
                result = search(vertices, adj, coloured_vertices, num_colours, domain,
                                use_mrv, use_lcv, use_ac3)
                if result is not None:
                    return result

            # Backtracking
            domain.update(domains)
            del coloured_vertices[k]

    return None

def validate_solution(result, adj, num_colours, vertices):
    # Check if all vertices are coloured
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

# Randomly pre-assigning some vertices to colours to reduce the search space
def random_preassign(domain, vertices, num_colours, adj):
    # Pick between 1 and 1/3 of vertices to pre-assign
    num_to_assign = random.randint(1, max(1, len(vertices) // 3))
    chosen = random.sample(list(vertices), num_to_assign)

    print(f"\nPre-assigning {num_to_assign} vertex/vertices randomly:")
    for v in chosen:
        colour = random.randint(1, num_colours)
        domain[v] = {colour}
        print(f"  Vertex {v} pre-assigned to colour {colour}")
    print()

    return domain

# Running a single variant of the search with given configuration
def run_variant(label, vertices, adj, num_colours, base_domain,
                use_mrv, use_lcv, use_ac3):
    print(f"\n{'='*50}")
    print(f"Running: {label}")
    print(f"{'='*50}")

    # Deep copy domain so each run is independent
    domain = {v: set(base_domain[v]) for v in base_domain}

    if use_ac3:
        # Check if there's a need to run AC3 before search
        total_domain_size = sum(len(domain[v]) for v in vertices)
        full_domain_size = num_colours * len(vertices)

        if total_domain_size < full_domain_size:
            print("Running initial AC3...")
            print("Initial domain sizes:")
            for v in vertices: print(f"  Vertex {v}: {len(domain[v])} possible colours")

            if not AC3(domain, adj):
                print("AC3 detected no solution exists.")
                return None

            print("Domain sizes after AC3:")
            for v in vertices: print(f"  Vertex {v}: {len(domain[v])} possible colours")

            # Checking if AC3 reduced any domains
            reduced = [v for v in vertices if len(domain[v]) < len(base_domain[v])]
            if reduced:
                print(f"AC3 reduced domains for vertices: {reduced}")
            else:
                print("AC3 made no reductions before search.")

    print("Searching for a solution...")
    start = time.time()
    result = search(vertices, adj, {}, num_colours, domain,
                    use_mrv=use_mrv, use_lcv=use_lcv, use_ac3=use_ac3)
    end = time.time()

    elapsed = end - start
    print("Search completed in {:.4f} seconds.".format(elapsed))
    print("-----------------------")
    if result is not None:
        if validate_solution(result, adj, num_colours, vertices):
            print("Solution found:")
            if len(vertices) <= 20:
                for vertex, colour in result.items():
                    print(f"  Vertex {vertex}: Colour {colour}")
            else:
                print("Too many vertices to display. Showing first 20:")
                for i, (vertex, colour) in enumerate(result.items()):
                    if i >= 20:
                        break
                    print(f"  Vertex {vertex}: Colour {colour}")
        else:
            print("INVALID solution found.")
    else:
        print("No solution found.")
    print("-----------------------")
    return elapsed

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
    base_domain = {v: set(range(1, num_colours + 1)) for v in vertices}

    print("Choose domain option:")
    print("  1 - Keep full domains for all vertices")
    print("  2 - Random pre-assignments")
    mode = input("Enter 1 or 2: ").strip()

    if mode == "2":
        base_domain = random_preassign(base_domain, vertices, num_colours, adj)

    end = time.time()
    print("Domains initialized in {:.2f} seconds.".format(end - start))

    # Define all variants to run
    variants = [
        ("MRV + LCV + AC3",      True,  True,  True),
        ("MRV + LCV, no AC3",    True,  True,  False),
        ("No heuristics + AC3",  False, False, True),
        ("No heuristics, no AC3",False, False, False),
    ]

    times = {}
    for label, use_mrv, use_lcv, use_ac3 in variants:
        t = run_variant(label, vertices, adj, num_colours, base_domain,
                        use_mrv, use_lcv, use_ac3)
        times[label] = t

    # Printing summary of execution times
    print(f"\n{'='*50}")
    print("SUMMARY - Execution Times")
    print(f"{'='*50}")
    for label, t in times.items():
        if t is not None:
            print(f"  {label:<25} {t:.4f} seconds")
        else:
            print(f"  {label:<25} No solution / AC3 failed early")


if __name__ == "__main__":
    while True:
        input_fine_name = input("Enter the input file name: ")
        if input_fine_name.lower() == "":
            print("Program terminated.")
            break
        try:
            main(input_fine_name)
        except FileNotFoundError:
            print(f"File not found. Please try again.")