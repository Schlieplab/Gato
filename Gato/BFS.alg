for v in Vertices:
    visited[v] = 0	
	
root = PickVertex()
Q.Append(root)

while Q.IsNotEmpty():
    v = Q.Top()
    # print "# ", v
    for w in Neighborhood(v):
	if visited[w] == 0:
	    #print " ",w
	    visited[w] = 1
	    Q.Append(w)

