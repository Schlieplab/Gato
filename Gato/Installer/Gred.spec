# -*- mode: python;-*-

scriptbase=os.path.split(os.path.abspath(SPECPATH))[0]

exeext=""
scripts=[os.path.join(HOMEPATH,'support','_mountzlib.py'),
         os.path.join(HOMEPATH,'support','useUnicode.py'),
         os.path.join(scriptbase,'Gred.py')]

a = Analysis(scripts, pathex=[])

tclSupportFile=[]
tclSupportDir=[]
if sys.platform[:3]=='win':
    print "Win32"
    # microsoft world
    # exe extension needed for executables
    exeext=".exe"
    # add tcl/tk support
    winscripts=[os.path.join(HOMEPATH,'support','unpackTk.py'),
                os.path.join(HOMEPATH,'support','useTk.py')]
    winscripts.extend(scripts)
    winscripts.extend([os.path.join(HOMEPATH,'support','removeTk.py')])
    scripts=winscripts
    tclSupportFile=TkPKG()
    tclSupportDir=TkTree()

# Gred.py is also used as module
# Modules needed for Algorithm sandbox environment
a.pure.extend([('AnimatedAlgorithms',
                os.path.join(scriptbase,'AnimatedAlgorithms.pyc'),
                'PYMODULE'),
               ('AnimatedDataStructures',
                os.path.join(scriptbase,'AnimatedDataStructures.pyc'),
                'PYMODULE'),
               ('Gred',
                os.path.join(scriptbase,'Gred.pyc'),
                'PYMODULE'),
               ])
#module strop excluded, this step needs modification in Installer/carchive.py
a.binaries-=[('strop','',''),('pcre','',''),('libX11.so.6','',''),('termios','',''),('sha','',''),('libtcl8.3.so','',''),('libtk8.3.so','','')]

#a.binaries-=[('libcrypto.so.0.9.6','',''),('libssl.so.0.9.6','',''),('_socket','','')]
pyz = PYZ(a.pure)

#build one file deployment
exe = EXE(pyz,
	  tclSupportFile,
          a.scripts,
          a.binaries,
          name=specnm+exeext,
          debug=1,
          strip=1,
          console=1)
#and distribution in distGred
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build%s'%specnm,specnm+exeext),
          debug=1,
          strip=1,
          console=1)
coll = COLLECT(exe,
	       tclSupportDir,
               a.binaries,
               name='dist%s'%specnm)