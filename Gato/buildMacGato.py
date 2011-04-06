################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   buildMacGato.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 2005-2010, Alexander Schliep, Winfried Hochstaettler
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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
#
# MacOS X 10.4-10.6 have a MacPython with Tk on board.
#
#  10.4: N/A
#  10.5: We can deploy semi-stand-alones (using the System Python and Tk)
#  10.6: Tk/Tkinter/Python combo still broken in 10.6.7: Need to build standalones on 10.5
#
# /usr/bin/python buildMacGredSA.py -v --python=/usr/bin/python -a --standalone build
#
# NOTE: --python=/usr/bin/pythonw produces pesky Python name
#
# The -a is needed to keep whomever from passing dorky args.
#
from bundlebuilder import buildapp

buildapp(
    name='Gato.app', # what to build
    mainprogram='Gato.py', # your app's main()
    argv_emulation=0, # drag&dropped filenames show up in sys.argv
    iconfile='Gato.icns', # file containing your app's icons
    #standalone=0, # make this app self contained.
    includeModules=[
    'AnimatedAlgorithms',
    'AnimatedDataStructures',
    'DataStructures',
    'EditObjectAttributesDialog',
    'Embedder',
    'GatoConfiguration',
    'GatoDialogs',
    'GatoFile',
    'GatoGlobals',
    'GatoIcons',
    'GatoSystemConfiguration',
    'GatoUtil',
    'Graph',
    'GraphCreator',
    'GraphDisplay',
    'GraphUtil',
    'PlanarEmbedding',
    'PlanarityTest',
    'TextTreeWidget',
    'TreeWidget',
    'logging'
    ],
    includePackages=['argvemulator'], # list of additional Packages to force in
    # Works on 10.4.7 without it
    #libs=['/System/Library/Frameworks/Tk.Framework',
    #      '/System/Library/Frameworks/Tcl.Framework'
    #]
)

### end of makeapplication.p
