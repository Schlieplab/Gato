root = PickVertex()
Q.Append(root)
pred[root] = root
step = 1

while Q.IsNotEmpty():
    v = Q.Top()
    label[v] = step
    step = step + 1
    for w in Neighborhood(v):
        if not pred[w]:
            Q.Append(w)
            pred[w] = v
                
