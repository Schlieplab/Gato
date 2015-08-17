#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoTest.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2015, Alexander Schliep, Winfried Hochstaettler and 
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
import re
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
    '07-MinimumCostFlows/CostScaling.alg':[
    '07-MinimumCostFlows/MCF4to1B.cat'
    ],
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
    '08-Matching/Edmonds5.cat'
    ],
    '09-WeightedMatching/WeightedMatching.alg':[
    '09-WeightedMatching/rote4.cat'
    ]
    }


# Production version:
#
# List of algorithms and instances actually used in the book
# and some extra instances
svg_instance = [
    {
        'chapter_directory': '02-GraphsNetworks',
        'chapter_number': 2,
        'title': 'Basics, Notation and Data Structures',
        'shortened_title': 'Basics',
        'algorithms': [
            {
                'title': 'BFS-Components',
                'file': 'BFS-components.alg',
                'description': 'Finds connected components in a graph using iterated ' \
                'Breadth-First-Search (BFS).',
                'graphs': [
                    '02-GraphsNetworks/1Component.cat', '02-GraphsNetworks/2Components.cat',
                    '02-GraphsNetworks/3Components.cat'
                ]
            },
            {
                'title': 'DFS Recursive',
                'file': 'DFS-Recursive.alg',
                'description': 'A recursive implementation of Depth-First-Search (DFS), ' \
                'which computes a DFS labeling.',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '02-GraphsNetworks/3Components.cat'
                ]
            },
            {
                'title': 'Iterative BFS',
                'file': 'BFS.alg',
                'description': 'An iterative implementation of Breadth-First-Search ' \
                '(BFS), which computes a BFS labeling.',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '02-GraphsNetworks/3Components.cat'
                ]
            },
            {
                'title': 'BFS to DFS',
                'file': 'BFStoDFS.alg',
                'description': 'Converting the iterative BFS implementation to an iterative ' \
                'DFS implementation by exchanging the Queue for a Stack.',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '06-MaximalFlows/FordFulkerson5.cat'
                ]
            },
            {
                'title': 'Iterative DFS',
                'file': 'DFS.alg',
                'description': 'An iterative implementation of Depth-First-Search (DFS), which ' \
                'computes a DFS labeling.',
                'graphs': [
                    '02-GraphsNetworks/BFS.cat', '02-GraphsNetworks/3Components.cat'
                ]
            }
        ]
    },
    {
        'chapter_directory': '03-MinimalSpanningTrees',
        'chapter_number': 3,
        'title': 'Minimum Spanning Trees',
        'shortened_title': 'Minimum Spanning Trees',
        'algorithms': [
            {   
                'title': 'Kruskal\'s Algorithm',
                'file': 'Kruskal.alg',
                'description': 'Kruskal\'s algorithm computes a minimum spanning tree in ' \
                'a connected, weighted graph.',
                'graphs': [
                    '03-MinimalSpanningTrees/Kruskal1.cat', '03-MinimalSpanningTrees/Kruskal2.cat',
                    '03-MinimalSpanningTrees/Kruskal3.cat',
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Prim2.cat'
                ]
            },
            {
                'title': 'Kruskal\'s Algorithm using FindCircuit',
                'file': 'KruskalFindCircuit.alg',
                'description': 'A more detailed, but naive implementation of Kruskal\'s ' \
                'algorithm, which checks for each edge to be added whether it completes a circuit.',
                'graphs': [
                    '03-MinimalSpanningTrees/Kruskal1.cat','03-MinimalSpanningTrees/Kruskal2.cat',
                    '03-MinimalSpanningTrees/Kruskal3.cat',
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Prim2.cat'
                ]
            },
            {
                'title': 'Inefficient Kruskal\'s Algorithm',
                'file': 'KruskalInefficient.alg',
                'description': 'An improved, but still somewhat naive implementation of ' \
                'Kruskal\'s algorithm, which bypasses the explicit test for circuit ' \
                'completion by maintaining component labels for vertices and testing for equality.',
                'graphs': [
                    '03-MinimalSpanningTrees/Kruskal1.cat','03-MinimalSpanningTrees/Kruskal2.cat',
                    '03-MinimalSpanningTrees/Kruskal3.cat',
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Prim2.cat'
                ]
            },
            {
                'title': 'Efficient Kruskal\'s Algorithm',
                'file': 'KruskalTrace.alg',
                'description': 'An efficient implementation of Kruskal\'s algorithm, which ' \
                'minimizes the number of component label updates.',
                'graphs': [
                    '03-MinimalSpanningTrees/Kruskal1.cat','03-MinimalSpanningTrees/Kruskal2.cat',
                    '03-MinimalSpanningTrees/Kruskal3.cat',
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Prim2.cat'
                ]   
            },
            {
                'title': 'Prim\'s Algorithm',
                'file': 'Prim.alg',
                'description': 'Prim\'s Algorithm computes a minimum spanning tree in a ' \
                'connected, weighted graph.',
                'graphs': [
                    '03-MinimalSpanningTrees/Kruskal1.cat','03-MinimalSpanningTrees/Kruskal2.cat',
                    '03-MinimalSpanningTrees/Kruskal3.cat',
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Prim2.cat'
                ]
            },
            {
                'title': 'Matroid Dual of Kruskal\'s Algorithm',
                'file': 'MatroidDualKruskal.alg',
                'description': 'An implementation of a matroid dual of Kruskal\'s Algorithm.', 
                'graphs': [
                    '03-MinimalSpanningTrees/Kruskal1.cat','03-MinimalSpanningTrees/Kruskal2.cat',
                    '03-MinimalSpanningTrees/Kruskal3.cat',
                    '03-MinimalSpanningTrees/Prim1.cat','03-MinimalSpanningTrees/Prim2.cat'
                ]
            },
        ]
    },
    {
        'chapter_directory': '04-LPDuality',
        'chapter_number': 4,
        'title': 'Linear Programming Duality',
        'shortened_title': 'Linear Programming Duality',
        'algorithms': [
            {
                'title': 'Primal Dual of Kruskal\'s Algorithm',
                'file': 'PrimalDualKruskal.alg',
                'description': 'A primal dual version of Kruskal\'s Algorithm.',
                'graphs': [
                    '04-LPDuality/PD_Kruskal1.cat','04-LPDuality/PD_Kruskal2.cat',
                    '04-LPDuality/PD_Kruskal3.cat', '04-LPDuality/PD_Kruskal4.cat',
                    '04-LPDuality/PD_Kruskal5.cat'
                ]
            }
        ]
    },
    {
        'chapter_directory': '05-ShortestPaths',
        'chapter_number': 5,
        'title': 'Shortest Paths',
        'shortened_title': 'Shortest Paths',
        'algorithms': [
            {
                'title': 'Dijkstra\'s Algorithm',
                'file': 'Dijkstra.alg',
                'description': 'Dijkstra\'s algorithm for finding a shortest path tree in ' \
                'a graph. This is an example of a label setting algorithm.',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected02.cat',
                    '05-ShortestPaths/ShortestPathsUndirected03.cat',
                    '05-ShortestPaths/7x7grid.cat',
                    '05-ShortestPaths/NegCircuit.cat', 
                    '05-ShortestPaths/NegArc.cat'
                ]
            },
            {
                'title': 'Dijkstra\'s Algorithm using a Priority Queue',
                'file': 'DijkstraPQ.alg',
                'description': 'Dijkstra\'s algorithm for finding a shortest path tree in a ' \
                'graph implemented using a Priority Queue.',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected02.cat',
                    '05-ShortestPaths/ShortestPathsUndirected03.cat',
                    '05-ShortestPaths/7x7grid.cat',      
                    '05-ShortestPaths/NegArc.cat',
                    '05-ShortestPaths/NegCircuit.cat'                   
                ]
            },
            {
                'title': 'Find Path',
                'file': 'FindPath.alg',
                'description': 'A variant of Dijkstra\'s algorithm for finding a shortest s-t ' \
                'path in a graph. Terminates early, as soon as a shortest s-t path has been found.',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected03.cat',
                    '05-ShortestPaths/ShortestPathsUndirected06.cat',
                    '05-ShortestPaths/7x7grid.cat'
                ]
            },
            {
                'title': 'Find Path in an Euclidean Graph',
                'file': 'FindPathEuclid.alg',
                'description': 'A variant of Dijkstra\'s algorithm for finding a shortest s-t ' \
                'path in an Euclidean graph (edge weights correspond to Euclidean distance ' \
                'between vertices). Terminates early, as soon as a shortest s-t path has been ' \
                'found and only visits a small part of the graph. Similar ideas are used in ' \
                'A*-type algorithms.',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected03.cat',
                    '05-ShortestPaths/ShortestPathsUndirected06.cat',
                    '05-ShortestPaths/7x7grid.cat'
                 ]
            },
            {
                'title': 'Bellman Ford',
                'file': 'BellmanFord.alg',
                'description': 'Bellman and Ford\'s algorithm for finding a shortest path tree in ' \
                'a graph with a label correcting approach.',
                'graphs': [
                    '05-ShortestPaths/ShortestPathsUndirected02.cat',
                    '05-ShortestPaths/ShortestPathsUndirected03.cat',
                    '05-ShortestPaths/7x7grid.cat',
                    '05-ShortestPaths/BellmanFordWC.cat',
                    '05-ShortestPaths/NegArc.cat'
                ]
            },
            {
                'title': 'Finding Negative Circuits',
                'file': 'NegativeCircuits.alg',
                'description': 'Most shortest path algorithms require that graphs do not have ' \
                    'negative circuits. This algorithms detects negative circuits in a graph.',
                'graphs': [
                    '05-ShortestPaths/NegCircuit.cat',
                    '05-ShortestPaths/NegCircuit2.cat'
                ]
            },
            {
                'title': 'Find Path from Two Sources',
                'file': 'TwoSources.alg',
                'description': 'Finding a path can be accelerated by searching from start and ' \
                'destination simultaneously.',
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
        'shortened_title': 'Maximal Flows',
        'algorithms': [
            {
                'title': 'The Ford-Fulkerson Algorithm',
                'file': 'FordFulkerson.alg',
                'description': 'The Ford-Fulkerson algorithm finds a maximal flow in a ' \
                'capacitated network by successive shortest path applications.',
                'graphs': [
                    '06-MaximalFlows/FordFulkerson1.cat',
                    '06-MaximalFlows/FordFulkerson4.cat',
                    '06-MaximalFlows/FordFulkerson6.cat',
                    '06-MaximalFlows/FordFulkersonBad.cat',
                    '06-MaximalFlows/FordFulkersonWC.cat',
                    '06-MaximalFlows/PreflowPushWC.cat',
                    '06-MaximalFlows/EdmondsKarpWC.cat'
                ]
            },
            {
                'title': 'Preflow Push',
                'file': 'PreflowPush.alg',
                'description': 'The Preflow Push algorithm due to Goldberg and Tarjan ' \
                'computes a maximal flow by saturating a network and correcting possible ' \
                'excesses later.',
                'graphs': [
                    '06-MaximalFlows/PreflowPush1.cat',
                    '06-MaximalFlows/PreflowPush6.cat',
                    '06-MaximalFlows/FordFulkerson1.cat',
                    '06-MaximalFlows/FordFulkerson4.cat',
                    '06-MaximalFlows/FordFulkerson6.cat',
                    '06-MaximalFlows/FordFulkersonBad.cat',
                    '06-MaximalFlows/FordFulkersonWC.cat',
                    '06-MaximalFlows/PreflowPushWC.cat'
                ]
            }
        ]
    },
    {
        'chapter_directory': '07-MinimumCostFlows',
        'chapter_number': 7,
        'title': 'Minimum-Cost Flows',
        'shortened_title': 'Minimum-Cost Flows',
        'algorithms': [
            {
                'title': 'Negative Cycle Canceling',
                'file': 'NegativeCycleCanceling.alg',
                'description': 'The Negative Cycle Canceling algorithm establishes a maximal flow ' \
                'and reduces costs by finding negative circuits.',
                'graphs': [
                    '07-MinimumCostFlows/MCF4to1A.cat', '07-MinimumCostFlows/MCFCycle.cat'
                ]
            },
            {
                'title': 'Successive Shortest Paths',
                'file': 'SuccessiveShortestPath.alg',
                'description': 'This algorithm finds a minimum cost flow by repeatedly ' \
                'finding shortest, augmenting paths.',
                'graphs': [
                    '07-MinimumCostFlows/MCF4to1A.cat', '07-MinimumCostFlows/MCFCycle.cat'
                ]
            },
            {
                'title': 'Cost Scaling',
                'file': 'CostScaling.alg',
                'description': 'The cost scaling algorithm directly operates on the bits ' \
                'of the cost function.',
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
        'shortened_title': 'Matching',
        'algorithms': [
            {
                'title': 'Bipartite',
                'file': 'Bipartite.alg',
                'svg_file': 'Bipartite_app.alg',
                'description': 'This algorithm finds a maximal cardinality matching ' \
                'in a bipartite graph. In other words it maximizes the number of matched ' \
                'vertices.',
                'graphs': [
                    '08-Matching/Bi003.cat', '08-Matching/Bi006.cat', '08-Matching/Bi008.cat',
                    '08-Matching/Bi009.cat', '08-Matching/Bi010.cat'
                ]
            },
            {
                'title': 'Cardinality Matching',
                'file': 'CardinalityMatching.alg',
                'svg_file': 'CardinalityMatching_app.alg',
                'description': 'This algorithm finds a maximal cardinality matching in graphs ' \
                'which are not necessarily bipartite.',
                'graphs': [
                    '08-Matching/Edmonds1.cat', '08-Matching/Edmonds3.cat',
                    '08-Matching/Edmonds6.cat', '08-Matching/Edmonds8.cat', '08-Matching/Koenig.cat'
                ]
            }
        ]
    },

    {
        'chapter_directory': '09-WeightedMatching',
        'chapter_number': 9,
        'title': 'Weighted Matching',
        'shortened_title': 'Weighted Matching',
        'algorithms': [
            {
                'title': 'Weighted Matching',
                'file': 'WeightedMatching.alg',
                'description': 'This algorithm considers vertices as points in 2-dimensional ' \
                'space and implicitly assumes the existence of all edges in the complete ' \
                'graph. Furthermore, edge weights are Euclidean. It finds a matching of minimal ' \
                'weight. The matching is perfect if the number of vertices is even', 
                'graphs': [
                    '09-WeightedMatching/twotriangles.cat', '09-WeightedMatching/3223.cat',
                    '09-WeightedMatching/11vs13.cat'
                ]
            }
        ]
    }
]

svg_instance = [
    {
        'chapter_directory': '09-WeightedMatching',
        'chapter_number': 9,
        'title': 'Weighted Matching',
        'shortened_title': 'Weighted Matching',
        'algorithms': [
            {
                'title': 'Weighted Matching',
                'file': 'WeightedMatching.alg',
                'description': 'This algorithm considers vertices as points in 2-dimensional ' \
                'space and implicitly assumes the existence of all edges in the complete ' \
                'graph. Furthermore, edge weights are Euclidean. It finds a matching of minimal ' \
                'weight. The matching is perfect if the number of vertices is even', 
                'graphs': [
                    '09-WeightedMatching/twotriangles.cat'
                ]
            }
        ]
    }
]

alphabetic_algorithms = [
    {'algo_div_id': 'BellmanFord', 'title': 'Bellman Ford'}, 

    {'algo_div_id': 'Bipartite', 'title': 'Bipartite'}, 

    {'algo_div_id': 'IterativeBFS', 'title': 'Iterative BFS'}, 
    {'algo_div_id': 'BFSComponents', 'title': 'BFS-Components'}, 
    {'algo_div_id': 'BFStoDFS', 'title': 'BFS to DFS'}, 

    {'algo_div_id': 'CardinalityMatching', 'title': 'Cardinality Matching'}, 

    {'algo_div_id': 'CostScaling', 'title': 'Cost Scaling'}, 

    {'algo_div_id': 'DFSRecursive', 'title': 'DFS Recursive'}, 
    {'algo_div_id': 'IterativeDFS', 'title': 'Iterative DFS'}, 

    {'algo_div_id': "Dijkstra'sAlgorithm", 'title': "Dijkstra's Algorithm"}, 
    {'algo_div_id': "Dijkstra'sAlgorithmusingaPriorityQueue", 'title': "Dijkstra's Algorithm using a Priority Queue"}, 

    {'algo_div_id': 'FindingNegativeCircuits', 'title': 'Finding Negative Circuits'},

    {'algo_div_id': 'FindPath', 'title': 'Find Path'}, 
    {'algo_div_id': 'FindPathfromTwoSources', 'title': 'Find Path from Two Sources'}, 
    {'algo_div_id': 'FindPathinanEuclideanGraph', 'title': 'Find Path in an Euclidean Graph'}, 

    {'algo_div_id': 'TheFordFulkersonAlgorithm', 'title': 'The Ford-Fulkerson Algorithm'}, 

    {'algo_div_id': "Kruskal'sAlgorithm", 'title': "Kruskal's Algorithm"}, 
    {'algo_div_id': "Kruskal'sAlgorithmusingFindCircuit", 'title': "Kruskal's Algorithm using FindCircuit"}, 
    {'algo_div_id': "EfficientKruskal'sAlgorithm", 'title': "Efficient Kruskal's Algorithm"}, 
    {'algo_div_id': "InefficientKruskal'sAlgorithm", 'title': "Inefficient Kruskal's Algorithm"}, 
    {'algo_div_id': "MatroidDualofKruskal'sAlgorithm", 'title': "Matroid Dual of Kruskal's Algorithm"}, 
    {'algo_div_id': "PrimalDualofKruskal'sAlgorithm", 'title': "Primal Dual of Kruskal's Algorithm"}, 

    {'algo_div_id': 'NegativeCycleCanceling', 'title': 'Negative Cycle Canceling'}, 

    {'algo_div_id': 'PreflowPush', 'title': 'Preflow Push'}, 

    {'algo_div_id': "Prim'sAlgorithm", 'title': "Prim's Algorithm"}, 

    {'algo_div_id': 'SuccessiveShortestPaths', 'title': 'Successive Shortest Paths'}, 

    {'algo_div_id': 'WeightedMatching', 'title': 'Weighted Matching'}
]

#
# Dictionary of graph name substitutes(e.g. if a graph name is too long we can map it to a different name here, and the sub will be used in the index page)
#
friendly_graph_names = {
    'ShortestPathsUndirected01': 'Shortest Paths Undirected 01',
    'ShortestPathsUndirected02': 'Shortest Paths Undirected 02',
    'ShortestPathsUndirected03': 'Shortest Paths Undirected 03',
    'ShortestPathsUndirected04': 'Shortest Paths Undirected 04',
    'ShortestPathsUndirected05': 'Shortest Paths Undirected 05',
    'ShortestPathsUndirected06': 'Shortest Paths Undirected 06',
}

# Keys: e.g. '09-WeightedMatching/k4.cat', values: graph description
graph_descriptions = {
    #'02-GraphsNetworks/BFS.cat': 'BFS Graph Description'
}

def create_svg_index_page(graph_pngs):
    ''' Creates an HTML index page that leads to the SVG 
        animations generated from the svg_instance dictionary
    '''
    import jinja2
    svg_locations = {}
    for chapter_dict in svg_instance:
        for algo in chapter_dict['algorithms']:
            algo_name = os.path.splitext(algo['file'])[0]
            algo['algo_div_id'] = algo['title'].replace(' ', '').replace('-', '')
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
                'svg_locations': svg_locations,
                'alphabetic_algorithms': alphabetic_algorithms
             }))

def should_generate_animation(algo_file_name, graph_file_name, svg_file_name):
    # If the svg we have is more current than all it's component files then we don't
    # have to generate the animation
    catbox_path = os.path.split(algo_file_name)[0]
    algo_pro_file_name = os.path.splitext(os.path.basename(algo_file_name))[0] + '.pro'
    if os.path.isfile(svg_file_name):
        svg_age = os.path.getmtime(svg_file_name)
    else: # File does not exist, so generate 
        return True
    graph_age = os.path.getmtime(graph_file_name)
    pro_age = os.path.getmtime(os.path.join(catbox_path, algo_pro_file_name))
    algo_age = os.path.getmtime(algo_file_name)
    webgato_js_age = os.path.getmtime('WebGatoJS.py')
    this_age = os.path.getmtime('GatoTest.py')

    if svg_age > max(graph_age, pro_age, algo_age, webgato_js_age, this_age):
        return False
    return True

def should_generate_png(algo_file_name, graph_file_name, png_file_name):
    # If the png we have is more current than the graph/algo combo it came from then we don't have to re-generate
    catbox_path = os.path.split(algo_file_name)[0]
    algo_pro_file_name = os.path.splitext(os.path.basename(algo_file_name))[0] + '.pro'
    if os.path.isfile(png_file_name):
        png_age = os.path.getmtime(png_file_name)
    else: # File does not exist, so generate 
        return True
    graph_age = os.path.getmtime(graph_file_name)
    pro_age = os.path.getmtime(os.path.join(catbox_path, algo_pro_file_name))
    algo_age = os.path.getmtime(algo_file_name)

    if png_age > max(graph_age, pro_age, algo_age):
        return False
    return True

#------------------------------------------------------------------
def usage():
    print "Usage: GatoTest.py"
    print "       GatoTest.py -v -d"
    print "               -v or --verbose switches on the logging information"
    print "               -d or --debug switches on the debugging  information"
    print "               -s or --svg generates svg animations if the animation sources have been updated"
    print "               -f or --force_animation used with -s to force generation of svg animations, even if there have been no updates"



if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "asdvtf",
                                   ["all", "svg","debug","verbose", "test", "force_animation"])
    except getopt.GetoptError:
        usage()
        exit()

    print "Welcome to GatoTest!"

    all = False
    svg = False
    force_animation = False
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
        if o in ("-f", "--force_animation"):
            force_animation = True
            
            
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
        print "# Producing SVG output"
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
                    print "=== TEST === "+algo['file']+" === "+graph_file+" ==="
                    graph_name = os.path.splitext(os.path.basename(graph_file))[0]
                    png_file_name = 'svgs/img/%s--%s.png' % (os.path.splitext(algo['file'])[0], graph_name)
                    svg_file_name = 'svgs/%s--%s.html' % (os.path.splitext(algo['file'])[0], graph_name)
                    algo_location = testPath + chapter_dict['chapter_directory'] + '/' + algo.get('svg_file', algo['file'])

                    generate_anim = should_generate_animation(algo_location, testPath+graph_file, svg_file_name)
                    generate_png = should_generate_png(algo_location, testPath+graph_file, png_file_name) or force_animation
                    if generate_anim or generate_png or force_animation:
                        app.OpenAlgorithm(algo_location)
                        app.OpenGraph(testPath + graph_file)
                        g.Interactive = 0 # This is set to 0 above.  Do we need to do it here as well?
                        g.GeneratingSVG = 1
                        app.algorithm.ClearBreakpoints()
                        app.update_idletasks()
                        app.update()
                        app.update_idletasks()
                        app.update()
                        # coordinate_diff = app.GetSVGCoordinateDiff()
                        # Run it ...
                        app.after_idle(app.CmdContinue) # after idle needed since CmdStart
                        # does not return
                        app.CmdStart()
                        app.update_idletasks()

                        # Generate the SVG
                        app.ExportSVGAnimation(svg_file_name, chapter_number=chapter_dict['chapter_number'], 
                            algo_div=algo['title'].replace(' ', '').replace('-',''),
                            chapter_name=chapter_dict['title'])
                    else:
                        print "Animation already generated, skipping."

                    if generate_png:
                        # Generate the PNG
                        index_page_graph_name = friendly_graph_names.get(graph_name, graph_name)
                        if png_file_name not in graph_pngs and has_png_libs:
                            # png_dimensions = app.ExportSVG(png_file_name, write_to_png=True, start_graph_coord_diff=coordinate_diff)
                            png_dimensions = app.ExportSVG(png_file_name, write_to_png=True)
                            path_from_index = '/'.join(png_file_name.split('/')[1:])
                            graph_pngs[algo['title'] + graph_file] = {'file': path_from_index, 'name': index_page_graph_name, 'width': png_dimensions['width'], 'height': png_dimensions['height']}
                        else:
                            from PIL import Image
                            img = Image.open(png_file_name)
                            graph_pngs[algo['title'] + graph_file] = {'file': '/'.join(png_file_name.split('/')[1:]), 'name': index_page_graph_name, 'width': img.size[0], 'height': img.size[1]}


        if has_png_libs and graph_pngs:
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

            
