################################################################################
#
#       This is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/Gato
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
from Graph import Graph
from DataStructures import Point2D, VertexLabeling, EdgeLabeling, EdgeWeight, Queue

################################################################################
#
# Syntactic Sugar
#
################################################################################
def Vertices(G):
    """ Returns the vertices of G. Hide method call """
    return G.vertices

def Edges(G):
    """ Returns the edges of G. Hide method call """
    return G.Edges()


################################################################################
#
# Basic algorithms
#
################################################################################

def BFS(G,root,direction='forward'):
    """ Calculate BFS distances and predecessor without showing animations. 
        If G is directed, direction does matter:

        - 'forward'  BFS will use outgoing edges
        - 'backward' BFS will use incoming edges

	It uses gInfinity (from GatoGlobals.py) as infinite distance.
        returns (dist,pred) """

    Q = Queue()
    d = {}
    pred = {}

    for v in G.vertices:
	d[v] = gInfinity
    d[root] = 0
    pred[root] = None

    Q.Append(root)

    while Q.IsNotEmpty():
        v = Q.Top()
	for w in G.InNeighbors(v):
	    if d[w] == gInfinity:
		d[w] = d[v] + 1
		Q.Append(w)

    return (d,pred)






################################################################################
#
# GraphInformer
#
################################################################################


class GraphInformer:
    """ Provides information about edges and vertices of a graph.
        Used as argument for GraphDisplay.RegisterGraphInformer() """

    def __init__(self,G):
	self.G = G

    def DefaultInfo(self):
        """ Provide an default text which is shown when no edge/vertex
	    info is displayed """  
	return ""
	
    def VertexInfo(self,v):
        """ Provide an info text for vertex v """  
        return "Vertex %d at position (%d,%d)" % (v, 
                                                  self.G.embedding[v].x, 
                                                  self.G.embedding[v].y)
	
    def EdgeInfo(self,tail,head):
        """ Provide an info text for edge (tail,head)  """        
        return "Edge (%d,%d)" % (tail, head) 


class WeightedGraphInformer(GraphInformer):
    """ Provides information about weighted edges and vertices of a graph.
        Used as argument for GraphDisplay.RegisterGraphInformer() """

    def __init__(self,G,weightDesc="weight"):
	""" G is the graph we want to supply information about and weightDesc
	    a textual interpretation of the weight """
	GraphInformer.__init__(self,G)
	self.weightDesc = weightDesc
    
    def EdgeInfo(self,tail,head):
        """ Provide an info text for weighted edge (tail,head)  """  
        # How to handle undirected graph
        if self.G.QDirected() == 0:
            try:
                w = self.G.edgeWeights[0][(tail, head)]
            except KeyError:
                w = self.G.edgeWeights[0][(head, tail)]
        else:
            w = self.G.edgeWeights[0][(tail, head)]
	if self.G.edgeWeights[0].QInteger():
	    return "Edge (%d,%d) %s: %d" % (tail, head, self.weightDesc, w) 
	else:
	    return "Edge (%d,%d) %s: %f" % (tail, head, self.weightDesc, w) 


class MSTGraphInformer(WeightedGraphInformer):
    def __init__(self,G,T):
	WeightedGraphInformer.__init__(self,G)
	self.T = T

    def DefaultInfo(self):
        """ Provide an default text which is shown when no edge/vertex
	    info is displayed """  
	return "Spanning Tree has %d vertices and weight %5.2f" % (self.T.Order(),self.T.Weight())
		

################################################################################
#
# FILE I/O
#
################################################################################

def OpenCATBoxGraph(fileName):
    """ Reads in a graph from file fileName. File-format is supposed
        to be from old CATBOX++ (*.cat) """
    G = Graph()
    E = VertexLabeling()
    W = EdgeWeight(G)
    L = VertexLabeling()

    file = open(fileName, 'r')
    lineNr = 1

    firstVertexLineNr = -1    
    lastVertexLineNr  = -1
    firstEdgeLineNr   = -1
    lastEdgeLineNr    = -1

    while 1:
	
	line = file.readline()
	
	if not line:
	    break

	if lineNr == 2: # Read directed and euclidian
	    splitLine = split(line[:-1],';')	    
	    G.directed = eval(split(splitLine[0],':')[1])
	    G.simple = eval(split(splitLine[1],':')[1])
	    G.euclidian = eval(split(splitLine[2],':')[1])
	    intWeights = eval(split(splitLine[3],':')[1])
	    nrOfWeights = eval(split(splitLine[4],':')[1])
	    for i in xrange(nrOfWeights):
		G.edgeWeights[i] = EdgeWeight(G)

	if lineNr == 5: # Read nr of vertices
	    nrOfVertices = eval(split(line[:-2],':')[1]) # Strip of "\n" and ; 
	    firstVertexLineNr = lineNr + 1
	    lastVertexLineNr  = lineNr + nrOfVertices
	
	if  firstVertexLineNr <= lineNr and lineNr <= lastVertexLineNr: 
	    splitLine = split(line[:-1],';')
	    v = G.AddVertex()
	    x = eval(split(splitLine[1],':')[1])
	    y = eval(split(splitLine[2],':')[1])
	    E[v] = Point2D(x,y)
	    
	if lineNr == lastVertexLineNr + 1: # Read Nr of edges
	    nrOfEdges = eval(split(line[:-2],':')[1]) # Strip of "\n" and ; 
	    firstEdgeLineNr = lineNr + 1
       	    lastEdgeLineNr  = lineNr + nrOfEdges

	if firstEdgeLineNr <= lineNr and lineNr <= lastEdgeLineNr: 
	    splitLine = split(line[:-1],';')
	    h = eval(split(splitLine[0],':')[1])
	    t = eval(split(splitLine[1],':')[1])
	    G.AddEdge(t,h)
	    for i in xrange(nrOfWeights):
		G.edgeWeights[i][(t,h)] = eval(split(splitLine[3+i],':')[1])
 
	lineNr = lineNr + 1


    file.close()

    for v in G.vertices:
	L[v] = v

    G.embedding = E
    G.labeling  = L
    if intWeights:
	G.Integerize('all')

    return G

def SaveCATBoxGraph(G, fileName):
    """ Save graph to file fileName in file-format from old CATBOX++ (*.cat) """
    
    file = open(fileName, 'w')
  
    nrOfEdgeWeights = len(G.edgeWeights.keys())
    integerWeights = G.edgeWeights[0].QInteger()

    file.write("graph:\n")
    file.write("dir:%d; simp:%d; eucl:%d; int:%d; ew:%d; vw:0;\n" %
	       (G.QDirected(), G.simple, G.QEuclidian(), integerWeights,
	       nrOfEdgeWeights))
    file.write("scroller:\n")
    file.write("vdim:1000; hdim:1000; vlinc:10; hlinc:10; vpinc:50; hpinc:50;\n")
    file.write("vertices:" + `G.Order()` + ";\n")
    
    # Force continous numbering of vertices
    count = 1
    save = {}
    for i in G.vertices:
	save[i] = count
	#print "i=",i,"save=",save[i]
	count = count + 1
	file.write("n:%d; x:%d; y:%d;\n" % (save[i], G.embedding[i].x, G.embedding[i].y))
    file.write("edges:" + `G.Size()` + ";\n")
    for tail in G.vertices:
	for head in G.OutNeighbors(tail):
	    file.write("h:%d; t:%d; e:2;" % (save[head], save[tail]))

	    for i in xrange(nrOfEdgeWeights):
		if integerWeights:
		    file.write(" w:%d;" % int(round(G.edgeWeights[i][(tail,head)])))
		else:
		    file.write(" w:%d;" % G.edgeWeights[i][(tail,head)])
		    
	    file.write("\n")
		


   #file.close()


#### GML

def ParseGML(file):
    
    retval = []

    while 1:
	
	line = file.readline() 
    
	if not line:
	    return retval

	token = filter(lambda x: x != '', split(line[:-1],"[\t ]*"))

	if len(token) == 1 and token[0] == ']':
	    return retval

	elif len(token) == 2:
	    
	    if token[1] == '[':
		retval.append((token[0], ParseGML(file)))
	    else:
		retval.append((token[0], token[1]))

	else:
	    print "Serious format error in:", line



def PairListToDictionary(l):
    d = {}
    for i in xrange(len(l)):
	d[l[i][0]] = l[i][1]
    return d
	    


def OpenGMLGraph(fileName):
    """ Reads in a graph from file fileName. File-format is supposed
        to be GML (*.gml) """
    G = Graph()
    G.directed = 0
    E = VertexLabeling()
    W = EdgeWeight(G)
    L = VertexLabeling()
    VLabel = VertexLabeling()
    ELabel = EdgeLabeling()

    file = open(fileName, 'r')
    g = ParseGML(file)
    file.close()

    if g[0][0] != 'graph':
	print "Serious format error. first key is not graph"
	return
    else:
	l = g[0][1]
	for i in xrange(len(l)):
	    
	    key   = l[i][0]
	    value = l[i][1]
    
	    if key == 'node':
		
		d = PairListToDictionary(value)
		# print "Found node", value, d 
		v = G.AddVertex()
		
		try:
		    VLabel[v] = eval(d['label'])
		    P = PairListToDictionary(d['graphics'])
		    E[v] = Point2D(eval(P['x']), eval(P['y']))
		    
		except:
		    d = None 
		    P = None

	    elif key == 'edge':

		d = PairListToDictionary(value)
		#print "Found edge", value, d

		try:
		    s = eval(d['source'])
		    t = eval(d['target'])
		    G.AddEdge(s,t)
		    ELabel[(s,t)] = eval(d['label'])
		    W[(s,t)] = 0
		except:
		    d = None 
		  
	    elif key == 'directed':
		G.directed = 1 
 
    for v in G.vertices:
	L[v] = v
	
    G.embedding = E
    G.labeling  = L
    G.nrEdgeWeights = 1
    G.edgeWeights[0] = W
    G.vertexAnnotation = VLabel
    G.edgeAnnotation = ELabel

    return G

