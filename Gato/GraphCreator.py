################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GraphCreator.py
#	author: Ramazan Buzdemir
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
def DrawNewNodes(theGraphEditor,result):
    n=result[0] # number of nodes

    theGraphEditor.NewGraph(result[2],1,0,'None',0,'One',0)

    for i in range(0,n):
	theGraphEditor.AddVertex(whrandom.randint(10,990),
				 whrandom.randint(10,990))

def CompleteEdges(theGraphEditor,result):
    Edges=[]
    n=result[0]

    for i in range(0,n):
	source=theGraphEditor.G.vertices[i]
	for j in range(i+1,n):   
	    target=theGraphEditor.G.vertices[j]
	    Edges.append((source,target))
	    if result[2]: Edges.append((target,source))
    return Edges

def MaximalPlanarEdges(theGraphEditor,result):
    n=result[0]

    Edges=[] #6*n
    AdjEdges={}
    for v in theGraphEditor.G.vertices:
        AdjEdges[v]=[]

    index=0
    a=theGraphEditor.G.vertices[index]
    index=index+1
    b=theGraphEditor.G.vertices[index]
    index=index+1
    
    Edges.append((a,b))
    AdjEdges[a].append((a,b))
    Edges.append((b,a))
    AdjEdges[b].append((b,a))

    m=2
    while index < n:
        e=Edges[whrandom.randint(0,m-1)]
        v=theGraphEditor.G.vertices[index]
        index=index+1

        while e[1]!=v:
            x=(v,e[0])
            Edges.append(x)
            m=m+1
            AdjEdges[v].append(x)

            y=(e[0],v)
            Edges.append(y)
            m=m+1
            AdjEdges[e[0]].insert(AdjEdges[e[0]].index(e)+1,y)

            index2=AdjEdges[e[1]].index((e[1],e[0]))
            if index2==0:
                e=AdjEdges[e[1]][-1]
            else:
                e=AdjEdges[e[1]][index2-1]

    if result[2]==0: # undirected
        m=m-1
        while m>0:
          del Edges[m]
          m=m-2
          
    return Edges

#----------------------------------------------------------------------
class completeGraphCreator(Creator):

    def Name(self):
	return "create complete Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 0, 0, "create complete Graph")
        if dial.result is None:
            return

	DrawNewNodes(theGraphEditor,dial.result)
	Edges=CompleteEdges(theGraphEditor,dial.result)

	for e in Edges:
	    theGraphEditor.AddEdge(e[0],e[1])

#----------------------------------------------------------------------
class randomGraphCreator(Creator):

    def Name(self):
	return "create random Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 0, 1, "create random Graph")
        if dial.result is None:
            return

	DrawNewNodes(theGraphEditor,dial.result)
	Edges=CompleteEdges(theGraphEditor,dial.result)

	m=dial.result[1] # number of edges
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

	DrawNewNodes(theGraphEditor,dial.result)
        if dial.result[0]>1:
            Edges=MaximalPlanarEdges(theGraphEditor,dial.result)
            for e in Edges:
                theGraphEditor.AddEdge(e[0],e[1])

#----------------------------------------------------------------------
class randomPlanarGraphCreator(Creator):

    def Name(self):
        return "create random planar Graph" 
    
    def Create(self, theGraphEditor):
        dial = Dialog(theGraphEditor, 1, 1, "create random planar Graph")
        if dial.result is None:
            return

	DrawNewNodes(theGraphEditor,dial.result)

        if dial.result[0]>1:
            Edges=MaximalPlanarEdges(theGraphEditor,dial.result)
            m=dial.result[1] # number of edges
            for i in range(0,m):
                pos=whrandom.randint(0,len(Edges)-1)
                theGraphEditor.AddEdge(Edges[pos][0],Edges[pos][1])
                del Edges[pos]
        
#----------------------------------------------------------------------


""" Here instantiate all the creators you want to make available to
    a client. """
creator = [completeGraphCreator(), randomGraphCreator(),
           maximalPlanarGraphCreator(), randomPlanarGraphCreator()]
