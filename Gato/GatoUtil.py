################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoUtil.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2010, Alexander Schliep, Winfried Hochstaettler and 
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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

from Tkinter import *
    
def extension(pathAndFile):
    """ Return ext if path/filename.ext is given """
    import string
    return string.split(stripPath(pathAndFile),".")[-1]
    
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
    if length < 0.001:
        length = 0.001
    u1 = u1 / length
    u2 = u2 / length
    return (-u2,u1)
      
def ArgMin(list,val):
    """ Returns the element e of list for which val[e] is minimal.
    """
    values = [val[e] for e in list]
    return list[values.index(min(values))]
    
def ArgMax(list,val):
    """ Returns the element e of list for which val[e] is maximal """
    values = [val[e] for e in list]
    return list[values.index(max(values))]

            
class ImageCache:
    """ Provides a global cache for PhotoImages displayed in the 
        application. Singleton Pattern

        ic = ImageCache()

        # image_data is base64 encoded gif file
        ic.AddImage('some/path/image.gif', image_data)

        ...image_create('insert', image=ic['some/path/image.gif']
    """
    images = None	
    
    def __init__(self):
        if ImageCache.images == None:
            ImageCache.images = {}
            
    def __getitem__(self, relURL):
        """ Given a relative URL to an image file return the 
            corresponding PhotoImage. """
        try:    
            if relURL not in self.images.keys():
                ImageCache.images[relURL] = PhotoImage(file=relURL)
            return ImageCache.images[relURL]
        except IndexError, IOError:
            import logging
            log = logging.getLogger("GatoUtil.py")
            log.exception("Error finding image %s" % relURL)
            
    def AddImage(self, relURL, imageData):
        ImageCache.images[relURL] = PhotoImage(data=imageData)
