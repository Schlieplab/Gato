################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   AnimatedAlgorithms.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       Copyright (C) 1998-2002, Alexander Schliep, Winfried Hochstaettler and 
#       ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@zpr.uni-koeln.de, wh@zpr.uni-koeln.de             
#
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
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

