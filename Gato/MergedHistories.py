################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       You can find more information at 
#       http://gato.sf.net
#
#	file:   AnimatedDataStructures.py
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
#       This file is version $Revision: 455 $ 
#                       from $Date: 2012-02-14 16:45:23 -0500 (Tue, 14 Feb 2012) $
#             last change by $Author: smerking $.
#
################################################################################

import GatoGlobals
import AnimationHistory
import traceback

g = GatoGlobals.AnimationParameters

class MergedHistories:

    # TODO: Replace repetitive code with functions

    def __init__(self):
        self.history = []
        self.history_index = None
        self.animator1 = None
        self.animator2 = None
        self.auto_print = 0

    def _check_animator_set(self, animator, display):
        if self.animator1 is None:
            if display == 1:
                self.animator1 = animator
        if self.animator2 is None:
            if display == 2:
                self.animator2 = animator

    def UpdateEdgeInfo(self, tail, head, info, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.UpdateEdgeInfo, (tail, head), (info,))
        self.append(animation, display)

    def UpdateGraphInfo(self, info, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.UpdateGraphInfo, (), (info,))
        self.append(animation, display)

    def UpdateVertexInfo(self, v, info, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.UpdateVertexInfo, (v,), (info,))
        self.append(animation, display)

    def SetVertexColor(self, v, color, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.SetVertexColor, (v,), (color,),
                                                            undo_args=(animator.GetVertexColor(v),))
        animation.Do()
        self.append(animation, display)
        
    #seperate the setAllVert call into component SetVertexColor calls?  Make it undoable
    def SetAllVerticesColor(self, color, animator, display, graph=None, vertices=None):
        self._check_animator_set(animator, display)
        if graph:
            vertices = graph.Vertices()
        if vertices:
            animation = AnimationHistory.AnimationCommand(animator.SetAllVerticesColor,
                                         (color,),(),
                                         kwargs={'vertices':vertices},
                                         canUndo=False)
        else:
            animation = AnimationHistory.AnimationCommand(animator.SetAllVerticesColor, (color,), (),
                                         canUndo=False)  
        animation.Do()
        self.append(animation, display)

    def SetAllEdgesColor(self, color, animator, display, leaveColor=None, graph=None, edges=None):
        self._check_animator_set(animator, display)
        if graph:
            edges = graph.Edges()
        if edges:
            animation = AnimationHistory.AnimationCommand(animator.SetAllEdgesColor,
                                    (color,),(), kwargs={'edges':edges, 'leaveColors':leaveColor},
                                        canUndo=False)
        else:
            animation = AnimationHistory.AnimationCommand(animator.SetAllEdgesColor, (color,), (),
                                        kwargs={'leaveColors':leaveColor}, canUndo=False)        
        animation.Do()
        self.append(animation, display)
        
    def SetEdgesColor(self, edges, color, animator, display):
        self._check_animator_set(animator, display)
        for head, tail in edges:
            animation = AnimationHistory.AnimationCommand(animator.SetEdgeColor, (tail,head), 
                                        (color,), canUndo = False)
            animation.Do()
            self.append(animation, display)
    
    def SetEdgeColor(self, tail, head, color, animator, display):
        self._check_animator_set(animator, display)
        tail, head = animator.G.Edge(tail, head)
        animation = AnimationHistory.AnimationCommand(animator.SetEdgeColor, (tail,head), (color,),
                                     undo_args=(animator.GetEdgeColor(tail,head),))
        animation.Do()
        self.append(animation, display)
       
    def BlinkVertex(self, v, animator, display, color=None):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.BlinkVertex, (v,), (color,))
        animation.Do()
        self.append(animation, display)

    def CreateBubble(self, vertex_nums, offset_value, color, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.CreateBubble, (), (vertex_nums, offset_value, color), canUndo=False)
        animation.Do()
        self.append(animation, display)

    def ResizeBubble(self, vertex_nums, new_radius, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.ResizeBubble, (), (vertex_nums, new_radius), canUndo=False)
        animation.Do()
        self.append(animation, display)

    def DeleteBubble(self, vertex_nums, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.DeleteBubble, (), (vertex_nums,), canUndo=False)
        animation.Do()
        self.append(animation, display)


    def CreateMoat(self, moat_id, radius, color, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.CreateMoat, (moat_id,), (radius,color), canUndo=False)
        animation.Do()
        self.append(animation, display)

    def GrowMoat(self, moat_id, radius, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.GrowMoat, (moat_id,), (radius,), canUndo=False)
        animation.Do()
        self.append(animation, display)
    
    def BlinkEdge(self, tail, head, animator, display, color=None):
        self._check_animator_set(animator, display)
        tail, head = animator.G.Edge(tail, head)
        animation = AnimationHistory.AnimationCommand(animator.BlinkEdge, (tail,head), (color,))
        animation.Do()
        self.append(animation, display)
        
    def SetVertexFrameWidth(self, v, val, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.SetVertexFrameWidth, (v,), (val,),
                                     undo_args=(animator.GetVertexFrameWidth(v),))
        animation.Do()
        self.append(animation, display)
        
    def SetVertexAnnotation(self, v, annotation, animator, display, color="black"):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.SetVertexAnnotation, (v,), (annotation,),
                                     undo_args=(animator.GetVertexAnnotation(v),))
        animation.Do()
        self.append(animation, display)
        
    def AddVertex(self, x, y, animator, display, v = None):
        self._check_animator_set(animator, display)
        if v:
            animation = AnimationHistory.AnimationCommand(animator.AddVertex, (x,y), (v,),
                canUndo=False)
        else:
            animation = AnimationHistory.AnimationCommand(animator.AddVertex, (x,y), (),
                canUndo=False)
        result = animation.Do()
        if not v and result:
            animation = AnimationHistory.AnimationCommand(animator.AddVertex, (x,y), (result,),
                canUndo=False)
        self.append(animation, display)
        return result
        
    def AddEdge(self, tail, head, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.AddEdge, (tail,head), (),
                                     canUndo=False)
        animation.Do()
        self.append(animation, display)
        
    def Wait(self, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.Wait, (), (), canUndo=False)
        animation.Do()
        self.append(animation, display)

    def DeleteEdge(self, tail, head, animator, display, repaint=1):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.DeleteEdge, (tail,head), (repaint,),
                                     canUndo=False)
        animation.Do()
        self.append(animation, display)
        
    def DeleteVertex(self, v, animator, display):
        self._check_animator_set(animator, display)
        #Delete all edges containing v
        #Call deletevertex command
        for d in animator.drawEdges.keys():
            if d[0]==v or d[1]==v:
                self.DeleteEdge(d[0], d[1], animator, display)
        animation = AnimationHistory.AnimationCommand(animator.DeleteVertex, (v,), (), canUndo=False)
        animation.Do()
        self.append(animation, display)

    def HighlightPath(self, path, color, animator, display, closed=0):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.HighlightPath, (path,), (color,closed), canUndo=False)
        result = animation.Do()
        self.append(animation, display)
        return result
        # # XXXIMPLEMENTME
        # if self.auto_print == 1:
        #     AnimationHistory.merged.auto_print = 1
        # AnimationHistory.merged.HighlightPath(path, color, closed)

    def HidePath(self, pathID, animator, display):
        self._check_animator_set(animator, display)
        animation = AnimationHistory.AnimationCommand(animator.HidePath, (pathID,), (), canUndo=False)
        result = animation.Do()
        self.append(animation, display)
        
    def __getattr__(self,arg):
        print "Function tried to be called: ", arg
        raise AttributeError('Specified function of MergedHistories does not exist.')
            
    def Undo(self):
        """ Undo last command if there is one and if it can be undone """
        if self.history_index == None: # Have never undone anything
            self.history_index = len(self.history) - 1
            
        if self.history_index >= 0:
            if self.history[self.history_index][0].CanUndo():            
                self.history[self.history_index][0].Undo()
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
            self.history[self.history_index][0].Do()
            self.history_index += 1
            
    def DoAll(self):
        # Catchup
        if self.history_index is not None:
            for cmd, display in self.history[self.history_index:]:     #formerly time, cmd
                if cmd.canUndo:
                    #if cmd cannot undo, then it is the one blocking further undoes, do not do command
                    cmd.Do()
            self.history_index = None
            
    def Replay(self):
        if len(self.history) > 1 and self.history[-1][0].CanUndo():
            if self.history[-1][1] == 1:
                self.history[-1][0].Undo()
                self.animator1.update()
                self.animator1.canvas.after(10 * g.BlinkRate)
                self.history[-1][0].Do()
                self.animator1.update()
                self.animator1.canvas.after(10 * g.BlinkRate)
                self.history[-1][0].Undo()
                self.animator1.update()
                self.animator1.canvas.after(10 * g.BlinkRate)
                self.history[-1][0].Do()
                self.animator1.update()
            elif self.history[-1][1] == 2:  
                self.history[-1][0].Undo()
                self.animator2.update()
                self.animator2.canvas.after(10 * g.BlinkRate)
                self.history[-1][0].Do()
                self.animator2.update()
                self.animator2.canvas.after(10 * g.BlinkRate)
                self.history[-1][0].Undo()
                self.animator2.update()
                self.animator2.canvas.after(10 * g.BlinkRate)
                self.history[-1][0].Do()
                self.animator2.update()
            else:
                raise Error("Displaynum of function in merged history is neither 1 nor 2.")
            
    def append(self, animation, display):
        #if self.auto_print:
        #    print "disp" , display , "  " , animation.log_str() 
        tup = animation, display
        self.history.append(tup)
        
    def clear(self):
        self.history = []
        self.history_index = None
            
    def getHistoryOne(self):
        firstHistory = []
        for cmd in self.history:
            if cmd[1] == 1:
                firstHistory.append(cmd[0])
        return firstHistory
    
    def getHistoryTwo(self):
        secondHistory = []
        for cmd in self.history:
            if cmd[1] == 2:
                secondHistory.append(cmd[0])
        return secondHistory






















