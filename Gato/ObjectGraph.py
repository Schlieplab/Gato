################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   ObjectGraph.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 2006, Alexander Schliep
#                                   
#       Contact: alexander@schliep.org             
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
from DataStructures import Point2D, VertexLabeling, EdgeLabeling, EdgeWeight
#from math import log

import logging
log = logging.getLogger("ObjectGraph.py")

################################################################################
#
# Base classes
#
################################################################################

class VertexObject:
     # Python 2.3 kludge
    def nrOfVertexWeights():
        return 0
    NrOfVertexWeights = staticmethod(nrOfVertexWeights)

    def __init__(self):
        self.id = None
        self.embedding = None
        self.labeling = None
        self.inEdges = []
        self.outEdges = []
           


class EdgeObject:
    # Python 2.3 kludge
    def nrOfEdgeWeights():
        return 2
    NrOfEdgeWeights = staticmethod(nrOfEdgeWeights)

    def __init__(self, tail, head):
        self.tail = tail
        self.head = head
        self.weight = 0.0

    def key(self):
        return (self.tail.id, self.head.id)

    def GetEdgeWeight(self,i):
        if i == 0:
            return self.weight

    def SetEdgeWeight(self,i,value):
        if i == 0:
            self.weight = value
        

        


################################################################################
#
# ObjectGraph
#
################################################################################
class ObjectGraph:
    """ 

    
    """
    
    def __init__(self, vertexClass, edgeClass):
        self.vertexClass = vertexClass
        self.edgeClass = edgeClass
        self.vertices = {}
        self.edges = {}
        self.highVertexID     = 0    # INTERNAL
        self.simple           = 1
        self.euclidian        = 1
        self.directed         = 0


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
        v = self.vertexClass()
        v.id = self.GetNextVertexID()
        self.vertices[v.id] = v
        return v.id
        
    def DeleteVertex(self, v):
        """ Delete the vertex v and its incident edges """
        outEdges = self.vertices[v].outEdges[:] # Need a copy here
        inEdges = self.vertices[v].inEdges[:]
        for e in outEdges:
            (v,w) = e.key()
            self.DeleteEdge(v,w)
        for e in inEdges:
            (w,v) = e.key()            
            if w != v: # We have already deleted loops
                self.DeleteEdge(w,v)
        del(self.vertices[v])
        
    def QVertex(self, v):
        """ Check whether v is a vertex """
        return v in self.vertices.keys()

        
    def AddEdge(self,tail,head):
        """ Add an edge (tail,head). Returns nothing
            Raises GraphNotSimpleError if
            - trying to add a loop
            - trying to add an edge multiply 
        
            In case of directed graphs (tail,head) and (head,tail)
            are distinct edges """
        
        if self.simple == 1 and tail == head: # Loop
            raise GraphNotSimpleError, '(%d,%d) is a loop' % (tail,head)
        if self.directed == 0 and self.edges.has_key((head,tail)):
            raise GraphNotSimpleError, '(%d,%d) is already an undirected edge' % (head,tail)
        if self.edges.has_key((tail,head)): # Multiple edge
            raise GraphNotSimpleError, '(%d,%d) is already an directed edge' % (tail,head)

        e = self.edgeClass(self.vertices[tail],self.vertices[head])
        self.edges[(tail,head)] = e
        self.vertices[tail].outEdges.append(e)
        self.vertices[head].inEdges.append(e)

        if self.QEuclidian():
            t = self.GetEmbedding(tail)
            h = self.GetEmbedding(head)
            self.SetEdgeWeight(0,tail,head,sqrt((h.x - t.x)**2 + (h.y - t.y)**2))
        else:
            self.SetEdgeWeight(0,tail,head,0)
        for i in xrange(1,self.NrOfEdgeWeights()):
            self.SetEdgeWeight(i,tail,head,0)

        
    def DeleteEdge(self,tail,head):
        """ Deletes edge (tail,head). Does *not* handle undirected graphs
            implicitely. Raises NoSuchEdgeError upon error. """

        try:
            e = self.edges[(tail,head)]
        except KeyError:
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)

        self.vertices[tail].outEdges.remove(e)
        self.vertices[head].inEdges.remove(e)
        del(self.edges[(tail,head)])
            
            
    def Edge(self,tail,head):
        """  Handles undirected graphs by returning correctly ordered
             vertices as (tail,head). Raises NoSuchEdgeError upon error. """
        
        if tail not in self.vertices.keys() or head not in self.vertices.keys():
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
        if self.edges.has_key((tail,head)):
            return (tail,head)
        elif self.directed == 0 and self.edges.has_key((head,tail)):
            return (head,tail)
        else:
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
            
    def QEdge(self,tail,head):
        """ Returns 1 if (tail,head) is an edge in G. If G is undirected
            order of vertices does not matter """
        if self.directed == 1:	
            return self.edges.has_key((tail,head))
        else: 
            return self.edges.has_key((tail,head)) or self.edges.has_key((head,tail))


    def QEdgeWidth(self):
        """ Returns 1 if individual edge widths are defined, 0 else """
        return 0 # XXX NOT SUPPORTED
        

    def EdgeWidth(self, tail, head):
        return 0 # XXX NOT SUPPORTED 

            
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
        return map(lambda e: e.tail.id, self.vertices[v].inEdges)
        
        
    def OutNeighbors(self,v):
        """ Returns vertices w for which (v,w) is an edge """
        return map(lambda e: e.head.id, self.vertices[v].outEdges)
        
        
    def InOutNeighbors(self,v):
        """ Returns vertices w for which (v,w) or (w,v) is an edge """	
        return self.InNeighbors(v) + self.OutNeighbors(v)
        
        
    def InEdges(self,v):
        """ Returns edges (*,v) """	
        return map(lambda e: e.key(),self.vertices[v].inEdges) 
        
        
    def OutEdges(self,v):
        """ Returns edges (v,*) """	
        return map(lambda e: e.key(),self.vertices[v].outEdges) 
        
        
    def IncidentEdges(self,v):
        """ Returns edges (v,*) and (*,v) """	
        return self.InEdges(v) + self.OutEdges(v)
        
        
    def Edges(self):
        """ Returns all edges """		
        return self.edges.keys()

        
    def Vertices(self):
        """ Returns all edges """		
        return self.vertices.keys()
        
    def printMy(self):
        """ Debugging only """
        for v in self.vertices:
            print v, " -- ", self.adjLists[v]
            
            
    def GetNextVertexID(self):
        """ *Internal* returns next free vertex id """
        self.highVertexID += 1
        return self.highVertexID
        
        
    def Order(self):
        """ Returns order i.e., the number of vertices """
        return len(self.vertices.keys())
        
        
    def Size(self):
        """ Returns size i.e., the number of edge """
        return len(self.edges.keys()) 
        
        
    def Degree(self, v):
        """ Returns the degree of the vertex v, which is
            - the number of incident edges in the undirect case
            - the number of outgoing edges in the directed case """
        
        if self.directed:
            return len(self.vertices[v].outEdges)
        else:
            return len(self.vertices[v].outEdges) + len(self.vertices[v].inEdges)

            
    def InDegree(self, v):
        """ Returns the number of incoming edges for direct graphs """
        if self.directed:
            return len(self.vertices[v].inEdges)
        else:
            return None # Proper error to raise?
            
            
    def OutDegree(self, v):
        """ Returns the number of incoming edges for direct graphs """
        if self.directed:
            return len(self.vertices[v].outEdges)
        else:
            return None # Proper error to raise?
            
            
    def QEuclidian(self):
        """ Returns 1 if the graph is euclidian, 0 else """
        return self.euclidian
        
        
    def QDirected(self):
        """ Returns 1 if the graph is directed, 0 else """
        return self.directed
        
        
    def CalculateWidthFromWeight(self, scale, weightID = 0):
        """ Calculate width of edges (self.edgeWidth will be used by 
            GraphDisplay if not none) from the specified set of edge
            weights. 
        
            Default: weightID = 0 is used """
        pass  # XXX NOT SUPPORTED
##        self.edgeWidth = EdgeLabeling()
##        edges = self.Edges()
##        maxWeight = max(self.edgeWeights[weightID].label.values())
##        for e in edges:
##            self.edgeWidth[e] = scale * (1 + 35 * self.edgeWeights[weightID][e] / maxWeight) 
            
    def NrOfEdgeWeights(self):
        return self.edgeClass.NrOfEdgeWeights()

    def SetEdgeWeight(self,i,v,w,value):
        self.edges[(v,w)].SetEdgeWeight(i,value)

    def GetEdgeWeight(self,i,v,w):
        return self.edges[(v,w)].GetEdgeWeight(i)

    def QIntegerWeight(self,i):
        # Edge and Vertex class should take care of that ...class method
        return 0 # XXX UNSUPPORTED: FLOAT WEIGHTS ONLY. Barf
    

    def NrOfVertexWeights(self):
        return self.vertexClass.NrOfVertexWeights()

    def SetVertexWeight(self,i,v,value):
        pass 

    def GetVertexWeight(self,i,v):
        pass

    def GetLabeling(self,v):
        return self.vertices[v].labeling
    
    def SetLabeling(self,v, value):
        self.vertices[v].labeling = value

    def GetEmbedding(self,v):
        return self.vertices[v].embedding
    
    def SetEmbedding(self,v, x, y):
        self.vertices[v].embedding = Point2D(x,y)

                  
    def Euclidify(self):
        """ Replace edge weights with weightID = 0 with Euclidean distance 
            between incident vertices """
        pass  # XXX NOT SUPPORTED 
##        for v in self.vertices:
##            for w in self.adjLists[v]:
##                d = ((self.embedding[v].x - self.embedding[w].x)**2 + 
##                     (self.embedding[v].y - self.embedding[w].y)**2)**(.5)
                
##                if self.edgeWeights[0].QInteger():
##                    self.edgeWeights[0][(v,w)] = int(round(d))
##                else:
##                    self.edgeWeights[0][(v,w)] = d
                    
##        self.euclidian = 1
        
        
    def Integerize(self, weightID = 0):
        """ Integerize: Make all edge weights integers """
        pass  # XXX NOT SUPPORTED 
##        if weightID == 'all':
##            for w in self.edgeWeights.keys():
##                self.edgeWeights[w].Integerize()
##        else:
##            self.edgeWeights[weightID].Integerize()
            
            
    def Undirect(self):
        """ If (u,v) and (v,u) are edges in the directed graph, remove one of them.
            to make graph undirected (no multiple edges allowed). Which one gets
            deleted depends on ordering in adjacency lists. """
        if not self.directed:
            return
            
        for v in self.vertices.keys():
            for e in self.vertices[v].outEdges:
                w = e.head.id
                if v in self.OutNeighbors(w):
                    self.DeleteEdge(w,v)
                    
        self.directed = 0
        
    def SetProperty(self, name, val):
        """ Set the value of property 'name' to 'val' """
        pass # XXX NOT SUPPORTED 
        #self.properties[name] = val
        
    def Property(self,name):
        """ Return the value of property 'name'. If the property
           'name' has not been set 'Unknown' is returned """
        pass  # XXX NOT SUPPORTED 
        #try:
        #    return self.properties[name]
        #except:
        #    return 'Unknown'
            
    def About(self):
        """ Return string containing HTML code providing information
            about the graph """
        return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"
        
        
##        ################################################################################
##        #
##        # Induced Subgraph
##        #
##        ################################################################################
        
##class SubGraph(Graph):
##    """ Provides a subgraph, i.e., a subset of the vertices and edges 
##        of a specified graph
    
##        Vertices are specified via ids from its supergraph and edges via
##        (tail,head)-tuples 
    
##        It also keeps track of the subgraphs total weight (= sum of edge 
##        weights) for weights with weightID == 0
##    """
    
    
##    def __init__(self,G):
##        Graph.__init__(self)
##        self.superGraph    = G
        
##        self.embedding     = self.superGraph.embedding
##        self.labeling      = self.superGraph.labeling
##        self.edgeWeights   = self.superGraph.edgeWeights
        
##        self.directed = self.superGraph.directed
        
##        self.totalWeight   = 0
        
        
##    def AddVertex(self,v):
##        """ Add a vertex from the supergraph to the subgraph.
##            Returns NoSuchVertexError if v does not exist in
##            supergraph """
##        try:
##            self.vertices.append(v)
##            #f = lambda x, vertexList=self.vertices: x in vertexList
##            #self.adjLists[v]    = filter(f, self.superGraph.adjLists[v])
##            #self.invAdjLists[v] = filter(f, self.superGraph.invAdjLists[v])
##            self.adjLists[v]    = []
##            self.invAdjLists[v] = []
##        except:
##            raise NoSuchVertexError, "%d is not a vertex in the supergraph" % v
            
##    def AddEdge(self,tail,head):
##        """ Add an edge from the supergraph to the subgraph.
##            Will also add tail and/or head if there are not
##            already in subgraph """
##        try:
##            if not tail in self.vertices:
##                self.AddVertex(tail)
##            if not head in self.vertices:
##                self.AddVertex(head)
##            (tail,head) = self.superGraph.Edge(tail,head) 
            
##            self.adjLists[tail].append(head)
##            self.invAdjLists[head].append(tail)
##            self.size = self.size + 1
##            try:
##                w = self.superGraph.edgeWeights[0][(tail,head)]
##            except KeyError:
##                w = 0.0 # XXX we dont have w weight for the edge. Make totalWeight configurable/subclass
##            self.totalWeight += w
            
##        except (KeyError, NoSuchVertexError, NoSuchEdgeError):
##            raise NoSuchEdgeError, "(%d,%d) is not an edge in the supergraph." % (tail,head)
            
##    def AddSubGraph(self,G):
##        """ Add subgraph G to self. Will do nothing if self and G 
##            have distinct supergraphs """
##        if self.superGraph != G.superGraph:
##            log.error("AddSubGraph: distinct superGraphs")
##            return
##        for v in G.vertices:
##            self.AddVertex(v)
##        for e in G.Edges():
##            self.AddEdge(e[0],e[1])
            
            
##    def DeleteEdge(self,tail,head):
##        """ Delete edge from subgraph. Raises NoSuchEdgeError
##            upon error """
##        if tail in self.vertices and head in self.vertices:
##            superEdge = self.superGraph.Edge(tail,head)
##            self.totalWeight =  self.totalWeight - self.superGraph.edgeWeights[0][superEdge]
##            self.adjLists[tail].remove(head)
##            self.invAdjLists[head].remove(tail)
##            self.size = self.size - 1
##        else:
##            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
##    def Clear(self):
##        """ Delete all vertices and edges from the subgraph. """
##        self.vertices         = [] 
##        self.adjLists         = {}
##        self.invAdjLists      = {}   # Inverse Adjazenzlisten
##        self.size = 0
##        self.totalWeight   = 0
        
        
##    def GetNextVertexID(self):
##        """ *Internal* safeguard """
##        log.error("Induced Subgraph -> GetNextVertexID should never have been called")
        
##    def Weight(self):
##        """ Returns the total weight (= sum of edge weights) of subgraph """
##        return self.totalWeight
        
        
##    def QEuclidian(self):
##        """ Returns 1 if the super graph is euclidian, 0 else """
##        return self.superGraph.euclidian
        
        
##    def QDirected(self):
##        """ Returns 1 if the super graph is directed, 0 else"""
##        return self.superGraph.directed
        
##    def QEdge(self,tail,head):
##        """ Returns 1 if (tail,head) is an edge in G """
##        if not tail in self.vertices or not head in self.vertices:
##            return 0
##        if self.directed == 1:	
##            return head in self.adjLists[tail]
##        else: 
##            return head in self.adjLists[tail] or tail in self.adjLists[head]
            
            
