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
import copy


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

        if a blinkColor is specified the edge will blink
	"""

    def __init__(self,theAnimator,G,v,leaveColors = [],blinkColor=None):	
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
	self.Animator = theAnimator
	self.nbh = G.Neighborhood(v)
	self.v = v
	self.leaveColors = leaveColors
	self.blinkColor = blinkColor

    def __getitem__(self, i):
	if i < len(self.nbh):
	    if self.blinkColor != None:
		self.Animator.BlinkEdge(self.v,self.nbh[i],self.blinkColor)
	    c = self.Animator.GetEdgeColor(self.v,self.nbh[i])
	    if c not in self.leaveColors:
		self.Animator.SetEdgeColor(self.v,self.nbh[i],cTraversedEdge)
	    return self.nbh[i]
	else:
	    raise IndexError

    def __len__(self):
	return len(self.nbh)


class BlinkingNeighborhood:
    """ Visualizes visiting blinking (v,w) for all w when iterating over
        the Neighborhood

	#Neighborhood = lambda v,a=A,g=G: BlinkingNeighborhood(a,g,v,c)
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
	else:
	    raise IndexError

    def __len__(self):
	return len(self.nbh)

class BlinkingTrackLastNeighborhood(BlinkingNeighborhood):
    """ Visualizes visiting blinking (v,w) for all w when iterating over
        the Neighborhood. It also temporarily keeps the the last blinked
        edge grey

        #Neighborhood = lambda v,a=A,g=G: BlinkingTrackLastNeighborhood(a,g,v,c,track)
	#
	#for w in Neighborhood(v):
	#    doSomething
	will blink all edges with color c, the last blinked is tracked with color 
        track """
    old = None


    def __init__(self,theAnimator,G,v,c,track="grey"):
	BlinkingNeighborhood.__init__(self,theAnimator,G,v,c)
	self.trackColor = track

    def __getitem__(self, i):
	if BlinkingTrackLastNeighborhood.old != None and i < len(self.nbh): 
	    old = BlinkingTrackLastNeighborhood.old
	    self.Animator.SetEdgeColor(old[0],old[1],old[2])
	    
	BlinkingTrackLastNeighborhood.old = (self.v,self.nbh[i],
					     self.Animator.GetEdgeColor(self.v,self.nbh[i]))
	retVal = BlinkingNeighborhood.__getitem__(self,i)
	self.Animator.SetEdgeColor(self.v,self.nbh[i],self.trackColor)

	return retVal
   

class BlinkingContainerWrapper:
    """ Visualizes iterating over a list of vertices and/or edges by
        blinking.

	#List = lambda l, a=A: BlinkingContainerWrapper(a,l,color)
	#
	#for w in List:
	#    doSomething
	"""

    def __init__(self, theAnimator, l,  color=cOnQueue):	
	self.Animator = theAnimator
	self.list = copy.copy(l)
	self.color = color
	
    def __getitem__(self, i):
	if i < len(self.list):
	    item = self.list[i]
	    if type(item) == type(2): # vertex
		self.Animator.BlinkVertex(item,self.color)
	    else:
		self.Animator.BlinkEdge(item[0],item[1],self.color)
	    return item
	else:
	    raise IndexError

    def __len__(self):
	return len(self.list)


class ContainerWrapper(BlinkingContainerWrapper):
    """ Visualizes iterating over a list of vertices and/or edges by
        coloring. If color has changed in the meantime the original
        color will not be set again.

	#List = lambda l, a=A: ContainerWrapper(a,l,color)
	#
	#for w in List:
	#    doSomething
	"""

    def __init__(self, theAnimator, l, color=cOnQueue):
        BlinkingContainerWrapper.__init__(self,theAnimator,l,color)	
        self.lastitem  = None
        self.lastcolor = None
	
    def __getitem__(self, i):
	if i < len(self.list):
	    item = self.list[i]
	    if type(item) == type(2): # vertex
                dummy = self.Animator.GetVertexColor(item)
		if (self.lastitem != None) and (self.Animator.GetVertexColor(self.lastitem) == self.color):
                    self.Animator.SetVertexColor(self.lastitem,self.lastcolor)
		self.Animator.SetVertexColor(item,self.color)
                self.lastcolor = dummy
	    else:
                dummy = self.Animator.GetEdgeColor(item[0],item[1])
		if (self.lastitem != None) and (self.Animator.GetEdgeColor(self.lastitem[0],self.lastitem[1]) == self.color):
                    self.Animator.SetEdgeColor(self.lastitem[0],self.lastitem[1],self.lastcolor)
		self.Animator.SetEdgeColor(item[0],item[1],self.color)
                self.lastcolor = dummy
            self.lastitem = item
	    return item
	else:
	    raise IndexError
                         

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

    def __init__(self, theAnimator, initial=0):
	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) 
            initial is the value to cause coloring in cInitial """
	VertexLabeling.__init__(self)
	self.Animator = theAnimator
	self.initial=initial

    def __setitem__(self, v, val):
	VertexLabeling.__setitem__(self, v, val)
	if val == self.initial or val == None or val == gInfinity:
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

    def Clear(self, color="grey"):
	""" Delete all vertices and edges from the animated subgraph. 
            and color them with 'color' (grey is default) """

        # GraphDisplay functions save several update()'s
        self.Animator.SetAllVerticesColor(color,self)
        self.Animator.SetAllEdgesColor(color,self)

	self.vertices         = [] 
	self.adjLists         = {}
	self.invAdjLists      = {}   # Inverse Adjazenzlisten
	self.size = 0
	self.totalWeight   = 0


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
	    try:
	        self.Animator.SetEdgeColor(val,v,"red")
            except:
                None
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
    
    while (pred[v] != None) and (pred[v] != v):
	A.SetVertexColor(v,color)
	A.SetEdgeColor(pred[v],v,color)
	v = pred[v]

    A.SetVertexColor(v,color)

################################################################################
#
# Wrapper
#
################################################################################

class FlowWrapper:
    """ This class visualizes the flow in a directed graph G
        with animator GA and it's residual network R with
        animator RA.

        res     = R.edgeWeights[0] 
        cap     = {}
        flow    = FlowWrapper(G,A,R,RA,G.edgeWeights[0],cap,res)
    """
    def __init__(self,  G, GA, R, RA, flow, cap, res):
        self.G    = G
        self.GA   = GA
        self.R    = R
        self.RA   = RA
        self.flow = flow
        self.cap  = cap
        self.res  = res
	for e in self.G.Edges():
            self.cap[e]  = self.flow[e]
            self.res[e]  = self.flow[e] 
	    self.flow[e] = 0

    def __setitem__(self, e, val):  
        self.flow[e] = val
        if val == self.cap[e]:     
            self.GA.SetEdgeColor(e[0],e[1],"blue")
            self.GA.SetEdgeAnnotation(e[0],e[1],"%d/%d" % (val,self.cap[e]),"black")
	    try:
                self.RA.DeleteEdge(e[0],e[1])
            except:
                None
            if not self.R.QEdge(e[1],e[0]):
                self.RA.AddEdge(e[1],e[0])
        elif val == 0:             
            self.GA.SetEdgeColor(e[0],e[1],"black")
            self.GA.SetEdgeAnnotation(e[0],e[1],"%d/%d" % (val, self.cap[e]),"gray")
	    try:
                self.RA.DeleteEdge(e[1],e[0])
            except:
                None
            if not self.R.QEdge(e[0],e[1]):
                self.RA.AddEdge(e[0],e[1])
        else:                      
            self.GA.SetEdgeColor(e[0],e[1],"#AAAAFF")
            self.GA.SetEdgeAnnotation(e[0],e[1],"%d/%d" % (val,self.cap[e]),"black")
            if not self.R.QEdge(e[1],e[0]):
                self.RA.AddEdge(e[1],e[0])
            if not self.R.QEdge(e[0],e[1]):
                self.RA.AddEdge(e[0],e[1])
	if self.G.QEdge(e[0],e[1]):
            self.res[(e[1],e[0])]  = val
            self.res[(e[0],e[1])]  = self.cap[(e[0],e[1])] - val
        else:
            self.res[(e[0],e[1])]  = val
            self.res[(e[1],e[0])]  = self.cap[(e[1],e[0])] - val
        return

    def __getitem__(self, e):
        return self.flow[e]

