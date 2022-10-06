import argparse
from io import TextIOWrapper
from itertools import chain, cycle, islice, product
import json
from math import factorial
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
                        help='password file to be analyzed', metavar='nodeFile')
    parser.add_argument('edgefile', type=str,
                        help='password file to be analyzed', metavar='edgeFile')
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



    # Read node file data
    if (args.verbose >= 0): print("# [{}] Reading nodes from file".format(deltaf()))
    with open("{}".format(args.nodefile), "r") as infile:
        nodes = {}
        while True:
            key = infile.readline()[:-1]
            if not key: break
            value = eval(infile.readline())
            nodes[key] = value



    # Read edge file data
        if (args.verbose >= 0): print("# [{}] Reading edges from file".format(deltaf()))
    with open("{}".format(args.edgefile), "r") as infile:
        edges = {}
        while True:
            key = infile.readline()
            if not key: break
            key = eval(key)
            value = eval(infile.readline())
            edges[key] = value



    # Use file data to create a graph
    if (args.verbose >= 1): print("# [{}] Recreating graph".format(deltaf()))
    G = Graph(nodes, edges)



    # Recursively generate passwords
    if (args.verbose >= 1): print("# [{}] Generating passwords".format(deltaf()))
    with open("pwlist.txt", "w") as pwlist:
        for node in G.nodes.keys():
            if (args.verbose >= 2): print("\t> [{}] Analyzing starting node of <{}>".format(deltaf(), node))
            recursivePassword(G, args.cutoff, G.nodes[node]['size'], node, args.length, pwlist)
    global tally
    if (args.verbose >= 1): print("# [{}] {} Passwords generated".format(deltaf(), len(tally)))



    # Sorts password-probability dict on the probability key
    if (args.verbose >= 1): print("# [{}] Sorting passwords".format(deltaf()))
    tally = dict(sorted(tally.items(), key = lambda x: x[1], reverse=True))



    # Output to file
    if (args.verbose >= 1): print("# [{}] Passing passwords to file".format(deltaf()))
    with open("pwlist.txt", "w") as pwfile:
        for k, v in tally.items():
            pwfile.write("{:30s}| {:30.29f}\n".format(k, v))



    # Exit main
    if (args.verbose >= 1): print("# [{}] Done".format(deltaf()))
    return 0



# Depth-first search from a starting string. using the node-length N, the last N chars in the startStr determine a base node
# The for loop generates all possible transition char
def recursivePassword(G: Graph, cutoffProb: float, probability: float, startStr: str, nodeLength: int, pwfile: TextIOWrapper, min_pw_length=8, max_pw_length=24, repeatNode=0):
    if probability <= cutoffProb or len(startStr) > max_pw_length:
        return
    if len(startStr) >= min_pw_length:
        global tally 
        tally[startStr] = probability
        print("\t> [{}] {:30s}| {:30.29f}".format(deltaf(), startStr, probability))
        #pwfile.write("{:30s}| {:30.29f}\n".format(startStr, probability))
    for radiating_edge in list(zip(cycle([startStr[-nodeLength:]]), [startStr[(-nodeLength+1):] + ch for ch in charset])):
        if probability*G.edges[radiating_edge]['weight'] > cutoffProb:
            if (startStr[-nodeLength:] == radiating_edge[1]):
                recursivePassword(G, cutoffProb, probability*G.edges[radiating_edge]['weight']*.5 * pow(.9, factorial(repeatNode)-1), \
                    startStr + radiating_edge[1][-1], nodeLength, pwfile, min_pw_length, max_pw_length, repeatNode+1)
            else:
                recursivePassword(G, cutoffProb, probability*G.edges[radiating_edge]['weight']*.5 * pow(.9, factorial(repeatNode)-1), \
                    startStr + radiating_edge[1][-1], nodeLength, pwfile, min_pw_length, max_pw_length)
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
