################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GraphDisplay.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2015, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schliep.org, winfried.hochstaettler@fernuni-hagen.de
#
#       Information: http://gato.sf.net
#n
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
import tkFont
from Graph import Graph
from math import sqrt, pi, sin, cos, atan2, degrees, log10
import GatoGlobals
from GatoUtil import orthogonal
from GatoDialogs import AutoScrollbar
from DataStructures import Point2D, VertexLabeling, EdgeLabeling
from AnimatedDataStructures import ComponentMaker
import os
import colorsys

import logging
log = logging.getLogger("GraphDisplay.py")

g = GatoGlobals.AnimationParameters





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
        
        
class GraphDisplay(): #object): XXX New Style classes fuck up Tkinter
    """ Provide functionality to display a graph. Not for direct consumption.
        Use
    
        - GraphDisplayToplevel
        - GraphDisplayFrame 
    
        GraphDisplay also provides UI-Interface independent edit operations
        and basic animation methods

        XXX: FUTURE: Maybe this should be a DisplayedGraph which is a sub-class of
             ObjectGraph        
    """
    def __init__(self):
        self.hasGraph = 0

        # Canvas items for vertices and edges 
        self.drawVertex = VertexLabeling()
        self.drawEdges = EdgeLabeling()
        self.drawLabel = VertexLabeling()
        self.vertexAnnotation = VertexLabeling()
        self.edgeAnnotation = EdgeLabeling()

        # Inverse dicts for mapping canvas items to vertices and edges
        self.vertex = {}
        self.edge = {}
        self.label = {}
        
        self.zoomFactor = 100.0 # percent
        self.autoUpdateScrollRegion = 0
        
        self.windowingsystem = self.tk.call("tk", "windowingsystem")
        self.CreateWidgets()
        self.SetTitle("Gato - Graph")
        self.update()
        self.graphInformer = None
        self.clickhandler = None
        self.highlightedPath = {}
        
        # Used by ramazan's scaling code. Gives sizes in pixels at
        # current zoom level
        self.zVertexRadius = g.VertexRadius
        self.zArrowShape = (16, 20, 6)
        self.zFontSize = g.FontSize

        self.g = g # So algorithms can get to the globals (XXX)

        self.bubbles = {} # Mapping of vertex_list: (offset_value, color), used by WebGato
        self.moats = {}   # Mapping of moat_id: (radius, color), used by WebGato
        
    def font(self, size):
        return tkFont.Font(self, (g.FontFamily, size, g.FontStyle))
                
    def GetCanvasCenter(self): 
        """ *Internal* Return the center of the canvas in pixel """
        # XXX How to this for non-pixel
        return (g.PaperWidth/2, g.PaperHeight/2)
        
        
    def Zoom(self,percent):
        """ *Internal* Perform a zoom to specified level """
        
        zoomFactor = {' 50 %':50.0, 
                      ' 75 %':75.0, 
                      '100 %':100.0,
                      '125 %':125.0,
                      '150 %':150.0,
                      '':100.0}

        fontSize = {' 50 %':9, 
                    ' 75 %':10, 
                    '100 %':12,
                    '125 %':18,
                    '150 %':24,
                    '':12}
        
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
        
        self.zVertexRadius = (g.VertexRadius*self.zoomFactor) / 100.0
        self.zArrowShape = ((16*self.zoomFactor) / 100.0,
                            (20*self.zoomFactor) / 100.0,
                            (6*self.zoomFactor)  / 100.0)


        self.zFontSize = fontSize[percent]
        
        for v in self.G.Vertices():
            dv = self.drawVertex[v]
            oldVertexFrameWidth = self.canvas.itemcget(dv, "width")
            newVertexFrameWidth = float(oldVertexFrameWidth) * factor
            self.canvas.itemconfig(dv, width=newVertexFrameWidth)
            dl = self.drawLabel[v]
            self.canvas.itemconfig(dl, font=self.font(self.zFontSize))
            
        for e in self.G.Edges():
            de = self.drawEdges[e]
            oldEdgeWidth = self.canvas.itemcget(de, "width")
            newEdgeWidth = float(oldEdgeWidth) * factor
            self.canvas.itemconfig(de, width=newEdgeWidth,
                                   arrowshape=self.zArrowShape)
            
        self.canvas.scale("all", 0, 0, factor, factor)	
        
        newWidth = (self.zoomFactor / 100.0) * float(g.PaperWidth)
        newHeight = (self.zoomFactor/ 100.0) * float(g.PaperHeight)
        
        self.canvas.config(width=newWidth,height=newHeight,
                           scrollregion=(0,0,newWidth,newHeight))
        self.canvas.xview("moveto",self.Xview)
        self.canvas.yview("moveto",self.Yview)
        
        self.oldXview = self.canvas.xview()
        self.oldYview = self.canvas.yview()

        if self.autoUpdateScrollRegion:
            self.UpdateScrollRegion()

        
    def CanvasToEmbedding(self,x,y):
        """ *Internal* Convert canvas coordinates to embedding coordinates"""
        x = x * 100.0 / self.zoomFactor  
        y = y * 100.0 / self.zoomFactor
        return x,y
        
    def EmbeddingToCanvas(self,x,y):
        """ *Internal* Convert Embedding coordinates to Canvas coordinates"""
        x = x * self.zoomFactor / 100.0
        y = y * self.zoomFactor / 100.0
        return x,y
        
        
    def CreateWidgets(self):
        """ *Internal* Create UI-Elements (except Frame/Toplevel) """
        # Frame at bottom with zoom-popup and label
        self.infoframe = Frame(self, relief=FLAT)
        self.infoframe.pack(side=BOTTOM, fill=X)
        
        self.zoomValue = ZoomVar(self,'100 %')
        self.zoomMenu = OptionMenu(self.infoframe, self.zoomValue, 
                                  ' 50 %',' 75 %', '100 %','125 %','150 %')
        self.zoomMenu.config(height=1)
        self.zoomMenu.config(width=5)
        if self.windowingsystem == 'aqua':
            self.zoomMenu.config(font="Geneva 9")
            self.zoomMenu["menu"].config(font="Geneva 9")
        self.zoomMenu.grid(row=0,column=0,sticky="nwse") 
        self.infoframe.columnconfigure(0,weight=0)
        
        # To make things more windows like, we put the info-label
        # in a separate frame
        if self.windowingsystem == 'aqua':
            borderFrame = Frame(self.infoframe, relief=RIDGE, bd=1)
        else:
            borderFrame = Frame(self.infoframe, relief=SUNKEN, bd=1)

        self.info = Label(borderFrame, text="No information available", anchor=W)
        self.info.config(width=50)
        #if self.windowingsystem == 'aqua':
        #    self.info.config(font="Geneva 10")
        self.info.pack(side=LEFT, expand=1, fill=X)
        borderFrame.grid(row=0,column=1,sticky="nwse",padx=4,pady=3)
        self.infoframe.columnconfigure(1,weight=1)

        if self.windowingsystem == 'aqua':
            dummy = Frame(self.infoframe, relief=FLAT, bd=2)
            dummy.grid(row=0, column=2, padx=6, pady=3)   
            self.infoframe.columnconfigure(2,weight=0)
        
        # Scrolling Canvas
        # To make things more windows like, we put the canvas
        # in a separate frame	
        if self.windowingsystem == 'aqua':
            borderFrame = Frame(self, relief=FLAT, bd=1, background='#666666')
        else:
            borderFrame = Frame(self, relief=SUNKEN, bd=2)
        self.canvas = Canvas(borderFrame,
                             width=g.PaperWidth,
                             height=g.PaperHeight, 
                             background="white",
                             scrollregion=(0, 0, g.PaperWidth, g.PaperHeight))
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W) 
        
        self.canvas.vbar = AutoScrollbar(borderFrame, orient=VERTICAL)
        self.canvas['yscrollcommand']  = self.canvas.vbar.set
        self.canvas.vbar['command'] = self.canvas.yview
        self.canvas.vbar.grid(row=0, column=1, sticky=N+S)
 
        self.canvas.hbar = AutoScrollbar(borderFrame, orient=HORIZONTAL)
        self.canvas['xscrollcommand']  = self.canvas.hbar.set
        self.canvas.hbar['command'] = self.canvas.xview
        self.canvas.hbar.grid(row=1, column=0, sticky=E+W)

        borderFrame.grid_rowconfigure(0, weight=1)
        borderFrame.grid_columnconfigure(0, weight=1)
        borderFrame.pack(anchor=W, side=TOP, expand=1, fill=BOTH)
        try:
            self.geometry("500x483")
        except:
            try:
                self.master.geometry("500x483")
            except AttributeError:
                pass
            
    def ShowGraph(self, G, graphName):	
        """ Display graph G name graphName. Currently we assume that for 
            the embedding (x,y) of every vertex  0 < x < 1000 and 0 < y < 1000
            holds.
        
            NOTE: We need both a proper embedding and a labelling
            XXX: Fix (Randomize embedding, identity labeling if none given """
        self.G = G
        
        if self.hasGraph == 1:
            self.DeleteDrawItems()
            
        self.CreateDrawItems()
        self.hasGraph = 1
        self.SetTitle("Gato - " + graphName)
        self.update()
        self.DefaultInfo()
        

    def UpdateScrollRegion(self, auto=0):
        """ Set the sroll region to the bounding box of the elements on
            the canvas. This will hide the scrollbars, if the whole scroll
            region is displayed.

            Note: This might make things difficult for algorithms adding
            vertices.

            If auto is 1, then this will be done automatically after
            zooming etc.
        """
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        if auto:
            self.autoUpdateScrollRegion = 1
        
    def RegisterGraphInformer(self, Informer):
        """ A graph informer is an object which supplies information
            about the graph, its vertices and its edges. It needs methods
        
            - DefaultInfo()
            - VertexInfo(v)
            - EdgeInfo(tail,head)
        
            If none is registered, information will be produced by
            GraphDisplay. Infos are displayed in info field at the bottom
            of the graph window.
        """
        self.graphInformer = Informer
        
        
    def CreateDrawItems(self):
        """ *Internal* Create items on the canvas """
        for v in self.G.Vertices():
            for w in self.G.OutNeighbors(v):
                self.drawEdges[(v,w)] = self.CreateDrawEdge(v,w)

        # We want the vertices in front of the edges, so we paint
        # all edges first
        for v in self.G.Vertices():
            t = self.G.GetEmbedding(v)
            x = t.x * self.zoomFactor / 100.0
            y = t.y * self.zoomFactor / 100.0
            self.drawVertex[v] = self.CreateDrawVertex(v,x,y)
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
        self.drawVertex = VertexLabeling()
        self.drawEdges = EdgeLabeling()
        self.drawLabel = VertexLabeling()
        self.vertexAnnotation = VertexLabeling()
        self.edgeAnnotation = EdgeLabeling()
        self.bubbles = {}
        self.moats = {}
        
        
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

        
    def DeleteEdgeAnnotations(self):
        """ *Internal* Delete all edge annotations on the canvas """
        self.canvas.delete("edgeAnno")

        
    def CreateDrawVertex(self,v,x=None,y=None):
        """ *Internal* Create a draw vertex for v on the canvas. Position is
            determined by the embedding unless explictely passed as x,y in
            canvas coordinates
        """
        if x == None and y == None:
            t = self.G.GetEmbedding(v)
            x,y = self.EmbeddingToCanvas(t.x, t.y)
        d = self.zVertexRadius
        w = (g.VertexFrameWidth*self.zoomFactor) / 100.0
        dv = self.canvas.create_oval(x-d, y-d, x+d, y+d, 
                                     fill=g.cVertexDefault, 
                                     tag="vertices",
                                     width=w) 
        self.canvas.tag_bind(dv, "<Any-Leave>", self.DefaultInfo)
        self.canvas.tag_bind(dv, "<Any-Enter>", self.VertexInfo)
        self.vertex[dv] = v
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
                                     font=self.font(self.zFontSize),
                                     text=self.G.GetLabeling(v), 
                                     fill=g.cLabelDefault,
                                     tag="labels")
        self.canvas.tag_bind(dl, "<Any-Enter>", self.VertexInfo)
        self.label[dl] = v
        return dl
        # Label to the bottom, to the right
        #d = self.zVertexRadius
        #return self.canvas.create_text(x+d+1, y+d+1, anchor="w", justify="left", font="Arial %d" %self.zFontSize,text=v)
        
        
        
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
                                       fill=g.cEdgeDefault, 
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
                                       fill=g.cEdgeDefault, 
                                       width=w,
                                       smooth=TRUE,
                                       splinesteps=24,
                                       tag="edges")	
        
    def CreateUndirectedDrawEdge(self,t,h,w):
        """ *Internal* Create an undirected draw edge. t, h are Point2Ds """
        return self.canvas.create_line(t.x,t.y,h.x,h.y,
                                       fill=g.cEdgeDefault,
                                       width=w,
                                       tag="edges") 

    def directedDrawEdgePoints(self,tail,head,curved):
        """ Factored out from CreateDirectedDrawEdge. Compute points
            in Canvas coordiantes for a directed draw edge, such that
            the arrowhead is visible.
            
            All the parameters are heuristics. Note, we ignore vertex
            framewidth.
        """
        l = sqrt((head.x - tail.x)**2 + (head.y - tail.y)**2)
        if l < 0.001:
            l = 0.001
        c = (l - self.zVertexRadius)/l - 0.001 # Dont let them quite touch 
        # (tmpX,tmpY) is a point on a straight line between t and h
        # not quite touching the vertex disc
        tmpX = tail.x + c * (head.x - tail.x) 
        tmpY = tail.y + c * (head.y - tail.y)
        if curved == 0:
            return tail.x, tail.y, tmpX, tmpY
        else: # Compute middle point for curves
            # (mX,mY) to difference vector h - t
            (mX,mY) = orthogonal((head.x - tail.x, head.y - tail.y))
            c = 1.5 * self.zVertexRadius + l / 25
            # Add c * (mX,mY) at midpoint between h and t
            mX = tail.x + .5 * (head.x - tail.x) + c * mX
            mY = tail.y + .5 * (head.y - tail.y) + c * mY            
            return tail.x, tail.y, mX, mY, tmpX, tmpY
            
        
    def CreateDirectedDrawEdge(self,tail,head,curved,w):
        """ *Internal* Create an directed draw edge. t, h are Point2Ds """
        if curved == 0:
            x1,y1,x2,y2 = self.directedDrawEdgePoints(tail,head,0)
            return self.canvas.create_line(x1,y1,x2,y2,
                                           fill=g.cEdgeDefault,
                                           arrow="last",
                                           arrowshape=self.zArrowShape, 
                                           width=w,
                                           tag="edges")
        else:
            x1,y1,x2,y2,x3,y3 = self.directedDrawEdgePoints(tail,head,1)
            return self.canvas.create_line(x1,y1,x2,y2,x3,y3,
                                           fill=g.cEdgeDefault,
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
        
        if not self.G.QEdgeWidth():
            w = (g.EdgeWidth * self.zoomFactor) / 100.0
        else:
            w = (self.G.EdgeWidth(tail,head) * self.zoomFactor) / 100.0
            
        if self.G.QDirected() == 1:
            if tail == head:
                de = self.CreateDirectedLoopDrawEdge(t,w)		
            else:
                if tail in self.G.OutNeighbors(head):
                    # Remove old straight de for other direction ... 
                    try:
                        oldColor = self.canvas.itemconfig(self.drawEdges[(head,tail)],
                                                          "fill")[4] # Should call GetEdgeColor
                        self.canvas.delete(self.drawEdges[(head,tail)])
                        # ... and create a new curved one
                        if not self.G.QEdgeWidth():
                            wOld = (g.EdgeWidth * self.zoomFactor) / 100.0
                        else:
                            wOld = (self.G.EdgeWidth(head,tail) * self.zoomFactor) / 100.0
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
                        oldColor = g.cEdgeDefault # When opening a graph we can get here
                        
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
        da =  self.canvas.create_text(pos.x + self.zVertexRadius + 1,
                                      pos.y + self.zVertexRadius + 1, 
                                      anchor="w", 
                                      justify="left",
                                      font=self.font(self.zFontSize), 
                                      text=annotation,
                                      tag="vertexAnno",
                                      fill=color)
        return da
        
    def UpdateVertexAnnotationPosition(self,v):
        pos = self.VertexPosition(v)
        da = self.vertexAnnotation[v]
        self.canvas.coords(da,
                           pos.x + self.zVertexRadius + 1,
                           pos.y + self.zVertexRadius + 1)
        
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
                                      font=self.font(self.zFontSize),
                                      text=annotation,
                                      tag="edgeAnno",
                                      fill=color)
        return da


    def UpdateEdgeAnnotationPosition(self, tail, head):
        """ *Internal* Create an edge annotation for (tail,head) on the canvas. 
            Position is determined by the embedding specified. """
        t = self.VertexPosition(tail)  
        h = self.VertexPosition(head)
        da = self.edgeAnnotation[(tail,head)]
        (mX,mY) = orthogonal((h.x - t.x, h.y - t.y))
        c = self.zVertexRadius
        x = t.x + .5 * (h.x - t.x) + c * mX
        y = t.y + .5 * (h.y - t.y) + c * mY
        # Label to the bottom, to the right
        self.canvas.coords(da, x, y)


        
        
        
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
        if lightness < 0.2: 
            self.canvas.itemconfig( self.drawLabel[v], fill=g.cLabelDefaultInverted)
        else:
            self.canvas.itemconfig( self.drawLabel[v], fill=g.cLabelDefault)
        self.canvas.itemconfig( self.drawVertex[v], fill=color)
        self.update()


    # Empty function used to get updates in AnimationHistory
    def UpdateEdgeInfo(self, tail, head, info):
        pass

    # Empty function used to get updates in AnimationHistory
    def UpdateGraphInfo(self, info):
        pass

    # Empty function used to get updates in AnimationHistory
    def UpdateVertexInfo(self, v, info):
        pass

    def GetVertexColor(self,v):
        """ Return the color of v """
        dv = self.drawVertex[v]
        return self.canvas.itemconfig(dv, "fill")[4]

        
    def SetAllVerticesColor(self, color, graph=None, vertices=None):
        """ Change the color of all vertices to 'color' at once 
            You can also pass an induced subgraph  or a list of vertices
        """
        if graph == None and vertices == None: # All vertices of graph shown
            self.canvas.itemconfig("vertices", fill=color)
        elif graph is not None: # all vertices of induced subgraph
            vertices = graph.vertices
        if vertices is not None: # all specified vertices
            for v in vertices:
                self.canvas.itemconfig(self.drawVertex[v], fill=color)           
        self.update()        
        
        
    def SetAllEdgesColor(self, color, graph=None, leaveColors=None):
        """ Change the color of all edges to 'color' at once
            You can also pass an induced subgraph  """
        if graph == None:
            if leaveColors == None:	
                self.canvas.itemconfig("edges", fill=color)
            else:
                for e in self.G.Edges():
                    if not self.GetEdgeColor(e[0],e[1]) in leaveColors:
                        self.SetEdgeColor(e[0],e[1],color)
        else: # induced subgraph
            for e in graph.Edges():
                if leaveColors == None or not (self.GetEdgeColor(e[0],e[1]) in leaveColors):
                    self.SetEdgeColor(e[0],e[1],color)
        self.update()
        
        
    def SetEdgeColor(self, tail, head, color):
        """ Change color of (tail,head) to color. No error checking! 
            Handles undirected graphs. """
        if self.G.QDirected() == 1:
            de = self.drawEdges[(tail,head)]
        else:
            try:
                de = self.drawEdges[(tail,head)]
            except KeyError:
                de = self.drawEdges[(head,tail)]	    
        self.canvas.itemconfig( de, fill=color)
        self.update()

    def SetEdgeFill(self, tail, head, dashtype):
        """ Change color of (tail,head) to color. No error checking! 
            Handles undirected graphs. """
        if self.G.QDirected() == 1:
            de = self.drawEdges[(tail,head)]
        else:
            try:
                de = self.drawEdges[(tail,head)]
            except KeyError:
                de = self.drawEdges[(head,tail)]            
        self.canvas.itemconfig( de, dash=dashtype )
        self.update()    
        

    def SetEdgesColor(self, edges, color):
        """ Change color of [(tail1,head1),...] to color. No error checking! 
            Handles undirected graphs. """
        #print "in setEdgesColor in GraphDisplay"
        for tail, head in edges:
            if self.G.QDirected() == 1:
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
        
        
    def BlinkVertex(self, v, color=None):
        """ Blink vertex v with color. Number of times, speed, default color is
            specified in GatoGlobals.py. No error checking! """
        if color is None: # No self in default arg
            color=g.cVertexBlink
        dv = self.drawVertex[v]
        oldColor = self.canvas.itemconfig(dv, "fill")[4]
        for i in xrange(1,g.BlinkRepeat):
            self.canvas.after(g.BlinkRate)
            self.canvas.itemconfig( dv, fill=color)
            self.update()
            self.canvas.after(g.BlinkRate)
            self.canvas.itemconfig( dv, fill=oldColor)
            self.update()
            
            
    def BlinkEdge(self, tail, head, color=None):
        """ Blink edge (tail,head) with color. Number of times, speed, default 
            color is specified in GatoGlobals.py. No error checking!	Handles
            undirected graphs. """	
        if color is None: # No self in default arg
            color=g.cVertexBlink
        if self.G.QDirected() == 1:
            de = self.drawEdges[(tail,head)]
        else:
            try:
                de = self.drawEdges[(tail,head)]
            except KeyError:
                de = self.drawEdges[(head,tail)]	    
        oldColor = self.canvas.itemconfig(de, "fill")[4]
        for i in xrange(1,g.BlinkRepeat):
            self.canvas.after(g.BlinkRate)
            self.canvas.itemconfig( de, fill=color)
            self.update()
            self.canvas.after(g.BlinkRate)
            self.canvas.itemconfig( de, fill=oldColor)
            self.update()

            
    def Blink(self, list, color=None):
        """ Blink all edges or vertices in list with color.
            Edges are specified as (tail,head). 
        
            Number of times, speed, default color is specified in GatoGlobals.py. 
            No error checking!	Handles undirected graphs. """	
        if color is None: # No self in default arg
            color=g.cVertexBlink
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
                
        for i in xrange(1,g.BlinkRepeat):
            self.canvas.after(g.BlinkRate)
            for j in xrange(len(drawItems)):	
                self.canvas.itemconfig(drawItems[j], fill=color)
            self.update()
            self.canvas.after(g.BlinkRate)
            for j in xrange(len(drawItems)):	
                self.canvas.itemconfig(drawItems[j], fill=oldColor[j])
            self.update()

    def SetVertexFrameColor(self, v, color):
        """ Set the color of the outline of a vertex """
        dv = self.drawVertex[v]
        self.canvas.itemconfig(dv, outline=color)
        self.update()
            
    def GetVertexFrameColor(self,v):
        """ Get the color of the outline of a vertex """
        dv = self.drawVertex[v]
        return self.canvas.itemcget(dv, "outline")

        
    def GetVertexFrameWidth(self,v):
        """ Get the width of the black frame of a vertex"""
        dv = self.drawVertex[v]
        return (float(self.canvas.itemcget(dv, "width")) * 100.0) /  self.zoomFactor
        
        
    def SetVertexFrameWidth(self,v,val):
        """ Set the width of the black frame of a vertex to val """
        dv = self.drawVertex[v]
        oldwidth = float(self.canvas.itemcget(dv, "width"))
        self.canvas.itemconfig(dv, outline = "white", width=oldwidth * 2)
        self.update()
        self.canvas.itemconfig(dv, outline = "black", width=(val * self.zoomFactor) / 100.0)
        self.update()
        
        
    def GetVertexAnnotation(self,v):
        if not self.vertexAnnotation.QDefined(v):
            return ""
        else:
            return self.canvas.itemcget(self.vertexAnnotation[v],"text")

            
    def SetVertexAnnotation(self,v,annotation,color="black"):
        """ Add an annotation to v. Annotations are displayed to the left and
            the bottom of v and allow to display more info about a vertex. 
            No error checking!  Does not handle vertex deletions/moves !"""
        if v == None: return	
        if not self.vertexAnnotation.QDefined(v):
            self.vertexAnnotation[v] = self.CreateVertexAnnotation(v,annotation,color)
        else:
            da = self.vertexAnnotation[v]
            self.canvas.itemconfig(da, 
                                   font=self.font(self.zFontSize),
                                   text=annotation,
                                   fill=color)
            self.update()


    def ClearVertexAnnotations(self):
        """ Set all vertex annotations to the empty string """
        for v, da in self.vertexAnnotation.items():
            self.canvas.itemconfig(da,text='')     
        
            
    def SetEdgeAnnotation(self,tail,head,annotation,color="black"):
        """ Add an annotation to (tail,head). Annotations are displayed to the left and
            the bottom of v and allow to display more info about a vertex. """	
        if not self.edgeAnnotation.QDefined((tail,head)):
            self.edgeAnnotation[(tail,head)] = self.CreateEdgeAnnotation(tail,head,
                                                                         annotation,
                                                                         color)
        else:
            da = self.edgeAnnotation[(tail,head)]
            self.canvas.itemconfig(da,
                                   font=self.font(self.zFontSize),
                                   text=annotation,
                                   fill=color)
            self.update()
            
            
    def UpdateVertexLabel(self, v, blink=1, color=None):
        """ Visualize the changing of v's label. After changing G.labeling[v],
            call UpdateVertexLabel to update the label in the graph window,
            blinking blink times with color. No error checking!  """
        if color is None:
            color=g.cLabelBlink
        dl = self.drawLabel[v]
        if blink == 1:
            oldColor = self.canvas.itemconfig(dl, "fill")[4]
            for i in xrange(1,g.BlinkRepeat):
                self.canvas.after(g.BlinkRate)
                self.canvas.itemconfig( dl, fill=color)
                self.update()
                self.canvas.after(g.BlinkRate)
                self.canvas.itemconfig( dl, fill=oldColor)
                self.update()
                self.canvas.itemconfig( dl,
                                        font=self.font(self.zFontSize),
                                        text=self.G.GetLabeling(v))
        else:
            self.canvas.itemconfig( dl,
                                    font=self.font(self.zFontSize),
                                    text=self.G.GetLabeling(v))
            self.update()


    def GetEdgeWidth(self,tail,head):
        """ Get the edge width in canvas coordinates """
        de = self.drawEdges[(tail,head)]
        return self.canvas.itemcget(de, "width")

            
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
            t = self.G.GetEmbedding(v)             
            infoString = "Vertex %d at position (%d,%d)" % (v, t.x, t.y)
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
                
                
    def FindGridVertex(self,event):
        """ *Internal* Given an event find the correspoding grid vertex """
        x,y = self.WindowToCanvasCoords(event)
        if not event.widget.find_overlapping(x,y,x,y):
            return None
        else:
            try:
                widget = event.widget.find_overlapping(x,y,x,y)[-1]
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

    def CreateBubble(self, vertex_nums, offset_value, color):
        self.bubbles[vertex_nums] = (offset_value, color)

    def ResizeBubble(self, vertex_nums, new_radius):
        pass

    def DeleteBubble(self, vertex_nums):
        del self.bubbles[vertex_nums]

    def CreateMoat(self, moat_id, radius, color):
        # Moat ID is of form 'moat_{vertex_num}-{moat_num}'
        self.moats[moat_id] = (radius, color)

    def GrowMoat(self, moat_id, radius):
        pass

    def Wait(self):
        pass

    def EndOfProlog(self):
        pass

    # XXX: Needs reorganisation. We could highlight paths, circuits
    # and vertex sets. Pretty (but not obvious) would be a convex
    # hull around a vertex set.
    #
    # method names are inconsistent, there should be default color
    # and highlights should be handled without special casing.
    
    def HighlightVertices(self, vertices, color):
        """ Highlight the given vertices with wide circle underneath

            Returns a highlightID for hiding the highlight at a later time
        """
        highlightID = tuple(vertices)
        highlights = []
        d = self.zVertexRadius * 1.5
        for v in vertices:
            t = self.G.GetEmbedding(v)
            x = t.x * self.zoomFactor / 100.0
            y = t.y * self.zoomFactor / 100.0
            h = self.canvas.create_oval(x-d, y-d, x+d, y+d, 
                                        fill=color, 
                                        tag="highlight",
                                        width=0)
            self.canvas.lower(h,"edges")
            highlights.append(h)
        self.highlightedPath[highlightID] = highlights #XXX
        return highlightID

    def HideHighlight(self, highlightID):
        for h in self.highlightedPath[highlightID]:
            self.canvas.delete(h)

    def HighlightPath(self, path, color, closed = 0):
        """ Draw a wide poly line underneath the path in the graph
            Path is given as a list of vertices

            Returns a pathID for hiding the path at a later time
        """
        pathID = tuple(path)
        coords = ()
        for v in path:
            t = self.G.GetEmbedding(v)           
            coords += (t.x * self.zoomFactor / 100.0,
                       t.y * self.zoomFactor / 100.0)
        if closed:
            t = self.G.GetEmbedding(path[0])
            coords += (t.x * self.zoomFactor / 100.0,
                       t.y * self.zoomFactor / 100.0)
        c = self.canvas.create_line(coords, tag="highlight", fill=color,
                                    width=16)
        
        self.canvas.lower(c,"edges")
        self.highlightedPath[pathID] = c 
        return pathID
        
    def HidePath(self, pathID):
        #XXX Do we want to hide or delete?
        self.canvas.delete(self.highlightedPath[pathID])

    ############################################################################
    #				       
    # edit commands
    #
    def AddVertex(self, x, y, v=None):
        """ *Internal* Add a new vertex at (x,y) 
            NOTE: Assumes x,y to be in embedding coordinates
        
            If v is not None, then we assume that we can pass the
            ID v to AddVertex. This is true, when G is a subgraph
            """
        if v == None:
            v = self.G.AddVertex()
        else:
            self.G.AddVertex(v)
        self.G.SetEmbedding(v,x,y)
        self.G.SetLabeling(v, v)
        self.drawVertex[v] = self.CreateDrawVertex(v)
        self.drawLabel[v]  = self.CreateDrawLabel(v)
        for i in xrange(0,self.G.NrOfVertexWeights()):
            self.G.SetVertexWeight(i,v,0)
        if self.autoUpdateScrollRegion:
            self.UpdateScrollRegion()
        return v
        
    def AddVertexCanvas(self, x, y):
        """ *Internal* Add a new vertex at (x,y) 
            NOTE: Assumes x,y to be in canvas coordinates""" 
        v = self.G.AddVertex()
        embed_x, embed_y = self.CanvasToEmbedding(x,y)
        self.G.SetEmbedding(v,embed_x,embed_y)
        self.G.SetLabeling(v, v)
        self.drawVertex[v] = self.CreateDrawVertex(v,x,y)
        self.drawLabel[v]  = self.CreateDrawLabel(v)
        for i in xrange(0,self.G.NrOfVertexWeights()):
            self.G.SetVertexWeight(i,v,0)
        if self.autoUpdateScrollRegion:
            self.UpdateScrollRegion()
        return v
        
    def MoveVertex(self,v,x,y,doUpdate=None):
        """ *Internal* Move vertex v to position (x,y) 
            NOTE: Assumes x,y to be in canvas coordinates if 
                  doUpdate=None and in embedding coordinates else
        """ 	    
        if doUpdate == None: # User has moved drawvertex
            newX, newY = self.CanvasToEmbedding(x,y)
            self.G.SetEmbedding(v,newX, newY)
            
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
            self.G.SetEmbedding(v,x,y)
            
            
        # move incident edges
        outVertices = self.G.OutNeighbors(v)[:] # Need a copy here
        inVertices = self.G.InNeighbors(v)[:]
        euclidian = self.G.QEuclidian()
        
        # Handle outgoing edges
        t = self.G.GetEmbedding(v)
        for w in outVertices:
            de = self.drawEdges[(v,w)]
            color = self.canvas.itemconfig(de, "fill")[4]
            self.canvas.delete(de)
            de = self.CreateDrawEdge(v,w)
            self.canvas.itemconfig( de, fill=color)            
            self.drawEdges[(v,w)] = de
            self.canvas.lower(de,"vertices")
            if euclidian:
                h = self.G.GetEmbedding(w)
                self.G.SetEdgeWeight(0,v,w,sqrt((h.x - t.x)**2 + (h.y - t.y)**2))
            if self.edgeAnnotation.QDefined((v,w)):
                self.UpdateEdgeAnnotationPosition(v,w)
                
        # Handle incoming edges
        h = self.G.GetEmbedding(v)
        for w in inVertices:
            de = self.drawEdges[(w,v)]
            color = self.canvas.itemconfig(de, "fill")[4]
            self.canvas.delete(de)
            de = self.CreateDrawEdge(w,v)
            self.canvas.itemconfig( de, fill=color)            
            self.drawEdges[(w,v)] = de
            self.canvas.lower(de,"vertices")
            if euclidian:
                t = self.G.GetEmbedding(w)
                self.G.SetEdgeWeight(0,w,v,sqrt((h.x - t.x)**2 + (h.y - t.y)**2))
            if self.edgeAnnotation.QDefined((w,v)):
                self.UpdateEdgeAnnotationPosition(w,v)
        if self.vertexAnnotation.QDefined(v):
            self.UpdateVertexAnnotationPosition(v)
        if self.autoUpdateScrollRegion:
            self.UpdateScrollRegion()
            
            
    def DeleteVertex(self,v):
        """ *Internal* Delete vertex v """ 
        # if v has an annotation delete
        if self.vertexAnnotation.QDefined(v):
            self.canvas.delete(self.vertexAnnotation[v])
            del(self.vertexAnnotation.label[v])
        self.canvas.delete(self.drawVertex[v])
        del(self.drawVertex.label[v])
        self.canvas.delete(self.drawLabel[v])
        del(self.drawLabel.label[v])
        """ delete incident edges
        outVertices = self.G.OutNeighbors(v)[:] # Need a copy here
        inVertices = self.G.InNeighbors(v)[:]
        #for w in outVertices:
        #    self.DeleteEdge(v,w,0)
        #for w in inVertices:
        #    if w != v: # We have already deleted loops
               self.DeleteEdge(w,v,0)
        """
        self.G.DeleteVertex(v)

        
    def AddEdge(self,tail,head):
        """ *Internal* Add Edge. Note: unless graph is Euclidian weight is set
            to 0. No error checking ! Returns tail, head (See Subgraph.AddEdge
            in Graph.py for explanation) """ 
        try:
            tail, head = self.G.AddEdge(tail,head) # Note if we display a sub-graph
            # an edge (tail, head) might be (head, tail) in super-graph
            de = self.CreateDrawEdge(tail,head)
            self.drawEdges[(tail, head)] = de
            self.canvas.lower(de,"vertices")
            return tail, head                
        except GatoGlobals.GraphNotSimpleError:
            log.error("Inserting edge (%d,%d) would result in non-simple graph" % (tail,head))
            
            
    def DeleteEdge(self,tail,head,repaint=1):
        """ *Internal* Delete edge (tail,head) """ 
        self.canvas.delete(self.drawEdges[(tail,head)])
        # if (tail,head) has an annotation delete it
        if self.edgeAnnotation.QDefined((tail,head)):
            self.canvas.delete(self.edgeAnnotation[(tail,head)])
            del(self.edgeAnnotation.label[(tail,head)])
        del(self.drawEdges.label[(tail,head)]) # XXX
        self.G.DeleteEdge(tail,head)
        if repaint and self.G.QDirected() == 1 and tail in self.G.OutNeighbors(head):
            # i.e. parallel edge
            oldColor = self.canvas.itemconfig(self.drawEdges[(head,tail)],
                                              "fill")[4] # Should call GetEdgeColor
            self.canvas.delete(self.drawEdges[(head,tail)])
            de = self.CreateDrawEdge(head,tail)
            self.canvas.itemconfig(de, fill=oldColor) # Should call SetEdgeColor
            self.drawEdges[(head,tail)] = de
            self.canvas.lower(de,"vertices")

            
    def RaiseEdge(self,tail,head):
        """ *Internal* Raise edge above others ... useful for subgraphs on
        grid graphs
        """
        self.canvas.tkraise(self.drawEdges[(tail,head)], "edges")

        
    def SwapEdgeOrientation(self,tail,head):
        """ *Internal* If graph is directed and we do not have edges in both
            directions, change the orientation of the edge (tail,head) """ 
        
        if self.G.QDirected() == 0 or self.G.QEdge(head,tail): # Assuming (tail,head) is an edge
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
            t = self.G.GetEmbedding(v)            
            x,y = self.EmbeddingToCanvas(t.x,t.y)
            
        return Point2D(x,y)

        
    def VertexPositionAndRadius(self,v):
        """ Return the position and radius of vertex v in embedding
            coordinates
        """
        try:
            coords = self.canvas.coords(self.drawVertex[v])
            x = 0.5 * (coords[2] - coords[0]) + coords[0]
            y = 0.5 * (coords[3] - coords[1]) + coords[1]
            r = 0.5 * (coords[2] - coords[0])
            xe,ye = self.CanvasToEmbedding(x,y)
            re,dummy = self.CanvasToEmbedding(r,0)
            return xe,ye,re
        except: # Vertex is not on the canvas yet
            t = self.G.GetEmbedding(v)            
            return t.x, t.y, g.VertexRadius

        
    ############################################################################
    #				       
    # various stuff 
    #        
    def PrintToPSFile(self,fileName):
        """ Produce an EPSF of canvas in fileName. Note: Graph gets scaled
            and rotated as to maximize size while still fitting on paper """ 
        bb = self.canvas.bbox("all") # Bounding box of all elements on canvas
        # Give 10 pixels room to breathe
        print "PrintToPSFile", bb
        padding = 15
        x = bb[0] - padding
        y = bb[1] - padding
        width=bb[2] - bb[0] + 2*padding
        height=bb[3] - bb[1] + 2*padding
        
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
            

# MOVED to GatoExport
##    def ExportSVG(self, fileName, animation = None):
##        """ Export Canvas to a SVG file.

##            XXX Experimental version; spike solution. This will be refactored.
##            - Gato/Gred will move over to ObjectGraph model. If the GraphDisplay
##              DrawEdges and DrawVertexes becomes objects too, they should know how
##              to export them.
##            - For static export we could just dump everything on the Canvas. AFAIK
##              SVG is richer than Tk, so that should be straightforward.

##        """
##        bb = self.canvas.bbox("all") # Bounding box of all elements on canvas
##        # Give 10 pixels room to breathe
##        x = max(bb[0] - 20,0)
##        y = max(bb[1] - 20,0)
##        width=bb[2] - bb[0] + 20
##        height=bb[3] - bb[1] + 20

##        animationhead = """<?xml version="1.0" encoding="utf-8"?>
##<svg xmlns="http://www.w3.org/2000/svg"
##xmlns:xlink="http://www.w3.org/1999/xlink"
##xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
##viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm"
##onload="StartAnimation(evt)">
##<defs> 
##    <marker id="Arrowhead" 
##      viewBox="0 0 10 10" refX="0" refY="5" 
##      markerUnits="strokeWidth" 
##      markerWidth="4" markerHeight="3" 
##      orient="auto"> 
##      <path d="M 0 0 L 10 5 L 0 10 z" /> 
##    </marker> 
##</defs>
##<script type="text/ecmascript"><![CDATA[
##var step = 0;
##var v_ano_id = "va"; //ID prefix for vertex annotation
##var e_arrow_id = "ea"; //ID prefix for edge arrow
##var svgNS="http://www.w3.org/2000/svg";
##var the_evt;
##var element;
##var blinkcolor;
##var blinkcount;
##function StartAnimation(evt) {
##	the_evt = evt;	
##	ShowAnimation();
##}
##function SetVertexColor(v, color) {
##    element = the_evt.target.ownerDocument.getElementById(v);
##    element.setAttribute("fill", color);
##}
##// Cannot map: SetAllVerticesColor(self, color, graph=None, vertices=None):
##function SetEdgeColor(e, color) {
##    // NOTE: Gato signature SetEdgeColor(v, w, color)
##    element = the_evt.target.ownerDocument.getElementById(e);
##    element.setAttribute("stroke", color);
##    //added changes to color of arrowheads
##    element = the_evt.target.ownerDocument.getElementById(e_arrow_id + e);
##    if(element != null){
##        element.setAttribute("fill", color);
##    }
##}
##//function SetEdgesColor(edge_array, color) {
##// Cannot map: SetAllEdgesColor(self, color, graph=None, leaveColors=None)
##function BlinkVertex(v, color) {
##    element = the_evt.target.ownerDocument.getElementById(v);
##    blinkcolor = element.getAttribute("fill")
##    blinkcount = 3;
##    element.setAttribute("fill", "black");
##    setTimeout(VertexBlinker, 3);
##}
##function VertexBlinker() {
##    if (blinkcount %% 2 == 1) {
##       element.setAttribute("fill", blinkcolor); 
##    } else {
##       element.setAttribute("fill", "black"); 
##    }
##    blinkcount = blinkcount - 1;
##    if (blickcount >= 0)
##       setTimeout(VertexBlinker, 3);
##}




##//
##//BlinkEdge(self, tail, head, color=None):
##//
##//Blink(self, list, color=None):
##function SetVertexFrameWidth(v, val) {
##    var element = the_evt.target.ownerDocument.getElementById(v);
##    element.setAttribute("stroke-width", val);
##}
##function SetVertexAnnotation(v, annotation, color) //removed 'self' parameter to because 'self' parameter was assigned value of v, v of annotation, and so on.
##{
##    element = the_evt.target.ownerDocument.getElementById(v);
##    if(element != null){
##	if(the_evt.target.ownerDocument.getElementById(v_ano_id + v) !=null){
##		ano = the_evt.target.ownerDocument.getElementById(v_ano_id + v);
##		ano.parentNode.removeChild(ano);
	
##	}
	
##	var newano = the_evt.target.ownerDocument.createElementNS(svgNS,"text");
##	x_pos = parseFloat(element.getAttribute("cx")) + parseFloat(element.getAttribute("r")) + 1;
##	y_pos = parseFloat(element.getAttribute("cy")) + parseFloat(element.getAttribute("r")) + 1;
##	newano.setAttribute("x", x_pos);
##	newano.setAttribute("y", y_pos);
##	newano.setAttribute("fill",color);
##	newano.setAttribute("id", v_ano_id+v);
##	newano.setAttribute("text-anchor","center");
##	newano.setAttribute("font-size","14.0");
##	newano.setAttribute("font-family","Helvetica");
##	newano.setAttribute("font-style","normal");
##	newano.setAttribute("font-weight","bold");
##	newano.appendChild(the_evt.target.ownerDocument.createTextNode(annotation));
##	the_evt.target.ownerDocument.documentElement.appendChild(newano);
	
##    }
##}

##//function SetEdgeAnnotation(self,tail,head,annotation,color="black"):
##//def UpdateVertexLabel(self, v, blink=1, color=None):
##var animation = Array(%(animation)s
##);
##function ShowAnimation() {
##	var duration = animation[step][0] * 4;
##	animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
##	step = step + 1; 
##	if(step < animation.length) 
##		setTimeout(ShowAnimation, duration);
##}
##]]></script>
##        """
##        head = """<?xml version="1.0" encoding="utf-8"?>
##<svg xmlns="http://www.w3.org/2000/svg"
##xmlns:xlink="http://www.w3.org/1999/xlink"
##xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
##viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm">
##<defs> 
##    <marker id="Arrowhead" 
##      viewBox="0 0 10 10" refX="0" refY="5" 
##      markerUnits="strokeWidth" 
##      markerWidth="4" markerHeight="3" 
##      orient="auto"> 
##      <path d="M 0 0 L 10 5 L 0 10 z" /> 
##    </marker> 
##</defs>
##"""
##        footer = """
##</svg>
##"""

##        file = open(fileName,'w')
##        if animation is not None:
##            anivar = ",\n".join(animation)
##            vars = {'x':x, 'y':y, 'width':width, 'height':height, 'animation':anivar}
##            file.write(animationhead % vars)
##        else:
##            file.write(head % {'x':x,'y':y,'width':width,'height':height})

##        # Write Bubbles from weighted matching
##        # XXX We make use of the fact that they have a bubble tag
##        # XXX What to use as the bubble ID?
##        bubbles = self.canvas.find_withtag("bubbles")
##        for b in bubbles:
##            col = self.canvas.itemcget(b,"fill")
##            # Find center and convert to Embedding coordinates
##            coords = self.canvas.coords(b)
##            x = 0.5 * (coords[2] - coords[0]) + coords[0]
##            y = 0.5 * (coords[3] - coords[1]) + coords[1]
##            r = 0.5 * (coords[2] - coords[0])
##            xe,ye = self.CanvasToEmbedding(x,y)
##            re,dummy = self.CanvasToEmbedding(r,0)
##            file.write('<circle cx="%s" cy="%s" r="%s" fill="%s" '\
##                       ' stroke-width="0" />\n' % (xe,ye,re,col))           
            

##        # Write Highlighted paths
##        # XXX What to use as the bubble ID?
##        for pathID, draw_path in self.highlightedPath.items():
##            # XXX Need to check visibility? See HidePath
##            col = self.canvas.itemcget(draw_path,"fill")
##            width = self.canvas.itemcget(draw_path,"width")
##            points = ["%s,%s" % self.VertexPositionAndRadius(v)[0:2] for v in pathID]
##            file.write('<polyline points="%s" stroke="%s" stroke-width="%s" '\
##                       'fill="None" />\n' % (" ".join(points),col,width))
        
        

##        # Write Edges
##        for v,w in self.G.Edges():
##            vx,vy,r = self.VertexPositionAndRadius(v)
##            wx,wy,r = self.VertexPositionAndRadius(w)
##            col = self.GetEdgeColor(v,w)
##            width = self.GetEdgeWidth(v,w)

##            if self.G.directed == 0:
##                file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
##                           ' stroke-width="%s"/>\n' % ((v,w),vx,vy,wx,wy,col,width))
##            else:
##                # AAARGH. SVG has a retarded way of dealing with arrowheads 
##                # It is a known bug in SVG 1.1 that the color of the arrowhead is not inherited
##                # Will be fixed in SVG 1.2
##                # See bug 995815 in inkscape bug tracker on SF
##                # However, even 1.2 will keep the totally braindead way of sticking on the arrowhead
##                # to the end! of the arrow. WTF
##                # Workarounds:
##                # Implement arrows as closed polylines including the arrow (7 vs. 2 coordinates)
##                # Q> How to do curved edges with arrows? Loops? 
##                x1,y1,x2,y2 = self.directedDrawEdgePoints(self.VertexPosition(v),self.VertexPosition(w),0)
##                x1e,y1e = self.CanvasToEmbedding(x1,y1)
##                x2e,y2e = self.CanvasToEmbedding(x2,y2)


##                if self.G.QEdge(w,v): # Directed edges both ways
##                    file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
##                               ' stroke-width="%s"/>\n' % ((v,w),x1e,y1e,x2e,y2e,col,width))
##                else: # Just one directed edge
##                    # XXX How to color arrowhead?
##                    l = sqrt((float(wx)-float(vx))**2 + (float(wy)-float(vy))**2)
##                    if (l < .001):
##                        l = .001

##                    c = (l-2*self.zVertexRadius)/l + .01
##                    tmpX = float(vx) + c*(float(wx) - float(vx))
##                    tmpY = float(vy) + c*(float(wy) - float(vy))
                    

##                    #dx = 0 #offset of wx to make room for arrow
##                    #dy = 0 #offset of wy
##                    cr = 0
##                    #Took out marker-end="url(#Arrowhead)" and added polyline
##                    #Shrink line to make room for arrow
##                    for z in self.G.Vertices():
##                        cx,cy,cr = self.VertexPositionAndRadius(z)
##                        if(cx == wx and cy == wy):
##                            angle = atan2(int(float(wy))-int(float(vy)), int(float(wx))-int(float(vx)))
##                            file.write('<line id="%s" x1="%s" y1="%s" x2="%f" y2="%f" stroke="%s"'\
##                                   ' stroke-width="%s" />\n' % ((v,w),vx,vy,tmpX,tmpY,col,width))
##                            break
                        
##                    #Temporary settings for size of polyline arrowhead
##                    a_width = (1 + 1.5/(1*pow(log10(float(width)), 6)))
##                    if(a_width > 5.0):
##                        a_width = 5.0
##                    a_width *= float(width) 
##                    p1 = (0,0)
##                    p2 = (0, a_width) #0 + int(round(1.5*int(float(width)))))       float(wy) - (p2[1]+p1[1])/2
##                    p3 = (cr, a_width/2)
##                    angle = degrees(atan2(int(wy)-int(vy), int(wx)-int(vx)))
##                    c = (l-2*self.zVertexRadius)/l
##                    tmpX = float(vx) + c*(float(wx) - float(vx))
##                    tmpY = float(vy) + c*(float(wy) - float(vy))
##                    file.write('<polyline id="ea%s" points="%f %f %f %f %s %f" fill="%s" transform="translate(%f,%f)'\
##                               ' rotate(%f %f %f)" />\n' % ((v,w), p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))
                    

##            # Write Edge Annotations
##            if self.edgeAnnotation.QDefined((v,w)):
##                da = self.edgeAnnotation[(v,w)]
##                x,y = self.canvas.coords(self.edgeAnnotation[(v,w)])
##                xe,ye = self.CanvasToEmbedding(x,y)
##                text = self.canvas.itemcget(self.edgeAnnotation[(v,w)],"text") 
##                size = r * 0.9
##                offset = 0.33 * size
##                col = 'black'
##                if text != "":
##                    file.write('<text id="ea%s" x="%s" y="%s" text-anchor="center" '\
##                               'fill="%s" font-family="Helvetica" '\
##                               'font-size="%s" font-style="normal">%s</text>\n' % (xe,ye+offset,col,size,text))
               

##        for v in self.G.Vertices():
##            x,y,r = self.VertexPositionAndRadius(v)

##            # Write Vertex
##            col = self.GetVertexColor(v)
##            fw = self.GetVertexFrameWidth(v)
##            fwe,dummy = self.CanvasToEmbedding(fw,0)
##            stroke = self.GetVertexFrameColor(v)

##            #print x,y,r,col,fwe,stroke
##            file.write('<circle id="%s" cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"'\
##                       ' stroke-width="%s" />\n' % (v,x,y,r,col,stroke,fwe))
            
##            # Write Vertex Label
##            col = self.canvas.itemcget(self.drawLabel[v], "fill")
##            size = r*1.0
##            offset = 0.33 * size
            
##            file.write('<text id="vl%s" x="%s" y="%s" text-anchor="middle" fill="%s" font-family="Helvetica" '\
##                       'font-size="%s" font-style="normal" font-weight="bold" >%s</text>\n' % (v,x,y+offset,col,size,self.G.GetLabeling(v)))
            
##            # Write vertex annotation
##            size = r*0.9
##            text = self.GetVertexAnnotation(v)
##            col = 'black'
##            if text != "":
##                file.write('<text id="va%s" x="%s" y="%s" text-anchor="left" fill="%s" font-family="Helvetica" '\
##                           'font-size="%s" font-style="normal">%s</text>\n' % (v,x+r+1,y+r+1,col,size,text))
            


            
##        file.write(footer)
##        file.close()

             
    def About(self, graphName=""):
        """ Return a HTML-page giving information about the graph """
        if self.hasGraph == 1:
            return self.G.About(graphName)
        else:
            return "<HTML><BODY> <H3>No graph available</H3></BODY></HTML>"
            
            
            
            
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
    
    def __init__(self, master=None, number=1):
        Frame.__init__(self, master)
        self.pack() 
        self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
        self.num = number
        GraphDisplay.__init__(self)
        
    def SetTitle(self,title):
        log.info("change window title to %s" % title)

    def Show(self):
        pass

        
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
