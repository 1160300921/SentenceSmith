# triples2graphstring.py

import sys
import penman

def read_triples_from_input():
    triples = []
    for line in sys.stdin:
        line = line.strip()
        parts = line[1:-1].split(", ")
        if len(parts) == 3:
            s, p, o = parts
            # print("s, p, o", s, p, o)
            triples.append((s.strip("'"), p.strip("'"), o.strip("'")))
            # print("triples", (s.strip("'"), p.strip(), o.strip("'")))
    # print("triples")
    # print(triples)
    return triples

def triples_to_graph_string(triples):
    graph = penman.Graph(triples)
    return penman.encode(graph)

if __name__ == "__main__":
    triples = read_triples_from_input()
    graph_string = triples_to_graph_string(triples)
    print(graph_string)
