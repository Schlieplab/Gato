################################################################################
#
#       This is part of CATBox (Combinatorial Algorithm Toolbox)
#       version _VERSION_ from _BUILDDATE_. You can find more information at
#       http://www.zpr.uni-koeln.de/CATBox
#
#	file:   PreflowPush.pro
#	author: Torsten Pattberg (pattberg@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
#
################################################################################

import visual

#### Options #################################################

breakpoints = [9,29]
interactive = [1,2]
graphDisplays = 2
about = """<HTML>
<HEAD>
<TITLE>Maximal Flow - Preflow Push</TITLE>
</HEAD>
<BODY>

This algorithm finds a maximal flow in a directed graph. 

</BODY></HTML>
"""

from math import *

True            = 1
False           = 0
OldExcessVertex = 1

#### Graph management ########################################

import copy
R  = copy.deepcopy(G)

self.OpenSecondaryGraph(R,stripPath(self.graphFileName)+" (residual network)")

RA = self.GUI.secondaryGraphDisplay
G.CalculateWidthFromWeight(0.7)
A.ShowGraph(G, stripPath(self.graphFileName))

#### Wrapper #################################################

def InitPotential(s,t):
    (dist, dummy) = BFS(G,t,'backward')
    for v in G.vertices:
        pot[v] = dist[v]
    pot[s] = G.Order()

#### Internal functions ######################################

def FindExcessVertex():
    global OldExcessVertex

    RA.SetAllEdgesColor("black")
    maxpot  = 0
    maxpotv = None

    for v in Vertices():
	if (v != s) and (v != t):
	    if excess(v) > 0:
		if pot[v] > maxpot:
		    maxpot  = pot[v]
                    maxpotv = v
		#A.SetVertexAnnotation(v,"e")
	    else:
		A.SetVertexAnnotation(v,"")
		pass

    if maxpotv:
        RA.SetVertexFrameWidth(OldExcessVertex,2)
        RA.SetVertexFrameWidth(maxpotv,6)
        OldExcessVertex = maxpotv
                
    return maxpotv

def _ShowCut(A,R,s):
    Q = Queue() # Component S of s is green, component T of t is red 
    C = [s]     # edges between S and T are yellow

    pred = {}
    for v in R.vertices:
	pred[v] = None	
    Q.Append(s)

    while Q.IsNotEmpty():
	v = Q.Top()
	for w in R.Neighborhood(v):
	    if pred[w] == None and w != s:
		pred[w] = v
		Q.Append(w)
		C.append(w)

    #A.SetAllVerticesColor("red")

    for v in C:
        #A.SetVertexColor(v,"green")
	for w in G.Neighborhood(v):
	    if not w in C:
		A.SetEdgeColor(v,w,"yellow")

    return None

def Min(a,b):

    minimum = a
    if b < a:
        minimum = b

    RA.graphInformer.SetDefaultInfo("delta = %d"%minimum)
    RA.UpdateInfo("delta = %d"%minimum)

    return minimum

def _minResNeighborPot(v,R,RA):

    RA.BlinkVertex(v)

    minimum = gInfinity

    for u in R.Neighborhood(v):
	if minimum > pot[u]:
            minimum = pot[u]

    return minimum

#### Lambdas #################################################

Neighborhood          = lambda v, ra=RA, r=R: AnimatedNeighborhood(ra,r,v)
Vertices              = lambda g=G: g.vertices
Order                 = lambda g=G: g.Order()
ShowCut               = lambda s,a=A,r=R: _ShowCut(a,r,s)
minResNeighborPot     = lambda v,r=R,ra=RA: _minResNeighborPot(v,r,ra)
ForwardEdge           = lambda u,v,g=G: g.QEdge(u,v)

#### Variables ###############################################

class AnimatedPotential3D:
    """ Visualizes the potential from 0 (green) to
         max (brown) of a vertex. """
    def __init__(self,max,theAnimator1,theAnimator2=None):
        self.pot      = {}
        self.max      = max
        self.colors   = ['#00FF00','#11EE00','#22DD00','#33CC00','#44BB00',
                         '#55AA00','#669900','#778800','#887700','#996600',
                         '#AA5500','#BB4400','#CC3300']
        self.Animator1 = theAnimator1
	if theAnimator2 == None:
            self.Animator2 = theAnimator1
	else:
            self.Animator2 = theAnimator2 

    def __setitem__(self,v,val):
        self.pot[v] = val
        if val == gInfinity:
            self.Animator2.SetVertexAnnotation(v,"Inf")
        elif val == -gInfinity:
            self.Animator2.SetVertexAnnotation(v,"-Inf")
        else:
            self.Animator2.SetVertexAnnotation(v,"%d"%val)
	if val > self.max:
            val = self.max
        self.Animator1.SetVertexColor(v,self.colors[(val*(len(self.colors)-1))/self.max])
	(x,y,oldz) = self.Animator1.VertexPosition(v)
	z = oldz
	while z < val * 8:
	    z += 0.05
	    self.Animator1.MoveVertex(v, x, y, z)

    def __getitem__(self,v):
        return self.pot[v]




def pickCallback(A,RA,v,type):

    if type == "s":
        A.SetVertexAnnotation(v,type,"green")
        flow.excess[v] = gInfinity        
        RA.SetVertexColor(v,"green")
    else:
        A.SetVertexAnnotation(v,type,"red")
        flow.excess[v] = -gInfinity
        RA.SetVertexColor(v,"red")
    return


flow   = FlowWrapper(G,A,R,RA,G.edgeWeights[0],R.edgeWeights[0])
flow.zeroEdgeColor = "white"
cap         = lambda e: flow.cap[e]
res         = lambda e: flow.res[e]
excess      = lambda v: flow.excess[v]
pot         = AnimatedPotential3D(2*G.Order()-1,A,RA)

pickCallbackSource = lambda v, type="s", a=A,ra=RA: pickCallback(a,ra,v,type)
PickSource         = lambda f=pickCallbackSource: self.PickVertex(1,None,f)
pickCallbackSink   = lambda v, type="t", a=A,ra=RA: pickCallback(a,ra,v,type)
PickSink           = lambda f=pickCallbackSink: self.PickVertex(G.Order(),None,f)

#### Internal initialisation #################################

RA.SetAllVerticesColor("grey")

A.RegisterGraphInformer(FlowGraphInformer(G,flow))
RA.RegisterGraphInformer(ResidualGraphInformer(R,flow))

