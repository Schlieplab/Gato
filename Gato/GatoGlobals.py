################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GatoGlobals.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
#
################################################################################

# Globals
gVertexRadius     = 12  
gVertexFrameWidth      =  2     
gEdgeWidth        =  3     
gBlinkRate        = 50      # ms 100
gBlinkRepeat      =  4      # One more than you want 4

gPaperHeight      = 1500 # "20i" XXX Should be real paper size
gPaperWidth       = 1500 # "20i"

gInteractive      = 1
gGridSize         = 50 # Grid size for editor

gInfinity         = 9999999

# Internal Color Names
cVertexDefault    = "red"
cVertexBlink      = "black"
cEdgeDefault      = "black"
cLabelDefault     = "black"
cLabelBlink       = "green"

cInitial          = "green"
cVisited          = "grey"
#cOnQueue          = "red"
#cRemovedFromQueue = "blue"
cOnQueue          = "blue"
cRemovedFromQueue = "grey"
cTraversedEdge    = "grey"

gColors = ['#202020','#502020','#802020','#B02020',
	  '#205020','#505020','#805020','#B05020',
	  '#208020','#508020','#808020','#B08020',
	  '#20B020','#50B020','#80B020','#B0B020',
	  '#202050','#502050','#802050','#B02050',
	  '#205050','#505050','#805050','#B05050',
	  '#208050','#508050','#808050','#B08050',
	  '#20B050','#50B050','#80B050','#B0B050',
	  '#2020B0','#5020B0','#8020B0','#B020B0',
	  '#2050B0','#5050B0','#8050B0','#B050B0',
	  '#2080B0','#5080B0','#8080B0','#B080B0',
	  '#20B0B0','#50B0B0','#80B0B0','#B0B0B0']
	  

# Exceptions
GraphNotSimpleError = 'GraphNotSimpleError'
NoSuchVertexError   = 'NoSuchVertexError'
NoSuchEdgeError     = 'NoSuchEdgeError'

#             property     explanation
gProperty = {'Connected': 'has more than one connected component',
	     'Directed':  'edges are not directed'
	     }



