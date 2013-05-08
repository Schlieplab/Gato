################################################################################
#
#       This is part of CATBox (Combinatorial Algorithm Toolbox)
#       version 1.1 from 4/10/2011. You can find more information at
#       http://schliep.org/CATBox/
#
#	file:   BFS.pro
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
about = """
<HTML>
<HEAD>
<TITLE>Breadth-First-Search (BFS) Traversal</TITLE>
</HEAD>
<BODY>

<H1>Breadth-First-Search (BFS) Traversal</H1>

This algorithm traverses a graph in breadth-first order and visualizes
the predecessor tree being built and the BFS vertex labels. See
Chapter 2 in the CATBox book.

<H3>Visualization</H3>

<H5>Vertex Colors</H5>
<dl>
<dt><colordef color="#EEEEEE"></dt> <dd>Initial color for vertices that
have neither been <em>visited</em> nor <em>processed</em>.</dd>

<dt><colordef color="blue"></dt> <dd>Vertices which have been
<em>visited</em> as a neighbor while <em>processing</em> the
<em>active</em> vertex.</dd>

<dt><colordef color="red"></dt> <dd>Vertices of this color have been <em>processed</em>; i.e.,
their neighbors have been explored.</dd>

<dt><colordef color="black"></dt> <dd>The vertex being <em>processed</em> is
displayed with a wide outline in this color.</dd>

</dl>


<H5>Edge Colors</H5>
<dl>
<dt><colordef color="#EEEEEE"></dt> <dd>Initial color for edges. Edges
of this color have not been <em>traversed</em> yet.</dd>

<dt><colordef color="yellow"></dt> <dd>Color of the edge being <em>traversed</em>.</dd>

<dt><colordef color="red"></dt> <dd>Traversed edges displayed in the color are
part of the BFS tree.</dd>

<dt><colordef color="grey"></dt> <dd>Color of edges traversed
which are not part of the BFS tree.</dd>


</dl>

<H5>Further elements</H5> <dl> <dt><colordef color="black"></dt>
<dd>The BFS label assigned to visited vertices is displayed in this color.</dd> </dl>

</BODY></HTML>
"""
#--------------------------------------------------------------------------------

PickVertex   = lambda : self.PickVertex(1,None)
label        = VisibleVertexLabeling(A)
pred         = AnimatedPredecessor(A)
Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v,["red"])
Q            = AnimatedVertexQueue(A,"blue","red")

class MyGraphInformer(GraphInformer):

    def VertexInfo(self,v):
	if label[v]:
	    return "Vertex %d - label %d - pred %d"%(v,label[v],pred[v])
	elif v in Q.contents:
            return "Vertex %d - Queue position %d"%(v,Q.contents.index(v)+1)
	else:
            return "Vertex %d - not visited yet"%v
        return

A.SetAllVerticesColor("#EEEEEE")
for v in G.vertices:
    label[v] = None
    pred[v]  = None

A.RegisterGraphInformer(MyGraphInformer(G))
