#!/usr/bin/env python
################################################################################
#
#       This is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/Gato
#
#	file:   gred.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################
from Graph import Graph
from DataStructures import EdgeWeight
from GraphUtil import OpenCATBoxGraph, OpenGMLGraph, SaveCATBoxGraph, WeightedGraphInformer
from GraphEditor import GraphEditor
from Tkinter import *
from GatoUtil import stripPath, extension
from GatoGlobals import *

from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel
import tkSimpleDialog 
import whrandom
import string


class RandomizeEdgeWeightsDialog(tkSimpleDialog.Dialog):
    """ self.result is an array of triples (randomize, min, max)
        where 'randomize' indicates whether to randomize weight i
	and min and max give the range the random values are drawn
        from.

        If user cancelled, self.result is None """

    def __init__(self, master, nrOfWeights, keepFirst):
	self.keepFirst = keepFirst
	self.nrOfWeights = nrOfWeights
	tkSimpleDialog.Dialog.__init__(self, master, "Randomize Edge Weights")
	
    def body(self, master):
	self.resizable(0,0)
	label = Label(master, text="Weight", anchor=W)
	label.grid(row=0, column=0, padx=4, pady=3, sticky="e")
	label = Label(master, text="Randomize", anchor=W)
	label.grid(row=0, column=1, padx=4, pady=3, sticky="e")
	label = Label(master, text="Minimum", anchor=W)
	label.grid(row=0, column=2, padx=4, pady=3, sticky="e")
	label = Label(master, text="Maximum", anchor=W)
	label.grid(row=0, column=3, padx=4, pady=3, sticky="e")

	self.minimum = []
	self.maximum = []
	self.check = []
	self.checkVar = []

	for i in xrange(self.nrOfWeights):
	    label = Label(master, text="%d" % (i+1), anchor=W)
	    label.grid(row=i+1, column=0, padx=4, pady=3, sticky="e")
	    
	    if (i == 0 and not self.keepFirst) or i > 0:
		self.checkVar.append(IntVar())
		self.check.append(Checkbutton(master, 
					      variable=self.checkVar[i]))
		self.check[i].select()
		self.check[i].grid(row=i+1, column=1, padx=4, pady=3, sticky="e")
		
		self.minimum.append(Entry(master, width=6, exportselection=FALSE))
		self.minimum[i].insert(0,"0")
		self.minimum[i].grid(row=i+1, column=2, padx=4, pady=3, sticky="e")
		
		self.maximum.append(Entry(master, width=6, exportselection=FALSE))
		self.maximum[i].insert(0,"100")
		self.maximum[i].grid(row=i+1, column=3, padx=4, pady=3, sticky="e")
	    else:
		self.checkVar.append(None)
		self.check.append(None)
		self.minimum.append(None)
		self.maximum.append(None)
	    
    def validate(self):
	self.result = []
 	for i in xrange(self.nrOfWeights):
	    if self.checkVar[i] != None:
		self.result.append( (self.checkVar[i].get(), 
				     string.atof(self.minimum[i].get()),
				     string.atof(self.maximum[i].get())))
	    else:
		self.result.append( (0, None, None))
# 	    try:
# 		minimun = string.atof(self.minimum[i].get())
# 	    except ValueError:
# 		minimum = "Please enter an floating point number for minimum of weight %d." % (i+1) 
# 	    try:
# 		maximum = string.atof(self.maximum[i].get())
# 	    except ValueError:
# 		m = "Please enter an floating point number for maximum of weight %d." % (i+1) 
# 	    try:
# 		maximum = string.atof(self.maximum[i].get())
# 	    except ValueError:
# 		m = "Please enter an floating point number for maximum of weight %d." % (i+1) 
	return 1
		



class SAGraphEditor(GraphEditor, Frame):

    def __init__(self, master=None):
	Frame.__init__(self, master)
	self.G = None
	self.pack() 
	self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
	self.makeMenuBar()
	GraphEditor.__init__(self)
	self.fileName = None
	self.dirty = 0
	#self.zoomMenu['state'] = DISABLED
	self.SetGraphMenuOptions()

    def SetGraphMenuOptions(self):
	if not self.directedVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Directed'))	
	if not self.euclideanVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Euclidean'))
	if not self.gridding:
	    self.graphMenu.invoke(self.graphMenu.index('Grid'))	
	self.toolsMenu.invoke(self.toolsMenu.index('Add or move vertex'))	
	self.weightsSubmenu.invoke(self.weightsSubmenu.index('One'))


    def SetTitle(self,title):
	self.master.title(title)
	
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

	# Add graph menu
	self.graphMenu = Menu(self.menubar, tearoff=0)
	self.directedVar = IntVar()
	self.graphMenu.add_checkbutton(label='Directed',  
				       command=self.graphDirected,
				       var = self.directedVar)
	self.euclideanVar = IntVar()
	self.graphMenu.add_checkbutton(label='Euclidean', 
				       command=self.graphEuclidean,
				       var = self.euclideanVar)
	self.integerVar = IntVar()
	self.graphMenu.add_checkbutton(label='Integer Weights', 
				       command=self.graphIntegerWeights,
				       var = self.integerVar)
	self.graphMenu.add_separator()

	self.weightsSubmenu = Menu(self.graphMenu, tearoff=0)
	self.weightVar = IntVar()
	self.weightsSubmenu.add_radiobutton(label="One", 
					    command=self.ChangeEdgeWeights,
					    var = self.weightVar, value=1)
	self.weightsSubmenu.add_radiobutton(label="Two", 
					    command=self.ChangeEdgeWeights,
					    var = self.weightVar, value=2)
	self.weightsSubmenu.add_radiobutton(label="Three", 
					    command=self.ChangeEdgeWeights,
					    var = self.weightVar, value=3)
	self.graphMenu.add_cascade(label='Edge Weights', 
				   menu=self.weightsSubmenu)

    
	self.graphMenu.add_separator()
	self.graphMenu.add_checkbutton(label='Grid', 
						  command=self.ToggleGridding)	
	self.menubar.add_cascade(label="Graph", menu=self.graphMenu, 
				 underline=0)


	# Add Tools menu
	self.toolsMenu = Menu(self.menubar,tearoff=1)
	self.toolVar = StringVar()
	self.toolsMenu.add_radiobutton(label='Add or move vertex',  
				       command=self.ChangeTool,
				       var = self.toolVar, value='AddOrMoveVertex')
	self.toolsMenu.add_radiobutton(label='Add edge', 
				       command=self.ChangeTool,
				       var = self.toolVar, value='AddEdge')
	self.toolsMenu.add_radiobutton(label='Delete edge or vertex', 
				       command=self.ChangeTool,
				       var = self.toolVar, value='DeleteEdgeOrVertex')
	self.toolsMenu.add_radiobutton(label='Swap orientation', 
				       command=self.ChangeTool,
				       var = self.toolVar, value='SwapOrientation')
	self.toolsMenu.add_radiobutton(label='Edit Edge Weight', 
					command=self.ChangeTool,
				       var = self.toolVar, value='EditEdgeWeight')
	self.menubar.add_cascade(label="Tools", menu=self.toolsMenu, 
				 underline=0)
	self.master.configure(menu=self.menubar)

  	# Add extras menu
	self.extrasMenu = Menu(self.menubar, tearoff=0)
	self.extrasMenu.add_command(label='Randomize Layout',
				  command=self.RandomizeLayout)
	self.extrasMenu.add_separator()
	self.extrasMenu.add_command(label='Randomize Edge Weights',
				  command=self.RandomizeEdgeWeights)
	self.menubar.add_cascade(label="Extras", menu=self.extrasMenu, 
				 underline=0)
 
    ############################################################
    #
    # Menu Commands
    #
    # The menu commands are passed as call back parameters to 
    # the menu items.
    #

    def NewGraph(self):
	G = Graph()
	G.directed = 1
	self.graphName = "New"
	self.ShowGraph(G,self.graphName)
	self.RegisterGraphInformer(WeightedGraphInformer(G,"weight"))
	self.fileName = None
	self.SetTitle("Gred _VERSION_ - New Graph")
	self.SetGraphMenuOptions()
	if self.integerVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Integer Weights'))

    def OpenGraph(self):	
	file = askopenfilename(title="Open Graph",
			       defaultextension=".cat",
			       filetypes = ( ("Gato", ".cat"),
					     ("GML", ".gml"),
					     ("Graphlet", ".let")
					     )
			       )
	if file is "": 
	    print "cancelled"
	else:
	    #print file
	    self.fileName = file
	    self.dirty = 0
	    self.graphName = stripPath(file)
	    e = extension(file)
	    if e == 'cat':
		G = OpenCATBoxGraph(file)
	    elif e == 'gml':
		G = OpenGMLGraph(file)
	    else:
		print "Unknown extension" 
	    self.SetTitle("Gred _VERSION_ - " + self.graphName)

	    if not self.gridding:
		self.graphMenu.invoke(self.graphMenu.index('Grid'))	

	    if G.QDirected() != self.directedVar.get():
		self.graphMenu.invoke(self.graphMenu.index('Directed'))	

	    if G.QEuclidian() != self.euclideanVar.get():
		self.graphMenu.invoke(self.graphMenu.index('Euclidean'))	
	    
	    if G.edgeWeights[0].QInteger() != self.integerVar.get():
		self.graphMenu.invoke(self.graphMenu.index('Integer Weights'))

	    if G.NrOfEdgeWeights() == 1:
	    	self.weightsSubmenu.invoke(self.weightsSubmenu.index('One'))
	    elif G.NrOfEdgeWeights() == 2:
	    	self.weightsSubmenu.invoke(self.weightsSubmenu.index('Two'))
	    elif G.NrOfEdgeWeights() == 3:
	    	self.weightsSubmenu.invoke(self.weightsSubmenu.index('Three')) 

	    self.RegisterGraphInformer(WeightedGraphInformer(G,"weight"))
	    self.ShowGraph(G,self.graphName)



    def SaveGraph(self):
	#self.dirty = 0
	if self.fileName != None:
	    SaveCATBoxGraph(self.G,self.fileName)
	else:
	    self.SaveAsGraph()

    def SaveAsGraph(self):
	file = asksaveasfilename(title="Save Graph",
				 defaultextension=".cat",
				 filetypes = ( ("Gato", ".cat"),
					       ("Graphlet", ".let")
					       )
				 )
	if file is "": 
	    print "cancelled"
	else:
	    print file
	    self.fileName = file
	    self.dirty = 0
	    SaveCATBoxGraph(self.G,file)
	    self.graphName = stripPath(file)
	    self.SetTitle("Gred _VERSION_ - " + self.graphName)

    def ExportEPSF(self):
	file = asksaveasfilename(title="Export EPSF",
				 defaultextension=".eps",
				 filetypes = ( ("Encapsulated PS", ".eps"),
					       ("Postscript", ".ps")
					       ))
	if file is "": 
	    print "cancelled"
	else:
	    print file
	    self.PrintToPSFile(file)


    def Quit(self):
	if askokcancel("Quit","Do you really want to quit?"):
	    Frame.quit(self)


    #----- Graph Menu callbacks
    def graphDirected(self):
	if self.G != None:
	    if self.G.QDirected():
		self.G.Undirect()
	    else:
		self.G.directed = 1

	    self.ShowGraph(self.G,self.graphName)
  
    def graphEuclidean(self):
	if self.G != None:
	    if self.G.QEuclidian():
		self.G.euclidian = 0
	    else:
		self.G.Euclidify()

    def graphIntegerWeights(self):
	if self.G != None:
	    if not self.G.edgeWeights[0].QInteger():
		self.G.Integerize('all')
	    

    def ChangeEdgeWeights(self):
	if self.G == None:
	    return
	n = self.weightVar.get()
	k = self.G.edgeWeights.keys()
	if self.G.edgeWeights[0].QInteger():
	    initialWeight = 0
	else:
	    initialWeight = 0.0	

	if n == 1 or n == 2:
	    if 2 in k:
		del(self.G.edgeWeights[2])
	else:
	    if 2 not in k:
		self.G.edgeWeights[2] = EdgeWeight(self.G, initialWeight)  
		if self.G.edgeWeights[0].QInteger():
		    self.G.edgeWeights[2].Integerize()
	    
	if n == 1:
	    if 1 in k:
		del(self.G.edgeWeights[1])
	else:
	    if 1 not in k:
		self.G.edgeWeights[1] = EdgeWeight(self.G, initialWeight)  
		if self.G.edgeWeights[0].QInteger():
		    self.G.edgeWeights[1].Integerize()



    #----- Tools Menu callbacks
    def ChangeTool(self):
	self.SetEditMode(self.toolVar.get())

    #----- Extras Menu callbacks

    def RandomizeLayout(self):
	for v in self.G.vertices:
	    self.MoveVertex(v, 
			    whrandom.randint(10,990),
			    whrandom.randint(10,990), 
			    1)

    def RandomizeEdgeWeights(self):
	count = len(self.G.edgeWeights.keys())
	d = RandomizeEdgeWeightsDialog(self, count, self.G.QEuclidian()) 
	if d.result is None:
	    return

	for e in self.G.Edges():
	    for i in xrange(count):
		if d.result[i][0] == 1:
		    val = whrandom.uniform(d.result[i][1],d.result[i][2])
		    if self.G.edgeWeights[i].QInteger():
			self.G.edgeWeights[i][e] = round(int(val))
		    else:
			self.G.edgeWeights[i][e] = val


################################################################################
if __name__ == '__main__':
    graphEditor = SAGraphEditor(Tk())
    graphEditor.NewGraph()
    graphEditor.mainloop()

