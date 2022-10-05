import argparse
from io import TextIOWrapper
from itertools import chain, cycle, islice, product
import json
import pickle
import string
import sys
import time
import networkx as nx
import os
from Generate import Graph

start = time.time()

latin = {
    1 : "mono",
    2 : "di",
    3 : "tri",
    4 : "quad"
}

tally = {}

def main(argv):
    #parse args
    parser = argparse.ArgumentParser(description='Generates graphs for n-graphs')
    parser.add_argument('nodefile', type=str,
                        help='password file to be analyzed', metavar='file')
    parser.add_argument('edgefile', type=str,
                        help='password file to be analyzed', metavar='file')
    parser.add_argument('-l', '--length', choices=[1, 2, 3, 4], default=3, type=int, help='Sets the n-graph length for generating nodes.')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Level of verbosity (0-2). Default is 0.')
    parser.add_argument('-c', '--cutoff', default=1, type=float, help='Cutoff probability for passwords. Will be taken as x over one million.')
    
    #Error try-catch
    try:               
        args = parser.parse_args()
        open(args.nodefile, "r")
        open(args.edgefile, "r")
        args.cutoff = args.cutoff / 100000000
    except argparse.ArgumentError:
        sys.exit('Error: ArgumentParser failed to parse the arguments')

    # read file
    if (args.verbose >= 0): print("# [{}] Reading nodes from File".format(deltaf()))
    with open("{}".format(args.nodefile), "r") as infile:
        if (args.verbose >= 1): print("# [{}] reading node file".format(deltaf()))
        nodes = {}
        while True:
            key = infile.readline()[:-1]
            if not key: break
            value = eval(infile.readline())
            nodes[key] = value

    with open("{}".format(args.edgefile), "r") as infile:
        if (args.verbose >= 1): print("# [{}] reading edge file".format(deltaf()))
        edges = {}
        while True:
            key = infile.readline()
            if not key: break
            key = eval(key)
            value = eval(infile.readline())
            edges[key] = value

    if (args.verbose >= 1): print("# [{}] Recreating graph".format(deltaf()))
    G = Graph(nodes, edges)
    if (args.verbose >= 1): print("# [{}] Generating Passwords".format(deltaf()))
    for node in G.nodes.keys():
        if (args.verbose >= 2): print("\t> [{}] Analyzing starting node of <{}>".format(deltaf(), node))
        recursivePassword(G, args.cutoff, G.nodes[node]['size'], node, args.length, 10, open("pwlist.txt", "w"))
    if (args.verbose >= 1): print("# [{}] {} passwords generated".format(deltaf(), len(tally)))
    if (args.verbose >= 1): print("# [{}] Done".format(deltaf()))
    # exit main
    return 0

def recursivePassword(G: Graph, cutoffProb: float, probability: float, startStr: str, nodeLength: int, minPasswordLength: int, pwfile: TextIOWrapper):
    if probability <= cutoffProb:
        return
    if len(startStr) >= minPasswordLength:
        pwfile.write("{:30s}| {:30.29f}".format(startStr, probability))
        global tally 
        tally[startStr] = probability
        print("\t> [{}] {:30s}| {:30.29f}".format(deltaf(), startStr, probability))
        return
    for radiating_edge in list(zip(cycle([startStr[-nodeLength:]]), [startStr[(-nodeLength+1):] + ch for ch in charset])):
        if probability*G.edges[radiating_edge]['weight'] > cutoffProb:
            if (startStr[-nodeLength:] == radiating_edge[1]):
                recursivePassword(G, cutoffProb, probability*G.edges[radiating_edge]['weight']*.5, startStr + radiating_edge[1][-1], nodeLength, minPasswordLength, pwfile)
            else:
                recursivePassword(G, cutoffProb, probability*G.edges[radiating_edge]['weight'], startStr + radiating_edge[1][-1], nodeLength, minPasswordLength, pwfile)
    return


charset = []
for i in range(32, 127):
    charset += chr(i)

def delta() -> float:
    return time.time() - start

def deltaf() -> string:
    return str("%010.2fs" % delta())

if __name__ == "__main__":
   main(sys.argv[1:])
