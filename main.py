# Reading input file

def read_input(file):

    with open(file, 'r') as f:
        input_lines = f.readlines()
    
    num_colors = None
    adj = {}

    for line in input_lines:
        line = line.strip()

        # Ignoring lines with comments
        if not line or line.startswith("#"):
            continue

        # Reading the line where the number of colors
        if line.lower().startswith("colors"):
            num_colors = int(line.split("=")[1].strip())
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
    return num_colors, vertices, adj


def main():
    num_colors, vertices, adj = read_input('./inputs/input1.txt')

    print("Number of colors:", num_colors)
    print("Number of vertices:", len(vertices))
    print("Number of edges:", sum(len(neighbors) for neighbors in adj.values())//2)

if __name__ == "__main__":
    main()

