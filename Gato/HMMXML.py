#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   HMMXML.py
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
#################################################################################
#
#
#
#

#- Utility --------------------------------------------------------------------
from sys import *
from xml.dom.minidom import *
import copy
import string

def printDict(d):
    for k in d.keys():
        print k, d[k]

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def copyAttributes(XMLNode, object):
    for i in xrange(0,XMLNode.attributes.length):
        attrName = XMLNode.attributes.item(i).name
        attrValue = XMLNode.attributes.item(i).value

        object.__dict__[attrName] = attrValue

def attributesDict(XMLNode):
    retVal = {}
    for i in xrange(0,XMLNode.attributes.length):
        attrName = XMLNode.attributes.item(i).name
        attrValue = XMLNode.attributes.item(i).value

        retVal[attrName] = attrValue

    return retVal

#- GraphML ---------------------------------------------------------------------

class DataFactory:
    # Maps strings to callable objects

    def __init__(self):
        self.factories = {}

        self.factories['string'] = lambda s: s
        self.factories['int'] = int
        self.factories['float'] = float
        self.factories['intArray'] = lambda s, f=self.arrayFromCSV: f(s, int)
        self.factories['floatArray'] = lambda s, f=self.arrayFromCSV: f(s, float)
        self.factories['DiscreteProbDist'] = self.factories['floatArray']
        self.factories['HigherDiscreteProbDist'] = self.factories['floatArray']

    def __call__(self, type, stringArg):
        return self.factories[type](stringArg)

    def Types(self):
        return self.factories.keys()

    def arrayFromCSV(self, s, type):
        retVal = []

        print "DataFactory.arrayFromCSV(", s, ")"
        
        items = string.split(s,',')
        for i in items:
            retVal.append(type(i))
        return retVal
    


class GraphML:
    def __init__(self):
        # Prototypes for which we can set default values of instance variables
        self.graphProto = Graph()
        self.nodeProto = Node()
        self.edgeProto = Edge()

        # Key Tags
        self.desc = {} # Human readable descriptions
        self.domain = {} # To what objects do they apply 
        self.type = {} # Their Type

        self.graph = None
        self.dataFactory = DataFactory()


    # Graph, Edge, Node factories
    def NewGraph(self):
        g = copy.deepcopy(self.graphProto)
        return g

        
    def NewEdge(self,source,target):
        e = copy.deepcopy(self.edgeProto)
        e.source = source
        e.target = target
        return e


    def NewNode(self,id):
        n = copy.deepcopy(self.nodeProto)
        n.id = id
        return n


    def AddEdge(self,source,target):
        e = self.NewEdge(source,target)
        self.graph.edges.append(e)
        return e


    def AddNode(self,id):
        n = self.NewNode(id)
        self.graph.nodes.append(n)
        return n

    # XML Parsing

    def handleGraphML(self, graphML):
        keys = graphML.getElementsByTagName("key")
        for key in keys:
            self.handleKey(key)

        XMLGraph = graphML.getElementsByTagName("graph")
        self.handleGraph(XMLGraph[0]) # There should only be one graph per graphml
        
        HMMAlphabet = graphML.getElementsByTagName("hmm:alphabet")
        if len(HMMAlphabet) > 0: # We do have an HMM
            self.handleHMMAlphabet(HMMAlphabet[0])# There should only be one HMMAlphabet per graphml

    def handleKey(self, key):

        try: # valid values: all, graph, node, edge
            keyDomain =  key.attributes['for'].nodeValue
        except KeyError:
            keyDomain = 'all'

        try:
            keyType = key.attributes['gd:type'].nodeValue
        except KeyError:
            keyType = 'string'

        # ID required
        keyName = key.attributes['id'].nodeValue

        descNodes = key.getElementsByTagName("desc")
        if len(descNodes) > 0:
            keyDesc = descNodes[0].firstChild.nodeValue # There should be only one desc
        else:
            keyDesc = None
    
        #print keyName, keyDesc, keyType, keyDomain

        self.desc[keyName] = keyDesc
        self.type[keyName] = keyType
        self.domain[keyName] = keyDomain

        keyValue = None # For simple objects
        
        # Initialize complex objects
        if not keyType in self.dataFactory.Types():
            keyValue = Empty()
            partials = key.getElementsByTagName("*")
            for partial in partials:
                copyAttributes(partial, keyValue)
         
        # Add attributes to prototypes
        if keyDomain == 'all' or keyDomain == 'node':
            self.nodeProto.__dict__[keyName] = keyValue
           
        if keyDomain == 'all' or keyDomain == 'edge':
            self.edgeProto.__dict__[keyName] = keyValue
           
        if keyDomain == 'graph':
            self.graphProto.__dict__[keyName] = keyValue

            
    def handleGraph(self, XMLGraph):

        self.graph = self.NewGraph()
        
        nodes = XMLGraph.getElementsByTagName("node")
        for node in nodes:
           self.handleNode(node)

        edges = XMLGraph.getElementsByTagName("edge")
        for edge in edges:
           self.handleEdge(edge)


    def handleHMMAlphabet(self, XMLNode):

        if XMLNode.getAttribute("hmm:type") == "discrete":
            self.hmmAlphabet = DiscreteAlphabet()
            self.hmmAlphabet.low = int(XMLNode.getAttribute("hmm:low")) 
            self.hmmAlphabet.high = int(XMLNode.getAttribute("hmm:high")) 

            symbols = XMLNode.getElementsByTagName("symbol") # One map!
            
            for symbol in symbols:
                symbolCode = int(symbol.getAttribute("code"))
                symbolRep = symbol.firstChild.nodeValue
                self.hmmAlphabet.map[symbolCode] = symbolRep
            
        else:
            print "GraphML::handleHMMAlphabet does not handle alphabet type %s yet" % XMLNode.getAttribute("hmm:type") 

        print self.hmmAlphabet.__dict__



    def handleXMLNodeData(self, object, XMLNode):
        datas = XMLNode.getElementsByTagName("data")
        for data in datas:
            dataKey = data.attributes['key'].nodeValue
            dataValue = data.firstChild.nodeValue

            #print object, object.__dict__,dataKey, dataValue
            if dataValue is not None:
                object.__dict__[dataKey] = self.dataFactory(self.type[dataKey], dataValue)
            else:
                #copyAttributes(data.firstChild,object.__dict__[dataKey])
                partials = data.getElementsByTagName("*")
                for partial in partials:
                    copyAttributes(partial, object.__dict__[dataKey])

    def handleNode(self, node):
        nodeID = node.attributes['id'].nodeValue
        n = self.AddNode(nodeID)
        self.handleXMLNodeData(n, node)


    def handleEdge(self, edge):
        edgeSource = edge.attributes['source'].nodeValue
        edgeTarget = edge.attributes['target'].nodeValue
        e = self.AddEdge(edgeSource, edgeTarget)
        self.handleXMLNodeData(e, edge)
        

    def __str__(self):
        r =     "GraphML\n"
        r = r + "  #key\tdescription\n"
        for k in self.desc.keys():            
            r = r + "  %s\t%s\n" % (k,self.desc[k])
        r = r + "  #Nodes -------------------------\n"
        r = r + "  id  "
        for k in self.desc.keys():            
            if self.domain[k] == 'all' or self.domain[k] == 'node':
                r = r + "  %s " % k
        r = r + "\n"
        for n in self.graph.nodes:
            r = r + "  %s  " % n.id
            for k in self.desc.keys():
                if self.domain[k] == 'all' or self.domain[k] == 'node':
                    r = r + "  %s " % n.__dict__[k]
            r = r + "\n"
        r = r + "  #Edges -------------------------\n     "
        for k in self.desc.keys():            
            if self.domain[k] == 'all' or self.domain[k] == 'edge':
                r = r + "  %s " % k
        r = r + "\n"
        for e in self.graph.edges:
            r = r + "  (%s,%s) " % (e.source, e.target)
            for k in self.desc.keys():
                if self.domain[k] == 'all' or self.domain[k] == 'edge':
                    r = r + "  %s " % e.__dict__[k]
            r = r + "\n"
        return r


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.id = None

class Node:
    def __init__(self):
        self.id = None

class Edge:
    def __init__(self):
        self.id = None
        self.source = None
        self.target = None


class Empty:
    def __init__(self, **args):
        for k in args.keys():
            self.__dict__[k] = args[k]

    def __str__(self):
        r = "{"
        for k in self.__dict__.keys():
            r = r + "%s:%s," % (k, self.__dict__[k])
        r = r + "}"
        return r

class DiscreteAlphabet:
    def __init__(self):
        self.map = {}
        self.low = 0
        self.high = 0        

    def __getitem__(self, i):
        return self.map[i]


def WriteData(doc, e, object, keys):
    print doc, e, object, keys
    for k in keys:
        elem = doc.createElement("data")
        elem.setAttribute('key', k)
        contents = doc.createTextNode("%s" % object.__dict__[k])
        elem.appendChild(contents)
        e.appendChild(elem)
        
def WriteXML(gml):
    doc = Document()
    graphml = doc.createElement("graphml")
    doc.appendChild(graphml)

    node_keys = []
    edge_keys = []

    for k in gml.desc.keys():
        elem = doc.createElement("key")
        elem.setAttribute('id', k)
        if gml.domain[k] is not None:
            elem.setAttribute('for', gml.domain[k] )          
        elem.setAttribute('gd:type', gml.type[k])
        graphml.appendChild(elem)

        if gml.domain[k] == 'node' or gml.domain[k] == 'all':
            node_keys.append(k)
        if gml.domain[k] == 'edge' or gml.domain[k] == 'all':
            edge_keys.append(k)
        
        
    graphelem = doc.createElement("graph")
    graphml.appendChild(graphelem)

    for n in gml.graph.nodes:
        elem = doc.createElement("node")        
        elem.setAttribute('id', n.id)
        WriteData(doc,elem,n,node_keys)
        graphelem.appendChild(elem)

    for e in gml.graph.edges:
        elem = doc.createElement("edge")        
        elem.setAttribute('source', e.source)
        elem.setAttribute('target', e.target)
        WriteData(doc,elem,e,edge_keys)
        graphelem.appendChild(elem)

    print doc.toprettyxml()

    

        
if __name__ == '__main__':
    dom = parse(argv[1])
    assert dom.documentElement.tagName == "graphml"   

    gml = GraphML()
    gml.handleGraphML(dom)
    print gml

    WriteXML(gml)
    
    dom.unlink()
