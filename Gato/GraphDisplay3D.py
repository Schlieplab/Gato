################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GraphDisplay3D.py
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
################################################################################

from Tkinter import * # Frame, Canvas, Toplevel, StringVar and lots of handy constants
from Graph import Graph
from math import sqrt, pi, sin, cos
from GatoGlobals import *
from GatoUtil import orthogonal
from DataStructures import Point2D, VertexLabeling, EdgeLabeling
import os
import colorsys
import string

from visual import *

class GraphDisplay3D:
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

	self.zVertexRadius = gVertexRadius
	self.zArrowShape = (16, 20, 6)
	self.zFontSize = 10

	self.graphInformer = None
	self.clickhandler = None

        self.scene = display(title="Gato Graph", width=700, height=650, autoscale=1, autocenter=1, ambient=0.3)
        self.scene.select()

        self.tkcolor = {} # cache the color in tk for GetVertexColor etc
        self.shadowEdges = []


    def color(self, tkcolor):
        colmap = {'black': (0, 0, 0),
                  'grey':  (0.4, 0.4, 0.4),
                  'white': (1, 1, 1),
                  'red': (1,0,0),
                  'green': (0,1,0),
                  'blue': (0,0,1),
                  'yellow': (1,1,0)
                  }
        
        if colmap.has_key(tkcolor):
            return colmap[tkcolor]
        else: # tkcolor is #rrggbb
            r = string.atoi(tkcolor[1:3], 16) / 255.0
            g = string.atoi(tkcolor[3:5], 16) / 255.0
            b = string.atoi(tkcolor[5:7], 16) / 255.0
            return (r,g,b)


    def ShowGraph(self, G, graphName):	
	""" Display graph G name graphName. Currently we assume that for 
	    the embedding (x,y) of every vertex  < x < 1000 and 0 < y < 1000
	    holds """
	self.G          = G
	self.embedding  = G.embedding # Assuming 0 < x < 1000 and 0 < y < 1000
	self.Labeling   = G.labeling
	self.directed   = G.QDirected()

	if self.hasGraph == 1:
	    self.DeleteDrawItems()
	 
	self.CreateDrawItems()
	self.hasGraph = 1
	#self.SetTitle("Gato - " + graphName)
	#self.update()
	#self.DefaultInfo()


    def CreateDrawItems(self):
	""" *Internal* Create items on the canvas """
	for v in self.G.vertices:
	    x = self.embedding[v].x
	    y = self.embedding[v].y
            z = 0
	    self.drawVertex[v] = self.CreateDrawVertex(v,x,y,z)

	for v in self.G.vertices:
	    for w in self.G.OutNeighbors(v):
		self.drawEdges[(v,w)] = self.CreateDrawEdge(v,w)

	#for v in self.G.vertices:
	 #   self.drawLabel[v] = self.CreateDrawLabel(v)

    
    def DeleteDrawItems(self):
	""" *Internal* Delete all items on the canvas and clear up
            our references to it"""
	self.DeleteDrawEdges()
	self.DeleteDrawVertices()
	self.DeleteDrawLabels()
	self.DeleteVertexAnnotations()
	#self.DeleteEdgeAnnotations()
        #self.canvas.delete("all") # Remove whatever is left
	self.drawVertex       = VertexLabeling()
	self.drawEdges        = EdgeLabeling()
	self.drawLabel        = VertexLabeling()
	self.vertexAnnotation = VertexLabeling()
	#self.edgeAnnotation   = EdgeLabeling()


    def DeleteDrawEdges(self):
	""" *Internal* Delete draw edges on the canvas """
	self.edge = {} # XXX
        for de in self.drawEdges.label.values():
            de.visible = 0
        for de in self.shadowEdges:
            de.visible = 0

    def DeleteDrawVertices(self):
	""" *Internal* Delete draw vertices on the canvas """
	self.vertex = {} # XXX
        for dv in self.drawVertex.label.values():
            dv.visible = 0


    def DeleteDrawLabels(self):
	""" *Internal* Delete draw labels on the canvas """
	self.label = {} # XXX

    def DeleteVertexAnnotations(self):
	""" *Internal* Delete all vertex annotations on the canvas """
        for va in self.vertexAnnotation.label.values():
            va.visible = 0


    def DeleteEdgeAnnotations(self):
	""" *Internal* Delete all edge annotations on the canvas """
	pass

    def CreateDrawVertex(self, v, x, y, z):
	""" *Internal* Create a draw vertex for v on the canvas. Position is
            determined by the embedding unless explictely passed as x,y in
            canvas coordinates """
        dv = sphere(pos = (x,y,z),
                    radius = 15.0,
                    color = self.color("red")) #cVertexDefault))
        self.tkcolor[v] = "red"
	self.vertex[dv] = v
	return dv
    
    def CreateDrawLabel(self,v):
	""" *Internal* Create a draw label for v on the canvas. Position is
            determined by the embedding specified. Text is specified by the
	    labeling:  

	    Call only after CreateDrawVertex() """
        pass


    def CreateUndirectedLoopDrawEdge(self, v, w, orientation=None):
	""" *Internal* Create an undirected loop draw edge. v is a Point2D """
	loopRadius = 2 * self.zVertexRadius
	xMiddle = v.x
	yMiddle = v.y-((25*self.zoomFactor)/100.0)	
	Coords = []
	for degree in range(0,400,40):
	    Coords.append(loopRadius*cos(degree*(pi/180))+xMiddle)
	    Coords.append(loopRadius*sin(degree*(pi/180))+yMiddle)
	return self.canvas.create_line(Coords,
				       fill=cEdgeDefault, 
				       width=w,
				       smooth=TRUE,
				       splinesteps=24,
				       tag="edges")


    def CreateDirectedLoopDrawEdge(self,v,w, orientation=None):
	""" *Internal* Create an directed loop draw edge. v is a Point2D """
	loopRadius = 2 * self.zVertexRadius
	xMiddle = v.x
	yMiddle = v.y-((25*self.zoomFactor)/100.0)
	Coords = []
	for degree in range(95,440,25):
	    if degree != 395:
		Coords.append(loopRadius*cos(degree*(pi/180))+xMiddle)
		Coords.append(loopRadius*sin(degree*(pi/180))+yMiddle)
	return self.canvas.create_line(Coords,
				       arrow="last",
				       arrowshape=self.zArrowShape,
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
	c = (l - self.zVertexRadius)/l - 0.001 # Dont let them quite touch 
	# (tmpX,tmpY) is a point on a straight line between t and h
	# not quite touching the vertex disc
	tmpX = t.x + c * (h.x - t.x) 
	tmpY = t.y + c * (h.y - t.y)
	if curved == 0:
	    return self.canvas.create_line(t.x,t.y,tmpX,tmpY,
					   fill=cEdgeDefault,
					   arrow="last",
					   arrowshape=self.zArrowShape, 
					   width=w,
					   tag="edges")
	else:
	    # (mX,mY) to difference vector h - t
	    (mX,mY) = orthogonal((h.x - t.x, h.y - t.y))
	    c = 1.5 * self.zVertexRadius + l / 25
	    # Add c * (mX,mY) at midpoint between h and t
	    mX = t.x + .5 * (h.x - t.x) + c * mX
	    mY = t.y + .5 * (h.y - t.y) + c * mY
	    return self.canvas.create_line(t.x,t.y,mX,mY,tmpX,tmpY,
					   fill=cEdgeDefault,
					   arrow="last",
					   arrowshape=self.zArrowShape, 
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
	    w = 3.0
	else:
	    w = self.G.edgeWidth[(tail,head)] / 2.0
      
        axis = h - t
        #de = arrow(pos=t, axis=axis, color=color.yellow, shaftwidth=1)
        de = cylinder(pos=t, axis=axis, color=color.white, radius=w)
        self.tkcolor[(tail, head)] = "white"
        
        self.shadowEdges.append(cylinder(pos=(t[0], t[1], -50), axis=axis, color=(0.3,0.3,0.3), radius=2))

        return de

## 	if self.directed == 1:
## 	    if tail == head:
## 		de = self.CreateDirectedLoopDrawEdge(t,w)		
## 	    else:
## 		if tail in self.G.adjLists[head]:
## 		    # Remove old straight de for other direction ... 
## 		    try:
## 			oldColor = self.canvas.itemconfig(self.drawEdges[(head,tail)],
## 							  "fill")[4] # Should call GetEdgeColor
## 			self.canvas.delete(self.drawEdges[(head,tail)])
## 			# ... and create a new curved one
## 			if self.G.edgeWidth == None:
## 			    wOld = (gEdgeWidth * self.zoomFactor) / 100.0
## 			else:
## 			    wOld = (self.G.edgeWidth[(head,tail)] * self.zoomFactor) / 100.0
## 			de = self.CreateDirectedDrawEdge(h,t,1,wOld)
## 			self.canvas.itemconfig(de, fill=oldColor) # Should call SetEdgeColor
## 			self.drawEdges[(head,tail)] = de
## 			self.edge[de] = (head,tail)
## 			self.canvas.tag_bind(de, "<Any-Leave>", self.DefaultInfo)
## 			self.canvas.tag_bind(de, "<Any-Enter>", self.EdgeInfo)
## 			try:
## 			    self.canvas.lower(de,"vertices")
## 			except TclError:
## 			    None # can get here when opening graph
## 		    except KeyError:
## 			oldColor = cEdgeDefault # When opening a graph we can get here
		
## 		    # Finally create the one we wanted to ...
## 		    de = self.CreateDirectedDrawEdge(t,h,1,w)		
## 		else:
## 		    de = self.CreateDirectedDrawEdge(t,h,0,w)
		
## 	else:
## 	    if tail == head:
## 		de = self.CreateUndirectedLoopDrawEdge(t,w)
## 	    else:
## 		de = self.CreateUndirectedDrawEdge(t,h,w)

## 	self.edge[de] = (tail,head) # XXX
## 	self.canvas.tag_bind(de, "<Any-Leave>", self.DefaultInfo)
## 	self.canvas.tag_bind(de, "<Any-Enter>", self.EdgeInfo)
## 	return de


    def CreateVertexAnnotation(self,v,annotation,color):
	""" *Internal* Create a vertex annotation for v on the canvas. Position is
            determined by the position of the corresponding draw vertex 
            on the canvas. """
	pos = self.VertexPosition(v)    
	# Label to the bottom, to the right
        da = label(pos=pos, text=annotation, xoffset= 10, yoffset=12, space = 15, height=10, border=6)
        return da


    def CreateEdgeAnnotation(self,tail,head,annotation,color):
	""" *Internal* Create an edge annotation for (tail,head) on the canvas. 
	    Position is determined by the embedding specified. """
	t = self.VertexPosition(tail)  
	h = self.VertexPosition(head)  

	(mX,mY) = orthogonal((h.x - t.x, h.y - t.y))
	c = self.zVertexRadius
	x = t.x + .5 * (h.x - t.x) + c * mX
	y = t.y + .5 * (h.y - t.y) + c * mY
	# Label to the bottom, to the right
	da =  self.canvas.create_text(x, y, 
				      anchor="center", 
				      justify="center", 
				      font="Arial %d" %self.zFontSize,
				      text=annotation,
				      tag="edgeAnno",
				      fill=color)
        return da


    ############################################################################
    #				       
    # Animator commands
    #
    def SetVertexColor(self, v, color):
	""" Change color of v to color. No error checking! """
        self.drawVertex[v].color = self.color(color)
        self.tkcolor[v] = color

    def GetVertexColor(self,v):
	""" Return the color of v """
        return self.tkcolor[v]
 
    def SetAllVerticesColor(self,color,graph=None):
	""" Change the color of all vertices to 'color' at once 
            You can also pass an induced subgraph  """
	
    def SetAllEdgesColor(self,color,graph=None, leaveColors = None):
	""" Change the color of all edges to 'color' at once
            You can also pass an induced subgraph  """

    def SetEdgeColor(self, tail, head, tkcolor):
	""" Change color of (tail,head) to color. No error checking! 
	    Handles undirected graphs. """
        try:
            de = self.drawEdges[(tail,head)]
            self.tkcolor[(tail,head)] = tkcolor
        except KeyError:
            de = self.drawEdges[(head, tail)]
            self.tkcolor[(head,tail)] = tkcolor
        de.color = self.color(tkcolor)
        

    def GetEdgeColor(self, tail, head):
	""" Return color of (tail,head). No error checking! 
	    Handles undirected graphs. """	
        try:
            return self.tkcolor[(tail,head)]
        except KeyError:
            return self.tkcolor[(head,tail)]



    def BlinkVertex(self, v, color=cVertexBlink):
	""" Blink vertex v with color. Number of times, speed, default color is
	    specified in GatoGlobals.py. No error checking! """
	dv = self.drawVertex[v]
        oldColor = dv.color
        blinkColor = self.color(color)
	for i in xrange(1,gBlinkRepeat):
            self.drawVertex[v].color = blinkColor
            rate(gBlinkRate)
            self.drawVertex[v].color = oldColor
            rate(gBlinkRate)

            
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
	oldColor = self.de.color
        blinkColor = self.color(color)
        
	for i in xrange(1,gBlinkRepeat):
            de.color = blinkColor
	    rate(gBlinkRate)
            de.color = oldColor
            rate(gBlinkRate)


    def Blink(self, list, color=cVertexBlink):
	""" Blink all edges or vertices in list with color.
            Edges are specified as (tail,head). 
            Number of times, speed, default color is specified in GatoGlobals.py. 
            No error checking!	Handles undirected graphs. """	
	oldColor = [None] * len(list)
	drawItems = [None] * len(list)

        blinkColor = self.color(color)
	for i in xrange(len(list)):
	    try:
		e = list[i]
		l = len(e) # will raise an exception	
		drawItems[i] = self.drawEdges[e]
		oldColor[i] = drawItems[i].color
	    except: # It is a vertex
		v = list[i]
		drawItems[i] = self.drawVertex[v]
		oldColor[i] = drawItems[i].color

	for i in xrange(1,gBlinkRepeat):
            rate(gBlinkRate)
	    for j in xrange(len(drawItems)):	
		drawItems[i].color = blinkColor
            rate(gBlinkRate)
	    for j in xrange(len(drawItems)):	
		drawItems[j].color = oldColor[j]



    def SetVertexFrameWidth(self,v,val):
	""" Set the width of the black frame of a vertex to val """	
        pass


    def SetVertexAnnotation(self,v,annotation,color="white"):
	""" Add an annotation to v. Annotations are displayed to the left and
	    the bottom of v and allow to display more info about a vertex. 
            No error checking!  Does not handle vertex deletions/moves !"""	
	if not self.vertexAnnotation.QDefined(v):
	    self.vertexAnnotation[v] = self.CreateVertexAnnotation(v,annotation,color)
	else:
	    da = self.vertexAnnotation[v]
            if annotation == "":
                da.visible = 0
            else:
                da.text = annotation

        

    def SetEdgeAnnotation(self,tail,head,annotation,color="black"):
	""" Add an annotation to (tail,head). Annotations are displayed to the left and
	    the bottom of v and allow to display more info about a vertex. 
            No error checking!  Does not handle edge deletions/moves !"""
	return
	if not self.edgeAnnotation.QDefined((tail,head)):
	    self.edgeAnnotation[(tail,head)] = self.CreateEdgeAnnotation(tail,head,
									 annotation,
									 color)
	else:
	    da = self.edgeAnnotation[(tail,head)]


    def UpdateVertexLabel(self, v, blink=1, color=cLabelBlink):
	""" Visualize the changing of v's label. After changing G.labeling[v],
	    call UpdateVertexLabel to update the label in the graph window,
	    blinking blink times with color. No error checking!  """
	return
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
		self.canvas.itemconfig( dl,
					font="Arial %d" %self.zFontSize,
					text=self.Labeling[v])
	else:
	    self.canvas.itemconfig( dl,
				    font="Arial %d" %self.zFontSize,
				    text=self.Labeling[v])
	    self.update()

	
    def UpdateInfo(self, neuText):
	""" *Internal* Update text in info box """
	pass


    def DefaultInfo(self,event=None):
	""" *Internal* Put default info into info box """	
        pass
	if self.graphInformer == None:
	    self.UpdateInfo("")
	else:
	    self.UpdateInfo(self.graphInformer.DefaultInfo())


    def VertexInfo(self,event):
	""" *Internal* Call back routine bound to MouseEnter of vertices and
	    labels. Produces default info for vertices unless a user supplied
	    informer has been registered with RegisterGraphInformer() """
        pass


    def EdgeInfo(self,event):
	""" *Internal* Call back routine bound to MouseEnter of edges. 
	    Produces default info for edges unless a user supplied
	    informer has been registered with RegisterGraphInformer() """	
        pass


    def FindVertex(self,event):
	""" *Internal* Given an event find the correspoding vertex """
        pass


    def FindGridVertex(self,event):
	""" *Internal* Given an event find the correspoding grid vertex """
        pass

    def FindEdge(self,event):
	""" *Internal* Given an event find the correspoding edge """ 
        pass


    ############################################################################
    #				       
    # edit commands
    #
    def AddVertex(self, x, y):
	""" *Internal* Add a new vertex at (x,y) 
            NOTE: Assumes x,y to be in embedding coordinates""" 
        pass

    def AddVertexCanvas(self, x, y):
	""" *Internal* Add a new vertex at (x,y) 
            NOTE: Assumes x,y to be in canvas coordinates""" 
        pass

    def MoveVertex(self, v, x, y, z, doUpdate=None):
	""" *Internal* Move vertex v to position (x,y) 
            NOTE: Assumes x,y to be in canvas coordinates if 
                  doUpdate=None and in embedding coordinates else
        """
        import Numeric
        pos = vector(x,y,z)
        dv = self.drawVertex[v]
        dv.pos = pos
        if self.vertexAnnotation.label.has_key(v):
	    da = self.vertexAnnotation[v]
            da.pos = pos
            
        for e in self.G.OutEdges(v):
            de = self.drawEdges[e]
            de.pos = pos
            de.axis = self.drawVertex[e[1]].pos - pos

        for e in self.G.InEdges(v):
            de = self.drawEdges[e]
            de.pos = self.drawVertex[e[0]].pos
            de.axis = pos - self.drawVertex[e[0]].pos


    def AddEdge(self,tail,head):
	""" *Internal* Add Edge. Note: unless graph is Euclidian weight is set
	    to 0. No error checking !"""
        pass


    def DeleteEdge(self,tail,head,repaint=1):
	""" *Internal* Delete edge (tail,head) """ 
        pass
	    
    def SwapEdgeOrientation(self,tail,head):
	""" *Internal* If graph is directed and we do not have edges in both
            directions, change the orientation of the edge (tail,head) """ 
        pass

    def VertexPosition(self,v):
	""" Return the position of vertex v in canvas == embedding coordinates """
	return self.drawVertex[v].pos


    ############################################################################
    #				       
    # various stuff 
    #

    def PrintToPSFile(self,fileName):
	""" Produce an EPSF of canvas in fileName. Note: Graph gets scaled
	    and rotated as to maximize size while still fitting on paper """ 
        pass


    def About(self):
	""" Return a HTML-page giving information about the graph """
	if self.hasGraph == 1:
	    return self.G.About()
	else:
	    return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"
   

    def RegisterGraphInformer(self, informer):
        pass

	    
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
        pass
	
    def UnregisterClickhandler(self):
	""" Unregister the handler """
        pass

	
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
	

class GraphDisplayFrame(GraphDisplay3D, Frame):
    """ Provides graph display in a frame """

    def __init__(self, master=None):
	Frame.__init__(self, master)
	self.pack() 
	self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
	GraphDisplay.__init__(self)

    def SetTitle(self,title):
	print "change window title to" + `title`
	

class GraphDisplay3DToplevel(GraphDisplay3D, Toplevel):
    """ Provides graph display in a top-level window """

    def __init__(self, master=None):
	#Toplevel.__init__(self, master)
	GraphDisplay3D.__init__(self)
	#self.protocol('WM_DELETE_WINDOW',self.WMDelete)
	
    def Withdraw(self):
	""" Withdraw window from screen.
        """
        pass
	#self.withdraw()

    def WMDelete(self):
	""" Window-Manager Quits only yield withdraws unless you quit
	    the AlgoWin. Override if you want group leader to handle 
            quit """
	self.Withdraw()
	
    def Show(self):
        pass
	#self.deiconify()
	
    def SetTitle(self,title):
        pass
	#self.title(title)
