#!/usr/bin/env python

import argparse
from io import TextIOWrapper
import json
from math import factorial
import string
import sys
import time
import numpy as np
#from GenerateAdjArray import rebase, debase, concatRebases

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
    parser.add_argument('nodefile', type=argparse.FileType('rb'),
                        help='*-nodes.graph file')
    parser.add_argument('edgefile', type=argparse.FileType('rb'),
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
        args.threshold /= 1000000000
        global charsize 
        charsize = len(args.alphabet)
        global charset 
        charset = args.alphabet
    except argparse.ArgumentError:
        sys.exit('Error: ArgumentParser failed to parse the arguments')

    # Read node file data
    if (args.verbose >= 0): print("# [{}] Reading nodes from file".format(deltaf()))
    nodes = np.load(args.nodefile)

    # Read edge file data
    if (args.verbose >= 0): print("# [{}] Reading edges from file".format(deltaf()))
    edges = np.load(args.edgefile)

    # Recursively generate passwords
    if (args.verbose >= 1): print("# [{}] Generating passwords".format(deltaf()))

    with open("pwlist.txt", "w") as pwlist:
        for ind in range(len(nodes)):
            if (args.verbose >= 1): print("# [{}] testing <{}>".format(deltaf(), debase(ind, args.size)))
            recursivePassword(nodes, edges, pwlist, args.size, args.threshold, probability=nodes[ind], startInt=ind, min_pw_length=args.min, max_pw_length=args.max, pw=debase(ind, args.size))


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
def recursivePassword(N: list, E: list, pwfile: TextIOWrapper, nodeLength: int, threshold: float, probability=1, startInt=0, min_pw_length=8, max_pw_length=24, pw='', repeat=0):
    if probability <= threshold or len(pw) > max_pw_length:
        return
    if len(pw) >= min_pw_length:
        global passwordDict 
        passwordDict[pw] = probability
        #print("\t> [{}] {:30s}| {:30.29f}".format(deltaf(), pw, probability))
    
    # Taking the starting string, the last N chars are the current node. The last N-1 chars + a char from charset make all possible
    # transistions away from the current node. If the transition is above the threshold, recurse
    for i in range(charsize):
        if probability*E[startInt % charsize ** nodeLength][i] > threshold:
            if startInt == (startInt * charsize + i) % (charsize ** nodeLength):
                recursivePassword(N, E, pwfile, nodeLength, threshold, probability*E[startInt % charsize ** nodeLength][i] * (.5 **(factorial(repeat+1))), startInt*charsize+i, min_pw_length, max_pw_length, pw+charset[i], repeat=repeat+1)
            else:
                #print("\t> [{}] {:30s}| {:30.29f}".format(deltaf(), pw, probability))
                recursivePassword(N, E, pwfile, nodeLength, threshold, probability*E[startInt % charsize ** nodeLength][i], startInt*charsize+i, min_pw_length, max_pw_length, pw+charset[i], repeat=0)
    return

def rebase(node: str) -> int:
    rebasedNode = 0
    for ch in node:
        rebasedNode *= charsize
        rebasedNode += charset.index(ch)
    return rebasedNode

def concatRebases(str1: str, str2: str) -> int:
    num1 = rebase(str1)
    num2 = rebase(str2)
    return num1 * (charsize ** (len(str1) - 1)) + num2

def debase(node: int, length: int) -> str:
    if node == 0: return '0' * length
    debased = ''
    while node > 0:
        debased = charset[node % charsize] + debased
        node //= charsize
    return debased.rjust(length, "0")

# Pulls the time difference since program start 
def delta() -> float:
    return time.time() - start

# Formats delta() into a standardized string
def deltaf() -> string:
    return str("%010.2fs" % delta())

# Invoke main()
if __name__ == "__main__":
   main(sys.argv[1:])