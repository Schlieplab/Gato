s = PickSource()
t = PickSink()

InitPotential(s,t)
for v in G.Neighborhood(s):
    flow[(s,v)] = cap((s,v))

feasible = False
while not feasible:

    pushed = False
    v = FindExcessVertex()

    if not v:
        feasible = True
    else:
        for u in Neighborhood(v):
            if pot[v] > pot[u]:
                delta = Min(res((v,u)),excess(v))
                if ForwardEdge(v,u):
                    flow[(v,u)] = flow[(v,u)] + delta
                else:
                    flow[(u,v)] = flow[(u,v)] - delta
                pushed = True
                break
        if not pushed:
            pot[v] = minResNeighborPot(v)+1

ShowCut(s)
