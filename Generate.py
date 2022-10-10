import argparse
from itertools import cycle, product
import string
import sys
import time
import os

start = time.time()

latin = {
    1 : "mono",
    2 : "di",
    3 : "tri",
    4 : "quad"
}

def delta() -> float:
    return time.time() - start

def deltaf() -> string:
    return str("%010.2fs" % delta())

def main(argv):
    #parse args
    parser = argparse.ArgumentParser(description='Generates graphs for n-graphs')
    parser.add_argument('file', type=str,
                        help='password file to be analyzed', metavar='file')
    parser.add_argument('-a', '--alphabet', default='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ', \
        type=str, help='The characterset to be used in password generation. Must be a subset of character set of the generated graph')
    parser.add_argument('-l', '--length', choices=[1, 2, 3, 4], default=3, type=int, help='Sets the n-graph length for generating nodes')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help='Level of verbosity (0-2). Default is 0.')
    
    #Error try-catch
    try:               
        args = parser.parse_args()
        a = open(args.file)
        a.close()
    except argparse.ArgumentError:
        sys.exit('Error: ArgumentParser failed to parse the arguments')
    try:
        os.mkdir("Graphs")
    except os.error:
        if (args.verbosity >= 2): print("# [{}] ./Graphs already exists".format(deltaf()))

    #creates a nodes and edges to be used in the graph G; this step takes a long time
    nodeDict, edgeDict = createNodesAndEdges(args.verbosity, args.alphabet, args.length)

    #creates a graph of nodes and edges
    if (args.verbosity >= 0): print("# [{}] Creating graph".format(deltaf()))
    G = Graph(nodeDict, edgeDict)
    
    # Reads every line of a pw file. Will only parse printable ascii with a minimum size of the n-graph
    if (args.verbosity >= 0): print("# [{}] parsing file".format(deltaf()))
    with open(args.file, errors='ignore') as pwFile:
        for line in pwFile:
            line = str(line.strip())
            if (len(line) < args.length or (not str.isascii(line)) or (not line.isprintable())):
                continue
            if (args.verbosity >= 1): 
                print("# [{}] Analyzing \"{}\"".format(deltaf(), line))
            # If a password starts on a node, its 'size is incremented. Size denotes how many passwords start at the node
            G.nodes[line[:args.length]]["size"] += 1
            # For every transition from 'ab to 'bc' weight is added to the edge to show how much traffic occurs.
            for i in range(1, len(line) - args.length + 1):
                G.edges[line[(i-1):(i-1)+args.length],line[i:i+args.length]]['weight'] += 1
                if (args.verbosity >= 2): 
                    print("\t> [{}] Edited ['{}']['{}']".format(deltaf(), line[(i-1):(i-1)+args.length], line[i:i+args.length]))

    # probability calcs -- percentage of passwords starting at node
    #
    # Probability is 0 <= x <=1 (1 being always, 0 being never) of an node being the start of a password in pwfile
    # The probability is ratio of the size of the current node against all other nodes
    if (args.verbosity >= 0): print("# [{}] Probability Calculations on Nodes".format(deltaf(), total))
    total = 0
    for node in G.nodes:
        total += G.nodes[node]["size"]
    if (args.verbosity >= 0): print("# [{}] {} Passwords parsed".format(deltaf(), total))
    for node in G.nodes:
        G.nodes[node]["size"] /= max(total, 1)
    
    # probability calcs -- percentage of weight from all weighted edges originating at base node
    #
    # Probability is 0 <= x <=1 (1 being always, 0 being never) of an edge occuring in the pwfile
    # essentially, node 'ab' transitions into nodes 'b_' where every '_' is a char in the alphabet.
    # The probability is ratio of the weight of the current ('ab','b_') edge against all other ('ab','b_') edges
    if (args.verbosity >= 0): print("# [{}] Probability Calculations on edges".format(deltaf(), total))
    for base in nodeDict.keys():
        total = 0
        for radiating_edge in list(zip(cycle([base]), [base[1:] + ch for ch in args.alphabet])):
            total += G.edges[radiating_edge]["weight"]
        for radiating_edge in list(zip(cycle([base]), [base[1:] + ch for ch in args.alphabet])):
            G.edges[radiating_edge]["weight"] /= max(total, 1)   
    
    # Write files for nodes and edges in G for the sake of preserving results
    writeFiles(G, args.file, args.length, args.verbosity)
    
    # exit main
    if (args.verbosity >= 0): print("# [{}] Done".format(deltaf()))
    return 0


class Graph:
    def __init__(self, nodeDict : dict, edgeDict: dict):
        self.nodes = nodeDict
        self.edges = edgeDict
  
def createNodesAndEdges(verbosity: int, alphabet: str, length: int) -> tuple[dict, dict]:
    if (verbosity >= 0): print("# [{}] dicting nodes".format(deltaf()))
    nodeDict = dict.fromkeys(["".join(combo) for combo in product(alphabet, repeat=length)])
    for key in nodeDict:
        nodeDict[key] = {"size" : 0}
    
    if (verbosity >= 0): print("# [{}] mapping all edges".format(deltaf()))
    edges = []
    for base in nodeDict.keys():
        edges += ((w_edge) for w_edge in list(zip(cycle([base]), [base[1:] + ch for ch in alphabet])))

    if (verbosity >= 0): print("# [{}] dicting edges".format(deltaf()))
    edgeDict = dict.fromkeys(edges)
    if (verbosity >= 0): print("# [{}] keying edges".format(deltaf()))
    for key in edges:
        edgeDict[key] = {"weight" : 0}
    return nodeDict, edgeDict
    
def writeFiles(G: Graph, pwfile: str, length: int, verbosity: int):
    if (verbosity >= 0): print("# [{}] Writing Graph to File".format(deltaf()))
    with open("Graphs\{}graph-{}-nodes.graph".format(latin[length], pwfile), "w") as outfile:
        if (verbosity >= 1): print("# [{}] Creating node file".format(deltaf()))
        for key in G.nodes:
            outfile.write("{}\n{}\n".format(str(key), str(G.nodes[key])))

    with open("Graphs\{}graph-{}-edges.graph".format(latin[length], pwfile), "w") as outfile:
        if (verbosity >= 1): print("# [{}] Creating edge file".format(deltaf()))
        for key in G.edges:
            outfile.write("{}\n{}\n".format(str(key), str(G.edges[key])))

if __name__ == "__main__":
   main(sys.argv[1:])

# helpful for debugging
# test = dict(sorted(G.nodes.items(), key= lambda x: x[1]['size'], reverse=True))
# test = dict(sorted(G.edges.items(), key= lambda x: x[1]['weight'], reverse=True))
