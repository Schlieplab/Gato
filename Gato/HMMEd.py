#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Combinatorial Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   HMMEd.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

from DataStructures import Point2D
from Graph import Graph
from Gred import *
from GraphUtil import WeightedGraphInformer, VertexWeight
from GraphDisplay import GraphDisplay
from GatoUtil import stripPath, extension
from GatoGlobals import *
from GraphEditor import EditWeightsDialog
from tkFileDialog import askopenfilename, asksaveasfilename
import tkMessageBox
from tkMessageBox import askokcancel
import tkSimpleDialog 
import whrandom
import string
import ProbEditorBasics
import ProbEditorDialogs

import HMMXML import xml.dom.minidom
import EditObjectAttributesDialog
from import EditObjectAttributesDialog ValidatingString, ValidatingInt, ValidatingFloat, PopupableInt

class DOM_Map:
    def __init__(self):
        self.name = {}
        self.desc = {}
        self.hasDesc = None
        self.name2code = {}

    def addCode(self, code, name, desc = None):
        self.name[code] = name
        if desc != None:
            self.desc[code] = desc
            self.hasDesc = 1
        self.name2code[name] = code

    def low(self):
        return min(self.name.keys())

    def high(self):
        return max(self.name.keys())
    
    def fromDom(self, XMLNode):
        pass

    def symbolsFromDom(self, XMLNode):
        symbols = XMLNode.getElementsByTagName("symbol")
        
        for symbol in symbols:
            symbolCode = ValidatingInt(int(symbol.getAttribute("code")))
            symbolName = ValidatingString(symbol.firstChild.nodeValue)
            symbolDesc = symbol.getAttribute("desc")
            if symbolDesc != None:
                self.addCode(symbolCode, symbolName, ValidatingString(symbolDesc))
            else:
                self.addCode(symbolCode, symbolName)
                
    def toDom(self):
        return None
   

class DiscreteHMMAlphabet(DOM_Map):
    def __init__(self):
        DOM_Map.__init__()
        self.hmm_type = 'discrete'

    def fromDom(self, XMLNode):
        """Take dom subtree representing a <hmm:alphabet</hmm:alphabet> element"""
        # Not reading: hmm:low hmm:high
        if XMLNode.getAttribute("hmm:type") == self.hmm_type:
            self.symbolsFromDom(XMLNode)
        else:
            print "DiscreteHMMAlphabet does not handle alphabet type %s yet" % XMLNode.getAttribute("hmm:type") 

    
class HMMClass(DOM_Map):
    def __init__(self):
        DOM_Map.__init__()

    def fromDom(self, XMLNode):
        """Take dom subtree representing a <hmm:class></hmm:class> element"""
        self.symbolsFromDom(XMLNode)

    
class HMMState:
    def __init__(self, itsHMM):
        self.id = ValidatingString()
        self.state_class = PopupableInt()
        self.state_class.
        self.label = ValidatingString()
        self.initial = ValidatingFloat()
        self.tiedto = DefaultedString()


    


class HMM:
    def __init__(self):
	self.G = Graph()
	self.G.directed = 1
	self.G.euclidian = 0
	self.Pi = {}

        self.editableAttr = {}
        self.editableAttr['HMM'] = ['desc']
        self.desc = EditObjectAttributesDialog.ValidatingString()
        

    def OpenXML(self, fileName):
	self.G = Graph()
	self.G.simple = 0
	self.G.directed = 1
	self.G.euclidian = 0

        self.index = {} # Map id to index
        self.id    = {} # Map index to id
        self.label = {}

        dom = xml.dom.minidom.parse(fileName)
        assert dom.documentElement.tagName == "graphml"   

        gml = HMMXML.GraphML()
        gml.handleGraphML(dom)
        print gml
        dom.unlink()

        self.hmmAlphabet = gml.hmmAlphabet

        # Nr of Symbols:
        self.nrOfSymbols = gml.hmmAlphabet.high - gml.hmmAlphabet.low + 1
        for i in xrange(self.nrOfSymbols):
            self.G.vertexWeights[i] = VertexWeight(self.G)

        # Adding vertices
        #
        # XXX We assume we have label, initial, pos
        for n in gml.graph.nodes:
            i = self.G.AddVertex()
            self.index[n.id] = i
            self.id[i] = n.id
            self.G.labeling[i] = "%s\n%s" % (n.id, n.label) # XXX Hack Aaaargh!
            self.Pi.append(n.initial)
            self.G.embedding[i] = Point2D(float(n.ngeom.x),float(n.ngeom.y))
            for j in xrange(self.nrOfSymbols):
                #print n.id, i, j
                self.G.vertexWeights[j][i] = n.emissions[j]
            
        # Adding Edges
        for e in gml.graph.edges:
            i = self.index[e.source]
            j = self.index[e.target]
            #print i,j
            self.G.AddEdge(i, j)
            self.G.edgeWeights[0][(i,j)] = e.prob            



    def SaveAs(self, fileName):
        return
	file = open(fileName, 'w')
   



class EditEmissionProbDialog(tkSimpleDialog.Dialog):

    def __init__(self, master, G):
	self.G = G
	tkSimpleDialog.Dialog.__init__(self, master, "Edit emission probabilities")
  
    def body(self, master):
	self.resizable(0,0)	

	label = Label(master, text="Vertex", anchor=W)
	label.grid(row=0, column=0, padx=4, pady=3)

	n = self.G.NrOfVertexWeights()
	self.entry = {}

	for j in xrange(n):
	    label = Label(master, text="%d" % j, anchor=W)
	    label.grid(row=0, column=j+1, padx=4, pady=3)
	    
	i = 0
	for v in self.G.vertices:
	    label = Label(master, text=self.G.labeling[v], anchor=W)
	    label.grid(row=i+1, column=0, padx=2, pady=1, sticky="e")
 
	    for j in xrange(n):
		self.entry[(v,j)] = Entry(master, width=6, exportselection=FALSE)
		self.entry[(v,j)].insert(0,"%1.3f" % self.G.vertexWeights[j][v])
		self.entry[(v,j)].grid(row=i+1, column=j+1, padx=2, pady=1)

	    i = i + 1  


    def validate(self):
	
	for k in self.entry.keys():
	    try:
		val = string.atof(self.entry[k].get())
		#if val < 0.0 or val > 1.0:
	        #   raise ValueError
	    except ValueError:
		m = "Please enter a floating point number for probability of %d emitting %d" % (k[0],k[1]) 
		tkMessageBox.showwarning("Invalid Value", m, parent=self)
		self.entry[k].selection_range(0,"end")
		self.entry[k].focus_set()
		return 0
	    
	for v in self.G.vertices:
	    sum = 0.0
	    for i in xrange(self.G.NrOfVertexWeights()):
		sum = sum + string.atof(self.entry[(v,i)].get())

	    for i in xrange(self.G.NrOfVertexWeights()):
		if sum < 0.000001: # Uniform distribution
		    self.G.vertexWeights[i][v] = 1.0 / self.G.NrOfVertexWeights()
		else:
		    self.G.vertexWeights[i][v] = string.atof(self.entry[(v,i)].get()) / sum


	return 1

class HMMEditor(SAGraphEditor):

    def __init__(self, master=None):
	SAGraphEditor.__init__(self, master)
	
	self.HMM = None

    def makeMenuBar(self):
	self.menubar = Menu(self,tearoff=0)

	# Add file menu
	self.fileMenu = Menu(self.menubar, tearoff=0)
	self.fileMenu.add_command(label='New',            command=self.NewGraph)
	self.fileMenu.add_command(label='Open ...',       command=self.OpenGraph)
	self.fileMenu.add_command(label='Save',	     command=self.SaveGraph)
	self.fileMenu.add_command(label='Save as ...',    command=self.SaveAsGraph)
	self.fileMenu.add_separator()
	self.fileMenu.add_command(label='Export EPSF...', command=self.ExportEPSF)
	self.fileMenu.add_separator()
	self.fileMenu.add_command(label='Quit',	     command=self.Quit)
	self.menubar.add_cascade(label="File", menu=self.fileMenu, 
				 underline=0)
	
	self.graphMenu = Menu(self.menubar, tearoff=0)
	self.graphMenu.add_command(label='Edit HMM', command=self.EditHMM)
	self.graphMenu.add_command(label='Edit Emissions', command=self.EditEmissions)
	self.graphMenu.add_command(label='Edit Prior', command=self.EditPrior)
	self.graphMenu.add_separator()
	self.graphMenu.add_checkbutton(label='Grid', 
						  command=self.ToggleGridding)	
	self.menubar.add_cascade(label="HMM", menu=self.graphMenu, 
				 underline=0)

	# Add Tools menu
##	self.toolsMenu = Menu(self.menubar,tearoff=0)
##	self.toolVar = StringVar()
##	self.toolsMenu.add_radiobutton(label='Add or move vertex',  
##				       command=self.ChangeTool,
##				       var = self.toolVar, value='AddOrMoveVertex')
##	self.toolsMenu.add_radiobutton(label='Add edge', 
##				       command=self.ChangeTool,
##				       var = self.toolVar, value='AddEdge')
##	self.toolsMenu.add_radiobutton(label='Delete edge or vertex', 
##				       command=self.ChangeTool,
##				       var = self.toolVar, value='DeleteEdgeOrVertex')
##	self.toolsMenu.add_radiobutton(label='Swap orientation', 
##				       command=self.ChangeTool,
##				       var = self.toolVar, value='SwapOrientation')
##	self.toolsMenu.add_radiobutton(label='Edit Probabilities', 
##					command=self.ChangeTool,
##				       var = self.toolVar, value='EditWeight')
##	self.menubar.add_cascade(label="Tools", menu=self.toolsMenu, 
##				 underline=0)

	self.master.configure(menu=self.menubar)

    def SetGraphMenuOptions(self):
	if not self.gridding:
	    self.graphMenu.invoke(self.graphMenu.index('Grid'))	
	

    ############################################################
    #
    # Menu Commands
    #
    # The menu commands are passed as call back parameters to 
    # the menu items.
    #
    def NewGraph(self, nrOfSymbols=0):
	self.HMM = HMM()

	self.HMM.G.euclidian = 0
	self.HMM.G.directed = 1
	self.HMM.G.simple = 0
	self.graphName = "New"
	self.ShowGraph(self.HMM.G,self.graphName)
	self.RegisterGraphInformer(WeightedGraphInformer(self.HMM.G,"probability"))
	self.fileName = None
	self.SetTitle("HMMEd _VERSION_ - New Graph")
	self.SetGraphMenuOptions()
	if nrOfSymbols == 0:
	    nrOfSymbols  = tkSimpleDialog.askinteger("New HMM",
						     "Enter the number of output symbols")
	for i in xrange(nrOfSymbols):
	    self.HMM.G.vertexWeights[i] = VertexWeight(0.0)

    def OpenGraph(self):	
	file = askopenfilename(title="Open HMM",
			       defaultextension=".xml",
			       filetypes = (("XML", ".xml")
                                            )
			       )
	if file is "": 
	    print "cancelled"
	else:
	    self.fileName = file
	    self.graphName = stripPath(file)
	    e = extension(file)

	    if e == 'hmm':
		self.HMM.Open(file)
	    elif e == 'xml':
		self.HMM.OpenXML(file)
	    else:
		print "Unknown extension"
		return

	    self.ShowGraph(self.HMM.G,self.graphName)
	    self.RegisterGraphInformer(WeightedGraphInformer(self.HMM.G,"probability"))
	    self.SetTitle("HMMEd _VERSION_ - " + self.graphName)

	    if not self.gridding:
		self.graphMenu.invoke(self.graphMenu.index('Grid'))	


    def SaveGraph(self):
	if self.fileName != None:
	    self.HMM.SaveAs(self.fileName)
	else:
	    self.SaveAsGraph()
	

    def SaveAsGraph(self):
	file = asksaveasfilename(title="Save HMM",
				 defaultextension=".xml",
				 filetypes = ( ("XML", ".xml"),
					       )
				 )
	if file is "": 
	    print "cancelled"
	else:
	    print file
	    self.fileName = file
	    self.HMM.SaveAs(file)
	    self.graphName = stripPath(file)
	    self.SetTitle("HMMEd _VERSION_ - " + self.graphName)


    def EditWeightUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if "edges" in tags:
 		(tail,head) = self.edge[widget]

                transition_probabilities=ProbEditorBasics.ProbDict({})
		for head in self.HMM.G.OutNeighbors(tail):
		    weight=self.HMM.G.edgeWeights[0][(tail,head)]
		    label = "-> %d" % head
                    transition_probabilities.update({label:weight})

                if transition_probabilities.sum==0:
                    key_list=transition_probabilities.keys()
                    for key in key_list:
                        transition_probabilities[key]=1.0/len(key_list)
                e=ProbEditorBasics.emission_data(transition_probabilities)
                d = ProbEditorDialogs.emission_dialog(self,
                                                      e,
                                                      "transition probs from state %d" % tail)
                if d.success():
                    # write back normalized probabilities
                    for key in transition_probabilities.keys():
                        head = int(key[3:])
                        self.HMM.G.edgeWeights[0][(tail,head)]=transition_probabilities[key]/transition_probabilities.sum

	    else: # We have a vertex
		v = self.FindVertex(event)
		if v != None and self.HMM.G.NrOfVertexWeights() > 0:

                    emission_probabilities = ProbEditorBasics.ProbDict({})

                    count = self.HMM.G.NrOfVertexWeights()
                    for i in xrange(count):
                        weight = self.HMM.G.vertexWeights[i][v]
                        try:
                            label = "%s" % self.HMM.hmmAlphabet[i]
                        except:
                            label = "symbol %s" % i 
                        emission_probabilities.update({label:weight})

                    if emission_probabilities.sum == 0:
                        key_list = emission_probabilities.keys()
                        for key in key_list:
                            emission_probabilities[key] = 1.0 / len(key_list)

                            
                    e = ProbEditorBasics.emission_data(emission_probabilities)
                    d = ProbEditorDialogs.emission_dialog(self, e,
                                                          "emission probs of state %d" % v)
                    if d.success():
                        # write back normalized probabilities
                        for key in emission_probabilities.keys():
                            i = int(key[7:])
                            self.HMM.G.vertexWeights[i][v] = emission_probabilities[key] / emission_probabilities.sum	


    def EditHMM(self):
        d = EditObjectAttributesDialog.EditObjectAttributesDialog(self, self.HMM, self.HMM.editableAttr['HMM'])

    def EditEmissions(self):
	d = EditEmissionProbDialog(self, self.HMM.G)

    def EditPrior(self):
	if self.HMM.G.Order() == 0:
	    return
        
        pi_keys = self.HMM.Pi.keys()
	if len(pi_keys) == 0: # No prior yet, set uniform
            u = 1.0 / (self.HMM.G.Order() - 1)
            for id in self.HMM.G.vertices:
                self.HMM.Pi[id] = EditObjectAttributesDialog.ValidatingFloat(u)
        elif len(pi_keys) < self.HMM.G.Order(): # States have been added ... add a corresponding number of '0's
            for id in self.HMM.G.vertices:
                if id not in pi_keys:
                    self.HMM.Pi[id] = EditObjectAttributesDialog.ValidatingFloat(0.0)

        emission_probabilities = ProbEditorBasics.ProbDict({})
        for i in xrange(self.HMM.G.Order()):
            state = self.HMM.G.vertices[i]           
            label = "state %s" % state # XXX Ughhhhh! Must correspond to int(key[6:])
            weight = self.HMM.Pi[state]
            emission_probabilities.update({label:weight})

        e = ProbEditorBasics.emission_data(emission_probabilities)
        d = ProbEditorDialogs.emission_dialog(self, e, "initial probabilities")
        if d.success():
            # write back normalized probabilities
            for key in emission_probabilities.keys():
                state = int(key[6:])
                self.HMM.Pi[state] = emission_probabilities[key] / emission_probabilities.sum
                
                
    def AddVertex(self,x,y):
	v = GraphDisplay.AddVertex(self, x, y)
	n = self.HMM.G.NrOfVertexWeights()
	for i in xrange(n):
	    self.HMM.G.vertexWeights[i][v] = 1.0 / n
	
	



################################################################################
if __name__ == '__main__':
    graphEditor = HMMEditor(Tk())
    graphEditor.NewGraph(2)
    graphEditor.mainloop()
