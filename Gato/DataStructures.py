################################################################################
#
#       This is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/Gato
#
#	file:   DataStructures.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################


from GatoGlobals import *


################################################################################
#
# Embedding
#
################################################################################
class Point2D:
    """ Simple Wrapper class for a point in 2D-space. Used for Graph
        Embeddings. """
    def __init__(self, x = 0, y = 0):
	self.x = x
	self.y = y

			
################################################################################
#
# Vertex Labeling
#
################################################################################
class VertexLabeling:
    """ Simple Wrapper class for any mapping of vertices to values.
        E.g.,
	
	- strings (for labels)
        - Point2D (for embeddings) """

    def __init__(self):
	self.label = {}
	
    def __setitem__(self, v, val):
	self.label[v] = val
	
    def __getitem__(self, v):
	return self.label[v]

    def QDefined(self,v):
	return v in self.label.keys()

class VertexWeight(VertexLabeling):

    def __init__(self, theGraph, initialWeight = None):
	VertexLabeling.__init__(self)
	self.G = theGraph
	self.integer = 0
	if initialWeight is not None:
	    self.SetAll(initialWeight)

    def QInteger(self):
	""" Returns 1 if all weights are integers, 0 else """
	return self.integer

    def Integerize(self):
	if not self.integer:
	    for v in self.label.keys():
		self.label[v] = int(round(self.label[v]))
	    self.integer = 1	

    def SetAll(self, initialWeight):
	for v in self.G.vertices:
	    self.label[v] = initialWeight
	   


################################################################################
#
# Edge Labeling
#
################################################################################
class EdgeLabeling:
    """ Simple wrapper class for any mapping of edges to values.
        E.g.,
	
	- draw edges (for GraphDisplay)
        - weights (for embeddings) 

	Use EdgeLabeling[(u,v)] for access """

    def __init__(self):
	self.label = {}
	
    def __setitem__(self, e, val): # Use with (tail,head)
	self.label[e] = val
	
    def __getitem__(self, e): 
	return self.label[e]

    def QDefined(self,e):
	return e in self.label.keys()


class EdgeWeight(EdgeLabeling):
    """ Simple class for storing edge weights.
          
	Use EdgeWeight[(u,v)] for access, undirected graphs are
	handled properly. """

    def __init__(self, theGraph, initialWeight = None):
	EdgeLabeling.__init__(self)
	self.G       = theGraph
	self.integer = 0
	if initialWeight is not None:
	    self.SetAll(initialWeight)

    def __setitem__(self, e, val): # Use with (tail,head)
	if self.G.QDirected():
	    self.label[e] = val
	else:
	    try:
		tmp = self.label[(e[1], e[0])]
		self.label[(e[1], e[0])] = val
	    except KeyError:
		self.label[e] = val
	
    def __getitem__(self, e): 
	if self.G.QDirected():
	    return self.label[e]
	else:
	    try:
		return self.label[(e[1], e[0])]
	    except KeyError:
		return self.label[e]

    def QInteger(self):
	""" Returns 1 if all weights are integers, 0 else """
	return self.integer
	   
    def Integerize(self):
	if not self.integer:
	    for e in self.label.keys():
		self.label[e] = int(round(self.label[e]))
	    self.integer = 1	
	    
    def SetAll(self, initialWeight):
	for e in self.G.Edges():
	    self.label[e] = initialWeight
  


################################################################################
#
# Queue
#
################################################################################
class Queue:
    """ Simple Queue class implemented as a Python list """

    def __init__(self):
	self.contents = []

    def Append(self,v):
	self.contents.append(v)

    def Top(self):
	v = self.contents[0]
	self.contents = self.contents[1:]
	return v

    def Clear(self):
	self.contents = []

    def IsEmpty(self):
	return (len(self.contents) == 0)

    def IsNotEmpty(self):
	return (len(self.contents) > 0)

    def Contains(self,v):
	return v in self.contents


################################################################################
#
# Stack
#
################################################################################
class Stack:
    """ Simple Stack class implemented as a Python list """

    def __init__(self):
	self.contents = []

    def Push(self,v):
	self.contents.append(v)

    def Pop(self):
	v = self.contents[-1]
	self.contents = self.contents[:-1]
	return v

    def Clear(self):
	self.contents = []

    def IsEmpty(self):
	return (len(self.contents) == 0)

    def IsNotEmpty(self):
	return (len(self.contents) > 0)

    def Contains(self,v):
	return v in self.contents
