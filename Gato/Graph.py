################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   Graph.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################

from regsub import split
from GatoGlobals import *
from DataStructures import Point2D, VertexLabeling, EdgeLabeling, EdgeWeight
from math import log

################################################################################
#
# Graph
#
################################################################################
class Graph:
    """ Provides a mathematical graph object consisting of vertices 
        and (directed) edges connecting those vertices. Graphs have

	- a labeling for vertices allowing to specify names
	
	- an embedding of vertices into 2D-space

	- one or more sets of edge weights  

	Vertices are specified via id (integer number) and edges via
	(tail,head)-tuples 

	NOTE: ids are supposed to be consecutive and ranging from 0
	to G.Order() - 1 !!! Use the labeling to *display* other numbers
	for vertices.

	At least one set of edge weights is assumed to exist and accessible
	as self.edgeWeights[0]; self.euclidian and Euclidify refer to this
	self.edgeWeights[0]

    """

    def __init__(self):
	self.simple           = 1
	self.euclidian        = 1
	self.directed         = 0
	self.vertices         = [] 
	self.adjLists         = {}
	self.invAdjLists      = {}   # Inverse Adjazenzlisten
	self.highVertexID     = 0    # INTERNAL
 	self.embedding        = VertexLabeling() # 2D-Positions
	self.labeling         = VertexLabeling() # Names of vertices
	self.edgeWeights      = {}   # Dictionary of edge labellings
	self.edgeWeights[0]   = EdgeWeight(self)
	self.vertexWeights    = {}   # None by default
	self.size             = 0
	self.edgeWidth        = None
	self.vertexAnnotation = None
	self.edgeAnnotation   = None
	self.properties       = {}

    def AddVertex(self):
	""" Add an isolated vertex. Returns the id of the new vertex """
      	id = self.GetNextVertexID()	
	self.vertices.append(id)
	self.adjLists[id]    = []
	self.invAdjLists[id] = []
	return id


    def AddEdge(self,tail,head):
	""" Add an edge (tail,head). Returns nothing
	    Raises GraphNotSimpleError if
	    - trying to add a loop
	    - trying to add an edge multiply 

	    In case of directed graphs (tail,head) and (head,tail)
	    are distinct edges """

	if self.simple == 1 and tail == head: # Loop
	    raise GraphNotSimpleError
	if self.directed == 0 and tail in self.adjLists[head]: 
	    raise GraphNotSimpleError
	if head in self.adjLists[tail]: # Multiple edge
	    raise GraphNotSimpleError
	    
	self.adjLists[tail].append(head)
	self.invAdjLists[head].append(tail)
	self.size = self.size + 1


    def DeleteEdge(self,tail,head):
	""" Deletes edge (tail,head). Does *not* handle undirected graphs
	    implicitely. Raises NoSuchEdgeError upon error. """

	try:
	    self.adjLists[tail].remove(head)
	    self.invAdjLists[head].remove(tail)
	    self.size = self.size - 1
	except KeyError:
	    raise NoSuchEdgeError


    def Edge(self,tail,head):
	"""  Handles undirected graphs by return correct ordered
	     vertices as (tail,head). Raises NoSuchEdgeError upon error. """

	try:
	    if head in self.adjLists[tail]:
		return (tail,head)
	    if self.directed == 0 and tail in self.adjLists[head]:
		return (head,tail)
	except KeyError:
	    raise NoSuchEdgeError

    def QEdge(self,tail,head):
	""" Returns 1 if (tail,head) is an edge in G. If G is undirected
            order of vertices does not matter """
	if self.directed == 1:	
	    return head in self.adjLists[tail]
	else: 
	    return head in self.adjLists[tail] or tail in self.adjLists[head]


    def Neighborhood(self,v):
	""" Returns the vertices which are connected to v. Does handle
	    undirected graphs (i.e., returns vertices w s.t. either 
	    (v,w) or (w,v) is an edge) """
	
	if self.directed:
	    return self.OutNeighbors(v)
	else:
	    return self.InOutNeighbors(v)


    def InNeighbors(self,v):
	""" Returns vertices w for which (w,v) is an edge """
	return self.invAdjLists[v]


    def OutNeighbors(self,v):
	""" Returns vertices w for which (v,w) is an edge """
	return self.adjLists[v]


    def InOutNeighbors(self,v):
	""" Returns vertices w for which (v,w) or (w,v) is an edge """	
	return self.InNeighbors(v) + self.OutNeighbors(v)


    def InEdges(self,v):
	""" Returns edges (*,v) """	
	f = lambda x, vertex = v : (x,vertex)
	return map(f, self.invAdjLists[v])


    def OutEdges(self,v):
	""" Returns edges (v,*) """	
	f = lambda x, vertex = v : (vertex,x)
	return map(f ,self.adjLists[v])

    
    def IncidentEdges(self,v):
	""" Returns edges (v,*) and (*,v) """	
	return self.InEdges(v) + self.OutEdges(v)


    def Edges(self):
	""" Returns all edges """		
	tmp = []
	for v in self.vertices:
	    tmp = tmp + self.OutEdges(v)
	return tmp


    def printMy(self):
	""" Debugging only """
	for v in self.vertices:
	    print v, " -- ", self.adjLists[v]


    def GetNextVertexID(self):
	""" *Internal* returns next free vertex id """
       	self.highVertexID = self.highVertexID + 1
	return self.highVertexID


    def Order(self):
	""" Returns order i.e., the number of vertices """
	return len(self.vertices)


    def Size(self):
	""" Returns size i.e., the number of edge """
	return self.size 


    def QEuclidian(self):
	""" Returns 1 if the graph is euclidian, 0 else """
	return self.euclidian


    def QDirected(self):
	""" Returns 1 if the graph is directed, 0 else """
	return self.directed


    def CalculateWidthFromWeight(self, weightID = 0):
	""" Calculate width of edges (self.edgeWidth will be used by 
	    GraphDisplay if not none) from the specified set of edge
	    weights. 

            Default: weightID = 0 is used """

	self.edgeWidth = EdgeLabeling()
	edges = self.Edges()
	maxWeight = max(self.edgeWeights[weightID].label.values())
	for e in edges:
	    tmp = 1 + 35 * self.edgeWeights[weightID][e] / maxWeight 
	    self.edgeWidth[e] = tmp

    def NrOfEdgeWeights(self):
	return len(self.edgeWeights.keys())

    def NrOfVertexWeights(self):
	return len(self.vertexWeights.keys())

    def Euclidify(self):
	""" Replace edge weights with weightID = 0 with Euclidean distance 
            between incident vertices """

	for v in self.vertices:
	    for w in self.adjLists[v]:
		d = ((self.embedding[v].x - self.embedding[w].x)**2 + 
		     (self.embedding[v].y - self.embedding[w].y)**2)**(.5)

		if self.edgeWeights[0].QInteger():
		    self.edgeWeights[0][(v,w)] = int(round(d))
		else:
		    self.edgeWeights[0][(v,w)] = d

	self.euclidian = 1


    def Integerize(self, weightID = 0):
	""" Integerize: Make all edge weights integers """
	
	if weightID == 'all':
	    for w in self.edgeWeights.keys():
		self.edgeWeights[w].Integerize()
	else:
	    self.edgeWeights[weightID].Integerize()


    def Undirect(self):
	""" If (u,v) and (v,u) are edges in the directed graph, remove one of them.
            to make graph undirected (no multiple edges allowed). Which one gets
            deleted depends on ordering in adjacency lists. """
	if not self.directed:
	    return

	for v in self.vertices:
	    for w in self.adjLists[v]:
		if v in self.adjLists[w]:
		    self.DeleteEdge(w,v)
		
	self.directed = 0
	
    def SetProperty(self, name, val):
	""" Set the value of property 'name' to 'val' """
	self.properties[name] = val

    def Property(self,name):
	""" Return the value of property 'name'. If the property
           'name' has not been set 'Unknown' is returned """
	try:
	    return self.properties[name]
	except:
	    return 'Unknown'


################################################################################
#
# Induced Subgraph
#
################################################################################

class SubGraph(Graph):
    """ Provides a subgraph, i.e., a subset of the vertices and edges 
        of a specified graph

	Vertices are specified via ids from its supergraph and edges via
	(tail,head)-tuples 

	It also keeps track of the subgraphs total weight (= sum of edge 
	weights) for weights with weightID == 0
    """


    def __init__(self,G):
	Graph.__init__(self)
	self.superGraph    = G

	self.embedding     = self.superGraph.embedding
	self.labeling      = self.superGraph.labeling
	self.edgeWeights   = self.superGraph.edgeWeights

	self.totalWeight   = 0


    def AddVertex(self,v):
	""" Add a vertex from the supergraph to the subgraph.
	    Returns NoSuchVertexError if v does not exist in
	    supergraph """
	try:
	    self.vertices.append(v)
	    #f = lambda x, vertexList=self.vertices: x in vertexList
	    #self.adjLists[v]    = filter(f, self.superGraph.adjLists[v])
	    #self.invAdjLists[v] = filter(f, self.superGraph.invAdjLists[v])
	    self.adjLists[v]    = []
	    self.invAdjLists[v] = []
	except:
	    raise NoSuchVertexError

    def AddEdge(self,tail,head):
	""" Add an edge from the supergraph to the subgraph.
	    Will also add tail and/or head if there are not
	    already in subgraph """
	try:
	    if not tail in self.vertices:
		self.AddVertex(tail)
	    if not head in self.vertices:
		self.AddVertex(head)
	    (tail,head) = self.superGraph.Edge(tail,head) 

	    self.adjLists[tail].append(head)
	    self.invAdjLists[head].append(tail)
	    self.size = self.size + 1
	    self.totalWeight =  self.totalWeight + self.superGraph.edgeWeights[0][(tail,head)]
	    
	except (KeyError, NoSuchVertexError, NoSuchEdgeError):
	    raise NoSuchEdgeError
	    #print "SubGraph.AddEdge",(tail,head)
	    #print self.superGraph.vertices
	    #print self.vertices
	    #print self.superGraph.adjLists
	    #print self.adjLists


    def AddSubGraph(self,G):
	""" Add subgraph G to self. Will do nothing if self and G 
	    have distinct supergraphs """
	if self.superGraph != G.superGraph:
	    print "SubGraph->Add: distinct superGraphs"
	    return
	for v in G.vertices:
	    self.AddVertex(v)
	for e in G.Edges():
	    self.AddEdge(e[0],e[1])


    def DeleteEdge(self,tail,head):
	""" Delete edge from subgraph. Raises NoSuchEdgeError
	    upon error """
	if tail in self.vertices and head in self.vertices:
	    self.totalWeight =  self.totalWeight - self.superGraph.edgeWeights[0][(tail,head)]
	    self.adjLists[tail].remove(head)
	    self.invAdjLists[head].remove(tail)
	    self.size = self.size - 1
	else:
	    raise NoSuchEdgeError

    def GetNextVertexID(self):
	""" *Internal* safeguard """
	print "Induced Subgraph -> GetNextVertexID should never have been called"

    def Weight(self):
	""" Returns the total weight (= sum of edge weights) of subgraph """
	return self.totalWeight


    def QEuclidian(self):
	""" Returns 1 if the super graph is euclidian, 0 else """
	return self.superGraph.euclidian


    def QDirected(self):
	""" Returns 1 if the super graph is directed, 0 else"""
	return self.superGraph.directed

    def QEdge(self,tail,head):
	""" Returns 1 if (tail,head) is an edge in G """
	if not tail in self.vertices or not head in self.vertices:
	    return 0
	if self.directed == 1:	
	    return head in self.adjLists[tail]
	else: 
	    return head in self.adjLists[tail] or tail in self.adjLists[head]


