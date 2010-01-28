#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoDemo.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2009, Alexander Schliep, Winfried Hochstaettler and 
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
#       This file is version $Revision: 343 $ 
#                       from $Date: 2009-12-02 16:05:17 -0500 (Wed, 02 Dec 2009) $
#             last change by $Author: schliep $.
#
################################################################################
from Gato import *
import GatoGlobals
g = GatoGlobals.AnimationParameters
# To speed up running of tests
g.BlinkRepeat = 1
g.BlinkRate = 2

testPath = "../CATBox/"

instance = {
    '02-GraphsNetworks/BFS-components.alg':[
    '02-GraphsNetworks/BFS.cat'
    ],
    '02-GraphsNetworks/BFS.alg':[
    '02-GraphsNetworks/BFS.cat'
    ],
    '02-GraphsNetworks/BFStoDFS.alg':[
    '02-GraphsNetworks/BFS.cat'
    ],
    '02-GraphsNetworks/DFS-Recursive.alg':[
    '02-GraphsNetworks/BFS.cat'
    ],
    '02-GraphsNetworks/DFS.alg':[
    '02-GraphsNetworks/BFS.cat'
    ],
    '03-MinimalSpanningTrees/Kruskal.alg':[
    '03-MinimalSpanningTrees/Kruskal4.cat'
    ],
    '03-MinimalSpanningTrees/KruskalFindCircuit.alg':[
    '03-MinimalSpanningTrees/Kruskal4.cat'
    ],
    '03-MinimalSpanningTrees/KruskalInefficient.alg':[
    '03-MinimalSpanningTrees/Kruskal4.cat'
    ],
    '03-MinimalSpanningTrees/KruskalTrace.alg':[
    '03-MinimalSpanningTrees/Kruskal4.cat'
    ],
    # XXX Not sure whether it terminatas
    #'03-MinimalSpanningTrees/MSTInteractive.alg':[
    #],
    '03-MinimalSpanningTrees/MatroidDualKruskal.alg':[
    '03-MinimalSpanningTrees/Kruskal4.cat'    
    ],
    '03-MinimalSpanningTrees/Prim.alg':[
    '03-MinimalSpanningTrees/Prim4.cat'
    ],
    '04-LPDuality/PrimalDualKruskal.alg':[
    '03-MinimalSpanningTrees/Kruskal4.cat'
    ],
    '05-ShortestPaths/BellmanFord.alg':[
    '05-ShortestPaths/BellmanFordWC.cat'
    ],
    '05-ShortestPaths/Dijkstra.alg':[
    '05-ShortestPaths/DijkstraRelabel.cat'
    ],
    '05-ShortestPaths/DijkstraPQ.alg':[
    '05-ShortestPaths/DijkstraRelabel.cat'
    ],
    '05-ShortestPaths/FindPath.alg':[
    '05-ShortestPaths/11x11grid.cat'
    ],
    '05-ShortestPaths/FindPathEuclid.alg':[
    '05-ShortestPaths/11x11grid.cat'
    ],
    '05-ShortestPaths/NegativeCircuits.alg':[
    '05-ShortestPaths/NegCircuit.cat'
    ],
    '05-ShortestPaths/TwoSources.alg':[
    '05-ShortestPaths/11x11grid.cat'    
    ],
    '06-MaximalFlows/FordFulkerson.alg':[
    '06-MaximalFlows/FordFulkerson4.cat'
    ],
    '06-MaximalFlows/PreflowPush.alg':[
    '06-MaximalFlows/FordFulkerson4.cat'
    ],
    '07-MinimumCostFlows/CostScaling.alg':[
    '07-MinimumCostFlows/MCF4to1B.cat'
    ],
    '07-MinimumCostFlows/NegativeCircuit.alg':[
    '07-MinimumCostFlows/MCFCycle.cat'
    ],
    '07-MinimumCostFlows/SuccessiveShortestPath.alg':[
    '07-MinimumCostFlows/MCF4to1B.cat'    
    ],
    '08-Matching/Bipartite.alg':[
    '08-Matching/Bi006.cat'
    ],
    '08-Matching/CardinalityMatching.alg':[
    '08-Matching/Edmonds5.cat'
    ],
    '09-WeightedMatching/WeightedMatching.alg':[
    '09-WeightedMatching/rote4.cat'
    ]
    }


##tests = [('02-GraphsNetworks/BFS.alg',
##          '02-GraphsNetworks/BFS.cat'),
##         ('02-GraphsNetworks/DFS.alg',
##          '02-GraphsNetworks/BFS.cat'),
##         ('06-MaximalFlows/FordFulkerson.alg',
##          '06-MaximalFlows/FordFulkerson4.cat')
##        ]
##testPath = "./"

##tests = [ ("BFS.alg", "sample.cat") ]

tests = [(algo, graph) for algo in instance.keys() for graph in instance[algo]]

if __name__ == '__main__':
    app = AlgoWin()    
    app.algorithm.logAnimator = 2
    g.Interactive = 0
    if sys.version_info[0:2] < (2,4):
        log.addHandler(logging.StreamHandler(sys.stdout))
        log.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.DEBUG,
                            stream=sys.stdout,
                            format='%(name)s %(levelname)s %(message)s')
        
    while 1:
        for case in tests:
            print "=== TEST ===",case[0],"===",case[1],"==="
            app.OpenAlgorithm(testPath + case[0])
            g.Interactive = 0
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
