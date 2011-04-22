#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoTest.py
#	author: Alexander Schliep (alexander@schliep.org)
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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
import getopt
import sys
import os
import fnmatch
import logging
from Gato import *
import GatoGlobals
g = GatoGlobals.AnimationParameters



def allInstances(exclude_algorithms=[]):
    """ Compute instances for all *.alg and all *.cat files across directories.
        Algorithms need to set self.NeededProperties() in Prolog correctly to
        avoid incompatible algorithm-graph pairings. E.g.
        self.NeededProperties({'EvenOrder':1}) for WeightedMatching
    """
    testPath = "../CATBox/"
    directories = [
        '02-GraphsNetworks/',
        '03-MinimalSpanningTrees/',
        '04-LPDuality/',
        '05-ShortestPaths/',
        '06-MaximalFlows/',
        '07-MinimumCostFlows/',
        '08-Matching/',
        '09-WeightedMatching/'
        ]

    algorithms = []
    graphs = []

    for d in directories:
        algorithms += [os.path.join(d,file) for file in os.listdir(os.path.join(testPath,d)) \
                       if (fnmatch.fnmatch(file, '*.alg') and not file in exclude_algorithms)]
        graphs += [os.path.join(d,file) for file in os.listdir(os.path.join(testPath,d)) if \
                   fnmatch.fnmatch(file, '*.cat')]

    instance = {}
    for a in algorithms:
        instance[a] = graphs

    return instance


# instance is a dictionary where the keys are 
# algorithms and their value is a list of graphs
# they will work on.
#
# Testcases are all combinations of algorithm with all their
# graphs.
instance = {
    '02-GraphsNetworks/BFS-components.alg':[
    '02-GraphsNetworks/3Components.cat'
    ],
    '02-GraphsNetworks/BFS.alg':[
    '02-GraphsNetworks/DoubleTriangle.cat'
    ],
    '02-GraphsNetworks/BFStoDFS.alg':[
    '02-GraphsNetworks/BFS.cat'
    ],
    '02-GraphsNetworks/DFS-Recursive.alg':[
    '02-GraphsNetworks/DoubleTriangle.cat'
    ],
    '02-GraphsNetworks/DFS.alg':[
    '02-GraphsNetworks/DoubleTriangle.cat'
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
    # XXX Not sure whether it terminates: on a small instance it does
    # But since this is random this is not good for regression testing
    #'03-MinimalSpanningTrees/MSTInteractive.alg':[
    #'03-MinimalSpanningTrees/Kruskal3.cat'
    #],
    '03-MinimalSpanningTrees/MatroidDualKruskal.alg':[
    '03-MinimalSpanningTrees/Kruskal3.cat'    
    ],
    '03-MinimalSpanningTrees/Prim.alg':[
    '03-MinimalSpanningTrees/Prim1.cat'
    ],
    '04-LPDuality/PrimalDualKruskal.alg':[
    '04-LPDuality/PD_Kruskal3.cat'
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
    '05-ShortestPaths/ShortestPathsUndirected05.cat'
    ],
    '05-ShortestPaths/FindPathEuclid.alg':[
    '05-ShortestPaths/ShortestPathsUndirected05.cat'
    ],
    '05-ShortestPaths/NegativeCircuits.alg':[
    '05-ShortestPaths/NegCircuit.cat'
    ],
    '05-ShortestPaths/TwoSources.alg':[
    '05-ShortestPaths/ShortestPathsUndirected05.cat'    
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

# svg_instance is a dictionary where the keys are 
# algorithms and their value is a list of graphs
# they will work on.
#
# Testcases are all combinations of algorithm with all their
# graphs.
svg_instance = {
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
    ]
    }


#------------------------------------------------------------------
def usage():
    print "Usage: GatoTest.py"
    print "       GatoTest.py -v -d"
    print "               -v or --verbose switches on the logging information"
    print "               -d or --debug switches on the debugging  information"


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "asdvt",
                                   ["all", "svg","debug","verbose", "test"])
    except getopt.GetoptError:
        usage()
        exit()

    all = False
    svg = False
    debug = False
    verbose = False
    test = False
    for o, a in opts:
        if o in ("-a", "--all"):
            all = True
        if o in ("-v", "--verbose"):
            verbose = True
        if o in ("-d", "--debug"):
            debug = True
        if o in ("-s", "--svg"):
            svg = True
        if o in ("-t", "--test"):
            test = True
            
            
    if test:
        testPath = "./"
        tests = [ ("BFS.alg", "sample.cat") ]
    else:
        if svg:
            instance = svg_instance
        if all:
            instance = allInstances(exclude_algorithms=['MSTInteractive.alg'])
        algorithms = instance.keys()
        algorithms.sort()
        tests = [(algo, graph) for algo in algorithms for graph in instance[algo]]
        testPath = "../CATBox/"


    app = AlgoWin()
    # To speed up running of tests
    g.BlinkRepeat = 1 
    g.BlinkRate = 2
    
    g.Interactive = 0 # Same effect as hitting continue for interactive lines
    log = logging.getLogger("Gato")

    if debug:
        app.algorithm.logAnimator = 2
    if verbose:
        if sys.version_info[0:2] < (2,4):
            log.addHandler(logging.StreamHandler(sys.stdout))
            log.setLevel(logging.DEBUG)
        else:
            logging.basicConfig(level=logging.DEBUG,
                                stream=sys.stdout,
                                format='%(name)s %(levelname)s %(message)s')
    else:
        if app.windowingsystem == 'win32':

           class NullHandler(logging.Handler):
               def emit(self, record):
                   pass
           h = NullHandler()
           logging.getLogger("Gato").addHandler(h)

        else:
            logging.basicConfig(level=logging.WARNING,
                                filename='/tmp/Gato.log',
                                filemode='w',
                                    format='%(name)s %(levelname)s %(message)s')        
    for case in tests:
        log.info("=== TEST === "+case[0]+" === "+case[1]+" ===")
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

        if svg:
            app.ExportSVGAnimation('%s-%s.svg' %
                                   (os.path.splitext(os.path.basename(case[0]))[0],
                                    os.path.splitext(os.path.basename(case[1]))[0]))
