#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   gred.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
from Graph import Graph
from DataStructures import EdgeWeight, VertexWeight
from GraphUtil import OpenCATBoxGraph, OpenGMLGraph, SaveCATBoxGraph, WeightedGraphInformer
from GraphEditor import GraphEditor
from Tkinter import *
from GatoUtil import stripPath, extension
from GatoGlobals import *
import GatoDialogs
from ScrolledText import *

from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel
import tkSimpleDialog 
import whrandom
import string
import sys
import os

class GredSplashScreen(GatoDialogs.SplashScreen):

    def CreateWidgets(self):
	self.catIcon = PhotoImage(file=sys.path[0] + "/gred.gif")
	self.label = Label(self, image=self.catIcon)
	self.label.pack(side=TOP)
	self.label = Label(self, text=GatoDialogs.crnotice1)
	self.label.pack(side=TOP)
	label = Label(self, font="Helvetica 10", text=GatoDialogs.crnotice2, justify=LEFT)
	label.pack(side=TOP)

class GredAboutBox(GatoDialogs.AboutBox):

    def body(self, master):
	self.resizable(0,0)
	self.catIconImage = PhotoImage(file=sys.path[0] + "/gred.gif")
	self.catIcon = Label(master, image=self.catIconImage)
	self.catIcon.pack(side=TOP)
	label = Label(master, text=GatoDialogs.crnotice1)
	label.pack(side=TOP)
	label = Label(master, font="Helvetica 10", text=GatoDialogs.crnotice2, justify=LEFT)
	label.pack(side=TOP)
 	color = self.config("bg")[4]
	self.infoText = ScrolledText(master, relief=FLAT, 
				     padx=3, pady=3,
				     background=color, 
				     #foreground="black",
				     wrap='word',
				     width=60, height=12,
				     font="Times 10")
	self.infoText.pack(expand=0, fill=X, side=BOTTOM)
	self.infoText.delete('0.0', END)
	inputFile=open(sys.path[0] +"/LGPL.txt", 'r')
       	text = inputFile.read()
	inputFile.close()
	self.infoText.insert('0.0', text)	
	self.infoText.configure(state=DISABLED)
	self.title("Gred - About")

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
	Splash = GredSplashScreen(self.master)
	self.G = None
	self.pack() 
	self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
	self.makeMenuBar()
	GraphEditor.__init__(self)
	self.fileName = None
	self.dirty = 0
	#self.zoomMenu['state'] = DISABLED
	self.SetGraphMenuOptions()
	Splash.Destroy()

    def SetGraphMenuOptions(self):
	if not self.directedVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Directed'))	
	if not self.euclideanVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Euclidean'))
	if not self.gridding:
	    self.graphMenu.invoke(self.graphMenu.index('Grid'))	
	self.toolsMenu.invoke(self.toolsMenu.index('Add or move vertex'))	
	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('One'))
	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('None'))


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
	self.graphMenu.add_separator()

	# vertex weigths
	self.vertexIntegerWeightsVar = IntVar()
	self.graphMenu.add_checkbutton(label='Integer Vertex Weights', 
				       command=self.vertexIntegerWeights,
				       var = self.vertexIntegerWeightsVar)

	self.vertexWeightsSubmenu = Menu(self.graphMenu, tearoff=0)
	self.vertexWeightVar = IntVar()
	self.vertexWeightsSubmenu.add_radiobutton(label="None", 
					    command=self.ChangeVertexWeights,
					    var = self.vertexWeightVar, value=0)
	self.vertexWeightsSubmenu.add_radiobutton(label="One", 
					    command=self.ChangeVertexWeights,
					    var = self.vertexWeightVar, value=1)
	self.vertexWeightsSubmenu.add_radiobutton(label="Two", 
					    command=self.ChangeVertexWeights,
					    var = self.vertexWeightVar, value=2)
	self.vertexWeightsSubmenu.add_radiobutton(label="Three", 
					    command=self.ChangeVertexWeights,
					    var = self.vertexWeightVar, value=3)
	self.graphMenu.add_cascade(label='Vertex Weights', 
				   menu=self.vertexWeightsSubmenu)

    

	# edge weigths
	self.edgeIntegerWeightsVar = IntVar()
	self.graphMenu.add_checkbutton(label='Integer Edge Weights', 
				       command=self.edgeIntegerWeights,
				       var = self.edgeIntegerWeightsVar)

	self.edgeWeightsSubmenu = Menu(self.graphMenu, tearoff=0)
	self.edgeWeightVar = IntVar()
	self.edgeWeightsSubmenu.add_radiobutton(label="One", 
					    command=self.ChangeEdgeWeights,
					    var = self.edgeWeightVar, value=1)
	self.edgeWeightsSubmenu.add_radiobutton(label="Two", 
					    command=self.ChangeEdgeWeights,
					    var = self.edgeWeightVar, value=2)
	self.edgeWeightsSubmenu.add_radiobutton(label="Three", 
					    command=self.ChangeEdgeWeights,
					    var = self.edgeWeightVar, value=3)
	self.graphMenu.add_cascade(label='Edge Weights', 
				   menu=self.edgeWeightsSubmenu)


    
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
	self.toolsMenu.add_radiobutton(label='Edit Weight', 
					command=self.ChangeTool,
				       var = self.toolVar, value='EditWeight')
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

	# On a Mac we put our about box under the Apple menu ... 
	if os.name == 'mac':
	    self.apple=Menu(self.menubar, tearoff=0, name='apple')
	    self.apple.add_command(label='About Gred',	
				   command=self.AboutBox)
	    self.menubar.add_cascade(menu=self.apple)
	else: # ... on other systems we add a help menu 
	    self.helpMenu=Menu(self.menubar, tearoff=0, name='help')
	    self.helpMenu.add_command(label='About Gred',	
				      command=self.AboutBox)
	    self.menubar.add_cascade(label="Help", menu=self.helpMenu, 
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
	if self.edgeIntegerWeightsVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Integer Edge Weights'))
	if self.vertexIntegerWeightsVar.get():
	    self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights'))

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
	    
	    if G.edgeWeights[0].QInteger() != self.edgeIntegerWeightsVar.get():
		self.graphMenu.invoke(self.graphMenu.index('Integer Edge Weights'))
		self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights')) 
		# Just one integer flag for vertex and edge weights 

	    if G.NrOfEdgeWeights() == 1:
	    	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('One'))
	    elif G.NrOfEdgeWeights() == 2:
	    	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('Two'))
	    elif G.NrOfEdgeWeights() == 3:
	    	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('Three')) 

	    if G.NrOfVertexWeights() == 0 or (G.NrOfVertexWeights() > 0 and 
					      G.vertexWeights[0].QInteger()):
		self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights'))
	

	    if G.NrOfVertexWeights() == 0:
	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('None'))
	    elif G.NrOfVertexWeights() == 1:
	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('One'))
	    elif G.NrOfVertexWeights() == 2:
	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('Two'))
	    elif G.NrOfVertexWeights() == 3:
	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('Three'))



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

    def edgeIntegerWeights(self):
	if self.G != None:
	    if not self.G.edgeWeights[0].QInteger():
		self.G.Integerize('all')
	    
    def vertexIntegerWeights(self):
	if self.G != None:
	    for i in xrange(0,self.G.NrOfVertexWeights()):
		if not self.G.vertexWeights[i].QInteger(): 
		    self.G.vertexWeights[i].Integerize()
		else:
		    self.G.vertexWeights[i] = 0
	    

    def ChangeEdgeWeights(self):
	if self.G == None:
	    return
	n = self.edgeWeightVar.get()
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


    def ChangeVertexWeights(self):
	if self.G == None:
	    return
	n = self.vertexWeightVar.get()
	old = self.G.NrOfVertexWeights()
	k = self.G.vertexWeights.keys()
	if self.vertexIntegerWeightsVar.get() == 1:
	    initialWeight = 0
	else:
	    initialWeight = 0.0	
		
	if n > old: # Add additional weigths
	    for i in xrange(old,n):
		self.G.vertexWeights[i] = VertexWeight(self.G, initialWeight) 
		if self.vertexIntegerWeightsVar.get() == 1:
		    self.G.vertexWeights[i].Integerize()
	else:       # Delete superfluos weigths
	    for i in xrange(n,old):
		del(self.G.vertexWeights[i])
	
	# Integerize remaining weigths if necessary
	if self.vertexIntegerWeightsVar.get() == 1:
	    for i in xrange(0,min(n,old)): 
		self.G.vertexWeights[i].Integerize()
	    



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

    def AboutBox(self):
	print "AboutBox"
	d = GredAboutBox(self.master)


################################################################################
if __name__ == '__main__':
    graphEditor = SAGraphEditor(Tk())
    graphEditor.NewGraph()
    graphEditor.mainloop()

