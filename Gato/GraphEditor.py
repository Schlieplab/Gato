################################################################################
#
#       This is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/Gato
#
#	file:   GraphEditor.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################


from Tkinter import *
from Graph import Graph, Point2D
from math import sqrt
from GatoGlobals import *
from GraphDisplay import GraphDisplay
from tkSimpleDialog import askinteger, askfloat
import tkSimpleDialog 
import string
import tkMessageBox

class EditWeightsDialog(tkSimpleDialog.Dialog):

    def __init__(self, master, edge, nrOfWeights, weights, intFlag):
	self.nrOfWeights = nrOfWeights
	self.weights = weights
	self.intFlag = intFlag
	tkSimpleDialog.Dialog.__init__(self, master, "Edit edge weights (%d,%d)" % edge)


    def body(self, master):
	self.resizable(0,0)
	#label = Label(master, text="Weight", anchor=W)
	#label.grid(row=0, column=0, padx=4, pady=3)
	label = Label(master, text="Value", anchor=W)
	label.grid(row=0, column=1, padx=4, pady=3)

	self.entry = [None] * self.nrOfWeights

	for i in xrange(self.nrOfWeights):
	    label = Label(master, text="Weight %d" %(i+1), anchor=W)
	    label.grid(row=i+1, column=0, padx=4, pady=3, sticky="e")
	    self.entry[i] = Entry(master, width=6, exportselection=FALSE)
	    if self.intFlag[i]:
		self.entry[i].insert(0,"%d" % self.weights[i])
	    else:
		self.entry[i].insert(0,"%f" % self.weights[i])
	    self.entry[i].grid(row=i+1, column=1, padx=4, pady=3, sticky="w")

    def validate(self):
	self.result = [None] * self.nrOfWeights
	for i in xrange(self.nrOfWeights):	    
	    try:
		if self.intFlag[i]:
		    self.result[i] = string.atoi(self.entry[i].get())
		else:
		    self.result[i] = string.atof(self.entry[i].get())
	    except ValueError:
		if self.intFlag[i]:
		    m = "Please enter an integer value for weight %d." % (i+1) 
		else:
		    m = "Please enter an floating point number for weight %d." % (i+1) 
		tkMessageBox.showwarning("Invalid Value", m, parent=self)
		self.entry[i].selection_range(0,"end")
		self.entry[i].focus_set()
		self.result = None
		return 0
	return 1

class GraphEditor(GraphDisplay):
    """ GraphEditor is a subclass of GraphDisplay providing an user interface
        for editing options. Core edit operations are defined in  GraphDisplay.
	GraphEditor is not designed for direct consumption, use 

	- GraphEditorFrame
	- GraphEditorToplevel

	instead. 

	Bindings:
	- Mouse, button 1 down/up: Add a vertex if nothing underneath mouse
	  else select for move vertex
	- Mouse, move: move vertex 
	- Mouse, button 2 down: select tail for adding an edge 
	- Mouse, button 2 up: select head for adding an edge 
	- Mouse, button 3 up: delete vertex/edge  underneath mouse
	"""


    def __init__(self):
	GraphDisplay.__init__(self)

	self.rubberbandLine = None
	self.movedVertex = None
	self.startx = None # position where MouseDown first occurred
	self.starty = None
	self.lastx = None # position at last MouseMove
	self.lasty = None
	self.gridSize = gGridSize
	self.gridding = 0
	self.mode = 'AddOrMoveVertex'
        # 'AddEdge' 'DeleteEdgeOrVertex' 'SwapOrientation' 'EditEdgeWeight'

    def ToggleGridding(self):
	""" Toggle gridding """
	if self.gridding:
	    self.gridding = 0
	else:
	    self.gridding = 1

    def SetEditMode(self,mode):
	self.mode = mode

    def WindowToCanvasCoords(self,event):
	""" Given an event return the (x,y) in canvas coordinates while 
	    using gridding if a gridsize is specified in gGridSize """
	if not self.gridding:
	    x = self.canvas.canvasx(event.x)
	    y = self.canvas.canvasy(event.y)
	else:
	    x = self.canvas.canvasx(event.x,self.gridSize)
	    y = self.canvas.canvasy(event.y,self.gridSize)
	return (x,y)

    def Zoom(self,percent,doUpdate=1):
	try:
	    GraphDisplay.Zoom(self,percent,doUpdate)
	    self.gridSize = (gGridSize * self.zoomFactor) / 100.0
	except:
	    return None

    def CreateWidgets(self):
	""" Add additional bindings with proper callbacks to canvas  """
	GraphDisplay.CreateWidgets(self)

	Widget.bind(self.canvas, "<1>", self.MouseDown) 
        Widget.bind(self.canvas, "<B1-Motion>", self.MouseMove)
        Widget.bind(self.canvas, "<B1-ButtonRelease>", self.MouseUp) 
	Widget.bind(self.canvas, "<2>", self.Mouse2Down) 
        Widget.bind(self.canvas, "<B2-Motion>", self.Mouse2Move)
        Widget.bind(self.canvas, "<B2-ButtonRelease>", self.Mouse2Up) 
        Widget.bind(self.canvas, "<B3-ButtonRelease>", self.Mouse3Up)


	

    #===== ACTIONS ==============================================================

    def AddOrMoveVertexDown(self,event):
	v = self.FindVertex(event)
	if v == None: 
	    (x,y) = self.WindowToCanvasCoords(event)
	    self.AddVertex(x,y)
	    self.movedVertex = None
	else:
	    self.canvas.addtag("mySel", "withtag", self.drawVertex[v])
	    self.canvas.addtag("mySel", "withtag", self.drawLabel[v])
	    # We want to start off with user clicking smack in middle of
	    # vertex -- cant force him, so we fake it
	    c = self.canvas.coords(self.drawVertex[v])
	    # c already canvas coordinates
	    self.lastx = (c[2] - c[0])/2 + c[0]
	    self.lasty = (c[3] - c[1])/2 + c[1]
	    self.movedVertex = v
	    self.didMoveVertex = 0


    def AddOrMoveVertexMove(self,event):
	x = self.canvas.canvasx(event.x)
	y = self.canvas.canvasy(event.y)
	self.update_idletasks()
	try:
	    self.canvas.move("mySel", x - self.lastx, y - self.lasty)
	    self.lastx = x
	    self.lasty = y
	    self.didMoveVertex = 1
	except:
	    i = 1 # Need instruction after except

    def AddOrMoveVertexUp(self,event):
	if self.movedVertex != None:
	    (x,y) = self.WindowToCanvasCoords(event)
	    # Moving within vertex oval does not move vertex
	    self.update_idletasks()
	    if self.didMoveVertex:
		self.canvas.move("mySel", x - self.lastx, y - self.lasty)
		self.MoveVertex(self.movedVertex,x,y)
		#self.VertexInfo(event)
	    self.movedVertex = None
	    self.canvas.dtag("mySel")


    def AddEdgeDown(self,event):
	self.tail = self.FindVertex(event)
	if self.tail != None:
	    c = self.canvas.coords(self.drawVertex[self.tail])
	    self.startx = (c[2] - c[0])/2 + c[0]
	    self.starty = (c[3] - c[1])/2 + c[1] 


    def AddEdgeMove(self,event):
	if self.tail != None:	
	    # canvas x and y take the screen coords from the event and translate
	    # them into the coordinate system of the canvas object
	    x = self.canvas.canvasx(event.x)
	    y = self.canvas.canvasy(event.y)
 
	    if (self.startx != event.x)  and (self.starty != event.y) : 
		self.canvas.delete(self.rubberbandLine)
		self.rubberbandLine = self.canvas.create_line(
		    self.startx, self.starty, x, y)
		self.canvas.lower(self.rubberbandLine,"vertices")
		# this flushes the output, making sure that 
		# the rectangle makes it to the screen 
		# before the next event is handled
		self.update_idletasks()



    def AddEdgeUp(self,event):
	if self.tail != None:	
	    x = self.canvas.canvasx(event.x)
	    y = self.canvas.canvasy(event.y)
	    self.canvas.delete(self.rubberbandLine)
 
	    widget = event.widget.find_closest(x,y,None,self.rubberbandLine)
	    if widget:
		widget = widget[0]
		tags = self.canvas.gettags(widget)
		if "vertices" in tags:
		    head = self.vertex[widget]
		elif "labels" in tags:
		    head = self.label[widget]

		if not self.tail == head:
		    self.AddEdge(self.tail,head)
		    # DEBUG print "edge weight", self.G.edgeWeights[0][(self.tail,head)]


    def DeleteEdgeOrVertexUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if "edges" in tags:
		(tail,head) = self.edge[widget]
		self.DeleteEdge(tail,head)
	    else:
		if "vertices" in tags:
		    v = self.vertex[widget]
		elif "labels" in tags:
		    v = self.label[widget]
		    self.DeleteVertex(v)


    def SwapOrientationUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if "edges" in tags:
		(tail,head) = self.edge[widget]
		self.SwapEdgeOrientation(tail,head)


    def EditEdgeWeightUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if "edges" in tags:
 		(tail,head) = self.edge[widget]

		weights = ()
		intFlag = ()
		count = len(self.G.edgeWeights.keys())
		for i in xrange(count):
		    weights = weights + (self.G.edgeWeights[i][(tail,head)],)
		    intFlag = intFlag + (self.G.edgeWeights[i].QInteger(),)

		d = EditWeightsDialog(self, (tail,head), count, weights, intFlag) 
		if d.result is not None:
		    for i in xrange(count):
			self.G.edgeWeights[i][(tail,head)] = d.result[i]
	

    #===== GUI-Bindings FOR ACTIONS ================================================

    def MouseDown(self,event):
	if self.mode == 'AddOrMoveVertex':
	    self.AddOrMoveVertexDown(event)
	elif self.mode == 'AddEdge':
	    self.AddEdgeDown(event)

    def MouseMove(self,event):
	if self.mode == 'AddOrMoveVertex':
	    self.AddOrMoveVertexMove(event)
	elif self.mode == 'AddEdge':
	    self.AddEdgeMove(event)

    def MouseUp(self,event):
	if self.mode == 'AddOrMoveVertex':
	    self.AddOrMoveVertexUp(event)
	elif self.mode == 'AddEdge':
	    self.AddEdgeUp(event)
	elif self.mode == 'DeleteEdgeOrVertex':
	    self.DeleteEdgeOrVertexUp(event)
	elif self.mode == 'SwapOrientation':
	    self.SwapOrientationUp(event)
	elif self.mode == 'EditEdgeWeight':
	    self.EditEdgeWeightUp(event)

    def Mouse2Down(self,event):
	self.AddEdgeDown(event)

    def Mouse2Move(self,event):
	self.AddEdgeMove(event)

    def Mouse2Up(self,event):
	self.AddEdgeUp(event)

    def Mouse3Up(self,event):
	self.DeleteEdgeOrVertexUp(event)


class GraphEditorFrame(GraphEditor, Frame):
    """ A GraphEditor in a frame """
    def __init__(self, master=None):
	Frame.__init__(self, master)
	self.pack() 
	self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
	GraphEditor.__init__(self)

    def SetTitle(self,title):
	print "change window title to" + `title`
	

class GraphEditorToplevel(GraphEditor, Toplevel):
    """ A GraphEditor in a top-level window """

    def __init__(self, master=None):
	Toplevel.__init__(self, master)
	GraphEditor.__init__(self)

    def SetTitle(self,title):
	self.title(title)
