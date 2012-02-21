################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   AnimationHistory.py
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

import time
import GatoGlobals
import inspect

g = GatoGlobals.AnimationParameters


class AnimationCommand:


    def __init__(self, method, target, args, kwargs={},
                 undo_method=None, undo_args=None, canUndo=True):
        self.target = target
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.canUndo = canUndo
        self.undo_method = undo_method
        self.undo_args = undo_args

        self.time = time.time()

    def CanUndo(self):
        return self.canUndo
        
    def Do(self):
        #return apply(self.method, self.target + self.args)
        args = self.target + self.args
        return self.method(*args,**self.kwargs)
        
        
    def Undo(self):
        if self.canUndo:
            if self.undo_method == None:
                apply(self.method, self.target + self.undo_args)
            else:
                apply(self.undo_method, self.target + self.undo_args)


    def __repr__(self):
        return self.log_str()

    def log_str(self):
        if len(self.target) == 1:
            t = self.target[0]
        else:
            t = self.target

        if self.kwargs:
            kwstr = ["%s=%s" % (str(key),str(val)) for key,val in self.kwargs.items()]
            kwstr = ",".join(kwstr)
        else:
            kwstr = ''
           
        if len(self.args) == 0:
            return "%s(%s) %s" % (self.method.__name__, t, kwstr)
        elif len(self.args) == 1:
            argstr = str(self.args[0])
        else:
            argstr = ",".join(self.args)
                
        return "%s(%s,%s) %s" % (self.method.__name__, t, argstr, kwstr)      


class AnimationHistory:
    """AnimationHistory provides a history of animation commands, and a undo and
       redo facility. It is to be used as a wrapper around a GraphDisplay and it
       will happily dispatch all calls to GraphDisplay.
    
       Animation commands for which undo/redo is provided, have to be methods of
       AnimationHistory.

       If AnimationHistory.auto_print is true, textual representations of animation
       commands are written to stdout to allow regression testing of animations.

       This might also be helpful in debugging.

       The AnimationHistory is also used for providing SVG output of animations.

       
       XXX Maybe decorators for graph display would be a better way to implement
       it. Here we incurr overhead for every method call
    """
    def __init__(self, animator, logPrefix = ''):
        """ We wrap animator. If self.auto_print is true, then we prepend the
            logPrefix to the output
        """
        self.animator = animator
        self.history = []
        self.history_index = None
        self.auto_print = 0
        self.logPrefix = logPrefix
        self.g = g

        
    #========== Provide Undo/Redo for animation commands from GraphDisplay ======
    def SetVertexColor(self, v, color):
        animation = AnimationCommand(self.animator.SetVertexColor, (v,), (color,), 
                                     undo_args=(self.animator.GetVertexColor(v),))
        animation.Do()
        self.append(animation)

    def SetAllVerticesColor(self, color, graph=None, vertices=None):
        #print "SetAllVerticesColor", color, graph, vertices
        if graph:
            vertices = graph.Vertices()
        if vertices:
            animation = AnimationCommand(self.animator.SetAllVerticesColor,
                                         (color,),(),
                                         kwargs={'vertices':vertices},
                                         canUndo=False)
        else:
            animation = AnimationCommand(self.animator.SetAllVerticesColor, (color,), (),
                                         canUndo=False)        
        animation.Do()
        self.append(animation)
        
        

    def SetAllEdgesColor(self, color, graph=None, edges=None):
        if graph:
            edges = graph.Edges()
        if edges:
            animation = AnimationCommand(self.animator.SetAllEdgesColor,
                                    (color,),(), kwargs={'edges':edges},
                                        canUndo=False)
        else:
            animation = AnimationCommand(self.animator.SetAllEdgesColor, (color,), (),
                                        canUndo=False)        
        animation.Do()
        self.append(animation)
        
    #Recently added, beware
    #Need to handle directed/undirected differently?
    def SetEdgesColor(self, edges, color):
        #print "In setEdgesColor in AnimationHistory"
        for head, tail in edges:
            animation = AnimationCommand(self.animator.SetEdgeColor, (tail,head), 
                                        (color,), canUndo = False)
            animation.Do()
            self.append(animation)
            
            
    def SetEdgeColor(self, tail, head, color):
        tail, head = self.animator.G.Edge(tail, head)
        animation = AnimationCommand(self.animator.SetEdgeColor, (tail,head), (color,),
                                     undo_args=(self.animator.GetEdgeColor(tail,head),))
        animation.Do()
        self.append(animation)
        
    def BlinkVertex(self, v, color=None):
        animation = AnimationCommand(self.animator.BlinkVertex, (v,), (color,))
        animation.Do()
        self.append(animation)
        
    def BlinkEdge(self, tail, head, color=None):
        tail, head = self.animator.G.Edge(tail, head)
        animation = AnimationCommand(self.animator.BlinkEdge, (tail,head), (color,))
        animation.Do()
        self.append(animation)
        
        
    def SetVertexFrameWidth(self, v, val):
        animation = AnimationCommand(self.animator.SetVertexFrameWidth, (v,), (val,),
                                     undo_args=(self.animator.GetVertexFrameWidth(v),))
        animation.Do()
        self.append(animation)
        
    def SetVertexAnnotation(self, v, annotation,color="black"):
        animation = AnimationCommand(self.animator.SetVertexAnnotation, (v,), (annotation,),
                                     undo_args=(self.animator.GetVertexAnnotation(v),))
        animation.Do()
        self.append(animation)


    def AddVertex(self, x, y, v = None):
        if v:
            animation = AnimationCommand(self.animator.AddVertex, (x,y), (v,),
                                         
                                         canUndo=False)
        else:
            animation = AnimationCommand(self.animator.AddVertex, (x,y), (),
                                         canUndo=False)
        result = animation.Do()
        self.append(animation)
        return result

    def AddEdge(self, tail, head):
        animation = AnimationCommand(self.animator.AddEdge, (tail,head), (),
                                     canUndo=False)
        animation.Do()
        self.append(animation)

    def DeleteEdge(self, tail, head, repaint=1):
        animation = AnimationCommand(self.animator.DeleteEdge, (tail,head), (repaint,),
                                     canUndo=False)
        animation.Do()
        self.append(animation)
        
    def DeleteVertex(self, v):
        #Delete all edges containing v
        #Call deletevertex command
        for d in self.animator.drawEdges.keys():
            if d[0]==v or d[1]==v:
                self.DeleteEdge(d[0], d[1])
        animation = AnimationCommand(self.animator.DeleteVertex, (v,), (), canUndo=False)
        animation.Do()
        self.append(animation)
        
        
        

    #def HighlightPath(self, path, color, closed):
    #    XXXIMPLEMENTME
            
        
    #========== Handle all other methods from GraphDisplay =====================
    def __getattr__(self,arg):
        # XXX This is broken. Calls to self.animator methods as args
        # in self.animator method calls should fail. NOT sure about
        # this
        tmp = getattr(self.animator,arg)
        #print "###AnimationHistory.__getattr__ ", arg
        if callable(tmp):
            self.methodName = arg
            self.method = tmp
            return getattr(self,'caller')
        else:
            return self.animator.__dict__[arg]
            
    def caller(self, *args, **keywords):
        # XXX This is broken with kw arguments
        #return apply(self.method,args)
        return self.method(*args, **keywords)
        
    #========== AnimationHistory methods =======================================
    def Undo(self):
        """ Undo last command if there is one and if it can be undone """
        if self.history_index == None: # Have never undone anything
            self.history_index = len(self.history) - 1
            
        if self.history_index >= 0:
            if self.history[self.history_index].CanUndo():            
                self.history[self.history_index].Undo()
                self.history_index -= 1
                #blink the element that can't be undone
                #Need to know if it's a vertex or edge
                #if deleted no blink
            
    def Do(self):
        if self.history_index is None:
            return
        if self.history_index >= len(self.history):
            self.history_index = None
        else:       
            self.history[self.history_index].Do()
            self.history_index += 1
            
    def DoAll(self):
        # Catchup
        if self.history_index is not None:
            for cmd in self.history[self.history_index:]:     #formerly time, cmd
                if cmd.canUndo:
                    #if cmd cannot undo, then it is the one blocking further undoes, do not do command
                    cmd.Do()
            self.history_index = None
            
    def Replay(self):
        if len(self.history) > 1 and self.history[-1].CanUndo():
            self.history[-1].Undo()
            self.animator.update()
            self.animator.canvas.after(10 * g.BlinkRate)
            self.history[-1].Do()
            self.animator.update()
            self.animator.canvas.after(10 * g.BlinkRate)
            self.history[-1].Undo()
            self.animator.update()
            self.animator.canvas.after(10 * g.BlinkRate)
            self.history[-1].Do()
            self.animator.update()
            
    def append(self, animation):
        if self.auto_print:
            print self.logPrefix + animation.log_str() 
        self.history.append(animation)
        

    def Clear(self):
        self.history = []
        self.history_index = None
        
