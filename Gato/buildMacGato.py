#
# MacOS X 10.3 has a MacPython (sans Tk) on board. So we can deploy
# semi-standalones
#
#/usr/bin/pythonw buildMacGato.py -v --python=/usr/bin/pythonw -a --semi-standalone build
#
# The -a is needed to keep whomever from passing dorky args.
#
### makeapplication.py
from bundlebuilder import buildapp

buildapp(
    name='Gato.app', # what to build
    mainprogram='Gato.py', # your app's main()
    argv_emulation=0, # drag&dropped filenames show up in sys.argv
    #iconfile='myapp.icns', # file containing your app's icons
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
    includePackages=[], # list of additional Packages to force in
    libs=['/Library/Frameworks/Tk.Framework',
          '/Library/Frameworks/Tcl.Framework'
    ]
)

### end of makeapplication.p
