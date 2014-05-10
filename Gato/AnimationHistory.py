################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   AnimationHistory.py
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
import sys
import inspect
import time
import GatoGlobals
import MergedHistories
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

        #if self.method.__name__ == 'SetAllVerticesColor':
        #    print 'it is:', self.kwargs
        #    print id(self)

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
        # Handle the two methods that only have strings for method attr
        """if self.method == "UpdateGraphInfo":
            return '%s("%s")' % (self.method, self.args[0])
        if self.method == "UpdateEdgeInfo":
            return '%s(%s, %s, "%s")' % (self.method, self.target[0], self.target[1], self.args[0])
        """
        # print self.method.__name__
        # print self.args

        if len(self.target) == 1:
            t = self.target[0]
        else:
            t = self.target

        if self.kwargs:
            kwstr = ["%s=%s" % (str(key),str(val)) for key,val in self.kwargs.items()]
            # if 'SetAll' in self.method.__name__:
            #     print 'kwargs: ', self.kwargs
            #     print 'kwstr: ', kwstr
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
    def __init__(self, animator, logPrefix = '', displayNum=1):
        """ We wrap animator. If self.auto_print is true, then we prepend the
            logPrefix to the output
        """
        self.animator = animator
        self.history = []
        self.history_index = None
        self.auto_print = 0
        self.logPrefix = logPrefix
        self.g = g
        self.displayNum = displayNum
        """if displayNum == 2:
            print "We're in display 2"
        else:
            print "We're in display 1"""
        AnimationHistory.merged = MergedHistories.MergedHistories()
        
    def UpdateEdgeInfo(self, tail, head, info):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.UpdateEdgeInfo(tail, head, info, self.animator, self.displayNum)

    def UpdateGraphInfo(self, info):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.UpdateGraphInfo(info, self.animator, self.displayNum)

    def UpdateVertexInfo(self, v, info):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.UpdateVertexInfo(v, info, self.animator, self.displayNum)
        
    #========== Provide Undo/Redo for animation commands from GraphDisplay ======
    def SetVertexColor(self, v, color):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetVertexColor(v, color, self.animator, self.displayNum)
       
    def Wait(self):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.Wait(self.animator, self.displayNum)

    def SetAllVerticesColor(self, color, graph=None, vertices=None):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetAllVerticesColor(color, self.animator, self.displayNum, graph, vertices)
        
    def SetAllEdgesColor(self, color, graph=None, leaveColor=None, edges=None):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetAllEdgesColor( color, self.animator, self.displayNum, leaveColor, graph, edges)
       
    #Need to handle directed/undirected differently?
    def SetEdgesColor(self, edges, color):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetEdgesColor(edges, color, self.animator, self.displayNum)
        
    def SetEdgeColor(self, tail, head, color):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetEdgeColor(tail, head, color, self.animator, self.displayNum)
        
    def BlinkVertex(self, v, color=None):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.BlinkVertex(v, self.animator, self.displayNum, color)
       
    def BlinkEdge(self, tail, head, color=None):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.BlinkEdge(tail, head, self.animator, self.displayNum, color)

    def CreateBubble(self, vertex_nums, offset_value, color):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.CreateBubble(vertex_nums, offset_value, color, self.animator, self.displayNum)
       

    def ResizeBubble(self, vertex_nums, new_radius):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.ResizeBubble(vertex_nums, new_radius, self.animator, self.displayNum)

    def DeleteBubble(self, vertex_nums):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.DeleteBubble(vertex_nums, self.animator, self.displayNum)


    def CreateMoat(self, moat_id, radius, color):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.CreateMoat(moat_id, radius, color, self.animator, self.displayNum)
       
    def GrowMoat(self, moat_id, radius):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.GrowMoat(moat_id, radius, self.animator, self.displayNum)

    def SetVertexFrameWidth(self, v, val):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetVertexFrameWidth(v, val, self.animator, self.displayNum)
        
    def SetVertexAnnotation(self, v, annotation,color="black"):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.SetVertexAnnotation(v, annotation, self.animator, self.displayNum, color)
        
    def AddVertex(self, x, y, v = None):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        return AnimationHistory.merged.AddVertex(x, y, self.animator, self.displayNum, v)  
        
    def AddEdge(self, tail, head):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.AddEdge(tail, head, self.animator, self.displayNum)
       
    def DeleteEdge(self, tail, head, repaint=1):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.DeleteEdge(tail, head, self.animator, self.displayNum, repaint)
        
        
    def DeleteVertex(self, v):
        #Delete all edges containing v
        #Call deletevertex command
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.DeleteVertex(v, self.animator, self.displayNum)
        

    def HighlightPath(self, path, color, closed=0):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        return AnimationHistory.merged.HighlightPath(path, color, self.animator, self.displayNum, closed)  

    def HidePath(self, pathID):
        if self.auto_print == 1:
            AnimationHistory.merged.auto_print = 1
        AnimationHistory.merged.HidePath(pathID, self.animator, self.displayNum)  

    #========== Handle all other methods from GraphDisplay =====================
    def __getattr__(self,arg):
        # XXX This is broken. Calls to self.animator methods as args
        # in self.animator method calls should fail. NOT sure about
        # this
        tmp = getattr(self.animator,arg)
        if callable(tmp):
            return tmp
        else:
            return self.animator.__dict__[arg]
            
    #========== AnimationHistory methods =======================================
    def Undo(self):
        """ Undo last command if there is one and if it can be undone """
        AnimationHistory.merged.Undo()
                
    def Do(self):
        AnimationHistory.merged.Do()
        
    def DoAll(self):
        AnimationHistory.merged.DoAll()
        
    def Replay(self):
        AnimationHistory.merged.Replay()
       
    #Deprecated Function
    def append(self, animation):
        if self.auto_print:
            print self.logPrefix + animation.log_str() 
        self.history.append(animation)
        

    def Clear(self):
        self.history = []
        self.history_index = None
        
    def getHistoryOne(self):
        return AnimationHistory.merged.getHistoryOne()
    
    def getHistoryTwo(self):
        return AnimationHistory.merged.getHistoryTwo()
        
