################################################################################
#
#       This is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/Gato
#
#	file:   GatoUtil.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################


def extension(pathAndFile):
    """ Return ext if path/filename.ext is given """
    import regsub
    return regsub.split(stripPath(pathAndFile),"\.")[1]

def stripPath(pathAndFile):
    """ Return filename.ext if path/filename.ext is given """
    import os 
    return os.path.split(pathAndFile)[1]

def orthogonal(u):
    """ Return a unit length vector (v1,v2) which has an angle of
        90 degrees clockwise to the vector u = (u1,u2) """
    from math import sqrt
    (u1,u2) = u
    length = sqrt(u1**2 + u2**2)
    u1 = u1 / length
    u2 = u2 / length
    return (-u2,u1)


def ArgMin(list,val):
    """ Returns the element e of list for which val[e] is minimal """
    if len(list) > 0:
	min     = val[list[0]]
	minElem = list[0]
    for e in list:
	if val[e] < min:
	    min     = val[e]
	    minElem = e
    return minElem


def ArgMax(list,val):
    """ Returns the element e of list for which val[e] is maximal """
    if len(list) > 0:
	max     = val[list[0]]
	maxElem = list[0]
    for e in list:
	if val[e] > max:
	    max     = val[e]
	    maxElem = e
    return maxElem


class MethodLogger:
    """ Provide logging of method calls with parameters 
        E.g., for regression testing

	XXX specify output channel (or do it via redirect ?)
    """

    def __init__(self, object):
	self.object = object

    def __getattr__(self,arg):
	self.methodName = arg
	self.method = getattr(self.object,arg)
	return getattr(self,'caller')

    def caller(self,*args):
	print self.methodName,"(",args,")"
	return apply(self.method,args)





