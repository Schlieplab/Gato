#!/usr/bin/env python2.2
################################################################################
#
#       This file is based on of Gato (Graph Animation Toolbox) 
#
#	file:   ViewClusterGraph.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 2003 Alexander Schliep
#                                   
#       Contact: alexander@schliep.org             
#
#       Information on Gato: http://gato.sf.net
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
from GatoGlobals import *
import GatoGlobals # Needed for help viewer.XXX
from Graph import Graph, VertexLabeling, Point2D
from DataStructures import EdgeWeight, VertexWeight, PriorityQueue
from GraphUtil import OpenCATBoxGraph, OpenGMLGraph, SaveCATBoxGraph, WeightedGraphInformer
from GraphEditor import GraphEditor
from Tkinter import *
import tkFont
from GatoUtil import stripPath, extension
import GatoDialogs
import GatoIcons
from ScrolledText import *

from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel
import tkSimpleDialog 
import random
import string
import sys
import os

import GraphCreator, Embedder


def hamming_distance(v,w):
    d = 0
    for i in xrange(len(v)):
        if v[i] is not w[i]:
            d += 1
    return d
    
    
def MSTPrim(G, root):
    """ Compute a minimal spanning tree using Prim's algorithm.
        Returns a set of edges """
    
    # Initialisation ...
    weight = G.edgeWeights[0]
    mst_edges = []
    mst_vertices = [root]
    pred = {}
    
    Q = PriorityQueue()
    
    for v in G.Neighborhood(root):
        Q.Insert((root,v), weight[(root,v)])
        pred[v] = root
        
    while len(mst_vertices) < len(G.vertices): # XXX Assume G is connected!!!
    
        (u,v) = Q.DeleteMin()
        mst_edges.append((u,v))
        if not u in mst_vertices:
            mst_vertices.append(u)        
        if not v in mst_vertices:
            mst_vertices.append(v)
            #print "Adding", (u,v), " of weight ", weight[(u,v)]
            
        for w in G.Neighborhood(v):
            if not w in mst_vertices and pred.has_key(w) and  weight[(pred[w],w)] > weight[(v,w)]:
                # Delete from PriorityQueue: weights are non-neg, set key to -1
                # and delete minimal
                Q.DecreaseKey((pred[w],w),-99)
                Q.DeleteMin()
                
                Q.Insert((v,w),weight[(v,w)])
                pred[w] = v
                
    return mst_edges
    
class AlleleVariationCluster:

    def __init__(self,fileName):
        self.fileName = fileName
        self.G = Graph()
        self.ST = {}
        self.STComplex = {}
        self.signature = {}
        self.read(self.fileName)
        self.addEdges()
        self.computeMST()
        self.computeEmbedding()
        
        
    def read(self,fileName):
        """ read datafile consisting of """
        #ST STCplx adk icd fumC gyrB purA recA mdh NumEHEC NumEIEC NumEPEC Numother NumK1 NumShigella
        self.firstSignatureColumn = 2
        self.lastSignatureColumn = 8
        L = VertexLabeling()
        signature_len = self.lastSignatureColumn - self.firstSignatureColumn
        
        file = open(fileName, 'r')
        line = file.readline() # Eat first line
        while 1:
            line = file.readline()
            if not line:
                break
            s = string.split(line[:-2],"\t") # Assume Windows end of line convention
            v = self.G.AddVertex()
            self.ST[v] = int(s[0])
            self.STComplex[v] = s[1]
            self.signature[v] = map(int,s[self.firstSignatureColumn:self.lastSignatureColumn])
            L[v] = "%s" % v
            
            #print v,self.ST[v],self.STComplex[v],self.signature[v]
            
        self.G.labeling = L
        file.close()
        
        
    def addEdges(self):
        signature_len = self.lastSignatureColumn - self.firstSignatureColumn
        self.G.edgeWeights[0] = EdgeWeight(self.G)
        
        for v in self.G.vertices:
            for w in self.G.vertices:
                if v < w: # Undirected Graph
                    d = hamming_distance(self.signature[v],self.signature[w])
                    if d <= signature_len: # At least one allele in common
                        self.G.AddEdge(v,w)
                        self.G.edgeWeights[0][(v,w)] = d
                        
    def computeMST(self):
        mst_edges = MSTPrim(self.G,1)
        #print mst_edges
        # Remove extra edges
        for e in self.G.Edges():
            if not e in mst_edges and not (e[1],e[0]) in mst_edges:
                self.G.DeleteEdge(e[0],e[1])
                
    def computeEmbedding(self):
        # NOTE: Need edges first 
    
        root = None
        rootDegree = 0
        for v in self.G.vertices:
            if self.G.Degree(v) > rootDegree:
                rootDegree = self.G.Degree(v)
                root = v
                
                #Embedder.RandomCoords(self.G)
        E = VertexLabeling()   
        Embedder.BFSRadialTreeCoords(self.G, v, 'forward')
        # This sets the G.xCoord[v], G.yCoord[v]) which we have to copy to the embedding
        for v in self.G.vertices:
            E[v] = Point2D(self.G.xCoord[v], self.G.yCoord[v])
        self.G.embedding = E
        
        
        
        
        
        
class GredSplashScreen(GatoDialogs.SplashScreen):

    def CreateWidgets(self):
        self.Icon = PhotoImage(data=GatoIcons.gred)
        self.label = Label(self, image=self.Icon)
        self.label.pack(side=TOP)
        self.label = Label(self, text=GatoDialogs.crnotice1)
        self.label.pack(side=TOP)
        label = Label(self, font="Helvetica 10", text=GatoDialogs.crnotice2, justify=CENTER)
        label.pack(side=TOP)
        
class GredAboutBox(GatoDialogs.AboutBox):

    def body(self, master):
        self.resizable(0,0)
        self.catIconImage = PhotoImage(data=GatoIcons.gred)
        self.catIcon = Label(master, image=self.catIconImage)
        self.catIcon.pack(side=TOP)
        label = Label(master, text=GatoDialogs.crnotice1)
        label.pack(side=TOP)
        label = Label(master, font="Helvetica 10", 
                      text=GatoDialogs.crnotice2, justify=CENTER)
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
        self.infoText.insert('0.0', GatoGlobals.gLGPLText)	
        self.infoText.configure(state=DISABLED)
        self.title("Gred - About")
        
        
        
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
        #self.SetGraphMenuOptions()
        Splash.Destroy()
        # Fix focus and stacking
        if os.name == 'nt' or os.name == 'dos':
            self.master.tkraise()
            self.master.focus_force()
        else:
            self.tkraise()
            
    def ReadConfiguration(self):
        self.gVertexRadius = 3
        
        self.gFontFamily = "Helvetica"
        self.gFontSize = 4
        self.gFontStyle = tkFont.NORMAL
        
        self.gEdgeWidth = 2
        
        self.gVertexFrameWidth = 2
        self.cVertexDefault = "red"
        self.cVertexBlink = "black"
        self.cEdgeDefault = "black"
        self.cLabelDefault = "black"
        self.cLabelDefaultInverted = "white"
        self.cLabelBlink = "green"
        
        # Used by ramazan's scaling code
        self.zVertexRadius = self.gVertexRadius
        self.zArrowShape = (16, 20, 6)
        self.zFontSize = 10
        
        
        
        
    def SetGraphMenuGrid(self,Grid):
        pass
        
    def SetTitle(self,title):
        self.master.title(title)
        
    def CreateWidgets(self):
    ##	toolbar = Frame(self, cursor='hand2', relief=FLAT)
    ##	toolbar.pack(side=LEFT, fill=Y) # Allows horizontal growth
    
    ##	extra = Frame(toolbar, cursor='hand2', relief=SUNKEN, borderwidth=2)
    ##	extra.pack(side=TOP) # Allows horizontal growth
    ##	extra.rowconfigure(5,weight=1)
    ##	extra.bind("<Enter>", lambda e, gd=self:gd.DefaultInfo())
    
    ##	px = 0 
    ##	py = 3 
    
    ##	self.toolVar = StringVar()
    ##        self.lastTool = None
    
    ##	# Load Icons
    ##        # 0 = "inactive", 1 = "mouse over", 2 = "active"
    ##	self.icons = {
    ##            'AddOrMoveVertex':[PhotoImage(data=GatoIcons.vertex_1),
    ##                               PhotoImage(data=GatoIcons.vertex_2),
    ##                               PhotoImage(data=GatoIcons.vertex_3)],
    ##            'AddEdge':[PhotoImage(data=GatoIcons.edge_1),
    ##                       PhotoImage(data=GatoIcons.edge_2),
    ##                       PhotoImage(data=GatoIcons.edge_3)],
    ##            'DeleteEdgeOrVertex':[PhotoImage(data=GatoIcons.delete_1),
    ##                                  PhotoImage(data=GatoIcons.delete_2),
    ##                                  PhotoImage(data=GatoIcons.delete_3)],
    ##            'SwapOrientation':[PhotoImage(data=GatoIcons.swap_1),
    ##                               PhotoImage(data=GatoIcons.swap_2),
    ##                               PhotoImage(data=GatoIcons.swap_3)],
    ##            'EditWeight':[PhotoImage(data=GatoIcons.edit_1),
    ##                          PhotoImage(data=GatoIcons.edit_2),
    ##                          PhotoImage(data=GatoIcons.edit_3)] }
    ##        self.buttons = {}
    ##	values = ['AddOrMoveVertex','AddEdge','DeleteEdgeOrVertex',
    ##                  'SwapOrientation','EditWeight']
    
    ##        text = {'AddOrMoveVertex':'Add or move vertex','AddEdge':'Add edge',
    ##                'DeleteEdgeOrVertex':'Delete edge or vertex',
    ##                'SwapOrientation':'Swap orientation','EditWeight':'Edit Weight'}
    
    ##        row = 0
    ##        for val in values:
    ##            b = Radiobutton(extra, width=32, padx=px, pady=py, 
    ##                            text=text[val],  
    ##                            command=self.ChangeTool,
    ##                            var = self.toolVar, value=val, 
    ##                            indicator=0, image=self.icons[val][0],
    ##                            selectcolor="#AFAFAF",)
    ##            b.grid(row=row, column=0, padx=2, pady=2)
    ##            self.buttons[val] = b
    ##            b.bind("<Enter>", lambda e,gd=self:gd.EnterButtonCallback(e))
    ##            b.bind("<Leave>", lambda e,gd=self:gd.LeaveButtonCallback(e))
    ##            row += 1
    
    ##        self.defaultButton = self.buttons['AddOrMoveVertex']
        # default doesnt work as config option           
        GraphEditor.CreateWidgets(self)
        
    def EnterButtonCallback(self,e):
        w = e.widget
        text = string.join(w.config("text")[4])
        self.UpdateInfo(text)
        value = w.config("value")[4]
        w.configure(image=self.icons[value][1])
        
    def LeaveButtonCallback(self,e):
        self.UpdateInfo("")
        w = e.widget
        value = w.config("value")[4]
        if self.toolVar.get() == value: # the button we are leaving is depressed
            w.configure(image=self.icons[value][2])
        else:
            w.configure(image=self.icons[value][0])        
            
    def makeMenuBar(self, toplevel=0):
        self.menubar = Menu(self,tearoff=0)
        
        # Add file menu
        self.fileMenu = Menu(self.menubar, tearoff=0)
        #self.fileMenu.add_command(label='New',            command=self.NewGraph)
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
        #self.graphMenu = Menu(self.menubar, tearoff=0)
        #self.directedVar = IntVar()
        #self.graphMenu.add_checkbutton(label='Directed',  
        #			       command=self.graphDirected,
        #			       var = self.directedVar)
        #self.euclideanVar = IntVar()
        #self.graphMenu.add_checkbutton(label='Euclidean', 
        #			       command=self.graphEuclidean,
        #			       var = self.euclideanVar)
        #self.graphMenu.add_separator()
        
        # vertex weigths
        #self.vertexIntegerWeightsVar = IntVar()
        #self.graphMenu.add_checkbutton(label='Integer Vertex Weights', 
        #			       command=self.vertexIntegerWeights,
        #			       var = self.vertexIntegerWeightsVar)
        #
        #self.vertexWeightsSubmenu = Menu(self.graphMenu, tearoff=0)
        #self.vertexWeightVar = IntVar()
        #self.vertexWeightsSubmenu.add_radiobutton(label="None", 
        #				    command=self.ChangeVertexWeights,
        #				    var = self.vertexWeightVar, value=0)
        #self.vertexWeightsSubmenu.add_radiobutton(label="One", 
        #				    command=self.ChangeVertexWeights,
        #				    var = self.vertexWeightVar, value=1)
        #self.vertexWeightsSubmenu.add_radiobutton(label="Two", 
        #				    command=self.ChangeVertexWeights,
        #				    var = self.vertexWeightVar, value=2)
        #self.vertexWeightsSubmenu.add_radiobutton(label="Three", 
        #				    command=self.ChangeVertexWeights,
        #				    var = self.vertexWeightVar, value=3)
        #self.graphMenu.add_cascade(label='Vertex Weights', 
        #			   menu=self.vertexWeightsSubmenu)
        
        
        
        # edge weigths
        #self.edgeIntegerWeightsVar = IntVar()
        #self.graphMenu.add_checkbutton(label='Integer Edge Weights', 
        #			       command=self.edgeIntegerWeights,
        #			       var = self.edgeIntegerWeightsVar)
        #
        #self.edgeWeightsSubmenu = Menu(self.graphMenu, tearoff=0)
        #self.edgeWeightVar = IntVar()
        #self.edgeWeightsSubmenu.add_radiobutton(label="One", 
        #				    command=self.ChangeEdgeWeights,
        #				    var = self.edgeWeightVar, value=1)
        #self.edgeWeightsSubmenu.add_radiobutton(label="Two", 
        #				    command=self.ChangeEdgeWeights,
        #				    var = self.edgeWeightVar, value=2)
        #self.edgeWeightsSubmenu.add_radiobutton(label="Three", 
        #				    command=self.ChangeEdgeWeights,
        #				    var = self.edgeWeightVar, value=3)
        #self.graphMenu.add_cascade(label='Edge Weights', 
        #			   menu=self.edgeWeightsSubmenu)
        #
        #
        #
        #self.graphMenu.add_separator()
        #self.graphMenu.add_checkbutton(label='Grid', 
        #					  command=self.ToggleGridding)	
        #self.menubar.add_cascade(label="Graph", menu=self.graphMenu, 
        #			 underline=0)
        
        
        # Add Tools menu
        # 	self.toolsMenu = Menu(self.menubar,tearoff=1)
        # 	self.toolVar = StringVar()
        # 	self.toolsMenu.add_radiobutton(label='Add or move vertex',  
        # 				       command=self.ChangeTool,
        # 				       var = self.toolVar, value='AddOrMoveVertex')
        # 	self.toolsMenu.add_radiobutton(label='Add edge', 
        # 				       command=self.ChangeTool,
        # 				       var = self.toolVar, value='AddEdge')
        # 	self.toolsMenu.add_radiobutton(label='Delete edge or vertex', 
        # 				       command=self.ChangeTool,
        # 				       var = self.toolVar, value='DeleteEdgeOrVertex')
        # 	self.toolsMenu.add_radiobutton(label='Swap orientation', 
        # 				       command=self.ChangeTool,
        # 				       var = self.toolVar, value='SwapOrientation')
        # 	self.toolsMenu.add_radiobutton(label='Edit Weight', 
        # 					command=self.ChangeTool,
        # 				       var = self.toolVar, value='EditWeight')
        # 	self.menubar.add_cascade(label="Tools", menu=self.toolsMenu, 
        # 				 underline=0)
        
        if toplevel:
            self.configure(menu=self.menubar)
        else:
            self.master.configure(menu=self.menubar)
            
            # Add extras menu
        self.extrasMenu = Menu(self.menubar, tearoff=0)
        
        # --------------------------------------------------------------
        # Add a menue item for all creators found in GraphCreator.creator
        #for create in GraphCreator.creator:
        #
        #    self.extrasMenu.add_command(label=create.Name(),
        #				command=lambda e=create,s=self:e.Create(s))
        # --------------------------------------------------------------
        
        # --------------------------------------------------------------
        # Add a menue item for all embedders found in Embedder.embedder
        self.extrasMenu.add_separator()
        for embed in Embedder.embedder:
        
            self.extrasMenu.add_command(label=embed.Name(),
                                        command=lambda e=embed,s=self:e.Embed(s))
            # --------------------------------------------------------------
            
            # --------------------------------------------------------------
        self.extrasMenu.add_separator()
        
        #self.extrasMenu.add_command(label='Randomize Edge Weights',
        #			  command=self.RandomizeEdgeWeights)
        self.menubar.add_cascade(label="Extras", menu=self.extrasMenu, 
                                 underline=0)
        # --------------------------------------------------------------
        
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
            
            ##    def NewGraph(self, Directed=1, Euclidean=1, IntegerVertexWeights=0, VertexWeights='None',
            ##		 IntegerEdgeWeights=0, EdgeWeights='One', Grid=1):
            ##	G=None
            ##	self.SetGraphMenuDirected(Directed)
            ##	self.SetGraphMenuEuclidean(Euclidean)
            ##	self.SetGraphMenuIntegerVertexWeights(IntegerVertexWeights)
            ##	self.SetGraphMenuVertexWeights(VertexWeights)
            ##	self.SetGraphMenuIntegerEdgeWeights(IntegerEdgeWeights)
            ##	self.SetGraphMenuEdgeWeights(EdgeWeights)
            ##	self.SetGraphMenuGrid(Grid)
            ##	self.defaultButton.select()
            
            ##	G = Graph()
            ##	G.directed = Directed
            ##	G.euclidian = Euclidean
            ##	self.graphName = "New"
            ##	self.ShowGraph(G,self.graphName)
            ##	self.RegisterGraphInformer(WeightedGraphInformer(G,"weight"))
            ##	self.fileName = None
            ##	self.SetTitle("Gred _VERSION_ - New Graph")
            
    def OpenGraph(self):	
        file = askopenfilename(title="Open Graph",
                               defaultextension=".txt",
                               filetypes = [  ("Cluster", ".txt")
                                             #,("GML", ".gml")
                                             #,("Graphlet", ".let")
                                           ]
                               )
        if file is "": 
            pass
        else:
            self.fileName = file
            self.dirty = 0
            self.graphName = stripPath(file)
            e = extension(file)
            if e == 'txt':
                self.cluster = AlleleVariationCluster(self.fileName)
            else:
                log.error("Unknown extension %s" % e)
                
            G = self.cluster.G
            
            ##	    if not self.gridding:
            ##		self.graphMenu.invoke(self.graphMenu.index('Grid'))	
            
            ##	    if G.QDirected() != self.directedVar.get():
            ##		self.graphMenu.invoke(self.graphMenu.index('Directed'))	
            
            ##	    if G.QEuclidian() != self.euclideanVar.get():
            ##		self.graphMenu.invoke(self.graphMenu.index('Euclidean'))	
            
            ##	    if G.edgeWeights[0].QInteger() != self.edgeIntegerWeightsVar.get():
            ##		self.graphMenu.invoke(self.graphMenu.index('Integer Edge Weights'))
            ##		self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights')) 
            ##		# Just one integer flag for vertex and edge weights 
            
            ##	    if G.NrOfEdgeWeights() == 1:
            ##	    	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('One'))
            ##	    elif G.NrOfEdgeWeights() == 2:
            ##	    	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('Two'))
            ##	    elif G.NrOfEdgeWeights() == 3:
            ##	    	self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('Three')) 
            
            ##	    if G.NrOfVertexWeights() == 0 or (G.NrOfVertexWeights() > 0 and 
            ##					      G.vertexWeights[0].QInteger()):
            ##		self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights'))
            
            
            ##	    if G.NrOfVertexWeights() == 0:
            ##	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('None'))
            ##	    elif G.NrOfVertexWeights() == 1:
            ##	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('One'))
            ##	    elif G.NrOfVertexWeights() == 2:
            ##	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('Two'))
            ##	    elif G.NrOfVertexWeights() == 3:
            ##	    	self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('Three'))
            
            
            
            self.RegisterGraphInformer(WeightedGraphInformer(G,"weight"))
            self.ShowGraph(G,self.graphName)
            self.SetTitle("Gred _VERSION_ - " + self.graphName)
            
            
            
    def SaveGraph(self):
        #self.dirty = 0
        if self.fileName != None:
            SaveCATBoxGraph(self.G,self.fileName)
        else:
            self.SaveAsGraph()
            
    def SaveAsGraph(self):
        file = asksaveasfilename(title="Save Graph",
                                 defaultextension=".cat",
                                 filetypes = [  ("Gato", ".cat")
                                               #,("Graphlet", ".let")
                                             ]
                                 )
        if file is not "":
            self.fileName = file
            self.dirty = 0
            SaveCATBoxGraph(self.G,file)
            self.graphName = stripPath(file)
            self.SetTitle("Gred _VERSION_ - " + self.graphName)
            
    def ExportEPSF(self):
        file = asksaveasfilename(title="Export EPSF",
                                 defaultextension=".eps",
                                 filetypes = [  ("Encapsulated PS", ".eps")
                                               ,("Postscript", ".ps")
                                             ]
                                 )
        if file is not "": 
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
        tool = self.toolVar.get()
        if self.lastTool is not None:
            self.buttons[self.lastTool].configure(image=self.icons[self.lastTool][0])
        self.SetEditMode(tool)
        self.lastTool = tool
        self.buttons[tool].configure(image=self.icons[tool][2])
        
        
        #----- Extras Menu callbacks
        
        # NOTE: Embedder handled by lambda passed as command
        
    def RandomizeEdgeWeights(self):
        count = len(self.G.edgeWeights.keys())
        d = RandomizeEdgeWeightsDialog(self, count, self.G.QEuclidian()) 
        if d.result is None:
            return
            
        for e in self.G.Edges():
            for i in xrange(count):
                if d.result[i][0] == 1:
                    val = random.uniform(d.result[i][1],d.result[i][2])
                    if self.G.edgeWeights[i].QInteger():
                        self.G.edgeWeights[i][e] = round(int(val))
                    else:
                        self.G.edgeWeights[i][e] = val
                        
    def AboutBox(self):
        d = GredAboutBox(self.master)
        
        
class SAGraphEditorToplevel(SAGraphEditor, Toplevel):

    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        Splash = GredSplashScreen(self.master)
        self.G = None
        
        self.mode = 'AddOrMoveVertex'
        self.gridding = 0
        self.graphInformer = None
        
        self.makeMenuBar(1)
        GraphEditor.__init__(self)
        self.fileName = None
        self.dirty = 0
        self.SetGraphMenuOptions()
        Splash.Destroy()
        
        # Fix focus and stacking
        self.tkraise()
        self.focus_force()
        
    def ExportEPSF(self):
        file = asksaveasfilename(title="Export EPSF",
                                 defaultextension=".eps",
                                 filetypes = [  ("Encapsulated PS", ".eps")
                                               ,("Postscript", ".ps")
                                             ]
                                 )
        if file is not "": 
            self.PrintToPSFile(file)
        self.tkraise()
        self.focus_force()
        
    def AboutBox(self):
        d = GredAboutBox(self)	
        
    def SetTitle(self,title):
        self.title(title)
        self.tkraise()
        self.focus_force()
        
    def Quit(self):	
        if askokcancel("Quit","Do you really want to quit?"):
            self.destroy()
        else:
            self.tkraise()
            self.focus_force()
            
            
            ################################################################################
if __name__ == '__main__':

    # Overide default colors for widgets ... maybe shouldnt be doing that for Windows?
    import logging
    logging.verbose = 1
    log = logging.getLogger("ViewClusterGraph.py")
    tk = Tk()
    tk.option_add('*ActiveBackground','#EEEEEE')
    tk.option_add('*background','#DDDDDD')
    tk.option_add('Tk*Scrollbar.troughColor','#CACACA')
    graphEditor = SAGraphEditor(tk)
    graphEditor.OpenGraph()
    graphEditor.mainloop()
    
