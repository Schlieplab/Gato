################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   Creator.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

import whrandom

class Creator:
    """ This class provides an abstract Creator as
        a base for actual Creator implementations """
    
    def Name(self):
	""" Return a short descriptive name for the creator e.g. usable as 
	    a menu item """
	return "none"

    def Create(self, theGraphEditor):
	""" Create a new graph. """
	return none
    
#----------------------------------------------------------------------
from Tkinter import *
import tkSimpleDialog 
import string
from tkMessageBox import showwarning

class Dialog(tkSimpleDialog.Dialog):

    def __init__(self, master, planar, visible, Text):
        self.planar=planar
        self.visible=visible
        tkSimpleDialog.Dialog.__init__(self, master, Text)
        

    def body(self, master):
        self.resizable(0,0)
        
        self.number_of_nodes=StringVar()
        self.number_of_nodes.set("1")
        label = Label(master, text="number of nodes :", anchor=W)
        label.grid(row=0, column=0, padx=4, pady=3, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,
		    textvariable=self.number_of_nodes)
        entry.selection_range(0,1)
        entry.focus_set()
	entry.grid(row=0,column=1, padx=4, pady=3, sticky="w")
	
        self.number_of_edges=StringVar()
        self.number_of_edges.set("0")
        if self.visible:
            label = Label(master, text="number of edges :", anchor=W)
            label.grid(row=1, column=0, padx=4, pady=3, sticky="w")
            entry=Entry(master, width=6, exportselection=FALSE,
                        textvariable=self.number_of_edges)
            entry.selection_range(0,1)
            entry.focus_set()
            entry.grid(row=1,column=1, padx=4, pady=3, sticky="w")
	
        self.direction=IntVar()
        self.direction.set(0)
        radio=Radiobutton(master, text="Undirected", variable=self.direction,
                          value=0)
        radio.grid(row=0, column=2, padx=4, pady=3, sticky="w") 
        radio=Radiobutton(master, text="Directed", variable=self.direction,
                          value=1)
        radio.grid(row=1, column=2, padx=4, pady=3, sticky="w")


    def validate(self):
        try:
            n=string.atoi(self.number_of_nodes.get())
            if n<1 or n>100:
                raise nodeError
        except:
           showwarning("Please try again !",
                       "min. number of nodes = 1\n" 
                       "max. number of nodes = 100")
           return 0            

        try:
            m=string.atoi(self.number_of_edges.get())
            
            if self.planar:
                if n==1: max_m=0
                else: max_m=6*n-12
            else:
                max_m=n*n-n
                
            if self.direction.get()==0:
                max_m = max_m/2
                
            if m<0 or m>max_m:
                raise edgeError
            
        except:
            showwarning("Please try again !",
                        "min. number of edges = 0\n"
                        "max. number of edges = %i" %max_m)
            return 0
        
        self.result=[]
        self.result.append(n)
        self.result.append(m)
        self.result.append(self.direction.get())
        return self.result
    
#----------------------------------------------------------------------

class completeGraphCreator(Creator):

    def Name(self):
	return "create complete Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 0, 0, "create complete Graph")
        if dial.result is None:
            return

        theGraphEditor.NewGraph(dial.result[2],1,0,'None',0,'One',0)

        n=dial.result[0] # number of nodes

        for i in range(0,n):
            theGraphEditor.AddVertex(whrandom.randint(10,990),
				     whrandom.randint(10,990))
            
        if theGraphEditor.G.QDirected()==0: # create a complete undirected Graph
            for i in range(1,n+1):
                for j in range(i+1,n+1): 
                    theGraphEditor.AddEdge(i,j)
        else:                               # create a complete directed Graph
            for i in range(1,n+1):
                for j in range(1,n+1):
                    if j!=i: theGraphEditor.AddEdge(i,j)
#----------------------------------------------------------------------

class randomGraphCreator(Creator):

    def Name(self):
	return "create random Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 0, 1, "create random Graph")
        if dial.result is None:
            return

        theGraphEditor.NewGraph(dial.result[2],1,0,'None',0,'One',0)
 
        n=dial.result[0] # number of nodes
        m=dial.result[1] # number of edges

        for i in range(0,n):
            theGraphEditor.AddVertex(whrandom.randint(10,990),
				     whrandom.randint(10,990))

        Edges=[]
        if theGraphEditor.G.QDirected()==0: # create a random undirected Graph
            for i in range(1,n+1):
                for j in range(i+1,n+1): 
                    Edges.append((i,j))
        else:                               # create a random directed Graph
            for i in range(1,n+1):
                for j in range(1,n+1):
                    if j!=i: Edges.append((i,j))
                    
        for i in range(0,m):
            pos=whrandom.randint(0,len(Edges)-1)
            theGraphEditor.AddEdge(Edges[pos][0],Edges[pos][1])
            del Edges[pos]
#----------------------------------------------------------------------

class maximalPlanarGraphCreator(Creator):

    def Name(self):
	return "create maximal planar Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 1, 0, "create maximal planar Graph")
        if dial.result is None:
            return

        theGraphEditor.NewGraph(dial.result[2],1,0,'None',0,'One',0)
        
        n=dial.result[0] # number of nodes

"""
	#------------------------------------------------------------------#
	# create a maximal planar Graph

	theGraphEditor.AddVertex(whrandom.randint(10,990),
				 whrandom.randint(10,990))
	a=theGraphEditor.G.vertices[0]

	n=n-1
	if n==0: return

	theGraphEditor.AddVertex(whrandom.randint(10,990),
				 whrandom.randint(10,990))
	b=theGraphEditor.G.vertices[1]

	n=n-1

	Edges=[] # 6*n

	Edges.append((a,b))
	Edges.append((b,a))

	m=2

	for i in range(1,n):
	    e=Edges[whrandom.randint(0,m-1)]
	    theGraphEditor.AddVertex(whrandom.randint(10,990),
				     whrandom.randint(10,990))
"""
#----------------------------------------------------------------------

class randomPlanarGraphCreator(Creator):

    def Name(self):
	return "create random planar Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 1, 1, "create random planar Graph")
        if dial.result is None:
            return

#----------------------------------------------------------------------


""" Here instantiate all the creators you want to make available to
    a client. """
creator = [completeGraphCreator(), randomGraphCreator()]
##         maximalPlanarGraphCreator(), randomPlanarGraphCreator()]
