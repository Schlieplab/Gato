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

import HMMXML
import xml.dom.minidom


class HMM:
    def __init__(self):
	self.G = Graph()
	self.G.directed = 1
	self.G.euclidian = 0
	self.Pi = []


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

            



    def Open(self, fileName):
	self.G = Graph()
	self.G.simple = 0
	self.G.directed = 1
	self.G.euclidian = 0

	import regex 
 
	commentPat = regex.compile('[\t ]*\#.')
	nrOfSymbolsPat = regex.compile('[\t ]*M[\t ]*=[\t ]*\([0-9]+\)')
	nrOfStatesPat  = regex.compile('[\t ]*N[\t ]*=[\t ]*\([0-9]+\)')
 
	ws = '[\t ]*'
	fg = '\([0-9]+.[0-9]+\)'
	beginOfA = regex.compile('[\t ]*A[\t ]*=[\t ]*matrix[\t ]*{')
	beginOfB = regex.compile('[\t ]*B[\t ]*=[\t ]*matrix[\t ]*{')
	beginOfP = regex.compile('[\t ]*Pi[\t ]*=[\t ]*vector[\t ]*{')
	beginOfEmbed = regex.compile('# E_M_B_E_D')
 	lineOfEmbed = regex.compile('# \([0-9]+\) \([0-9]+\) \([0-9]+\)')

	nrOfSymbols = nrOfStates = None
 
	try:
	    file = open(fileName, 'r')
	except:
	    print "File error",file
	    return None
 
	while 1:
 
	    line = file.readline()
	    if not line:
		break
 
	    # Skip comments
	    if commentPat.match(line) < 0:
 
		if nrOfSymbolsPat.match(line) > 0:
		    nrOfSymbols = eval(nrOfSymbolsPat.group(1))
		    pat = ws + fg + (ws + ',' + ws + fg) * (nrOfSymbols-1)
		    lineOfBPat = regex.compile(pat)
		    for i in xrange(nrOfSymbols):
			self.G.vertexWeights[i] = VertexWeight(self.G)

		elif nrOfStatesPat.match(line) > 0:
		    nrOfStates = eval(nrOfStatesPat.group(1))
		    pat = ws + fg + (ws + ',' + ws + fg) * (nrOfStates-1)
		    lineOfAPat = regex.compile(pat)
		    for i in xrange(nrOfStates):
			v = self.G.AddVertex()
			self.G.labeling[v] = "%d" % v
			#print "Added vertex", v, "i=",i
		    

		elif beginOfA.match(line) > 0:
		    for i in xrange(nrOfStates):
			line = file.readline()
			if not line:
			    break
			if lineOfAPat.match(line) > 0:
			    for j in xrange(nrOfStates):
				prob = eval(lineOfAPat.group(j+1))
				if prob > 0.0:
				    self.G.AddEdge(i+1,j+1)
				    self.G.edgeWeights[0][(i+1,j+1)] = prob
				    #print "Added Edge", (i+1,j+1), "prob=",prob

			else:
			    print "file error while reading A"


		elif beginOfB.match(line) > 0:
		    for i in xrange(nrOfStates):
			line = file.readline()
			if not line:
			    break
			if lineOfBPat.match(line) > 0:
			    for j in xrange(nrOfSymbols):
				prob = eval(lineOfBPat.group(j+1))
				#print i, j, prob
				self.G.vertexWeights[j][i+1] = prob

			else:
			    print "file error while reading B"

		elif beginOfP.match(line) > 0:
		    self.Pi = [0.0] * nrOfStates
		    line = file.readline()
		    if lineOfAPat.match(line) > 0:
			for j in xrange(nrOfStates):
			    self.Pi[j] = eval(lineOfAPat.group(j+1))
		    print "Pi = ",self.Pi
	    else:
		
		if beginOfEmbed.match(line) > 0:
		    for i in xrange(nrOfStates):
			line = file.readline()
			if not line:
			    break
		    
			if lineOfEmbed.match(line) > 0:
			    x = eval(lineOfEmbed.group(2))
			    y = eval(lineOfEmbed.group(3))
			    #print i, x, y
			    self.G.embedding[i+1] = Point2D(x,y)

			else:

			    print "file error while reading Embed"

        # If there was no embedding specified in file we create a random
        # one
	try:
	    x = self.G.embedding[1]
	except KeyError: # No Embedding yet 
	    for v in self.G.vertices:
		self.G.embedding[v] = Point2D(whrandom.randint(10,990),
					      whrandom.randint(10,990))	    
		



    def SaveAs(self, fileName):
	file = open(fileName, 'w')
   
	M = self.G.NrOfVertexWeights()

	file.write("HMM = {\n")
	file.write("M = %d;\n" % M)
	file.write("N = %d;\n" % self.G.Order())

	file.write("# E_M_B_E_D\n")
	for v in self.G.vertices:
	    file.write("# %d %d %d\n" % (v, self.G.embedding[v].x, self.G.embedding[v].y))
   

	file.write("A = matrix {\n")

	order = len(self.G.vertices)

	for v in self.G.vertices:
	    N = self.G.OutNeighbors(v)
	    
	    # Find out if user did edit the transition probs
	    # if not use uniform distribution
	    # Also chech sum for normalizing again (necessary
	    # if edges have been inserted)
	    didEdit = 0
	    sum = 0.0
	    for w in N:
		if self.G.edgeWeights[0][(v,w)] > 0.0:
		    didEdit = 1
		sum = sum + self.G.edgeWeights[0][(v,w)] 

	    for w in self.G.vertices:
		if w in N:
		    if didEdit == 1:
			file.write("%1.3f" % (self.G.edgeWeights[0][(v,w)] / sum))
		    else: # Uniform
			file.write("%1.3f" % (1.0 / len(N)))
		else:
		    file.write("0.000")

		if w == order:
		    file.write(";\n")
		else:
		    file.write(", ")
  
	file.write("};\n") # close A = {
	 
	file.write("B = matrix {\n")
	for v in self.G.vertices:

	    # Find out if user did edit the emission probs
	    # if not use uniform distribution
	    didEdit = 0
	    for i in xrange(M):
		if self.G.vertexWeights[i][v] > 0.0:
		    didEdit = 1	    
		    break

	    for i in xrange(M):
		if didEdit == 1:
		    file.write("%1.3f" % self.G.vertexWeights[i][v])
		else: # Uniform
		    file.write("%1.3f" % (1.0 / M))
		
		if i == M - 1:
		    file.write(";\n")
		else:
		    file.write(", ")
			
	file.write("};\n") # close B = ...

	sum = 0.0
	for i in xrange(order):
	    sum = sum + self.Pi[i]

	if sum < 0.00001: # Uniform
	    file.write("Pi = vector {\n%1.3f" % (1.0 / order))
	    for i in xrange(order-1):
		file.write(", %1.3f" % (1.0 / order))
	else:
	    file.write("Pi = vector {\n%1.3f" % (self.Pi[0] / sum))
	    for i in xrange(1,order):
		file.write(", %1.3f" % (self.Pi[i] / sum))
  	file.write(";\n};\n") # close Pi = ...


	file.write("};\n") # close HMM = {


class EditPriorDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, Pi):
	self.Pi = Pi
	tkSimpleDialog.Dialog.__init__(self, master, "Edit prior probabilities")
  
    def body(self, master):
	self.resizable(0,0)	

	label = Label(master, text="State", anchor=W)
	label.grid(row=0, column=0, padx=4, pady=3)
	label = Label(master, text="Prob", anchor=W)
	label.grid(row=1, column=0, padx=4, pady=3)

	n = len(self.Pi)
	self.entry = {}

	for i in xrange(n):
	    label = Label(master, text="%d" % (i+1), anchor=W)
	    label.grid(row=0, column=i+1, padx=4, pady=3)
	    
	    self.entry[i] = Entry(master, width=6, exportselection=FALSE)
	    self.entry[i].insert(0,"%1.3f" % self.Pi[i])
	    self.entry[i].grid(row=1, column=i+1, padx=2, pady=1)


    def validate(self):
	
	n = len(self.Pi)

	for i in xrange(n):
	    try:
		val = string.atof(self.entry[i].get())

	    except ValueError:
		m = "Please enter a floating point number for probability of starting in ste %d" % (k[0],k[1]) 
		tkMessageBox.showwarning("Invalid Value", m, parent=self)
		self.entry[i].selection_range(0,"end")
		self.entry[i].focus_set()
		return 0
	    
	sum = 0.0
	for i in xrange(n):
	    sum = sum + string.atof(self.entry[i].get())

	for i in xrange(n):
	    if sum < 0.000001: # Uniform distribution
		self.Pi[i] = 1.0 / n
	    else:
		self.Pi[i] = string.atof(self.entry[i].get()) / sum
	return 1





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
##	self.toolsMenu.invoke(self.toolsMenu.index('Add or move vertex'))	
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
	self.SetTitle("Gred _VERSION_ - New Graph")
	self.SetGraphMenuOptions()
	if nrOfSymbols == 0:
	    nrOfSymbols  = tkSimpleDialog.askinteger("New HMM",
						     "Enter the number of output symbols")
	for i in xrange(nrOfSymbols):
	    self.HMM.G.vertexWeights[i] = VertexWeight(0.0)

    def OpenGraph(self):	
	file = askopenfilename(title="Open HMM",
			       defaultextension=".cat",
			       filetypes = ( ("HMM", ".hmm"), ("XML", ".xml")
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
	    self.SetTitle("Gred _VERSION_ - " + self.graphName)

	    if not self.gridding:
		self.graphMenu.invoke(self.graphMenu.index('Grid'))	


    def SaveGraph(self):
	if self.fileName != None:
	    self.HMM.SaveAs(self.fileName)
	else:
	    self.SaveAsGraph()
	

    def SaveAsGraph(self):
	file = asksaveasfilename(title="Save HMM",
				 defaultextension=".hmm",
				 filetypes = ( ("HMM", ".hmm"),
					       )
				 )
	if file is "": 
	    print "cancelled"
	else:
	    print file
	    self.fileName = file
	    self.HMM.SaveAs(file)
	    self.graphName = stripPath(file)
	    self.SetTitle("Gred _VERSION_ - " + self.graphName)


    def EditWeightUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if "edges" in tags:
 		(tail,head) = self.edge[widget]

                import ProbEditorBasics
                import ProbEditorDialogs
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
                    import ProbEditorBasics
                    import ProbEditorDialogs
                    emission_probabilities=ProbEditorBasics.ProbDict({})

                    count = self.HMM.G.NrOfVertexWeights()
                    for i in xrange(count):
                        weight=self.HMM.G.vertexWeights[i][v]
                        label = "%s" % self.HMM.hmmAlphabet[i] # XXX
                        emission_probabilities.update({label:weight})

                    if emission_probabilities.sum==0:
                        key_list=emission_probabilities.keys()
                        for key in key_list:
                            emission_probabilities[key]=1.0/len(key_list)
                    e=ProbEditorBasics.emission_data(emission_probabilities)
                    d = ProbEditorDialogs.emission_dialog(self,
                                                          e,
                                                          "emission probs of state %d"%v)
                    if d.success():
                        # write back normalized probabilities
                        for key in emission_probabilities.keys():
                            i = int(key[7:])
                            self.HMM.G.vertexWeights[i][v]=emission_probabilities[key]/emission_probabilities.sum	

    def EditEmissions(self):
	d = EditEmissionProbDialog(self, self.HMM.G)

    def EditPrior(self):
	if self.HMM.G.Order() == 0:
	    return
	if self.HMM.Pi == None:
	    self.HMM.Pi = [1.0 / self.HMM.G.Order()] * self.HMM.G.Order()
	else:
	    if len(self.HMM.Pi) < self.HMM.G.Order():
		self.HMM.Pi = self.HMM.Pi + [0.0] * (self.HMM.G.Order() - len(self.HMM.Pi))
	d = EditPriorDialog(self, self.HMM.Pi)

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
