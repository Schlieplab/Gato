################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   Embedder.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################


class Embedder:
    """ This class provides an abstract Embedder as
        a base for actual Embedder implementations """
    
    def Name(self):
	""" Return a short descriptive name for the embedder e.g. usable as 
	    a menu item """
	return "none"

    def Embed(self, theGraphEditor):
	""" Compute the Embedding. Changed display through theGraphEditor.
            Return value != none designates error/warning message """
	return none


#----------------------------------------------------------------------
import whrandom

class RandomEmbedder(Embedder):

    def Name(self):
	return "Randomize Layout"
    
    def Embed(self, theGraphEditor):
	for v in theGraphEditor.G.vertices:
	    theGraphEditor.MoveVertex(v, 
				      whrandom.randint(10,990),
				      whrandom.randint(10,990), 
				      1)
#----------------------------------------------------------------------

from math import pi, sin, cos

class CircularEmbedder(Embedder):

    def Name(self):
	return "Circular Layout"
    
    def Embed(self, theGraphEditor):
        if theGraphEditor.G.Order()!=0: 
            distance = 2*pi/theGraphEditor.G.Order()
            degree = 0
            xMiddle=500; yMiddle=500; radius=450
            for v in theGraphEditor.G.vertices:
                xCoord=radius*cos(degree)+xMiddle
                yCoord=radius*sin(degree)+yMiddle
                theGraphEditor.MoveVertex(v,xCoord,yCoord,1)
                degree=degree+distance
#----------------------------------------------------------------------


""" Here instantiate all the embedders you want to make available to
    a client. """
embedder = [RandomEmbedder(), CircularEmbedder()]
