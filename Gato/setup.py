#!/usr/bin/env python2.6
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Gato.py
#	author: Janne Grunau
#
#       Copyright (C) 1998-2015, Alexander Schliep, Winfried Hochstaettler and 
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
#
#       This file is version $Revision: 291 $ 
#                       from $Date: 2006-10-18 16:04:35 +0200 (Wed, 18 Oct 2006) $
#             last change by $Author: schliep $.
#
################################################################################


import distutils
from distutils.core import setup

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
      package_data={'Gato': ['svgs/js/*', 'svgs/js/subModal/*', 'svgs/css/*']},
      scripts=['scripts/Gato', 'scripts/Gred', 'scripts/gato-create-js-css-symlinks'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: MacOS X',
                   'Environment :: Win32 (MS Windows)',
                   'Environment :: X11 Applications',
                   'Intended Audience :: Education',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Natural Language :: English',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Education',
                   'Topic :: Education :: Computer Aided Instruction (CAI)',
                   'Topic :: Scientific/Engineering :: Mathematics',
                   'Topic :: Scientific/Engineering :: Visualization'
                   ]
      )
