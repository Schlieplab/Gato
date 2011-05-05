#!/usr/bin/env python2.6
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Gato.py
#	author: Janne Grunau
#
#       Copyright (C) 1998-2011, Alexander Schliep, Winfried Hochstaettler and 
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

long_description = """
Gato, the Graph Animation Toolbox http://gato.sf.net by Alexander
Schliep and Winfried Hochstaettler, is a LGPL-licensed Python
application which animates algorithms on graphs. It uses Tkinter and
runs on Unix, MacOS X, Linux and Windows.

It is primarily a teaching tool, but can also be useful in research on
algorithm design and engineering, for example by demonstrating effects of
heuristics.

It is used in CATBox (Springer 2010, see authors' website
http://schliep.org/CATBox) by Winfried Hochstaettler and Alexander
Schliep. CATBox is a textbook on combinatorial optimization on graphs
(traversals, minimal spanning trees, shortest paths, maximum flows,
min-cost flows, cardinality and weighted matching) which uses Gato to
provide interactive animations and exercises for all algorithms.  A
screencast is at:
http://biomaps.rutgers.edu/~schliep/CATBox/Dijkstra.swf

Gato and CATBox has been used in university classrooms for several
years by us and colleagues on several continents at the undergraduate
and graduate level.  Winfried Hochstaettler is a professor in
mathematics at the FernUniversitaet Hagen, Germany and Alexander
Schliep is an associate professor in computer science and quantitative
biology at Rutgers University.
"""



setup(name="Gato",
      version="1.1.1",
      description="Graph Animation Toolbox: animating algorithms on graphs",
      long_description = long_description,
      author="Alexander Schliep and Winfried Hochstaettler",
      author_email="alexander@schliep.org",
      maintainer="Alexander Schliep",
      maintainer_email="alexander@schliep.org",
      url="http://gato.sf.net/",
      download_url = 'http://sourceforge.net/projects/gato/files/',
      packages=['Gato'],
      package_dir={'Gato': ''},
      scripts=['scripts/Gato', 'scripts/Gred'],
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
