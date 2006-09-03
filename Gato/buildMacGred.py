#
# MacOS X 10.3 has a MacPython (sans Tk) on board. So we can deploy
# semi-standalones
#
#/usr/bin/python buildMacGred.py -v --python=/usr/bin/python -a --semi-standalone build
#
# NOTE: --python=/usr/bin/pythonw produces pesky Python name
#
# The -a is needed to keep whomever from passing dorky args.
#
### makeapplication.py
from bundlebuilder import buildapp

buildapp(
    name='Gred.app', # what to build
    mainprogram='Gred.py', # your app's main()
    argv_emulation=0, # drag&dropped filenames show up in sys.argv
    #iconfile='Gato.icns', # file containing your app's icons
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
    # Works on 10.4.7 without it
    #libs=['/System/Library/Frameworks/Tk.Framework',
    #      '/System/Library/Frameworks/Tcl.Framework'
    #]
)

### end of makeapplication.p
