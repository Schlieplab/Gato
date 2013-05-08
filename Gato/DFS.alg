root = PickVertex()
S.Push(root)
pred[root] = root
step = 1

while S.IsNotEmpty():
    v = S.Pop()
    if not label[v]:
        label[v] = step
        step += 1
        for w in Neighborhood(v):
            if not label[w]:
                S.Push(w)
                pred[w] = v
