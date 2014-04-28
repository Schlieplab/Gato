#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoTest.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2013, Alexander Schliep, Winfried Hochstaettler and 
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

#
# Negative cycle property
#
# 05-ShortestPaths/BellmanFord.alg === 05-ShortestPaths/11x11neg.cat
# 05-ShortestPaths/BellmanFord.alg === 05-ShortestPaths/NegCircuit.cat
# 05-ShortestPaths/BellmanFord.alg === 05-ShortestPaths/NegCircuit2.cat
# 05-ShortestPaths/DijkstraPQ.alg === 05-ShortestPaths/11x11neg.cat
# 05-ShortestPaths/DijkstraPQ.alg === 05-ShortestPaths/NegCircuit2.cat
# 05-ShortestPaths/FindPath.alg === 05-ShortestPaths/11x11neg.cat
#
#
# 07-MinimumCostFlows/SuccessiveShortestPath.alg === 06-MaximalFlows/Didacta.cat

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
    '03-MinimalSpanningTrees/MSTInteractive.alg':[
    '03-MinimalSpanningTrees/Kruskal3.cat'
    ],
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


#
#
# TODO: Once the index page is being generated completely correctly come back to this svg_instance
# list and give all of the algorithms names that more closely reflect the names in the book
svg_instance = [
    {
        'chapter_directory': '02-GraphsNetworks',
        'chapter_number': 2,
        'title': 'chapter_title',
        'algorithms': [
            {
                'title': 'BFS-components',
                'file': 'BFS-components.alg',
                'description': 'bfs components description',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '02-GraphsNetworks/3Components.cat',
                    '02-GraphsNetworks/DoubleSquare.cat', '02-GraphsNetworks/DoubleTriangle.cat',
                    '02-GraphsNetworks/K10-10.cat', '02-GraphsNetworks/K3-3.cat'
                ]
            },
            {
                'title': 'BFS',
                'file': 'BFS.alg',
                'description': 'bfs description',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
                ]
            },
            {
                'title': 'BFS to DFS',
                'file': 'BFStoDFS.alg',
                'description': 'BFS to DFS description',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
                ]
            },
            {
                'title': 'DFS Recursive',
                'file': 'DFS-Recursive.alg',
                'description': 'DFS Recursive description',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
                ]
            },
            {
                'title': 'DFS',
                'file': 'DFS.alg',
                'description': 'DFS description',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
                ]
            }
        ]
    },

    
    {
        'chapter_directory': '03-MinimalSpanningTrees',
        'chapter_number': 3,
        'title': 'MinimalSpanningTrees',
        'algorithms': [
            {   
                'title': 'Kruskal\'s Algorithm',
                'file': 'Kruskal.alg',
                'description': 'kruskal description',
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]
            },
            {
                'title': 'KruskalFindCircuit',
                'file': 'KruskalFindCircuit.alg',
                'description': 'kruskal find circuit description',
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]
            },
            {
                'title': 'Kruskal Inefficient',
                'file': 'KruskalInefficient.alg',
                'description': 'KruskalInefficient description',
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]
            },
            {
                'title': 'Kruskal Trace',
                'file': 'KruskalTrace.alg',
                'description': 'KruskalTrace description',
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]   
            },
            {
                'title': 'MST Interactive',
                'file': 'MSTInteractive.alg',
                'description': 'mst interactive description',
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]
            },
            {
                'title': 'Matroid Dual Kruskal',
                'file': 'MatroidDualKruskal.alg',
                'description': 'matroid dual kruskal description', 
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]
            },
            {
                'title': 'Prim',
                'file': 'Prim.alg',
                'description': 'Prim description',
                'graphs': [
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
                ]
            }
        ]
    },

    {
        'chapter_directory': '04-LPDuality',
        'chapter_number': 4,
        'title': 'LPDuality',
        'algorithms': [
            {
                'title': 'Primal Dual Kruskal',
                'file': 'PrimalDualKruskal.alg',
                'graphs': [
                    '04-LPDuality/PD_Kruskal5.cat'
                ]
            }
        ]
    },

    {
        'chapter_directory': '05-ShortestPaths',
        'chapter_number': 5,
        'title': 'Shortest Paths',
        'algorithms': [
            {
                'title': 'Bellman Ford',
                'file': 'BellmanFord.alg',
                'graphs': [
                    '05-ShortestPaths/BellmanFordWC.cat'
                ]
            },
            {
                'title': 'Dijkstra',
                'file': 'Dijkstra.alg',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected06.cat'
                ]
            },
            {
                'title': 'DijkstraPQ',
                'file': 'DijkstraPQ.alg',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected06.cat'
                ]
            },
            {
                'title': 'FindPath',
                'file': 'FindPath.alg',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected06.cat'
                ]
            },
            {
                'title': 'FindPathEuclid',
                'file': 'FindPathEuclid.alg',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected06.cat'
                ]
            },
            {
                'title': 'NegativeCircuits',
                'file': 'NegativeCircuits.alg',
                'graphs': [
                    '05-ShortestPaths/NegCircuit2.cat'
                ]
            },
            # Could use highlighting of paths on this
            {
                'title': 'TwoSources',
                'file': 'TwoSources.alg',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected06.cat'
                ]
            }
        ]
    },

    {
        'chapter_directory': '06-MaximalFlows',
        'chapter_number': 6,
        'title': 'Maximal Flows',
        'algorithms': [
            {
                'title': 'FordFulkerson',
                'file': 'FordFulkerson.alg',
                'graphs': [
                    '06-MaximalFlows/FordFulkerson6.cat', #'06-MaximalFlows/FordFulkersonBad.cat'
                ]
            },
            {
                'title': 'PreflowPush',
                'file': 'PreflowPush.alg',
                'graphs': [
                    '06-MaximalFlows/PreflowPush5.cat', '06-MaximalFlows/PreflowPush6.cat'
                ]
            }
        ]
    },

    {
        'chapter_directory': '07-MinimumCostFlows',
        'chapter_number': 7,
        'title': 'Minimum Cost Flows',
        'algorithms': [
            {
                'title': 'SuccessiveShortestPath',
                'file': 'SuccessiveShortestPath.alg',
                'graphs': [
                    '07-MinimumCostFlows/MCF4to1A.cat', '07-MinimumCostFlows/MCFCycle.cat'
                ]
            },
        ]
    },

    {
        'chapter_directory': '08-Matching',
        'chapter_number': 8,
        'title': 'Matching',
        'algorithms': [
            {
                'title': 'Bipartite',
                'file': 'Bipartite.alg',
                'graphs': [
                    '08-Matching/Bi003.cat', '08-Matching/Bi006.cat', '08-Matching/Bi008.cat',
                    '08-Matching/Bi009.cat', '08-Matching/Bi010.cat'
                ]
            },
            {
                'title': 'CardinalityMatching',
                'file': 'CardinalityMatching.alg',
                'graphs': [
                    '08-Matching/Edmonds1.cat', '08-Matching/Edmonds3.cat', '08-Matching/Edmonds6.cat'
                ]
            }
        ]
    },

    {
        'chapter_directory': '09-WeightedMatching',
        'chapter_number': 9,
        'title': 'WeightedMatching',
        'algorithms': [
            {
                'title': 'WeightedMatching',
                'file': 'WeightedMatching.alg',
                'graphs': [
                    '09-WeightedMatching/k4.cat', '09-WeightedMatching/var2zero.cat',
                    '09-WeightedMatching/11vs13.cat'
                ]
            }
        ]
    }
]

# Keys: e.g. '09-WeightedMatching/k4.cat', values: graph description
graph_descriptions = {
    '02-GraphsNetworks/BFS.cat': 'BFS Graph Description'
}

# These are the algorithm/graph combos that are used to generate their 
# Webgato counterparts.  Each algorithm is marked with a "Good" or "Bad"
# to signify whether it works or not.  Working on getting rid of the "Bad"s
'''
svg_instance = {
    # Good
    '02-GraphsNetworks/BFS-components.alg':[
        '02-GraphsNetworks/BFS.cat', '02-GraphsNetworks/3Components.cat'
    ],

    # Good
    '02-GraphsNetworks/BFS.alg':[
        '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
    ],

    # Good
    '02-GraphsNetworks/BFStoDFS.alg':[
        '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
    ],

    # Good
    '02-GraphsNetworks/DFS-Recursive.alg':[
        '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
    ],

    # Good
    '02-GraphsNetworks/DFS.alg':[
        '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
    ],

    # Good
    '03-MinimalSpanningTrees/Kruskal.alg':[
    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],

    # Good
    '03-MinimalSpanningTrees/KruskalFindCircuit.alg':[
    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],

    # Good
    '03-MinimalSpanningTrees/KruskalInefficient.alg':[
    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],

    # Good
    '03-MinimalSpanningTrees/KruskalTrace.alg':[
    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],

    # Good
    '03-MinimalSpanningTrees/MSTInteractive.alg':[
    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],

    # Good
    '03-MinimalSpanningTrees/MatroidDualKruskal.alg':[
       '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],
    
    # Good
    '03-MinimalSpanningTrees/Prim.alg':[
        '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Kruskal1.cat'
    ],
    
    # Good
    '04-LPDuality/PrimalDualKruskal.alg':[
       '04-LPDuality/PD_Kruskal5.cat'
    ],

    # Good
    '05-ShortestPaths/BellmanFord.alg':[
        '05-ShortestPaths/BellmanFordWC.cat'  #,'05-ShortestPaths/NegCircuit.cat'(BellmanFord doesn't finish on negcircuit)
    ],

    # Good
    '05-ShortestPaths/Dijkstra.alg':[
        '05-ShortestPaths/ShortestPathsUndirected06.cat'
    ],

    # Good
    '05-ShortestPaths/DijkstraPQ.alg':[
        '05-ShortestPaths/ShortestPathsUndirected06.cat'
    ],

    # Good
    '05-ShortestPaths/FindPath.alg':[
        '05-ShortestPaths/ShortestPathsUndirected06.cat'
    ],

    # Good
    '05-ShortestPaths/FindPathEuclid.alg':[
        '05-ShortestPaths/ShortestPathsUndirected06.cat'
    ],

    # Good
    '05-ShortestPaths/NegativeCircuits.alg':[
        '05-ShortestPaths/NegCircuit2.cat'
    ],

    # Good -- Could use highlighting path in javascript
    '05-ShortestPaths/TwoSources.alg':[
        '05-ShortestPaths/ShortestPathsUndirected06.cat'
    ],

    # Good
    '06-MaximalFlows/FordFulkerson.alg':[
        '06-MaximalFlows/FordFulkerson6.cat','06-MaximalFlows/FordFulkersonBad.cat'
    ],

    # Good
    '06-MaximalFlows/PreflowPush.alg':[
       '06-MaximalFlows/PreflowPush5.cat', '06-MaximalFlows/PreflowPush6.cat'
    ],

    # Good
    '07-MinimumCostFlows/CostScaling.alg':[
        '07-MinimumCostFlows/MCFCycle.cat', '07-MinimumCostFlows/MCF4to4A.cat'
    ],

    # BAD
    #
    #'07-MinimumCostFlows/NegativeCircuit.alg':[
    #'07-MinimumCostFlows/MCF4to4A.cat',
    #'05-ShortestPaths/NegCircuit2.cat',
    #'07-MinimumCostFlows/MCFCycle.cat'
    #],

    # Good
    '07-MinimumCostFlows/SuccessiveShortestPath.alg':[
        '07-MinimumCostFlows/MCF4to1A.cat', '07-MinimumCostFlows/MCFCycle.cat'
    ],

    # Good
    '08-Matching/Bipartite.alg':[
        '08-Matching/Bi003.cat', '08-Matching/Bi006.cat', '08-Matching/Bi008.cat',
        '08-Matching/Bi009.cat', '08-Matching/Bi010.cat'
    ],

    # Good
    '08-Matching/CardinalityMatching.alg':[
        '08-Matching/Edmonds1.cat', '08-Matching/Edmonds3.cat', '08-Matching/Edmonds6.cat'
    ],
    
    # Good
    '09-WeightedMatching/WeightedMatching.alg':[
       '09-WeightedMatching/k4.cat', '09-WeightedMatching/var2zero.cat',
       '09-WeightedMatching/11vs13.cat'
    ]
}
'''

def create_svg_index_page(graph_pngs):
    ''' Creates an HTML index page that leads to the SVG 
        animations generated from the svg_instance dictionary
    '''
    import jinja2
    svg_locations = {}
    for chapter_dict in svg_instance:
        for algo in chapter_dict['algorithms']:
            algo_name = os.path.splitext(algo['file'])[0]
            for graph in algo['graphs']:
                graph_name = os.path.splitext(os.path.basename(graph))[0]
                svg_locations[algo['title'] + graph] = algo_name + '--' + graph_name + '.html'

    with open('svg_index_template.html', 'r') as template_in:
        with open('svgs/index.html', 'w') as index_out:
            template = jinja2.Template(template_in.read())
            index_out.write(template.render({
                'svg_instance': svg_instance, 
                'graph_pngs': graph_pngs, 
                'graph_descriptions': graph_descriptions,
                'svg_locations': svg_locations
            }))

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
    elif not svg:
        if all:
            ei = {
                '05-ShortestPaths/BellmanFord.alg':['05-ShortestPaths/11x11neg.cat',
                                                    '05-ShortestPaths/NegCircuit.cat',
                                                    '05-ShortestPaths/NegCircuit2.cat'
                                                    ],
                '05-ShortestPaths/FindPath.alg':['05-ShortestPaths/11x11neg.cat',
                                                 '05-ShortestPaths/NegCircuit.cat',
                                                 '05-ShortestPaths/NegCircuit2.cat'
                                                 ],
                '05-ShortestPaths/FindPathEuclid.alg':['05-ShortestPaths/11x11neg.cat',
                                                       '05-ShortestPaths/NegCircuit.cat',
                                                       '05-ShortestPaths/NegCircuit2.cat'
                                                       ],
                '05-ShortestPaths/Dijkstra.alg':['05-ShortestPaths/11x11neg.cat',
                                                 '05-ShortestPaths/NegCircuit.cat',
                                                 '05-ShortestPaths/NegCircuit2.cat'
                                                 ],
                '05-ShortestPaths/DijkstraPQ.alg':['05-ShortestPaths/11x11neg.cat',
                                                   '05-ShortestPaths/NegCircuit.cat',
                                                   '05-ShortestPaths/NegCircuit2.cat'
                                                   ]
                }
            instance = allInstances(exclude_algorithms=['MSTInteractive.alg'],
                                    exclude_instances=ei)
        algorithms = instance.keys()
        algorithms.sort()
        tests = [(algo, graph) for algo in algorithms for graph in instance[algo]]
        testPath = "../CATBox/"


    # To speed up running of tests
    g.BlinkRepeat = 1 
    g.BlinkRate = 2
    
    g.Interactive = 0 # Same effect as hitting continue for interactive lines
    log = logging.getLogger("Gato")
    
    app = AlgoWin()
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
    
    if svg:
        if not os.path.exists('./svgs'):
            os.makedirs('./svgs')

        # Warn the user if they don't have the correct libraries for PNG generation
        has_png_libs = True
        try:
            import cairo
            import rsvg
        except:
            has_png_libs = False
            err_msg = ('*******\nWARNING:\n'
                'Generation of an SVG Index page requires the python packages for cairo(http://cairographics.org/)'
                ' and librsvg(https://wiki.gnome.org/action/show/Projects/LibRsvg?action=show&redirect=LibRsvg).'
                '  SVG generation will continue, but no index page will be generated.\n*******')
            print err_msg

        graph_pngs = {}
        testPath = "../CATBox/"
        for chapter_dict in svg_instance:
            for algo in chapter_dict['algorithms']:
                for graph_file in algo['graphs']:
                    log.info("=== TEST === "+algo['file']+" === "+graph_file+" ===")
                    app.OpenAlgorithm(testPath + chapter_dict['chapter_directory'] + '/' + algo['file'])
                    g.Interactive = 0 # This is set to 0 above.  Do we need to do it here as well?
                    app.algorithm.ClearBreakpoints()
                    app.update_idletasks()
                    app.update()
                    app.OpenGraph(testPath + graph_file)
                    app.update_idletasks()
                    app.update()
                    # Run it ...
                    app.after_idle(app.CmdContinue) # after idle needed since CmdStart
                    # does not return
                    app.CmdStart()
                    app.update_idletasks()

                    # Generate the SVG
                    app.ExportSVGAnimation('svgs/%s--%s.html' %
                        (os.path.splitext(algo['file'])[0], os.path.splitext(os.path.basename(graph_file))[0]))
                    # Generate the PNG
                    if graph_file not in graph_pngs and has_png_libs:
                        file_name = 'svgs/img/%s.png' % (os.path.splitext(os.path.basename(graph_file))[0])
                        png_file = app.ExportSVG(file_name, write_to_png=True)
                        graph_name = os.path.splitext(os.path.basename(graph_file))[0]
                        path_from_index = '/'.join(file_name.split('/')[1:])
                        graph_pngs[graph_file] = {'file': path_from_index, 'name': graph_name}

        if has_png_libs:
            create_svg_index_page(graph_pngs)

    else:
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

            