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


""" Here instantiate all the embedders you want to make available to
    a client. """
embedder = [RandomEmbedder()]
