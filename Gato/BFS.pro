################################################################################
#
#       This is part of CATBox (Combinatorial Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/CATBox
#
#	file:   CATBox.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################

# Options ----------------------------------------------------------------------
breakpoints = [9]
interactive = [4]
graphDisplays = 1
about = """<HTML>
<HEAD>
<TITLE>Breadth-First-Search</TITLE>
</HEAD>
<BODY>

This algorithm traverses a graph in breadth-first
order.

</BODY></HTML>
"""
#--------------------------------------------------------------------------------
#self.NeededProperties({'pMist':1})

pickCallback = lambda v, a=A: A.SetVertexAnnotation(v,"source")
PickVertex   = lambda f=pickCallback: self.PickVertex(1,None,f)
Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v)
Vertices     = G.vertices          
visited      = AnimatedVertexLabeling(A)    
Q            = AnimatedVertexQueue(A)

# End-of BFS.pro
