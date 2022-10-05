import argparse
from itertools import cycle, product
import json
import networkx as nx
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
    parser.add_argument('-l', '--length', choices=[1, 2, 3, 4], default=3, type=int, help='Sets the n-graph length for generating nodes')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Level of verbosity (0-2). Default is 0.')
    
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
        if (args.verbose >= 2): print("# [{}] ./Graphs already exists".format(deltaf()))
    
    charset = []
    for i in range(32, 127):
        charset += chr(i)
    
    if (args.verbose >= 0): print("# [{}] dicting nodes".format(deltaf()))
    nodeD = dict.fromkeys(["".join(combo) for combo in product(charset, repeat=args.length)])
    for key in nodeD:
        nodeD[key] = {"size" : 0}
    
    if (args.verbose >= 0): print("# [{}] mapping all edges".format(deltaf()))
    edges = []
    for base in nodeD.keys():
        edges += ((w_edge) for w_edge in list(zip(cycle([base]), [base[1:] + ch for ch in charset])))#for base in nodeD.keys())))

    if (args.verbose >= 0): print("# [{}] dicting edges".format(deltaf()))
    edgeD = dict.fromkeys(edges)
    if (args.verbose >= 0): print("# [{}] keying edges".format(deltaf()))
    for key in edges:
        edgeD[key] = {"weight" : 0}


    if (args.verbose >= 0): print("# [{}] Creating graph".format(deltaf()))
    G = Graph(nodeD, edgeD)
    
    if (args.verbose >= 0): print("# [{}] parsing file".format(deltaf()))
    with open(args.file, errors='ignore') as pwFile:
        for line in pwFile:
            line = str(line.strip())
            if (len(line) < args.length or (not str.isascii(line)) or (not line.isprintable())):
                continue
            if (args.verbose >= 1): print("# [{}] Analyzing \"{}\"".format(deltaf(), line))
            G.nodes[line[:args.length]]["size"] += 1
            for i in range(1, len(line) - args.length + 1):
                G.edges[line[(i-1):(i-1)+args.length],line[i:i+args.length]]['weight'] += 1
                if (args.verbose >= 2): print("\t> [{}] Edited ['{}']['{}']".format(deltaf(), line[(i-1):(i-1)+args.length], line[i:i+args.length]))

    # probability calcs -- percentage of passwords starting at node
    total = 0
    for node in G.nodes:
        total += G.nodes[node]["size"]
    if (args.verbose >= 0): print("# [{}] {} Passwords parsed".format(deltaf(), total))
    if (args.verbose >= 0): print("# [{}] Probability Calculations on Nodes".format(deltaf(), total))
    for node in G.nodes:
        G.nodes[node]["size"] /= max(total, 1)
    
    # probability calcs -- percentage of weight from all weighted edges originating at base node
    if (args.verbose >= 0): print("# [{}] Probability Calculations on edges".format(deltaf(), total))
    for base in nodeD.keys():
        total = 0
        for radiating_edge in list(zip(cycle([base]), [base[1:] + ch for ch in charset])):
            total += G.edges[radiating_edge]["weight"]
        for radiating_edge in list(zip(cycle([base]), [base[1:] + ch for ch in charset])):
            G.edges[radiating_edge]["weight"] /= max(total, 1)   

    # test = dict(sorted(G.nodes.items(), key= lambda x: x[1]['size'], reverse=True))
    # test = dict(sorted(G.edges.items(), key= lambda x: x[1]['weight'], reverse=True))
    
    
    # write file
    if (args.verbose >= 0): print("# [{}] Writing Graph to File".format(deltaf()))
    with open("Graphs\{}graph-{}-nodes.graph".format(latin[args.length], args.file), "w") as outfile:
        if (args.verbose >= 1): print("# [{}] Creating node file".format(deltaf()))
        for key in G.nodes:
            outfile.write("{}\n{}\n".format(str(key), str(G.nodes[key])))

    with open("Graphs\{}graph-{}-edges.graph".format(latin[args.length], args.file), "w") as outfile:
        if (args.verbose >= 1): print("# [{}] Creating edge file".format(deltaf()))
        for key in G.edges:
            outfile.write("{}\n{}\n".format(str(key), str(G.edges[key])))


    # exit main
    if (args.verbose >= 0): print("# [{}] Done".format(deltaf()))
    return 0


class Graph:
    def __init__(self, nodeD : dict, edgeD: dict):
        self.nodes = nodeD
        self.edges = edgeD
  

if __name__ == "__main__":
   main(sys.argv[1:])
