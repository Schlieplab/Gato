################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GraphDisplay.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

from Tkinter import * # Frame, Canvas, Toplevel, StringVar and lots of handy constants
from Graph import Graph
from math import sqrt
from GatoGlobals import *
from GatoUtil import orthogonal
from DataStructures import Point2D, VertexLabeling, EdgeLabeling
import os
import colorsys

class ZoomVar(StringVar):
    """ *Internal* helper class to have TK update variable correspoding
        to pop-up state """

    def __init__(self, graphDisplay,initialValue):
	self.graphDisplay = graphDisplay
	StringVar.__init__(self)
	StringVar.set(self,initialValue)

    def set(self, value):
	try:
	    self.graphDisplay.Zoom(value)
	except:
	    None
	return StringVar.set(self,value)


class GraphDisplay:
    """ Provide functionality to display a graph. Not for direct consumption.
        Use
	
	- GraphDisplayToplevel
	- GraphDisplayFrame 

	GraphDisplay also provides UI-Interface independent edit operations
	and basic animation methods """


    def __init__(self):
	self.hasGraph = 0
	self.drawVertex       = VertexLabeling()
	self.drawEdges        = EdgeLabeling()
	self.drawLabel        = VertexLabeling()
	self.vertexAnnotation = VertexLabeling()
	self.edgeAnnotation   = EdgeLabeling()

	self.vertex = {} # XXX Dynamic array which memorizes vertex for each draw vertex
	self.edge = {}   # XXX ditto for draw edge
	self.label = {}  # XXX ditto for label

	self.zoomFactor = 100.0 # percent

	self.CreateWidgets()
	self.SetTitle("Gato - Graph")
	self.update()
	self.graphInformer = None
	self.clickhandler = None

    def GetCanvasCenter(self): 
	""" *Internal* Return the center of the canvas in pixel """
	# XXX How to this for non-pixel
	return (gPaperWidth/2, gPaperHeight/2)


    def Zoom(self,percent):
	""" *Internal* Perform a zoom to specified level """

	zoomFactor = {' 50 %':50.0, 
		      ' 75 %':75.0, 
		      '100 %':100.0,
		      '125 %':125.0,
		      '150 %':150.0,
		      '':100.0}

	self.newXview = self.canvas.xview()
	self.newYview = self.canvas.yview()

	try:
	    if (self.newXview != self.oldXview or 
		self.newYview != self.oldYview or
		self.zoomIn == 0):
		self.Xview = self.newXview[0]
		self.Yview = self.newYview[0]   
	except:
	    self.Xview = self.newXview[0]
	    self.Yview = self.newYview[0] 

	if zoomFactor[percent] < self.zoomFactor:
	    self.zoomIn = 1
	else:
	    self.zoomIn = 0

	factor = zoomFactor[percent] / self.zoomFactor	    
	self.zoomFactor = zoomFactor[percent]
	if self.directed == 1:
	    arrowShape = ((16*self.zoomFactor) / 100.0,
			  (20*self.zoomFactor) / 100.0,
			  (6*self.zoomFactor)  / 100.0)
	    self.canvas.itemconfigure("edges",arrowshape=arrowShape)
	self.canvas.scale("all", 0, 0, factor, factor)	

	newWidth = (self.zoomFactor / 100.0) * float(gPaperWidth)
	newHeight = (self.zoomFactor/ 100.0) * float(gPaperHeight)

	self.canvas.config(width=newWidth,height=newHeight,
			   scrollregion=(0,0,newWidth,newHeight))	
	self.canvas.xview("moveto",self.Xview)
	self.canvas.yview("moveto",self.Yview)

	self.oldXview = self.canvas.xview()
	self.oldYview = self.canvas.yview()

    def CanvasToEmbedding(self,x,y):
	""" *Internal* Convert canvas coordinates to embedding """
	x = x * 100.0 / self.zoomFactor  
	y = y * 100.0 / self.zoomFactor
	return x,y
	
    def EmbeddingToCanvas(self,x,y):
	""" *Internal* Convert Embedding coordinates to Canvas """
	x = x * self.zoomFactor / 100.0
	y = y * self.zoomFactor / 100.0
	return x,y
	

    def CreateWidgets(self):
	""" *Internal* Create UI-Elements (except Frame/Toplevel) """
	# Frame at bottom with zoom-popup and label
	self.infoframe = Frame(self, relief=FLAT)
	self.infoframe.pack(side=BOTTOM, fill=X)
	
	self.zoomValue = ZoomVar(self,'100 %')
	# XXX self.zoomValue.set('100 %')
	self.zoomMenu = OptionMenu(self.infoframe, self.zoomValue, 
				  ' 50 %',' 75 %', '100 %','125 %','150 %')
	self.zoomMenu.config(height=1)
	self.zoomMenu.config(width=5)
	if os.name == 'mac':
	    self.zoomMenu.config(font="Geneva 10")
	    self.zoomMenu["menu"].config(font="Geneva 10")
	self.zoomMenu.grid(row=0,column=0,sticky="nwse") 
	self.infoframe.columnconfigure(0,weight=0)

	# To make things more windows like, we put the info-label
        # in a separate frame
	borderFrame = Frame(self.infoframe, relief=SUNKEN, bd=1)
	self.info = Label(borderFrame, text="No information available", anchor=W)
	self.info.config(width=50)
	if os.name == 'mac':
	    self.info.config(font="Geneva 10")
	self.info.pack(side=LEFT, expand=1, fill=X)
	borderFrame.grid(row=0,column=1,sticky="nwse",padx=4,pady=3)
	self.infoframe.columnconfigure(1,weight=1)

	# Scrolling Canvas
	# To make things more windows like, we put the canvas
        # in a separate frame	
	borderFrame = Frame(self, relief=SUNKEN, bd=2)
	self.canvas = Canvas(borderFrame, width=gPaperWidth, height=gPaperHeight, 
			     background="white",
			     scrollregion=(0, 0, gPaperWidth, gPaperHeight))

	# Vertical scroll bar in a frame and with corner 
	vbarFrame = Frame(borderFrame,borderwidth=0)
	vbarFrame.pack(fill=Y, side=RIGHT)

        self.canvas.vbar = Scrollbar(borderFrame, orient=VERTICAL)
        self.canvas['yscrollcommand']  = self.canvas.vbar.set
        self.canvas.vbar['command'] = self.canvas.yview

        self.canvas.vbar.pack(in_=vbarFrame, expand=1, side=TOP, fill=Y)
	
	sbwidth = self.canvas.vbar.winfo_reqwidth()
	corner = Frame(vbarFrame, width=sbwidth, height=sbwidth)
	corner.propagate(0)
	corner.pack(side=BOTTOM)

	# Horizontal scroll bar 
        self.canvas.hbar = Scrollbar(borderFrame, orient=HORIZONTAL)
	self.canvas['xscrollcommand']  = self.canvas.hbar.set
        self.canvas.hbar['command'] = self.canvas.xview
        self.canvas.hbar.pack(side=BOTTOM, fill=X)

	self.canvas.pack(anchor=W, side=TOP)
	borderFrame.pack(anchor=W, side=TOP, expand=1, fill=BOTH)

	self.master.geometry("500x483")
	#print self.infoframe.cget('width')
	#print self.infoframe.cget('height')


    def ShowGraph(self, G, graphName):	
	""" Display graph G name graphName. Currently we assume that for 
	    the embedding (x,y) of every vertex  < x < 1000 and 0 < y < 1000
	    holds """
	self.G          = G
	self.embedding  = G.embedding # Assuming 0 < x < 1000 and 0 < y < 1000
	self.Labeling   = G.labeling
	self.directed   = G.QDirected()

	oldZoom = "100 %"
	if self.hasGraph == 1:
	    self.DeleteDrawItems()
	    # Honor whatever zoom the user has choosen
	    oldZoom = "%3d %c" % (int(self.zoomFactor), '%')
	    self.zoomFactor = 100.0
	    
	self.CreateDrawItems()
	self.Zoom(oldZoom) # Dont Delay update
	self.hasGraph = 1
	self.SetTitle("Gato - " + graphName)
	self.update()
	self.DefaultInfo()


    def RegisterGraphInformer(self, Informer):
	""" A graph informer is an object which supplies information
            about the graph, its vertices and its edges. It needs methods

	    - DefaultInfo()
	    - VertexInfo(v)
	    - EdgeInfo(tail,head)

	    If none is registered, information will be produced by
	    GraphDisplay. Infos are displayed in info field at the bottom
	    of the graph window."""
	self.graphInformer = Informer


    def CreateDrawItems(self):
	""" *Internal* Create items on the canvas """
	for v in self.G.vertices:
	    for w in self.G.OutNeighbors(v):
		self.drawEdges[(v,w)] = self.CreateDrawEdge(v,w)

	for v in self.G.vertices:
	    x = self.embedding[v].x * self.zoomFactor / 100.0
	    y = self.embedding[v].y * self.zoomFactor / 100.0
	    self.drawVertex[v] = self.CreateDrawVertex(v,x,y)

	for v in self.G.vertices:
	    self.drawLabel[v] = self.CreateDrawLabel(v)

    
    def DeleteDrawItems(self):
	""" *Internal* Delete all items on the canvas and clear up
            our references to it"""
	self.DeleteDrawEdges()
	self.DeleteDrawVertices()
	self.DeleteDrawLabels()
	self.DeleteVertexAnnotations()
	self.DeleteEdgeAnnotations()
        self.canvas.delete("all") # Remove whatever is left
	self.drawVertex       = VertexLabeling()
	self.drawEdges        = EdgeLabeling()
	self.drawLabel        = VertexLabeling()
	self.vertexAnnotation = VertexLabeling()
	self.edgeAnnotation   = EdgeLabeling()


    def DeleteDrawEdges(self):
	""" *Internal* Delete draw edges on the canvas """
	self.edge = {} # XXX
	self.canvas.delete("edges")


    def DeleteDrawVertices(self):
	""" *Internal* Delete draw vertices on the canvas """
	self.vertex = {} # XXX
	self.canvas.delete("vertices")


    def DeleteDrawLabels(self):
	""" *Internal* Delete draw labels on the canvas """
	self.label = {} # XXX
	self.canvas.delete("labels")

    def DeleteVertexAnnotations(self):
	""" *Internal* Delete all vertex annotations on the canvas """
	self.canvas.delete("vertexAnno")
	pass

    def DeleteEdgeAnnotations(self):
	""" *Internal* Delete all edge annotations on the canvas """
	self.canvas.delete("edgeAnno")
	pass

    def CreateDrawVertex(self,v,x=None,y=None):
	""" *Internal* Create a draw vertex for v on the canvas. Position is
            determined by the embedding unless explictely passed as x,y in
            canvas coordinates """
	if x == None and y == None:
	    x,y = self.EmbeddingToCanvas(self.embedding[v].x, self.embedding[v].y)
	d = (gVertexRadius * self.zoomFactor) / 100.0
 	dv = self.canvas.create_oval(x-d, y-d, x+d, y+d, 
				     fill=cVertexDefault, tag="vertices",
				     width=gVertexFrameWidth) 
	self.canvas.tag_bind(dv, "<Any-Leave>", self.DefaultInfo)
	self.canvas.tag_bind(dv, "<Any-Enter>", self.VertexInfo)
	self.vertex[dv] = v # XXX
	return dv
    
    def CreateDrawLabel(self,v):
	""" *Internal* Create a draw label for v on the canvas. Position is
            determined by the embedding specified. Text is specified by the
	    labeling:  

	    Call only after CreateDrawVertex() """
	    
        pos = self.VertexPosition(v)
	# To make label more readable on darker vertices we change colors
	# depending on brightness
	#
	# XXX Note: we assume that the defaults are reasonable 
	dl = self.canvas.create_text(pos.x, pos.y, 
				     anchor="center", 
				     justify="center", 
				     text=self.Labeling[v], 
				     fill=cLabelDefault,
				     tag="labels")
	self.canvas.tag_bind(dl, "<Any-Enter>", self.VertexInfo)
	self.label[dl] = v # XXX
        return dl
	# Label to the bottom, to the right
	#d = gVertexRadius
	#return self.canvas.create_text(x+d+1, y+d+1, anchor="w", justify="left", text=v)



    def CreateUndirectedLoopDrawEdge(self, v, w, orientation=None):
	""" *Internal* Create an undirected loop draw edge. v is a Point2D """
	d = 32       # Diameter
	offset = 10  # selected based on trial-and-error 
	return self.canvas.create_line(v.x, v.y + offset, v.x - d, v.y - d, 
				       v.x, v.y - 2*d + offset, v.x + d, v.y - d, 
				       v.x, v.y + offset,
				       fill=cEdgeDefault,
				       width=w,
				       smooth=TRUE,
				       splinesteps=24,
				       tag="edges")

    def CreateDirectedLoopDrawEdge(self,v,w, orientation=None):
	""" *Internal* Create an directed loop draw edge. v is a Point2D """
	d = 32       # Diameter
	offset = 10  # selected based on trial-and-error 
	l = sqrt((v.x + d - v.x)**2 + (v.y - d - v.y - offset)**2)
	if l < 0.001:
	    l = 0.001
	zVertexRadius = (gVertexRadius * self.zoomFactor) / 100.0
	c = (l - zVertexRadius)/l - 0.001 # Dont let them quite touch 
	tmpX = v.x + c * (v.x + d - v.x) 
	tmpY = v.y + offset + c * (v.y - d - v.y - offset)
	arrowShape = ((16*self.zoomFactor) / 100.0,
		      (20*self.zoomFactor) / 100.0,
		      (6*self.zoomFactor)  / 100.0)
	return self.canvas.create_line(v.x, v.y + offset, v.x - d, v.y - d, 
				       v.x, v.y - 2*d + offset, v.x + d, v.y - d, 
				       v.x + offset, v.y - offset,
				       #tmpX, tmpY,
				       arrow="last",
				       arrowshape=arrowShape, 
				       fill=cEdgeDefault,
				       width=w,
				       smooth=TRUE,
				       splinesteps=24,
				       tag="edges")
	

    def CreateUndirectedDrawEdge(self,t,h,w):
	""" *Internal* Create an undirected draw edge. t, h are Point2Ds """
	return self.canvas.create_line(t.x,t.y,h.x,h.y,
				       fill=cEdgeDefault,
				       width=w,
				       tag="edges") 
 
    def CreateDirectedDrawEdge(self,t,h,curved,w):
	""" *Internal* Create an directed draw edge. t, h are Point2Ds """
	l = sqrt((h.x - t.x)**2 + (h.y - t.y)**2)
	if l < 0.001:
	    l = 0.001
	zVertexRadius = (gVertexRadius * self.zoomFactor) / 100.0
	c = (l - zVertexRadius)/l - 0.001 # Dont let them quite touch 
	# (tmpX,tmpY) is a point on a straight line between t and h
	# not quite touching the vertex disc
	tmpX = t.x + c * (h.x - t.x) 
	tmpY = t.y + c * (h.y - t.y)
	arrowShape = ((16*self.zoomFactor) / 100.0,
		      (20*self.zoomFactor) / 100.0,
		      (6*self.zoomFactor)  / 100.0)
	if curved == 0:
	    return self.canvas.create_line(t.x,t.y,tmpX,tmpY,
					   fill=cEdgeDefault,
					   arrow="last",
					   arrowshape=arrowShape, 
					   width=w,
					   tag="edges")
	else:
	    # (mX,mY) to difference vector h - t
	    (mX,mY) = orthogonal((h.x - t.x, h.y - t.y))
	    c = 1.5 * zVertexRadius + l / 25
	    # Add c * (mX,mY) at midpoint between h and t
	    mX = t.x + .5 * (h.x - t.x) + c * mX
	    mY = t.y + .5 * (h.y - t.y) + c * mY
	    return self.canvas.create_line(t.x,t.y,mX,mY,tmpX,tmpY,
					   fill=cEdgeDefault,
					   arrow="last",
					   arrowshape=arrowShape, 
					   width=w,
					   smooth=TRUE,
					   tag="edges")


    def CreateDrawEdge(self,tail,head):
	""" *Internal* Create a draw edge for (tail,head) on the canvas. Position is
            determined by the position of the vertices (or the embedding if the draw
            vertices do not exist yet)."""
	t = self.VertexPosition(tail)
	h = self.VertexPosition(head)

	if self.G.edgeWidth == None:
	    w = gEdgeWidth
	else:
	    w = self.G.edgeWidth[(tail,head)]

	if self.directed == 1:
	    if tail == head:
		de = self.CreateDirectedLoopDrawEdge(t,w)		
	    else:
		if tail in self.G.adjLists[head]:
		    # Remove old straight de for other direction ... 
		    try:
			oldColor = self.canvas.itemconfig(self.drawEdges[(head,tail)],
							  "fill")[4] # Should call GetEdgeColor
			self.canvas.delete(self.drawEdges[(head,tail)])
			# ... and create a new curved one
			if self.G.edgeWidth == None:
			    wOld = gEdgeWidth
			else:
			    wOld = self.G.edgeWidth[(head,tail)]		    
			de = self.CreateDirectedDrawEdge(h,t,1,wOld)
			self.canvas.itemconfig(de, fill=oldColor) # Should call SetEdgeColor
			self.drawEdges[(head,tail)] = de
			self.edge[de] = (head,tail)
			self.canvas.tag_bind(de, "<Any-Leave>", self.DefaultInfo)
			self.canvas.tag_bind(de, "<Any-Enter>", self.EdgeInfo)
			try:
			    self.canvas.lower(de,"vertices")
			except TclError:
			    None # can get here when opening graph
		    except KeyError:
			oldColor = cEdgeDefault # When opening a graph we can get here
		
		    # Finally create the one we wanted to ...
		    de = self.CreateDirectedDrawEdge(t,h,1,w)		
		else:
		    de = self.CreateDirectedDrawEdge(t,h,0,w)
		
	else:
	    if tail == head:
		de = self.CreateUndirectedLoopDrawEdge(t,w)
	    else:
		de = self.CreateUndirectedDrawEdge(t,h,w)

	self.edge[de] = (tail,head) # XXX
	self.canvas.tag_bind(de, "<Any-Leave>", self.DefaultInfo)
	self.canvas.tag_bind(de, "<Any-Enter>", self.EdgeInfo)
	return de


    def CreateVertexAnnotation(self,v,annotation,color):
	""" *Internal* Create a vertex annotation for v on the canvas. Position is
            determined by the position of the corresponding draw vertex 
            on the canvas. """
	pos = self.VertexPosition(v)    
	# Label to the bottom, to the right
	zVertexRadius = (gVertexRadius * self.zoomFactor) / 100.0
	da =  self.canvas.create_text(pos.x+zVertexRadius+1, pos.y+zVertexRadius+1, 
				      anchor="w", 
				      justify="left", 
				      text=annotation,
				      tag="vertexAnno",
				      fill=color)
        return da


    def CreateEdgeAnnotation(self,tail,head,annotation,color):
	""" *Internal* Create an edge annotation for (tail,head) on the canvas. 
	    Position is determined by the embedding specified. """
	t = self.VertexPosition(tail)  
	h = self.VertexPosition(head)  

	(mX,mY) = orthogonal((h.x - t.x, h.y - t.y))
	c = (gVertexRadius * self.zoomFactor) / 100.0
	x = t.x + .5 * (h.x - t.x) + c * mX
	y = t.y + .5 * (h.y - t.y) + c * mY
	# Label to the bottom, to the right
	da =  self.canvas.create_text(x, y, 
				      anchor="center", 
				      justify="center", 
				      text=annotation,
				      tag="edgeAnno",fill=color)
        return da


    ############################################################################
    #				       
    # Animator commands
    #
    def SetVertexColor(self, v, color):
	""" Change color of v to color. No error checking! """
	rgb_color = self.winfo_rgb(color)
	# Tk has 16 bits per color 
	hls_color = colorsys.rgb_to_hls(rgb_color[0] / 65536.0, 
					rgb_color[1] / 65536.0, 
					rgb_color[2] / 65536.0)
	lightness =  hls_color[1]
	#print rgb_color, hls_color
	if lightness < 0.4: 
	    self.canvas.itemconfig( self.drawLabel[v], fill=cLabelDefaultInverted)
	else:
	    self.canvas.itemconfig( self.drawLabel[v], fill=cLabelDefault)
	self.canvas.itemconfig( self.drawVertex[v], fill=color)
	self.update()


    def GetVertexColor(self,v):
	""" Return the color of v """
	dv = self.drawVertex[v]
	return self.canvas.itemconfig(dv, "fill")[4]

 
    def SetAllVerticesColor(self,color,graph=None):
	""" Change the color of all vertices to 'color' at once 
            You can also pass an induced subgraph  """
	if graph == None:
	    self.canvas.itemconfig("vertices", fill=color)
	else: # induced subgraph
	    for v in graph.vertices:
		self.canvas.itemconfig(self.drawVertex[v], fill=color)
	self.update()
	
    def SetAllEdgesColor(self,color,graph=None):
	""" Change the color of all edges to 'color' at once
            You can also pass an induced subgraph  """
	if graph == None:
	    self.canvas.itemconfig("edges", fill=color)
	else: # induced subgraph
	    for e in graph.Edges():
		self.SetEdgeColor(e[0],e[1],color)
	self.update()


    def SetEdgeColor(self, tail, head, color):
	""" Change color of (tail,head) to color. No error checking! 
	    Handles undirected graphs. """
	if self.directed == 1:
	    de = self.drawEdges[(tail,head)]
	else:
	    try:
		de = self.drawEdges[(tail,head)]
	    except KeyError:
		de = self.drawEdges[(head,tail)]	    
	self.canvas.itemconfig( de, fill=color)
	self.update()


    def GetEdgeColor(self, tail, head):
	""" Return color of (tail,head). No error checking! 
	    Handles undirected graphs. """	
        (u,v) = self.G.Edge(tail,head)
	de = self.drawEdges[(u,v)]
	return self.canvas.itemconfig(de, "fill")[4]


    def BlinkVertex(self, v, color=cVertexBlink):
	""" Blink vertex v with color. Number of times, speed, default color is
	    specified in GatoGlobals.py. No error checking! """	
	dv = self.drawVertex[v]
	oldColor = self.canvas.itemconfig(dv, "fill")[4]
	for i in xrange(1,gBlinkRepeat):
	    self.canvas.after(gBlinkRate)
	    self.canvas.itemconfig( dv, fill=color)
	    self.update()
	    self.canvas.after(gBlinkRate)
	    self.canvas.itemconfig( dv, fill=oldColor)
	    self.update()


    def BlinkEdge(self, tail, head, color=cVertexBlink):
	""" Blink edge (tail,head) with color. Number of times, speed, default 
	    color is specified in GatoGlobals.py. No error checking!	Handles
	    undirected graphs. """	
	if self.directed == 1:
	    de = self.drawEdges[(tail,head)]
	else:
	    try:
		de = self.drawEdges[(tail,head)]
	    except KeyError:
		de = self.drawEdges[(head,tail)]	    
	oldColor = self.canvas.itemconfig(de, "fill")[4]
	for i in xrange(1,gBlinkRepeat):
	    self.canvas.after(gBlinkRate)
	    self.canvas.itemconfig( de, fill=color)
	    self.update()
	    self.canvas.after(gBlinkRate)
	    self.canvas.itemconfig( de, fill=oldColor)
	    self.update()

    def Blink(self, list, color=cVertexBlink):
	""" Blink all edges or vertices in list with color.
            Edges are specified as (tail,head). 

            Number of times, speed, default color is specified in GatoGlobals.py. 
            No error checking!	Handles undirected graphs. """	
	oldColor = [None] * len(list)
	drawItems = [None] * len(list)

	for i in xrange(len(list)):
	    try:
		e = list[i]
		l = len(e) # will raise an exception	
		drawItems[i] = self.drawEdges[e]
		oldColor[i] = self.canvas.itemconfig(drawItems[i], "fill")[4]
	    except: # It is a vertex
		v = list[i]
		drawItems[i] = self.drawVertex[v]
		oldColor[i] = self.canvas.itemconfig(drawItems[i], "fill")[4]

	for i in xrange(1,gBlinkRepeat):
	    self.canvas.after(gBlinkRate)
	    for j in xrange(len(drawItems)):	
		self.canvas.itemconfig(drawItems[j], fill=color)
	    self.update()
	    self.canvas.after(gBlinkRate)
	    for j in xrange(len(drawItems)):	
		self.canvas.itemconfig(drawItems[j], fill=oldColor[j])
	    self.update()
		


    def SetVertexFrameWidth(self,v,val):
	""" Set the width of the black frame of a vertex to val """	
	dv = self.drawVertex[v]
	self.canvas.itemconfig(dv, width=val)
        self.update()

    def SetVertexAnnotation(self,v,annotation,color="black"):
	""" Add an annotation to v. Annotations are displayed to the left and
	    the bottom of v and allow to display more info about a vertex. 
            No error checking!  Does not handle vertex deletions/moves !"""	
	if not self.vertexAnnotation.QDefined(v):
	    self.vertexAnnotation[v] = self.CreateVertexAnnotation(v,annotation,color)
	else:
	    da = self.vertexAnnotation[v]
	    self.canvas.itemconfig(da, text=annotation)
	    self.canvas.itemconfig(da, fill=color)
	    self.update()

    def SetEdgeAnnotation(self,tail,head,annotation,color="black"):
	""" Add an annotation to (tail,head). Annotations are displayed to the left and
	    the bottom of v and allow to display more info about a vertex. 
            No error checking!  Does not handle edge deletions/moves !"""	
	if not self.edgeAnnotation.QDefined((tail,head)):
	    self.edgeAnnotation[(tail,head)] = self.CreateEdgeAnnotation(tail,head,
									 annotation,
									 color)
	else:
	    da = self.edgeAnnotation[(tail,head)]
	    self.canvas.itemconfig(da, text=annotation)
	    self.canvas.itemconfig(da, fill=color)
	    self.update()


    def UpdateVertexLabel(self, v, blink=1, color=cLabelBlink):
	""" Visualize the changing of v's label. After changing G.labeling[v],
	    call UpdateVertexLabel to update the label in the graph window,
	    blinking blink times with color. No error checking!  """	
	dl = self.drawLabel[v]
	if blink == 1:
	    oldColor = self.canvas.itemconfig(dl, "fill")[4]
	    for i in xrange(1,gBlinkRepeat):
		self.canvas.after(gBlinkRate)
		self.canvas.itemconfig( dl, fill=color)
		self.update()
		self.canvas.after(gBlinkRate)
		self.canvas.itemconfig( dl, fill=oldColor)
		self.update()
		self.canvas.itemconfig( dl, text=self.Labeling[v])
	else:
	    self.canvas.itemconfig( dl, text=self.Labeling[v])
	    self.update()

	
    def UpdateInfo(self, neuText):
	""" *Internal* Update text in info box """	
	self.info.config(text=neuText)
	self.update()


    def DefaultInfo(self,event=None):
	""" *Internal* Put default info into info box """	
	if self.graphInformer == None:
	    self.UpdateInfo("")
	else:
	    self.UpdateInfo(self.graphInformer.DefaultInfo())


    def VertexInfo(self,event):
	""" *Internal* Call back routine bound to MouseEnter of vertices and
	    labels. Produces default info for vertices unless a user supplied
	    informer has been registered with RegisterGraphInformer() """
	widget = event.widget.find_withtag(CURRENT)[0]
	tags = self.canvas.gettags(widget)
	if "vertices" in tags:
	    v = self.vertex[widget]
	elif "labels" in tags:
	    v = self.label[widget]
	else:
	    return

	if self.graphInformer == None:
	    infoString = "Vertex %d at position (%d,%d)" % (v, 
							    self.embedding[v].x, 
							    self.embedding[v].y)
	else:
	    infoString = self.graphInformer.VertexInfo(v)
	self.UpdateInfo(infoString)


    def EdgeInfo(self,event):
	""" *Internal* Call back routine bound to MouseEnter of edges. 
	    Produces default info for edges unless a user supplied
	    informer has been registered with RegisterGraphInformer() """	
	widget = event.widget.find_withtag(CURRENT)[0]
	(tail,head) = self.edge[widget]
	if self.graphInformer == None:
	     infoString = "Edge (%d,%d)" % (tail, head) 
	else:
	    infoString = self.graphInformer.EdgeInfo(tail,head) 
	self.UpdateInfo(infoString)


    def FindVertex(self,event):
	""" *Internal* Given an event find the correspoding vertex """
	if not event.widget.find_withtag(CURRENT):
	    return None
	else:
	    try:
		widget = event.widget.find_withtag(CURRENT)[0]
		tags = self.canvas.gettags(widget)
		if "vertices" in tags:
		    v = self.vertex[widget]
		elif "labels" in tags:
		    v = self.label[widget]
		else:
		    v = None
		return v
	    except:
		return None

    def FindEdge(self,event):
	""" *Internal* Given an event find the correspoding edge """ 
	if not event.widget.find_withtag(CURRENT):
	    return None
	else:
	    try:
		widget = event.widget.find_withtag(CURRENT)[0]
		e = self.edge[widget]
		return e
	    except:
		return None


    ############################################################################
    #				       
    # edit commands
    #
    def AddVertex(self, x, y):
	""" *Internal* Add a new vertex at (x,y) 
            NOTE: Assumes x,y to be in embedding coordinates""" 
	v = self.G.AddVertex()
	self.embedding[v]  = Point2D(x,y)
	self.Labeling[v]   = v
	self.drawVertex[v] = self.CreateDrawVertex(v)
	self.drawLabel[v]  = self.CreateDrawLabel(v)
	for i in xrange(0,self.G.NrOfVertexWeights()):
	    self.G.vertexWeights[i][v] = 0
	return v

    def AddVertexCanvas(self, x, y):
	""" *Internal* Add a new vertex at (x,y) 
            NOTE: Assumes x,y to be in canvas coordinates""" 
	v = self.G.AddVertex()
        embed_x, embed_y = self.CanvasToEmbedding(x,y)
	self.embedding[v]  = Point2D(embed_x,embed_y)
	self.Labeling[v]   = v
	self.drawVertex[v] = self.CreateDrawVertex(v,x,y)
	self.drawLabel[v]  = self.CreateDrawLabel(v)
	for i in xrange(0,self.G.NrOfVertexWeights()):
	    self.G.vertexWeights[i][v] = 0
	return v

    def MoveVertex(self,v,x,y,doUpdate=None):
	""" *Internal* Move vertex v to position (x,y) 
            NOTE: Assumes x,y to be in canvas coordinates if 
                  doUpdate=None and in embedding coordinates else 
        """ 	    
        if doUpdate == None: # User has moved drawvertex
	    newX, newY = self.CanvasToEmbedding(x,y)
	    self.embedding[v] = Point2D(newX, newY)

	else:
	    # Here translation of canvas does not matter, since we
	    # move vertex relatively anyways   
	    pos = self.VertexPosition(v)
	    canvas_x,canvas_y = self.EmbeddingToCanvas(x,y)
	    dx = canvas_x - pos.x
	    dy = canvas_y - pos.y
	    
	    dv = self.drawVertex[v]
	    self.canvas.move(dv, dx, dy)
	    self.canvas.move(self.drawLabel[v], dx, dy)
	    self.embedding[v] = Point2D(x,y)


	# move incident edges
	outVertices = self.G.OutNeighbors(v)[:] # Need a copy here
	inVertices = self.G.InNeighbors(v)[:]
	#print outVertices, inVertices

	euclidian = self.G.QEuclidian()
	
	# Handle outgoing edges
	t = self.embedding[v]
	for w in outVertices:
	    de = self.drawEdges[(v,w)]
	    #print (v,w),de
	    self.canvas.delete(de)
	    de = self.CreateDrawEdge(v,w)
	    self.drawEdges[(v,w)] = de
	    self.canvas.lower(de,"vertices")
	    if euclidian:
		h = self.embedding[w]
		self.G.edgeWeights[0][(v,w)] = sqrt((h.x - t.x)**2 + (h.y - t.y)**2)
		
	# Handle incoming edges
	h = self.embedding[v]
	for w in inVertices:
	    de = self.drawEdges[(w,v)]
	    #print (w,v),de
	    self.canvas.delete(de)
	    de = self.CreateDrawEdge(w,v)
	    self.drawEdges[(w,v)] = de
	    self.canvas.lower(de,"vertices")
	    if euclidian:
		t = self.embedding[w]
		self.G.edgeWeights[0][(w,v)] = sqrt((h.x - t.x)**2 + (h.y - t.y)**2)




    def DeleteVertex(self,v):
	""" *Internal* Delete vertex v """ 
	del(self.Labeling.label[v]) # XXX
	del(self.embedding.label[v]) # XXX
	# if v has an annotation delete
	if self.vertexAnnotation.QDefined(v):
	    self.canvas.delete(self.vertexAnnotation[v])
	    del(self.vertexAnnotation.label[v])
	self.canvas.delete(self.drawVertex[v])
	del(self.drawVertex.label[v])
	self.canvas.delete(self.drawLabel[v])
	del(self.drawLabel.label[v])
	# delete incident edges
	outVertices = self.G.OutNeighbors(v)[:] # Need a copy here
	inVertices = self.G.InNeighbors(v)[:]
	for w in outVertices:
	    self.DeleteEdge(v,w)
	for w in inVertices:
	    if w != v: # We have already deleted loops
		self.DeleteEdge(w,v)
	#del(self.G.adjLists[v]) # XXX
	# and finally the vertex itself
	self.G.vertices.remove(v) # XXX


    def AddEdge(self,tail,head):
	""" *Internal* Add Edge. Note: unless graph is Euclidian weight is set
	    to 0. No error checking !""" 
	try:
	    self.G.AddEdge(tail,head)
	    de = self.CreateDrawEdge(tail,head)
	    self.drawEdges[(tail, head)] = de
	    self.canvas.lower(de,"vertices")
	    if self.G.QEuclidian():
		t = self.embedding[tail]
		h = self.embedding[head]
		self.G.edgeWeights[0][(tail,head)] = sqrt((h.x - t.x)**2 + (h.y - t.y)**2)
	    else:
 		self.G.edgeWeights[0][(tail,head)] = 0
	    for i in xrange(1,self.G.NrOfEdgeWeights()):
		self.G.edgeWeights[i][(tail,head)] = 0
	
	except GraphNotSimpleError:
	    #print "Inserting edge would result in non-simple graph"
	    return


    def DeleteEdge(self,tail,head):
	""" *Internal* Delete edge (tail,head) """ 
	# print "Removing edge (",tail,",",head,")"
	self.canvas.delete(self.drawEdges[(tail,head)])
	# if (tail,head) has an annotation delete it
	if self.edgeAnnotation.QDefined((tail,head)):
	    self.canvas.delete(self.edgeAnnotation[(tail,head)])
	    del(self.edgeAnnotation.label[(tail,head)])
	del(self.drawEdges.label[(tail,head)]) # XXX
	self.G.DeleteEdge(tail,head)
	if self.directed == 1 and tail in self.G.adjLists[head]: 
	    # i.e. parallel edge
	    oldColor = self.canvas.itemconfig(self.drawEdges[(head,tail)],
					      "fill")[4] # Should call GetEdgeColor
	    self.canvas.delete(self.drawEdges[(head,tail)])
	    de = self.CreateDrawEdge(head,tail)
	    self.canvas.itemconfig(de, fill=oldColor) # Should call SetEdgeColor
	    self.drawEdges[(head,tail)] = de
	    self.canvas.lower(de,"vertices")
	    
    def SwapEdgeOrientation(self,tail,head):
	""" *Internal* If graph is directed and we do not have edges in both
            directions, change the orientation of the edge (tail,head) """ 

	if self.directed == 0 or self.G.QEdge(head,tail): # Assuming (tail,head) is an edge
	    return

	self.DeleteEdge(tail,head)
	self.AddEdge(head,tail)

    def VertexPosition(self,v):
	""" Return the position of vertex v in canvas coordinates """
	try:
	    coords = self.canvas.coords(self.drawVertex[v])
	    x = 0.5 * (coords[2] - coords[0]) + coords[0]
	    y = 0.5 * (coords[3] - coords[1]) + coords[1]
	except: # Vertex is not on the canvas yet
	    #print "XXX VertexPosition excepted: No draw Vertex ?"
	    x,y = self.EmbeddingToCanvas(self.embedding[v].x,self.embedding[v].y)

	return Point2D(x,y)


    ############################################################################
    #				       
    # various stuff 
    #

    def PrintToPSFile(self,fileName):
	""" Produce an EPSF of canvas in fileName. Note: Graph gets scaled
	    and rotated as to maximize size while still fitting on paper """ 
	bb = self.canvas.bbox("all") # Bounding box of all elements on canvas
	# Give 10 pixels room to breathe
	x = max(bb[0] - 10,0)
	y = max(bb[1] - 10,0)
	width=bb[2] - bb[0] + 10
	height=bb[3] - bb[1] + 10

	printablePageHeight=280 #m
	printablePageWidth =190 #m

	printableRatio=printablePageHeight/printablePageWidth
	
	bbRatio = height/width

	if bbRatio > printableRatio: # Height gives limiting dimension
	    self.canvas.postscript(file=fileName, pageheight="%dm" % printablePageHeight,
				   x=x,y=y,height=height,width=width)	
	else:
	    self.canvas.postscript(file=fileName, pagewidth="%dm" % printablePageWidth,
				   x=x,y=y,height=height,width=width)	


    def About(self):
	""" Return a HTML-page giving information about the graph """
	if self.hasGraph == 1:
	    return self.G.About()
	else:
	    return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"
   


	    
    ############################################################################
    #				       
    # Clickhandler commands
    #
	
    def RegisterClickhandler(self, handler):
	""" A clickhandler is a function being called when the user
            clicks on a vertex or an edge (actually releases mouse
            button 1 over a vertex or an edge).

            The clickhandler takes a string 'vertex' or 'edge' as the
	    first and the vertex/edge clicked on as the second argument """
	self.clickhandler = handler
	self.canvas.bind("<B1-ButtonRelease>", self.MouseUp)
	
    def UnregisterClickhandler(self):
	""" Unregister the handler """
	self.clickhandler = None
	self.canvas.unbind("<B1-ButtonRelease>")
	
    def MouseUp(self, event):	
	""" Callback method for <B1-ButtonRelease>. Finds the vertex/edge 
            clicked and calls the registered clickhandler """
	if self.clickhandler != None:
	    v = self.FindVertex(event)
	    if v != None:
		self.clickhandler('vertex',v)
	    else:
		e = self.FindEdge(event)
		if e != None:
		    self.clickhandler('edge',e)
	

class GraphDisplayFrame(GraphDisplay, Frame):
    """ Provides graph display in a frame """

    def __init__(self, master=None):
	Frame.__init__(self, master)
	self.pack() 
	self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
	GraphDisplay.__init__(self)

    def SetTitle(self,title):
	print "change window title to" + `title`
	

class GraphDisplayToplevel(GraphDisplay, Toplevel):
    """ Provides graph display in a top-level window """

    def __init__(self, master=None):
	Toplevel.__init__(self, master)
	GraphDisplay.__init__(self)
	self.protocol('WM_DELETE_WINDOW',self.WMDelete)
	
    def Withdraw(self):
	""" Withdraw window from screen.
        """
	self.withdraw()

    def WMDelete(self):
	""" Window-Manager Quits only yield withdraws unless you quit
	    the AlgoWin. Override if you want group leader to handle 
            quit """
	self.Withdraw()
	
    def Show(self):
	self.deiconify()
	
    def SetTitle(self,title):
	self.title(title)



