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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
from Gato import *

testPath = "../CATBox/"

tests = [ ("04-MinimalSpanningTrees/Prim.alg",
	   "04-MinimalSpanningTrees/MinimalSpanningTrees08.cat"),
          ("04-MinimalSpanningTrees/Kruskal.alg",
	   "04-MinimalSpanningTrees/MinimalSpanningTrees08.cat"),
          ("06-MaximalFlows/FordFulkerson.alg",
	   "06-MaximalFlows/FordFulkerson3.cat"),
          ("06-MaximalFlows/PreflowPush.alg",
	   "06-MaximalFlows/PreflowPush2.cat")
        ]


if __name__ == '__main__':
    app = AlgoWin()    
    app.algorithm.logAnimator=1
    globals()['gInteractive'] = 0
    print "GatoTest",globals()['gInteractive']
   
    for case in tests:
	print "=== TEST ===",case[0],"===",case[1],"==="
	app.OpenAlgorithm(testPath + case[0])
	globals()['gInteractive'] = 0
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
