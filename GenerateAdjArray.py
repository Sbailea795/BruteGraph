#!/usr/bin/env python

import argparse
import json
import string
import sys
import time
import os
import numpy as np

start = time.time()

latin = {
    1 : "mono",
    2 : "di",
    3 : "tri",
    4 : "quad"
}

charsize = -1
charset = ''

def delta() -> float:
    return time.time() - start

def deltaf() -> string:
    return str("%010.2fs" % delta())

def main(argv):
    #parse args
    parser = argparse.ArgumentParser(description='Generates graphs for n-graphs')
    parser.add_argument('file', type=argparse.FileType('r', errors='ignore'),
                        help='password file to be analyzed', metavar='file')
    parser.add_argument('-s', '--size', choices=[1, 2, 3, 4], default=2, type=int, \
        help='Declare the n-graph node size for the nodes and edges in the node/edge files.')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Level of verbosity (0-2). Default is 0.')
    parser.add_argument('-a', '--alphabet', default='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ', \
        type=str, help='The character set to be used in password generation.')
    
    #Error try-catch
    try:               
        args = parser.parse_args()
        global charsize 
        charsize = len(args.alphabet)
        global charset 
        charset = args.alphabet
    except argparse.ArgumentError:
        sys.exit('Error: ArgumentParser failed to parse the arguments')
    try:
        os.mkdir("{}\\{}-{}graph".format(os.getcwd(), os.path.splitext(str(args.file.name))[0], latin[args.size]))
    except os.error:
        print("# [{}] ./{}-{}graph/ already exists".format(deltaf(), os.path.splitext(str(args.file.name))[0], latin[args.size]))
        #sys.exit('Error: a password file serialization folder exists. Rename, delete, or move the existing folder')

    if (args.verbose >= 0): print("# [{}] creating matrix".format(deltaf())) 

    nodeArray = np.zeros((charsize ** args.size + 1), dtype=float)
    edgeMatrix = np.zeros((len(nodeArray)+1,charsize+1), dtype=float)
    
    if (args.verbose >= 0): print("# [{}] parsing file".format(deltaf()))
    for line in args.file:
        line = str(line.strip())
        if len(line) < args.size or any(ch not in charset for ch in line):
            continue
        if (args.verbose >= 1): print("# [{}] Analyzing \"{}\"".format(deltaf(), line))
        nodeArray[rebase(line[:args.size])] += 1
        for i in range(1, len(line) - args.size + 1):
            edgeMatrix[rebase(line[(i-1):(i-1)+args.size])][rebase(line[(i-1)+args.size])] += 1
            if (args.verbose >= 2): print("\t> [{}] Edited ['{}']['{}']".format(deltaf(), line[(i-1):(i-1)+args.size], line[i:i+args.size]))
    if (args.verbose >= 0): print("# [{}] closing file".format(deltaf()))
    
    total = sum(nodeArray)
    if (args.verbose >= 0): print("# [{}] {} passwords parsed".format(deltaf(), total))

    # probability calcs -- percentage of passwords starting at node
    if (args.verbose >= 0): print("# [{}] Probability Calculations on Nodes".format(deltaf(), total))
    for i in range(len(nodeArray)):
        nodeArray[i] /= total
    
    # probability calcs -- percentage of weight from all weighted edges originating at base node
    if (args.verbose >= 0): print("# [{}] Probability Calculations on edges".format(deltaf(), total))
    for i in range(len(edgeMatrix)):
        edgeMatrix[i] /= max(1, sum(edgeMatrix[i]))

    # write file
    if (args.verbose >= 0): print("# [{}] Writing Graph to File".format(deltaf()))
    with open("{}\\{}-{}graph\\nodes".format(os.getcwd(), os.path.splitext(str(args.file.name))[0], latin[args.size]), "wb") as outfile:
        np.save(outfile, nodeArray)
    with open("{}\\{}-{}graph\\edges".format(os.getcwd(), os.path.splitext(str(args.file.name))[0], latin[args.size]), "wb") as outfile:
        np.save(outfile, edgeMatrix)

    # exit main
    if (args.verbose >= 0): print("# [{}] Done".format(deltaf()))
    return 0

def rebase(node: str) -> int:
    rebasedNode = 0
    for i in range(len(node)):
        rebasedNode += charset.index(node[i])*charsize**(len(node)-i-1)
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

if __name__ == "__main__":
   main(sys.argv[1:])
