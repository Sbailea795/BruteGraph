import argparse
from io import TextIOWrapper
from itertools import chain, cycle, islice, product
import json
from math import factorial
import pickle
import string
import sys
import time
from unittest import skip
import networkx as nx
import os
from Generate import Graph

# timer for sake of time-stamping verbosity logs
start = time.time()

# QoL number-latin prefix translation
latin = {
    1 : "mono",
    2 : "di",
    3 : "tri",
    4 : "quad"
}

# holder for passwords. Note that 
# this is a global variable that 
# is used by recursivePassword(...)
passwordDict = {}

def main(argv):
    # Parser for args
    parser = argparse.ArgumentParser(description='Generates graphs for n-graphs')
    parser.add_argument('nodefile', type=str,
                        help='*-nodes.graph file')
    parser.add_argument('edgefile', type=str,
                        help='*-edges.graph file')
    parser.add_argument('-a', '--alphabet', default='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ', \
        type=str, help='The characterset to be used in password generation. Must be a subset of character set of the generated graph')
    parser.add_argument('-m', '--min', default=8, type=int, \
        help='Set a minimum password length for generated passwords.')
    parser.add_argument('-M', '--max', default=24, type=int, \
        help='Set a maximum password length for generated passwords.')
    parser.add_argument('-s', '--size', choices=[1, 2, 3, 4], default=2, type=int, \
        help='Declare the n-graph node size for the nodes and edges in the node/edge files.')
    parser.add_argument('-v', '--verbose', action='count', default=0, \
        help='Level of verbosity (0-2). Default is 0. Counts of the verbosity flag determine the verbosity')
    parser.add_argument('-t', '--threshold', default=1, type=float, \
        help='Cutoff probability for passwords; anything probabalistically above the threshold will be output. Threshold is taken as a coeffient to one in a one billion.')
    
    #Error try-catch
    try:               
        args = parser.parse_args()
        open(args.nodefile, "r")
        open(args.edgefile, "r")
        args.threshold /= 1000000000
    except argparse.ArgumentError:
        sys.exit('Error: ArgumentParser failed to parse the arguments')

    # Read node file data
    if (args.verbose >= 0): print("# [{}] Reading nodes from file".format(deltaf()))
    with open("{}".format(args.nodefile), "r") as infile:
        nodes = readNodeFile(infile)

    # Read edge file data
    if (args.verbose >= 0): print("# [{}] Reading edges from file".format(deltaf()))
    with open("{}".format(args.edgefile), "r") as infile:
        edges = readEdgeFile(infile)

    # Use file data to create a graph
    if (args.verbose >= 1): print("# [{}] Recreating graph".format(deltaf()))
    G = Graph(nodes, edges)

    # Recursively generate passwords
    if (args.verbose >= 1): print("# [{}] Generating passwords".format(deltaf()))
    with open("pwlist.txt", "w") as pwlist:
        for node in G.nodes.keys():
            if (args.verbose >= 1): print("\t> [{}] Analyzing starting node of <{}>".format(deltaf(), node))
            recursivePassword(G, args.alphabet, args.size, args.threshold, G.nodes[node]['size'], node, pwlist, args.min, args.max)
    global passwordDict
    if (args.verbose >= 1): print("# [{}] {} Passwords generated".format(deltaf(), len(passwordDict)))

    # Sorts {password:probability} dict on the probability value
    if (args.verbose >= 1): print("# [{}] Sorting passwords".format(deltaf()))
    passwordDict = dict(sorted(passwordDict.items(), key = lambda x: x[1], reverse=True))

    # Output to file
    if (args.verbose >= 1): print("# [{}] Passing passwords to file".format(deltaf()))
    with open("pwlist.txt", "w") as pwfile:
        for k, v in passwordDict.items():
            pwfile.write("{:30s}| {:30.29f}\n".format(k, v))

    # Exit main
    if (args.verbose >= 1): print("# [{}] Done".format(deltaf()))
    return 0



# Depth-first search from a starting string. using the node-length N, the last N chars in the startStr determine a base node
# The for loop generates all possible transition char
def recursivePassword(G: Graph, charset: str, nodeLength: int, threshold: float, probability: float, startStr: str,  pwfile: TextIOWrapper, min_pw_length=8, max_pw_length=24, repeatNode=0):
    if probability <= threshold or len(startStr) > max_pw_length:
        return
    if len(startStr) >= min_pw_length:
        global passwordDict 
        passwordDict[startStr] = probability
        #print("\t> [{}] {:30s}| {:30.29f}".format(deltaf(), startStr, probability))
    
    # Taking the starting string, the last N chars are the current node. The last N-1 chars + a char from charset make all possible
    # transistions away from the current node. If the transition is above the threshold, recurse
    for radiating_edge in list(zip(cycle([startStr[-nodeLength:]]), [startStr[(-nodeLength+1):] + ch for ch in charset])):
        if probability*G.edges[radiating_edge]['weight'] < threshold:
            break

        if (startStr[-nodeLength:] == radiating_edge[1]):
            recursivePassword(G, charset, nodeLength, threshold,  probability*G.edges[radiating_edge]['weight']*.5 * pow(.9, factorial(repeatNode)-1), \
                startStr + radiating_edge[1][-1], pwfile, min_pw_length, max_pw_length, repeatNode+1)
        else:
            recursivePassword(G, charset, nodeLength, threshold,  probability*G.edges[radiating_edge]['weight']*.5 * pow(.9, factorial(repeatNode)-1), \
                startStr + radiating_edge[1][-1], pwfile, min_pw_length, max_pw_length)
    return


# Reads the nodeFile and parses it, returning a dict of nodes. 
# Nodes are of the form:
# The key is a string of the node's name such as '12', or '23'. 
# The value is a dict of key size with a value of percentage of
# all passwords that start at that node
def readNodeFile(nodeFile: TextIOWrapper) -> dict:
    nodes = {}
    while True:
        key = nodeFile.readline()[:-1]
        if not key: break
        value = eval(nodeFile.readline())
        nodes[key] = value
    return nodes


# Reads the edgeFile and parses it, returning a dict of edges. 
# Edges are of the form:
# The key is a tuple of origin-end nodes such as 
# ('12', '23') where node '12' points to '23'. The value is a
# dict of key weight with a value of probability of that path 
# versus all other paths out of the origin node
def readEdgeFile(edgeFile: TextIOWrapper) -> dict:
    edges = {}
    while True:
        key = edgeFile.readline()
        if not key: break
        key = eval(key)
        value = eval(edgeFile.readline())
        edges[key] = value
    return edges

# Pulls the time difference since program start 
def delta() -> float:
    return time.time() - start

# Formats delta() into a standardized string
def deltaf() -> string:
    return str("%010.2fs" % delta())

# Invoke main()
if __name__ == "__main__":
   main(sys.argv[1:])