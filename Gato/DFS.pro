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

PickVertex = self.PickVertex
A = self.GUI.graphDisplay
Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v)
Vertices = G.vertices          
visited = AnimatedVertexLabeling(A)    
Q = AnimatedVertexQueue(A)
S = AnimatedVertexStack(A)
