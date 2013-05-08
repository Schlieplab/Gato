################################################################################
#
#       This is part of CATBox (Combinatorial Algorithm Toolbox)
#       version 1.1 from 4/10/2011. You can find more information at
#       http://schliep.org/CATBox/
#
#	file:   DFS.pro
#	author: Torsten Pattberg (torsten.pattberg@klf.de)
#               Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2011, Winfried Hochstaettler and Alexander Schliep.
#	(C) 2010 Springer Verlag.
#       
#	This is part of the Springer textbook "CATBox - an interactive course in 
#       discrete optimization".
#
#       All rights reserved. Do not distribute without written permission. 
#




#
#       This file is version $Revision$
#                       from $Date$
#             last change by $Author$.
#
#
################################################################################

# Options ----------------------------------------------------------------------
breakpoints = [6]
interactive = [1]
graphDisplays = 1
about = """<HTML>
<HEAD>
<TITLE>Depth-First-Search Traversal</TITLE>
</HEAD>
<BODY>

<H1>Depth-First-Search (DFS) Traversal</H1>

This algorithm traverses a graph in depth-first order and visualizes
the predecessor tree being built and the DFS vertex labels. See
Chapter 2 in the CATBox book. Non-recursive implementation.

<H3>Visualization</H3>

<H5>Vertex Colors</H5>
<dl>
<dt><colordef color="#EEEEEE"></dt> <dd>Initial color for vertices that
have neither been <em>visited</em> nor <em>processed</em>.</dd>

<dt><colordef color="blue"></dt> <dd>Vertices which have been
<em>visited</em> as a neighbor while <em>processing</em> the
<em>active</em> vertex.</dd>

<dt><colordef color="red"></dt> <dd>Vertices of this color have
been <em>processed</em>; i.e.,
their neighbors have been explored.</dd>

<dt><colordef color="black"></dt> <dd>The vertex being <em>processed</em> is
displayed with a wide outline in this color.</dd>

</dl>


<H5>Edge Colors</H5>
<dl>
<dt><colordef color="#EEEEEE"></dt> <dd>Initial color for edges. Edges
of this color have not been <em>traversed</em> yet.</dd>

<dt><colordef color="yellow"></dt> <dd>Color of the edge being <em>traversed</em>.</dd>

<dt><colordef color="#EE9900"></dt> <dd>A traversed edge for which the label
of the head has not been set yet. Upon setting of the label the color
will change to  <colordef color="red">.</dd>

<dt><colordef color="red"></dt> <dd>Traversed edges displayed in the color are
part of the DFS tree.</dd>

<dt><colordef color="grey"></dt> <dd>Color of edges traversed
which are not part of the DFS tree.</dd>


</dl>

<H5>Further elements</H5>

<dl>

<dt><colordef color="black"></dt> <dd>The DFS label assigned to
visited vertices is displayed in this color.</dd>

</dl>

</BODY></HTML>
"""
#--------------------------------------------------------------------------------
class BlinkVisibleVertexLabeling(VisibleVertexLabeling):
    def __init__(self, A, pred):
        self.pred = pred
        VisibleVertexLabeling.__init__(self, A)

    def __getitem__(self, v):
        self.A.BlinkVertex(v)
        return VisibleVertexLabeling.__getitem__(self,v)

    def __setitem__(self, v, val):
        VisibleVertexLabeling.__setitem__(self, v, val)
        if not val is None and pred[v] != v:
            self.A.SetEdgeColor(pred[v],v,'red')

    def get(self, v):
        """ So that reading the label in the graph informer will not blink the vertex"""
        return VisibleVertexLabeling.__getitem__(self,v)
   
PickVertex = lambda : self.PickVertex(1,None)
pred = AnimatedPredecessor(A, predColor='#EE9900')
label = BlinkVisibleVertexLabeling(A,pred)
Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v,['#EE9900','red'])
S = AnimatedVertexStack(A,"blue","red")

class MyGraphInformer(GraphInformer):

    def __init__(self, G, label):
	GraphInformer.__init__(self, G)
        self.label = label

    def VertexInfo(self,v):
	if self.label.get(v):
	    return "Vertex %d - label %d - pred %d"%(v,self.label.get(v),pred[v])
	elif v in S.contents:
            return "Vertex %d - Stack position %d"%(v,len(S.contents)-S.contents.index(v))
	else:
            return "Vertex %d - not visited yet"%v
        return

A.SetAllVerticesColor("#EEEEEE")

for v in G.vertices:
    label[v] = None
    pred[v]  = None

A.RegisterGraphInformer(MyGraphInformer(G, label))
