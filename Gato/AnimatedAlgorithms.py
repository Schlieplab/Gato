################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   AnimatedAlgorithms.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
################################################################################
from GatoGlobals import *
from DataStructures import VertexLabeling, Queue
from AnimatedDataStructures import *
#from GraphDisplay import GraphDisplay
#from Graph import SubGraph

def shortestPath(G,A,s,t):
    """ Find a shortest path and return it as a set of edges. If no
        path exists, it returns None """
    pred = AnimatedVertexLabeling(A)    
    Q    = AnimatedVertexQueue(A)    

    A.SetAllEdgesColor("black")
    for v in G.vertices:
	pred[v] = None	
    Q.Append(s)

    while Q.IsNotEmpty() and pred[t] == None:
	v = Q.Top()
	for w in AnimatedNeighborhood(A,G,v):
	    if pred[w] == None and w != s:
		pred[w] = v
		Q.Append(w)

    if pred[t] == None: # No augmenting path found
	return None

    path = []
    v = t
    while pred[v] != None:
	A.SetVertexColor(v,"red")
	A.SetEdgeColor(pred[v],v,"red")
	path.append((pred[v],v))
	v = pred[v]
    A.SetVertexColor(v,"red")
    return path

