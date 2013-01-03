import math
#import Tkinter
#
#t = Tkinter.Text(A.canvas, width=20, height=2)
#w = A.canvas.create_window(500, 500, window=t, anchor="w", state='normal')
#t.insert('end', 'Hello World!!!')
#
#A.SetEdgeAnnotation(1,2,'bla-di-la')
A.MoveVertex(2, 200, 200, 1)
for i in range(1000):
    A.MoveVertex(1, 200+200*math.cos(i/500.0*math.pi), 200+200*math.sin(i/500.0*math.pi), 1)

