#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GatoTest.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file has version _FILE_REVISION_ from _FILE_DATE_
#
#
################################################################################
from Gato import *

testPath = "../CATBox/"

tests = [ ("FindpathEuclid.alg","cm.cat"),
	  ("Findpath.alg","cm.cat") ]


if __name__ == '__main__':
    app = AlgoWin()    
    app.algorithm.logAnimator=1
    
    for case in tests:
	print "=== TEST ===",case[0],"===",case[1],"==="
	app.OpenAlgorithm(testPath + case[0])
	app.algorithm.ClearBreakpoints()
	app.update_idletasks()
	app.update()
	app.OpenGraph(testPath + case[1])
	app.update_idletasks()
	app.update()
	# Run it ...
	app.after_idle(app.CmdContinue) # after idle needed since CmdStart
        # does not return
	app.CmdStart()
	app.update_idletasks()
	#app.mainloop()
