################################################################################
#
#       This is part of Gato (Graph Algorithm Toolbox) 
#       You can find more information at 
#       http://gato.sf.net
#
#	file:   BFS.pro
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2006, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schliep.org, winfried.hochstaettler@fernuni-hagen.de             
#
#       Information: http://gato.sf.net
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
self.NeededProperties({'Simple':0})

pickCallback = lambda v, a=A: A.SetVertexAnnotation(v,"source")
PickVertex   = lambda f=pickCallback: self.PickVertex(1,None,f)
Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v)
Vertices     = G.vertices          
visited      = AnimatedVertexLabeling(A)    
Q            = AnimatedVertexQueue(A)

# End-of BFS.pro
