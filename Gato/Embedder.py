################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   Embedder.py
#	author: Ramazan Buzdemir
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################


class Embedder:
    """ This class provides an abstract Embedder as
        a base for actual Embedder implementations """
    
    def Name(self):
	""" Return a short descriptive name for the embedder e.g. usable as 
	    a menu item """
	return "none"

    def Embed(self, theGraphEditor):
	""" Compute the Embedding. Changed display through theGraphEditor.
            Return value != none designates error/warning message """
	return none


#----------------------------------------------------------------------
import whrandom

class RandomEmbedder(Embedder):

    def Name(self):
	return "Randomize Layout"
    
    def Embed(self, theGraphEditor):
	theGraphEditor.SetGraphMenuGrid(0)
	for v in theGraphEditor.G.vertices:
	    theGraphEditor.MoveVertex(v, 
				      whrandom.randint(10,990),
				      whrandom.randint(10,990), 
				      1)
#----------------------------------------------------------------------

from math import pi, sin, cos

class CircularEmbedder(Embedder):

    def Name(self):
	return "Circular Layout"
    
    def Embed(self, theGraphEditor):
	theGraphEditor.SetGraphMenuGrid(0)
        if theGraphEditor.G.Order()!=0: 
            distance = 2*pi/theGraphEditor.G.Order()
            degree = 0
            xMiddle=500; yMiddle=500; radius=450
            for v in theGraphEditor.G.vertices:
                xCoord=radius*cos(degree)+xMiddle
                yCoord=radius*sin(degree)+yMiddle
                theGraphEditor.MoveVertex(v,xCoord,yCoord,1)
                degree=degree+distance
#----------------------------------------------------------------------

from Tkinter import *
import tkSimpleDialog 
import string
from tkMessageBox import showwarning
from GraphUtil import BFS

class BFSLayoutDialog(tkSimpleDialog.Dialog):

    def __init__(self, master, G):
        self.G = G
        tkSimpleDialog.Dialog.__init__(self, master, "BFS Layout")
        

    def body(self, master):
        self.resizable(0,0)
        
        self.root=StringVar()
        self.root.set("1")
        label = Label(master, text="root (1-%i):" %self.G.Order(), anchor=W)
        label.grid(row=0, column=0, padx=4, pady=3, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,textvariable=self.root)
        entry.selection_range(0,1)
        entry.focus_set()
	entry.grid(row=0,column=1, padx=4, pady=3, sticky="w")
        
        self.direction=StringVar()
        self.direction.set("forward")
        if self.G.QDirected():
            radio=Radiobutton(master, text="forward", variable=self.direction, 
                               value="forward")
            radio.grid(row=0, column=2, padx=4, pady=3, sticky="w") 
            radio=Radiobutton(master, text="backward", variable=self.direction,
                               value="backward")
            radio.grid(row=1, column=2, padx=4, pady=3, sticky="w") 


    def validate(self):
        try: 
            if string.atoi(self.root.get())<0 or string.atoi(self.root.get())>self.G.Order():
                raise rootError
            self.result=[]
            self.result.append(string.atoi(self.root.get()))
            self.result.append(self.direction.get())
            return self.result
        except:
           showwarning("Warning", "Please try again !")
           return 0


class BFSTreeEmbedder(Embedder):

    def Name(self):
	return "BFS-Tree Layout"

    def Embed(self, theGraphEditor):
	theGraphEditor.SetGraphMenuGrid(0)
	if theGraphEditor.G.Order()!=0:
	    dial = BFSLayoutDialog(theGraphEditor, theGraphEditor.G)
            if dial.result is None:
                return

            BFSdistance = BFS(theGraphEditor.G,dial.result[0],dial.result[1])[0]
            maxDistance=0
            maxBreadth=0
            list = {}
	    for v in theGraphEditor.G.vertices:
                list[BFSdistance[v]] = []
            for v in theGraphEditor.G.vertices:
                list[BFSdistance[v]].append(v)
            maxDistance=len(list)
            for d in list.values():
                if len(d)>maxBreadth: maxBreadth=len(d)
            xDist=900/(maxDistance-1)
            yDist=900/(maxBreadth-1)
            xCoord=950
            for d in list.values():
		yCoord=500-(len(d)-1)*yDist/2
                for v in d:
                    theGraphEditor.MoveVertex(v,xCoord+whrandom.randint(-20,20),yCoord,1)
                    yCoord=yCoord+yDist 
                xCoord=xCoord-xDist
#----------------------------------------------------------------------

from PlanarEmbedding import *

class FPP_PlanarEmbedder(Embedder):

    def Name(self):
	return "Planar Layout (FPP)"
    
    def Embed(self, theGraphEditor):
	FPP_PlanarEmbedding(theGraphEditor)

class Schnyder_PlanarEmbedder(Embedder):

    def Name(self):
	return "Planar Layout (Schnyder)"
    
    def Embed(self, theGraphEditor):
	Schnyder_PlanarEmbedding(theGraphEditor)
#----------------------------------------------------------------------

""" Here instantiate all the embedders you want to make available to
    a client. """
embedder = [RandomEmbedder(), CircularEmbedder(), BFSTreeEmbedder(),
            FPP_PlanarEmbedder(), Schnyder_PlanarEmbedder()]
