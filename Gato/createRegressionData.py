#!/usr/local/bin/python2.7
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   createRegressionData.py
#	author: Alexander Schliep (alexander@schlieplab.org)
#
#       Copyright (C) 2016-2020 Alexander Schliep and
#	Copyright (C) 1998-2015 Alexander Schliep, Winfried Hochstaettler and 
#       Copyright (C) 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schlieplab.org             
#
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
#       This file is version $Revision: 806 $ 
#                       from $Date: 2020-12-08 15:13:58 +0100 (Tue, 08 Dec 2020) $
#             last change by $Author: schliep $.
#
################################################################################
import getopt
import sys
import os
import re
import fnmatch
import logging
from Gato import *
import GatoGlobals

g = GatoGlobals.AnimationParameters

def allInstances(exclude_algorithms=[], exclude_instances = {}):
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
        if a in exclude_instances:
            instance[a] = list(set(graphs) - set(exclude_instances[a]))
        else:
            instance[a] = graphs

    return instance

exclude_instances = {
    '05-ShortestPaths/BellmanFord.alg':[
        '05-ShortestPaths/11x11neg.cat',
        '05-ShortestPaths/NegCircuit.cat',
        '05-ShortestPaths/NegCircuit2.cat'
    ],
    '05-ShortestPaths/FindPath.alg':[
        '05-ShortestPaths/11x11neg.cat',
        '05-ShortestPaths/NegCircuit.cat',
        '05-ShortestPaths/NegCircuit2.cat'
    ],
    '05-ShortestPaths/FindPathEuclid.alg':[
        '05-ShortestPaths/11x11neg.cat',
        '05-ShortestPaths/NegCircuit.cat',
        '05-ShortestPaths/NegCircuit2.cat'
    ],
    '05-ShortestPaths/Dijkstra.alg':[
        '05-ShortestPaths/11x11neg.cat',
        '05-ShortestPaths/NegCircuit.cat',
        '05-ShortestPaths/NegCircuit2.cat'
    ],
    '05-ShortestPaths/DijkstraPQ.alg':[
        '05-ShortestPaths/11x11neg.cat',
        '05-ShortestPaths/NegCircuit.cat',
        '05-ShortestPaths/NegCircuit2.cat'
    ]
}



# instance is a dictionary where the keys are 
# algorithms and their value is a list of graphs
# they will work on.
#
# Testcases are all combinations of algorithm with all their
# graphs.
catbox_instances = {
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
    # But since this selects edges at random this is not good for regression testing
    #'03-MinimalSpanningTrees/MSTInteractive.alg':[
    #    '03-MinimalSpanningTrees/Kruskal3.cat'
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
        '05-ShortestPaths/BellmanFordWC.cat', 
    ],
    '05-ShortestPaths/Dijkstra.alg':[
        '05-ShortestPaths/DijkstraRelabel.cat', 
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
    #'07-MinimumCostFlows/CostScaling.alg':[
    #    '07-MinimumCostFlows/MCF4to1B.cat'
    #],
    '07-MinimumCostFlows/NegativeCycleCanceling.alg':[
        '07-MinimumCostFlows/MCFCycle.cat'
    ],
    '07-MinimumCostFlows/SuccessiveShortestPath.alg':[
        '07-MinimumCostFlows/MCF4to1B.cat'    
    ],
    '08-Matching/Bipartite.alg':[
        '08-Matching/Bi006.cat'
    ],
    '08-Matching/CardinalityMatching.alg':[
        '08-Matching/Edmonds6.cat'
    ],
    '09-WeightedMatching/WeightedMatching.alg':[
        '09-WeightedMatching/rote4.cat'
    ]
}


def makeTests(instances):
    algorithms = instances.keys()
    algorithms.sort()
    tests = [(algo, graph) for algo in algorithms for graph in instances[algo]]
    return tests

def RunTests(args):
    app = GatoApp(args)
    
    if args.quick:
        testPath = "../CATBox"
        #tests = [ ("BFS.alg", "sample.cat") ]
        tests = [('04-LPDuality/PrimalDualKruskal.alg', '04-LPDuality/PD_Kruskal3.cat')]
        #tests = [ ("BFS.alg", "K2.cat") ]
        #tests = [
        #    ("BFS.alg", "K2.cat"),
        #    ("BFS.alg", "sample.cat"),
        #]
    elif args.all:
        instances = allInstances(
            exclude_algorithms=['MSTInteractive.alg'],
            exclude_instances=exclude_instances
        )
        tests = makeTests(instances)
        testPath = "../CATBox/"        
    else:
        tests = makeTests(catbox_instances)
        testPath = "../CATBox/"        

    # Accelerate execution by blinking less
    g.BlinkRepeat = 1 
    g.BlinkRate = 2

        
    for case in tests:
        algoName = os.path.splitext(os.path.basename(case[0]))[0]
        graphName = os.path.splitext(os.path.basename(case[1]))[0]

        # Hack!
        # Since we cannot re-configure logging we pass on the open file handle
        # in the GraphDisplay(s). OpenSecondaryGraph() does this for the second
        # graph display.
        if args.path:
            fileName = os.path.join(args.path,'%s--%s.out' % (algoName, graphName))
            outfile = open(fileName, 'w')
            app.graphDisplay.animationReportFileHandle = outfile
            outfile.write("=== CASE === %s === %s ===\n" % (case[0], case[1]))
        else:
            app.graphDisplay.animationReportFileHandle = sys.stdout
            app.graphDisplay.animationReportFileHandle.write("=== CASE === %s === %s ===\n" % (case[0], case[1]))
            
        logging.info("=== CASE === %s === %s ===" % (case[0], case[1]))
        app.OpenGraph(os.path.join(testPath, case[1]))
        app.OpenAlgorithm(os.path.join(testPath, case[0]))
        app.RunAlgorithmToCompletion()
        if args.path:
            outfile.close()
            outfile = None
            app.graphDisplay.animationReportFileHandle = None
            if app.secondaryGraphDisplay:
                app.secondaryGraphDisplay.animationReportFileHandle = None
        
if __name__ == '__main__':
    description = (
        "Run Gato for the CATBox algorithm on chapter-specific graphs "
        "and log animation output on the console or in files for"
        "regression tests."
        )

    parser = argparse.ArgumentParser(
        description=description,
        epilog="Example: createRegressionData.py"
    )

    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Run all algorithms against all compatible graphs.",
    )   
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Just run a tiny subset of tests.",
    )   
    parser.add_argument(
        "--path",
        "-p",
        help="Path to store regression data.",
    )   
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Output detailed debugging information.",
    )   
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Output information about the execution."
    )
    args = parser.parse_args()
    # Manually set the extra arguments defined in Gato.py
    args.experimental=False
    args.separate=False
    args.algorithmFileName=''
    args.gatoFileName=''
    args.gato_file=''
    args.log_file=''

    if args.verbose:
        logLevel = logging.INFO
    elif args.debug:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.WARNING
    logging.basicConfig(
        level=logLevel,
        stream=sys.stdout,
        format='%(levelname)s %(message)s'
    )
    RunTests(args)
    

            
