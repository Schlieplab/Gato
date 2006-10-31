#!/usr/bin/env python2.3
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Gato.py
#	author: Janne Grunau
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
#
#       This file is version $Revision: 291 $ 
#                       from $Date: 2006-10-18 16:04:35 +0200 (Wed, 18 Oct 2006) $
#             last change by $Author: schliep $.
#
################################################################################


import distutils
from distutils.core import setup,Extension

setup(name="Gato",
      version="0.999",
      description="the Graph Animation Toolbox",
      author="Gato authors",
      author_email="Gato",
      url="http://gato.sourceforge.net/",
      packages=['Gato'],
      package_dir={'Gato': ''},
      scripts=['scripts/Gato', 'scripts/Gred', 'scripts/Gato3D']
      )
