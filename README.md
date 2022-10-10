# BruteGraph
Using graph theory to develop a model of password probabilities

<p>This Project is a proof of concept meant to demonstrate the application of graph theory in predicting passwords. For this project I focus on the character set of A-Z, a-z, 0-9, and special characters. In total, this works to be 95 possible characters for a password. For a modern computer, a password of length ten would result in 95 * 95 * ... = 95^10 = 59,873,693,923,837,890,625 possible passwords. Obviously, some passwords are more commonplace than others, so brute forcing 58 cinqtillion passwords would be wasteful as well as impractical. Given a seed of leaked/cracked/stolen passwords, is it be possible to reduce the number of brute force passwords to a more managable number?</p>
<p>The modeling used in this repo uses two concepts: digraph/trigraph/n-graph analysis used in cryptography, and graph theory.</p> 
  
  
  
## N-Graphs:
  
<p>In english E, T, N, O, R, I, A and S are the most common letters in any sufficiently large text. This produces a signature for English, or a distribution of letter occurences in text. N-graph analysis is frequency analysis extended to tuples of letters. Pairs like 'er', 'gh', and 'on' are common pairings, and 'ike', 'ugh', and 'tes' are common trigraphs.</p>
  
  
  
## Graph Theory:
  
<p>Graph theory is a problem solving tool for relational data. Graphs are colloquially defined as a set of nodes and edges, where nodes are entities that are related to other nodes via an edge. Edges therefore are defined by the two nodes they connect. Example: a graph of nodes {A, B, C} can have edges {(A,B), (A,C), (B,C)}. For the purposes of generating probable passwords, nodes are an n-graph with an edge mapping a transition into a following n-graph.</p>
  
  
  
## Generate Overview:
  
<p>As an example, we will use the password 'BooksAreCool123' and use digraph analysis. Generate starts with making a list of all digraphs possible, and then making a  node to represent the digraph set. All valid edges/transitions are preemptively created too. Node 'ab' can transition into 'bc' because of the overlapping 'b'; 'ab' cannot transition into '12' because there is no overlap.</p>

<p>After initializing a graph, Generate.py will parse passwords, with the password 'BooksAreCool123' as an example Generate.py will analyze list letter pairs: 'Bo', 'oo', 'ok', 'ks', ... '12', '23'. Generate will look at the starting digraph 'Bo'. Since node 'Bo' starts a password, the attribute 'size' of node 'Bo' is incremented. Generate.py will then weight edges of nodes that overlap. The node 'Bo' transitions into 'oo', thus the edge ('Bo','oo') will now have a weight of 1. This process is done iteratively across all digraphs of the password.</p>

<p>After all passwords are parsed, the size of nodes and weight of edges are normalized. Weight and size are probabilities of an occurance in a range of 0-1. Size is recalculated to be the ratio of that nodes size against all other nodes. With a second password '123456' 'Bo' and '12' would have a size of .5. For edges, it is the ratio of that edge's weight against all edges that radiate from the starting node. in the instance 'oo', there is {('oo', 'ok'),('oo','ol')}, both with a weight of one. Both of these become .5, indicating that half the time 'oo' becomes 'ool' and the other half of the time becomes 'ook'.</p>
    
<p>Generate.py will produce a serialization of the nodes and edges and output it to files. The format is "[edge/node]\n[probability]\n". This is used later for the
predicting of passwords.</p>
    
    
    
## Predict Passwords Overview:
    
<p>The graph model created in Generate.py is a set of diagraphs, with possible transitions, and probabilities. To conceptually generate a password with this model, start at an arbitrary node. The password starts with a probabilty of the size of that node. Recursively, we can transition to other nodes, multiplying the probability by the weight of that edge. Using 'BooksAreCool123' again, 'Bo' has size 0.5, and thus the starting probability is the same. 'Bo' transitions into 'oo' with a weight of 1, soo 'Boo' has a probability of 0.5 still. Node 'oo' can branch to either 'ok' or 'ol' with equal 0.5 probabilty. Thus 'Book' and 'Bool' both are assigned a probability of 0.25. This can occur until either a maximum length is met or a probability threshold is met. PredictPasswords.py reads in the Generate.py graph data, and then recursively generates passwords using this method. It will rank-order passwords absed on probability and then create a password list text file.</p>
