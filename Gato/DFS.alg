
for v in Vertices:
    visited[v] = 0	
	
root = PickVertex()
S.Push(root)

while S.IsNotEmpty():
    v = S.Pop()
    print "# ", v
    for w in Neighborhood(v):
	if visited[w] == 0:
	    print " ",w
	    visited[w] = 1
	    S.Push(w)

