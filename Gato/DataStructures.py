################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   DataStructures.py
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


################################################################################
#
# Embedding
#
################################################################################
class Point2D:
    """ Simple Wrapper class for a point in 2D-space. Used for Graph
        Embeddings.  Use: Point2D([x,y]) or Point2D(x,y) """
    def __init__(self, x = None, y = None):	
	if y == None:
	    if x == None:
		self.x = 0
		self.y = 0
	    else:
		self.x = x[0]
		self.y = x[1]
	
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

    def keys(self):
	return self.label.keys()

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

    def __init__(self, elems=None):
	if elems == None: 
	    self.contents = []
	else:
	    self.contents = elems[:]

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

################################################################################
#
# Set
#
################################################################################
class Set:
    def __init__(self):
        self.members = []
        return

    def __getitem__(self,key):
	return self.members[key]

    def Add(self, e):
	self.members.append(e)
        return
 		
    def Delete(self, e):
	try:
            self.members.remove(e)
        except:
            None
        return

    def IsNotEmpty(self):
	return len(self.members) > 0

    def Contains(self,e):
	return e in self.members
