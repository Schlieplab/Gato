################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   AnimatedDataStructures.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
from GatoGlobals import *
from DataStructures import VertexLabeling, Queue, Stack
from Graph import SubGraph

class Animator:
    """ *Debugging* Text only Animator providing animation functions which
        only print to console """

    def SetVertexColor(self,v, color):
	print "set color of",v," to ",color
	
    def SetEdgeColor(self, tail, head, color):
	print "set color of edge (",tail,",", head ,") to ",color
	

class AnimatedNeighborhood:
    """ Visualizes visiting of neighbors by calling the Neighborhood
        method of graph for v and allowing to iterate over it, while 
	coloring (v,w) cTraversedEdge unless (v,w) is colored with
	one of the colors in leaveColors.

	#Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v,['red'])
	#
	#for w in Neighborhood(v):
	#    doSomething
	will color all edges cTraversedEdge unless the edge has been colored
	'red' at some point
	"""

    def __init__(self,theAnimator,G,v,leaveColors = []):	
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	self.Animator = theAnimator
	self.nbh = G.Neighborhood(v)
	self.v = v
	self.leaveColors = leaveColors
	
    def __getitem__(self, i):
	if i < len(self.nbh):
	    c = self.Animator.GetEdgeColor(self.v,self.nbh[i])
	    if c not in self.leaveColors:
		self.Animator.SetEdgeColor(self.v,self.nbh[i],cTraversedEdge)
	    return self.nbh[i]
	else:
	    raise IndexError

    def len(self):
	return len(self.nbh)


class BlinkingNeighborhood:
    """ Visualizes visiting blinking (v,w) for all w when iterating over
        the Neighborhood

	#Neighborhood = lambda v,a=A,g=G: BlinkingNeighborhood(a,g,v)
	#
	#for w in Neighborhood(v):
	#    doSomething
	will blink all edges"""

    def __init__(self,theAnimator,G,v,c):	
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	self.Animator = theAnimator
	self.nbh = G.Neighborhood(v)
	self.v = v
	self.color = c
	
    def __getitem__(self, i):
	if i < len(self.nbh):
	    self.Animator.BlinkEdge(self.v,self.nbh[i],self.color)
	return self.nbh[i]

    def len(self):
	return len(self.nbh)


class AnimatedVertexLabeling(VertexLabeling):
    """ Visualizes changes of values of the VertexLabeling
        by changing vertex colors appropriately.

	E.g.,
	#d = AnimatedVertexLabeling(A) 
	#d[v] = 0
	will color v cInitial.

	The coloring used for d[v] = val 
	- cInitial if val = 0,None,gInfinity
	- "blue" else """

    def __init__(self, theAnimator):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	VertexLabeling.__init__(self)
	self.Animator = theAnimator

    def __setitem__(self, v, val):
	VertexLabeling.__setitem__(self, v, val)
	if val == 0 or val == None or val == gInfinity:
	    self.Animator.SetVertexColor(v,cInitial)
	else:
	    self.Animator.SetVertexColor(v,"blue") #cVisited)


class BlinkingVertexLabeling(VertexLabeling):
    """ Visualizes changes of values of the VertexLabeling
        by blinking vertices """

    def __init__(self, theAnimator):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	VertexLabeling.__init__(self)
	self.Animator = theAnimator

    def __setitem__(self, v, val):
	VertexLabeling.__setitem__(self, v, val)
	if val == 0:
	    self.Animator.BlinkVertex(v)
	else:
	    self.Animator.BlinkVertex(v)


class AnimatedVertexQueue(Queue):
    """ Visualizes status of vertices in relation to the Queue by
        coloring them

	- cOnQueue if they are in the queue
	- cRemovedFromQueue if they have been on the queue and were
	  removed """

    def __init__(self, theAnimator, color=cOnQueue):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	Queue.__init__(self)
	self.Animator = theAnimator
	self.Color = color
	self.lastRemoved = None

    def Append(self,v):
	Queue.Append(self,v)
	self.Animator.SetVertexColor(v,self.Color)

    def Top(self):
	v = Queue.Top(self)
	self.Animator.SetVertexColor(v,cRemovedFromQueue)
	if self.lastRemoved is not None:
	    self.Animator.SetVertexFrameWidth(self.lastRemoved,gVertexFrameWidth)
	self.Animator.SetVertexFrameWidth(v,6)
	self.lastRemoved = v 
	return v

    def Clear(self):
	for v in self.contents:
	    self.Animator.SetVertexColor(v,cRemovedFromQueue)
	Queue.Clear(self) 


class AnimatedVertexStack(Stack):
    """ Visualizes status of vertices in relation to the Stack by
        coloring them

	- cOnQueue if they are in the queue
	- cRemovedFromQueue if they have been on the queue and were
	  removed """

    def __init__(self, theAnimator, color=cOnQueue):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	Stack.__init__(self)
	self.Animator = theAnimator
	self.Color = color
	self.lastRemoved = None

    def Push(self,v):
	Stack.Push(self,v)
	self.Animator.SetVertexColor(v,self.Color)

    def Pop(self):
	v = Stack.Pop(self)
	self.Animator.SetVertexColor(v,cRemovedFromQueue)
	if self.lastRemoved is not None:
	    self.Animator.SetVertexFrameWidth(self.lastRemoved,gVertexFrameWidth)
	self.Animator.SetVertexFrameWidth(v,6)
	self.lastRemoved = v 
	return v

    def Clear(self):
	for v in self.contents:
	    self.Animator.SetVertexColor(v,cRemovedFromQueue)
	Stack.Clear(self) 


class AnimatedVertexSet:
    """ Visualizes status of vertices in relation to the Set by
        coloring them

	- cVisited  if they have been in the set and were
	  removed """

    def __init__(self, theAnimator, vertexSet=None):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	if vertexSet == None:
	    self.vertices = []
	else:
	    self.vertices = vertexSet
	self.Animator = theAnimator
	
    def Set(self, vertexSet):
	""" Sets the set equal to a copy of vertexSet """
	self.vertices = vertexSet[:]
		
    def Remove(self, v):
	self.Animator.SetVertexColor(v,cVisited)
	self.vertices.remove(v)

    def Add(self,v):
	""" Add a single vertex v """
	self.vertices.append(v)
	
    def IsNotEmpty(self):
	return len(self.vertices) > 0

    def IsEmpty(self):
	return len(self.vertices) == 0

    def Contains(self,v):
	return v in self.vertices


class AnimatedEdgeSet:
    """ Visualizes status of edges in relation to the Set by
        coloring them

	- 'blue' if they are added to the set
	- cVisited  if they have been in the set and were
	  removed """

    def __init__(self, theAnimator,edgeSet=None):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	if edgeSet == None:
	    self.edges = []
	else:
	    self.edges = edgeSet	    
	self.Animator = theAnimator

    def __len__(self):
	return len(self.edges)

    def __getitem__(self,key):
	return self.edges[key]
		
    def Set(self, edgeSet):
	""" Sets the set equal to a copy of edgeSet """
	self.edges = edgeSet[:]

    def AddEdge(self, e):
	self.Animator.SetEdgeColor(e[0],e[1],"blue")
	self.edges.append(e)
 		
    def Remove(self, e):
	self.Animator.BlinkEdge(e[0],e[1],cVisited)
	self.Animator.SetEdgeColor(e[0],e[1],cVisited)
	self.edges.remove(e) 

    def IsNotEmpty(self):
	return len(self.edges) > 0

    def Contains(self,e):
	return e in self.edges


class AnimatedSubGraph(SubGraph):
    """ Visualizes status of vertices and edges in relation to the SubGraph by
        coloring them
        - color (default is 'blue') if they are added to the SubGraph """

    def __init__(self, G, theAnimator, color="blue"):
	""" color is used to color vertices and edges in the subgraph.
	    theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        SubGraph.__init__(self, G)
	self.Animator = theAnimator
	self.Color = color

    def AddVertex(self,v):
	 try:
	     SubGraph.AddVertex(self,v)
	     self.Animator.SetVertexColor(v,self.Color)
	     self.Animator.DefaultInfo()
	 except NoSuchVertexError:
	     return

    def AddEdge(self,edge,head=None):
	 # Poor mans function overload
	 if head == None and len(edge) == 2:
	     t = edge[0]
	     h = edge[1]
	 else:
	     t = edge
	     h = head
	 try:
	     SubGraph.AddEdge(self,t,h)
	     self.Animator.SetEdgeColor(t,h,self.Color)
	     self.Animator.DefaultInfo()
	 except NoSuchVertexError, NoSuchEdgeError:
	     return

    def DeleteEdge(self,edge,head=None):
	 if head == None and len(edge) == 2:
	     t = edge[0]
	     h = edge[1]
	 else:
	     t = edge
	     h = head
	 try:
	     SubGraph.DeleteEdge(self,t,h)
	     self.Animator.SetEdgeColor(t,h,"black")
	 except NoSuchVertexError, NoSuchEdgeError:
	     return


    def AddEdgeByVertices(self,tail,head):
	 try:
	     SubGraph.AddEdge(self,tail,head)
	     self.Animator.SetEdgeColor(tail,head,self.Color)
	     self.Animator.DefaultInfo()
	 except NoSuchVertexError, NoSuchEdgeError:
	     return



class AnimatedPredecessor(VertexLabeling):
    """ Animates a predecessor array by 

        - coloring edges (pred[v],v) 'red' 
        - coloring edges (pred[v],v) 'grey' if the value of
	  pred[v] is changed """

    def __init__(self,theAnimator):
	VertexLabeling.__init__(self)
	self.Animator = theAnimator
	
    def __setitem__(self, v, val):
	try:
	    oldVal = VertexLabeling.__getitem__(self, v)
	    if oldVal != None:
		self.Animator.SetEdgeColor(oldVal,v,"grey")
	except:
	    i = 0 
	if val != None:
	    self.Animator.SetEdgeColor(val,v,"red")
	    VertexLabeling.__setitem__(self, v, val)
     


class ComponentMaker:
    """ Subsequent calls of method NewComponent() will return differently
        colored subgraphs of G """
    def __init__(self,g,a):
	self.G = g
	self.A = a
	self.colors = ['#FF0000','#00FF00','#0000FF', # Triangle
		       '#999910','#991099','#109999', # Midpoints
		       '#DD6610','#996666','#DD1066', # lower left
		       '#666699','#1066DD','#6610DD', # lower right
		       '#669966','#66DD10','#10DD66'] # Upper
	self.lastColor = 0

    def NewComponent(self):
	comp = AnimatedSubGraph(self.G, self.A, self.colors[self.lastColor])
	self.lastColor = self.lastColor + 1
	if self.lastColor == len(self.colors):
	    self.lastColor = 0
	return comp
	

################################################################################
#
# Functions
#
################################################################################

def showPathByPredecessorArray(source,sink,pred,A,color="red"):
    """ Visualizes a path from source to sink in a graph G
        displayed in A. The path is specified in terms of the
	predecessor array pred and will be colored with color
	(default is 'red') """

    v = sink
    
    while pred[v] != None:
	A.SetVertexColor(v,color)
	A.SetEdgeColor(pred[v],v,color)
	v = pred[v]

    A.SetVertexColor(v,color)



