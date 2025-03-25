import sys
import ast
import nltk
import random
from nltk.corpus import wordnet as wn
import re

############################################ WordNet Utilities ############################################
def get_hypernyms(word):
    hypernyms = set()
    if '-' in word:
        word_prefix = word.split('-')[0]
    else:
        word_prefix = word
    
    best_synsets = []
    for pos in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
        synsets = wn.synsets(word_prefix, pos=pos)
        if len(synsets) > len(best_synsets):
            best_synsets = synsets
    
    for syn in best_synsets:
        if syn.hypernyms():  # Check if hypernyms exist
            for hyper in syn.hypernyms():
                hypernyms.update(hyper.lemma_names())
        else:  # If no hypernyms found, use synonyms as fallback
            hypernyms.update(syn.lemma_names())
    
    return list(hypernyms)

def get_hyponyms(word):
    hyponyms = set()
    if '-' in word:
        word_prefix = word.split('-')[0]
    else:
        word_prefix = word
    
    best_synsets = []
    for pos in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
        synsets = wn.synsets(word_prefix, pos=pos)
        if len(synsets) > len(best_synsets):
            best_synsets = synsets
    
    for syn in best_synsets:
        for hypo in syn.hyponyms():
            hyponyms.update(hypo.lemma_names())
    
    return list(hyponyms)

def get_antonyms(word):
    antonyms = set()
    if '-' in word:
        word_prefix = word.split('-')[0]
    else:
        word_prefix = word
    
    best_synsets = []
    for pos in [wn.NOUN, wn.VERB, wn.ADJ, wn.ADV]:
        synsets = wn.synsets(word_prefix, pos=pos)
        if len(synsets) > len(best_synsets):
            best_synsets = synsets
    
    for syn in best_synsets:
        for lemma in syn.lemmas():
            for ant in lemma.antonyms():
                antonyms.add(ant.name())
    
    return list(antonyms)

def read_triples(file):
    triples = []
    for line in file:
        triple = ast.literal_eval(line.strip())
        triples.append(triple)
    return triples

############################################ Random Swap Operation ############################################
def find_leaf_nodes_and_edges(triples):
    from collections import defaultdict

    # Build adjacency list for the graph
    graph = defaultdict(list)
    for s, r, o in triples:
        if r != ':instance':
            graph[s].append((r, o))
            graph[o].append((r, s))

    # Identify leaf nodes and their connecting edges
    leaf_nodes_edges = {(node, graph[node][0]) for node in graph if len(graph[node]) == 1}

    return leaf_nodes_edges

def random_swap(triples):
    from copy import deepcopy

    # Find leaf nodes and their edges
    leaf_nodes_edges = list(find_leaf_nodes_and_edges(triples))
    
    if len(leaf_nodes_edges) < 2:
        return triples

    # Randomly select two leaf nodes and their edges
    (leaf_node1, edge1), (leaf_node2, edge2) = random.sample(leaf_nodes_edges, 2)

    # Swap the edge connections
    new_triples = []
    for s, r, o in triples:
        if (s, r, o) == (leaf_node1, edge1[0], edge1[1]):
            new_triples.append((leaf_node1, edge2[0], edge2[1]))
        elif (s, r, o) == (edge1[1], edge1[0], leaf_node1):
            new_triples.append((edge2[1], edge2[0], leaf_node1))
        elif (s, r, o) == (leaf_node2, edge2[0], edge2[1]):
            new_triples.append((leaf_node2, edge1[0], edge1[1]))
        elif (s, r, o) == (edge2[1], edge2[0], leaf_node2):
            new_triples.append((edge1[1], edge1[0], leaf_node2))
        else:
            new_triples.append((s, r, o))

    return new_triples

############################################ Random Deletion Operation ############################################
def is_connected(triples):
    from collections import defaultdict, deque
    
    def build_graph(triples):
        graph = defaultdict(list)
        for s, r, o in triples:
            if r != ':instance':
                graph[s].append(o)
                graph[o].append(s)
        return graph
    
    def bfs(graph, start):
        visited = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                queue.extend(graph[node])
        return visited
    
    if not triples:
        return True
    
    graph = build_graph(triples)
    root = triples[0][0]
    visited = bfs(graph, root)
    
    nodes = {s for s, r, o in triples} | {o for s, r, o in triples}
    return visited == nodes

def random_deletion(triples, alpha=0.1):
    from copy import deepcopy

    # Find leaf nodes and their edges
    leaf_nodes_edges = find_leaf_nodes_and_edges(triples)
    
    if not leaf_nodes_edges:
        return triples

    # Randomly select a leaf node and its edge for deletion
    leaf_node, edge = random.choice(list(leaf_nodes_edges))

    # Construct new triples by removing the selected node and edge
    new_triples = [t for t in triples if not (t[0] == leaf_node and t[1] == ':instance')]
    new_triples = [t for t in new_triples if not (t[0] == edge[1] and t[1] == edge[0] and t[2] == leaf_node)]

    return new_triples

############################################ Random Insertion Operation ############################################
def random_insertion(triples, new_modifier='new_mod'):
    # Randomly select a node to insert new modifier
    target_idx = random.choice(range(len(triples)))
    target = triples[target_idx]
    triples.append((target[0], ':mod', new_modifier))
    return triples

def synonym_replacement(triples):
    for idx, (s, r, o) in enumerate(triples):
        if r == ':instance':
            synonyms = get_hypernyms(o)  # Use hypernyms as synonyms
            if synonyms:
                triples[idx] = (s, r, random.choice(synonyms))
    return triples

def is_action_verb(o):
    # Check if word ends with -number
    return re.match(r'.*-\d+$', o) is not None

def polarity_negation(triples):
    # Define pronouns set
    pronouns = {'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

    nodes = list(set(s for s, r, o in triples if o not in pronouns))

    if not nodes:
        print("No valid nodes found to apply polarity.")
        return triples

    # Randomly select a node for polarity negation
    target_node = random.choice(nodes)
    negated_triples = triples + [(target_node, ':polarity', '-')]

    return negated_triples

############################################ Main Modification Function ############################################
def modify_triples(triples, modification_type='SR', alpha=0.1):
    pronouns = {'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

    if modification_type == 'RS':
        return random_swap(triples)
    elif modification_type == 'RD':
        return random_deletion(triples, alpha=alpha)
    elif modification_type == 'RI':
        return random_insertion(triples)
    elif modification_type == 'SR':
        return synonym_replacement(triples)
    elif modification_type == 'polarity_negation':
        return polarity_negation(triples)
    elif modification_type == 'hypernym':
        # Find candidate triples for replacement
        candidates = [(s, r, o) for s, r, o in triples if r == ':instance' and o not in pronouns]
        if not candidates:
            return triples
        s, r, o = random.choice(candidates)
        
        if '-' in o:
            word_prefix, suffix = o.split('-', 1)
            hypernyms = get_hypernyms(word_prefix)
            if hypernyms:
                new_o = random.choice(hypernyms) + '-' + suffix
                return [(s, r, new_o) if (s == s_ and r == r_ and o == o_) else (s_, r_, o_) for s_, r_, o_ in triples]
        else:
            hypernyms = get_hypernyms(o)
            if hypernyms:
                new_o = random.choice(hypernyms)
                return [(s, r, new_o) if (s == s_ and r == r_ and o == o_) else (s_, r_, o_) for s_, r_, o_ in triples]
        return triples
    elif modification_type == 'hyponym':
        candidates = [(s, r, o) for s, r, o in triples if r == ':instance' and o not in pronouns]
        if not candidates:
            return triples
        s, r, o = random.choice(candidates)
        
        if '-' in o:
            word_prefix, suffix = o.split('-', 1)
            hyponyms = get_hyponyms(word_prefix)
            if hyponyms:
                new_o = random.choice(hyponyms) + '-' + suffix
                return [(s, r, new_o) if (s == s_ and r == r_ and o == o_) else (s_, r_, o_) for s_, r_, o_ in triples]
        else:
            hyponyms = get_hyponyms(o)
            if hyponyms:
                new_o = random.choice(hyponyms)
                return [(s, r, new_o) if (s == s_ and r == r_ and o == o_) else (s_, r_, o_) for s_, r_, o_ in triples]
        return triples
    elif modification_type == 'antonym':
        candidates = [(s, r, o) for s, r, o in triples if r == ':instance' and o not in pronouns]
        if not candidates:
            return triples
        
        while candidates:
            s, r, o = random.choice(candidates)
            candidates.remove((s, r, o))
            if '-' in o:
                word_prefix, suffix = o.split('-', 1)
                antonyms = get_antonyms(word_prefix)
                if antonyms:
                    new_o = random.choice(antonyms) + '-' + suffix
                    return [(s, r, new_o) if (s == s_ and r == r_ and o == o_) else (s_, r_, o_) for s_, r_, o_ in triples]
            else:
                antonyms = get_antonyms(o)
                if antonyms:
                    new_o = random.choice(antonyms)
                    return [(s, r, new_o) if (s == s_ and r == r_ and o == o_) else (s_, r_, o_) for s_, r_, o_ in triples]
        
        return triples

if __name__ == "__main__":
    triples = read_triples(sys.stdin)
    modification_type = sys.argv[1] if len(sys.argv) > 1 else 'SR'
    modified_triples = modify_triples(triples, modification_type)
    for triple in modified_triples:
        print(triple)