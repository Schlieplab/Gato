#!/usr/bin/env python2.7
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       You can find more information at http://gato.sf.net
#
#	file:   setup-win.py
#	author: Alexander Schliep (alexander@schlieplab.org)
#
#       Copyright (C) 2016-2020 Alexander Schliep and
#	Copyright (C) 1998-2015 Alexander Schliep, Winfried Hochstaettler and 
#       Copyright (C) 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schlieplab.org
#
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
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################


import distutils
from distutils.core import setup,Extension
import py2exe

# Read info from GatoGlobals.py ... the following code makes sure we read
# GatoGlobals.py in the current directory
import sys
if sys.version_info < (3,0):
    info={}
    execfile("GatoGlobals.py", info)
else:
    # Some variant of exec(open("GatoGlobals.py").read())
    raise NotImplementedError

long_description_text = open('README').readlines()



setup(name="Gato",
      version=info['gatoVersion'],
      description = info['gatoDescription'],
      long_description = long_description_text,
      author = "Alexander Schliep and Winfried Hochstaettler",
      author_email = info['gatoAuthorEmail'],
      maintainer = "Alexander Schliep",
      maintainer_email = info['gatoAuthorEmail'],
      url = info['gatoURL'],
      download_url = info['gatoDownloadURL'],
      packages=['Gato'],
      package_dir={'Gato': ''},
      scripts=['scripts/Gato', 'scripts/Gred'],
      console=['Gato.py','Gred.py'],
      zipfile = 'Gato.zip',
      options={'py2exe':{
            'unbuffered':True,
            'bundle_files':3,
            'includes':['AnimatedDataStructures','AnimatedAlgorithms']
           }
      }
      )
