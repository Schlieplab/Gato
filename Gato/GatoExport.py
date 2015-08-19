#!/usr/bin/env python2.6
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#   file:   GatoExport.py
#   author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 2010, Alexander Schliep, Winfried Hochstaettler and 
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
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1303.5  USA
#
#
#
#
#       This file is version $Revision: 353 $ 
#                       from $Date: 2010-06-03 14:58:37 -0400 (Thu, 03 Jun 2010) $
#             last change by $Author: schliep $.
#
################################################################################
import os
import StringIO
import tokenize
import re
import pdb
from bs4 import BeautifulSoup
from math import sqrt, pi, sin, cos, atan2, degrees, log10, floor, ceil
from WebGatoJS import animationhead

#Global constants for tokenEater
line_count = 1
keywordsList = [
          "del", "from", "lambda", "return",
          "and", "elif", "global", "not", "try",
          "break", "else", "if", "or", "while",
          "class", "except", "import", "pass",
          "continue", "finally", "in", "print",
          "def", "for", "is", "raise"]

operatorsList = ["+", "-", "*", "/", "^", "%", "=",
                 "+=", "-=", "*=", "/=", "^=", "%=",
                 ">", "<", "==", "!=", ">=", "<=",
                 "**", "<>", "|", "&", "<<", ">>",
                 "//", "~", "**="]

specialList = ["(", ",", ".", ")", "[", "]"]

begun_line = False
num_spaces = 0.0
algo_lines = []     # tokenEater uses this to write algorithm lines to
prev = ["",-1]
indent_stack = [0]
last_line = ''
id_prefixes = ['g1_', 'g2_']
svg_drop_shadow = '''
    <filter id="dropshadow" height="130%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="1"/> <!-- stdDeviation is how much to blur -->
        <feOffset dx="2.5" dy="2.5" result="offsetblur"/> <!-- how much to offset -->
        <feMerge> 
          <feMergeNode/> <!-- this contains the offset blurred image -->
          <feMergeNode in="SourceGraphic"/> <!-- this contains the element that the filter is applied to -->
       </feMerge>
    </filter>
'''


def tokenEater(type, token, (srow, scol), (erow, ecol), line):
    global line_count
    global prev
    global begun_line
    global num_spaces
    global algo_lines
    global indent_stack
    global last_line

    if begun_line and last_line != line:
        # This handles the case where there is a multi-line algorithm command 
        # that spans the lines with a backslash(look at line 10/11 of Prim)
        line_count += 1
        algo_lines.append('</text>\n')
        algo_lines.append('<text blank = "false" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal" style="cursor: pointer">' % ("l_" + str(line_count), 8*indent_stack[len(indent_stack)-1]))

    indent_const = 22
    if (type == 0): #EOF.  Reset globals
        line_count = 1
        num_spaces = 0.0
        indent_stack = [0]
        begun_line = False
        prev = ["",-1]
    elif (type == 1): #Word.  Potential keyword.  Must check keywordsList
        if begun_line == False:
            begun_line = True
            algo_lines.append('<text blank = "false" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal" style="cursor: pointer">' % ("l_" + str(line_count), 4*indent_stack[len(indent_stack)-1]))

        if token in keywordsList:
            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                algo_lines.append('<tspan font-weight="bold">%s</tspan>' % (token))
            elif (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
                algo_lines.append('<tspan font-weight="bold">%s</tspan>' % token)
            else:
                algo_lines.append('<tspan font-weight="bold"> %s</tspan>' % token)
        else:
            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                algo_lines.append('%s' % (token))
            elif (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
                algo_lines.append('%s' % token)
            else:
                algo_lines.append(' %s' % token)
    elif (type == 4): #Newline on nonempty line
        algo_lines.append('</text>\n')
        begun_line = False
        line_count += 1
    elif (type == 5):  #Arbitrary number of tabs at beginning of line  tabs are 4 spaces long
        num_spaces = 0.0
        for x in token:
            if ord(x) == 9:
                num_spaces += 7.7
            elif ord(x) == 32:
                num_spaces += 1.0

        num_spaces = int(floor(num_spaces))
        indent_stack.append(num_spaces)
        #num_spaces = int(floor(len(token))/4)
    elif (type == 6):  #One backpedal
        indent_stack.pop()
    elif (type == 51): #Operators and punctuation
        if begun_line == False:
            begun_line = True
            algo_lines.append('<text blank = "false" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal" style="cursor: pointer">' % ("l_" + str(line_count), 4*indent_stack[len(indent_stack)-1]))

        if token in operatorsList:
            if token == "<":
                token = "&lt;"
            elif token == "<<":
                token = "&lt;&lt;"
            elif token == "<=":
                token = "&lt;="
            elif token == "<>":
                token = "&lt;>"

            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                algo_lines.append('%s' % (token))
            else:
                algo_lines.append(' %s' % token)
        else:
            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                algo_lines.append('%s' % (token))
            elif prev[0] in operatorsList:
                algo_lines.append('%s' % token)
            else:
                algo_lines.append('%s' % token)
    elif (type == 53): #Comment
        if begun_line == False:
            begun_line = True
            algo_lines.append('<text blank = "false" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal" style="cursor: pointer">' % ("l_" + str(line_count), 4*indent_stack[len(indent_stack)-1]))

        if (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
            algo_lines.append('%s' % token)
        else:
            algo_lines.append('%s' % token)
    elif (type == 54): #Empty line with newline
        algo_lines.append('<text blank = "true" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal" style="cursor: pointer"></text>\n' % ("l_" + str(line_count), 4*indent_stack[len(indent_stack)-1]))
        line_begun = False
        line_count += 1
    else:
        if begun_line == False:
            begun_line = True
            algo_lines.append('<text blank = "false" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal" style="cursor: pointer">' % ("l_" + str(line_count), 4*indent_stack[len(indent_stack)-1]))

        if (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
            algo_lines.append('%s' % token)
        else:
            algo_lines.append(' %s' % token)
    
    last_line = line
    if type != 0:
        prev[0] = token
        prev[1] = type


def cmd_as_javascript(cmd, idPrefix=''):
    """ Return a list of methodname, target and args """
    def quote(s, prefix=''):
        return "\"%s\"" % (prefix+str(s))
    
    if len(cmd.target) == 1:
        target = quote(cmd.target[0], idPrefix)
    else:
        target = quote(cmd.target, idPrefix)
        
    result = [cmd.time, cmd.method.__name__, target]
    for arg in cmd.args:
        result.append(quote(arg))
    
    # Special case for some animation commands
    if cmd.method.__name__ == 'SetAllVerticesColor' and 'vertices' in cmd.kwargs:
        for v in cmd.kwargs['vertices']:
            result.append(quote(v))

    return result

def change_id_format(field):
    def edge_replace(match):
        return match.group().replace(' ', '').replace('(', '').replace(')', '').replace(',', '-')
    edge_re = re.compile(r'g[12]_\(\d+, \d+\)')
    if edge_re.search(field):
        return edge_re.sub(edge_replace, field)
    else:
        return field

def collectAnimations(histories, prefixes):
    """ Given a list of animation histories (aka list of AnimationCommands)
        combine them, giving all targets of animation commands their history-
        specific prefix, sort them and return a list of JavaScripts arrays.
    """
    mergedCmds = [cmd_as_javascript(cmd, prefixes[0]) for cmd in histories[0]]
    for i, h in enumerate(histories[1:]):
        mergedCmds += [cmd_as_javascript(cmd, prefixes[i+1]) for cmd in h]
    mergedCmds = sorted(mergedCmds, key=lambda cmd: cmd[0])

    # Replace absolute times by duration
    currentTime = mergedCmds[0][0]
    start_idx = 0
    for i, cmd in enumerate(mergedCmds):
        duration = max(1,int(round((cmd[0] - currentTime) * 1000, 0)))
        currentTime = cmd[0]
        mergedCmds[i][0] = str(duration)
        # We want to change the edge ids to a different form
        for j in xrange(2, len(mergedCmds[i])):
            if 'Edge' in mergedCmds[i][1]:
                mergedCmds[i][j] = change_id_format(mergedCmds[i][j])

        # While we're looping, find the first ShowActive command.
        # Prior to the first command there are just prolog commands which we can get rid of.
        if cmd[1] == 'ShowActive' and cmd[2] == '"l_1"' and start_idx == 0:
            start_idx = i

    mergedCmds = mergedCmds[start_idx:]
    return ["Array(" + ", ".join(cmd) + ")" for cmd in mergedCmds]

def get_edge_id(v, w, idPrefix):
    return idPrefix + '{}-{}'.format(v, w)


def get_graph_as_svg_str_standalone(graphDisplay, x_add, y_add, file, idPrefix='', translate=None, skip_edge_info=False):
    ''' Returns a 3-tuple of (svg_string, width, height).  The SVG string returned
        is designed for standalone viewing.
    '''
    def update_min_and_max(x, y, min_x, min_y, max_x, max_y):
        if min_x == None:
            min_x = x
        else:
            min_x = min(x, min_x)
        if max_x == None:
            max_x = x
        else:
            max_x = max(x, max_x)
        if min_y == None:
            min_y = y
        else:
            min_y = min(y, min_y)
        if max_y == None:
            max_y = y
        else:
            max_y = max(y, max_y)
        return min_x, min_y, max_x, max_y

    ret_strs = []
    min_x, max_x, min_y, max_y = None, None, None, None

    # Keep track of vertex_radius as we have to shift everything over by that much so 
    # vertices on the far left don't appear half off the screen
    vertex_radius = None
    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)
        if vertex_radius == None:
            vertex_radius = r
            x_add -= vertex_radius
            y_add -= vertex_radius
            break
    if translate:
        ret_strs.append('<g transform="translate(%d %d)">\n' % (translate[0], translate[1]))

    # Write Edges:
    for v,w in graphDisplay.G.Edges():
        vx, vy, r = graphDisplay.VertexPositionAndRadius(v)
        wx, wy, r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)
        
        vy -= y_add
        wy -= y_add
        vx -= x_add
        wx -= x_add
        min_x, min_y, max_x, max_y = update_min_and_max(vx, vy, min_x, min_y, max_x, max_y)
        min_x, min_y, max_x, max_y = update_min_and_max(wx, wy, min_x, min_y, max_x, max_y)

        if graphDisplay.G.directed == 0:
            ret_strs.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                       ' stroke-width="%s"/>\n' % (vx, vy, wx, wy, col, width))
        else:
            x1,y1,x2,y2 = graphDisplay.directedDrawEdgePoints(graphDisplay.VertexPosition(v),
                graphDisplay.VertexPosition(w), 0)
            
            x1e,y1e = graphDisplay.CanvasToEmbedding(x1,y1)
            x2e,y2e = graphDisplay.CanvasToEmbedding(x2,y2)
            y1e -= y_add
            y2e -= y_add
            x1e -= x_add
            x2e -= x_add
            min_x, min_y, max_x, max_y = update_min_and_max(x1e, y1e, min_x, min_y, max_x, max_y)
            min_x, min_y, max_x, max_y = update_min_and_max(x2e, y2e, min_x, min_y, max_x, max_y)

            if graphDisplay.G.QEdge(w,v): # Directed edges both ways
                ret_strs.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                           ' stroke-width="%s"/>\n' % (x1e, y1e, x2e, y2e, col, width))
            else: # Just one directed edge
                # XXX How to color arrowhead?
                l = sqrt((float(wx)-float(vx))**2 + (float(wy)-float(vy))**2)
                if (l < .001):
                    l = .001

                c = (l-2*graphDisplay.zVertexRadius)/l + .01
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                
                #dx = 0 #offset of wx to make room for arrow
                #dy = 0 #offset of wy
                cr = 0
                #Took out marker-end="url(#Arrowhead)" and added polyline
                #Shrink line to make room for arrow
                for z in graphDisplay.G.Vertices():
                    cx,cy,cr = graphDisplay.VertexPositionAndRadius(z)
                    cy -= y_add
                    cx -= x_add
                    min_x, min_y, max_x, max_y = update_min_and_max(cx, cy, min_x, min_y, max_x, max_y)
                    if(cx == wx and cy == wy):
                        angle = atan2(int(float(wy))-int(float(vy)), int(float(wx))-int(float(vx)))
                        ret_strs.append('<line x1="%s" y1="%s" x2="%f" y2="%f" stroke="%s"'\
                               ' stroke-width="%s" />\n' % (vx, vy, tmpX, tmpY,
                                                            col, width))
                        break

                #Temporary settings for size of polyline arrowhead
                a_width = (1 + 1.5/(1*pow(log10(float(width)), 6)))
                if(a_width > 5.0):
                    a_width = 5.0
                a_width *= float(width) 
                p1 = (0,0)
                p2 = (0, a_width)
                p3 = (cr, a_width/2)
                angle = degrees(atan2(int(wy)-int(vy), int(wx)-int(vx)))
                c = (l-2*graphDisplay.zVertexRadius)/l
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                ret_strs.append('<polyline points="%f %f %f %f %s %f" fill="%s" transform="translate(%f,%f)'\
                           ' rotate(%f %f %f)" />\n' % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                                        col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))


        # Write Edge Annotations
        if graphDisplay.edgeAnnotation.QDefined((v,w)):
            da = graphDisplay.edgeAnnotation[(v,w)]
            x,y = graphDisplay.canvas.coords(graphDisplay.edgeAnnotation[(v,w)])
            xe,ye = graphDisplay.CanvasToEmbedding(x,y)
            y -= y_add
            ye -= y_add
            x -= x_add
            xe -= x_add
            min_x, min_y, max_x, max_y = update_min_and_max(x, y, min_x, min_y, max_x, max_y)
            min_x, min_y, max_x, max_y = update_min_and_max(xe, ye, min_x, min_y, max_x, max_y)
            text = graphDisplay.canvas.itemcget(graphDisplay.edgeAnnotation[(v,w)],"text") 
            size = r * 0.9
            offset = 0.33 * size
            col = 'black'
            if text != "" and not skip_edge_info:
                ret_strs.append('<text x="%s" y="%s" text-anchor="center" '\
                           'fill="%s" font-family="Helvetica" '\
                           'font-size="%s" font-style="normal">%s</text>\n' % (xe+offset,ye+offset,col,size,text))

    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)
        y -= y_add
        x -= x_add
        min_x, min_y, max_x, max_y = update_min_and_max(x, y, min_x, min_y, max_x, max_y)

        # Write Vertex
        col = graphDisplay.GetVertexColor(v)
        fw = graphDisplay.GetVertexFrameWidth(v)
        fwe,dummy = graphDisplay.CanvasToEmbedding(fw,0)
        stroke = graphDisplay.GetVertexFrameColor(v)

        ret_strs.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"'\
                   ' stroke-width="%s" style="filter:url(#dropshadow)"/>\n' % (x,y,r,col,stroke,fwe))

        # Write Vertex Label
        col = graphDisplay.canvas.itemcget(graphDisplay.drawLabel[v], "fill")
        size = r*1.0
        offset = 0.33 * size

        ret_strs.append('<text x="%s" y="%s" text-anchor="middle" fill="%s" font-family="Helvetica" '\
                   'font-size="%s" font-style="normal" font-weight="bold" >%s</text>\n' % (x, y+offset,col,size, graphDisplay.G.GetLabeling(v)))
        # Write vertex annotation
        #size = r*0.9
        size = 14
        text = graphDisplay.GetVertexAnnotation(v)
        col = 'black'
        if text != "":
            ret_strs.append('<text x="%s" y="%s" text-anchor="left" fill="%s" font-weight="bold" font-family="Helvetica" '\
                       'font-size="%s" font-style="normal">%s</text>\n' % (x+r+1,y+r*1.5+2.5,col,size,text))

    if translate:
        ret_strs.append('</g>')

    if all([min_x, max_x, vertex_radius]):
        width = max_x-min_x+vertex_radius*2
        height = max_y-min_y+vertex_radius*2
        return '\n'.join(ret_strs), width, height
    else:
        return '', 0, 0



def get_graph_as_svg_str_for_animation(graphDisplay, x_add, y_add, file, idPrefix=''):
    ''' Returns an svg string.  The SVG string returned 
        is designed for use with javascript with WebGato.
        x_add and y_add are offsets for transforming coordinate system to (0, 0) origin
    '''
    ret_strs = []

    # Write Edges
    for v,w in graphDisplay.G.Edges():
        vx,vy,r = graphDisplay.VertexPositionAndRadius(v)
        wx,wy,r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)
        
        vy -= y_add
        wy -= y_add
        vx -= x_add
        wx -= x_add
        
        edge_id = get_edge_id(v, w, idPrefix)
        ret_strs.append('<g id="%s" class="edge_group" style="cursor: pointer">' % (edge_id + '_group'))
        if graphDisplay.G.directed == 0:
            ret_strs.append('<line id="%s" class="edge" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                       ' stroke-width="%s"/>\n' % (edge_id, vx, vy, wx, wy, col, width))
        else:
            x1,y1,x2,y2 = graphDisplay.directedDrawEdgePoints(graphDisplay.VertexPosition(v),
                graphDisplay.VertexPosition(w), 0)
            
            x1e,y1e = graphDisplay.CanvasToEmbedding(x1,y1)
            x2e,y2e = graphDisplay.CanvasToEmbedding(x2,y2)
            y1e -= y_add
            y2e -= y_add
            x1e -= x_add
            x2e -= x_add

            if graphDisplay.G.QEdge(w,v): # Directed edges both ways
                ret_strs.append('<line id="%s" class="edge" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                           ' stroke-width="%s"/>\n' % (edge_id, x1e, y1e, x2e, y2e, col, width))
            else: # Just one directed edge
                # XXX How to color arrowhead?
                l = sqrt((float(wx)-float(vx))**2 + (float(wy)-float(vy))**2)
                if (l < .001):
                    l = .001

                c = (l-2*graphDisplay.zVertexRadius)/l + .01
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                
                #dx = 0 #offset of wx to make room for arrow
                #dy = 0 #offset of wy
                cr = 0
                #Took out marker-end="url(#Arrowhead)" and added polyline
                #Shrink line to make room for arrow
                for z in graphDisplay.G.Vertices():
                    cx,cy,cr = graphDisplay.VertexPositionAndRadius(z)
                    cy -= y_add
                    cx -= x_add
                    if(cx == wx and cy == wy):
                        angle = atan2(int(float(wy))-int(float(vy)), int(float(wx))-int(float(vx)))
                        ret_strs.append('<line id="%s" class="edge" x1="%s" y1="%s" x2="%f" y2="%f" stroke="%s"'\
                               ' stroke-width="%s" />\n' % (edge_id, vx, vy, tmpX, tmpY,
                                                            col, width))
                        break

                #Temporary settings for size of polyline arrowhead
                a_width = (1 + 1.5/(1*pow(log10(float(width)), 6)))
                if(a_width > 5.0):
                    a_width = 5.0
                a_width *= float(width) 
                p1 = (0,0)
                p2 = (0, a_width)
                p3 = (cr, a_width/2)
                angle = degrees(atan2(int(wy)-int(vy), int(wx)-int(vx)))
                c = (l-2*graphDisplay.zVertexRadius)/l
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                ret_strs.append('<polyline id="%s" class="arrowhead" points="%f %f %f %f %s %f" fill="%s" transform="translate(%f,%f)'\
                           ' rotate(%f %f %f)" />\n' % ('ea' + edge_id, p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                                        col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))
        ret_strs.append('</g>')


        # Write Edge Annotations
        if graphDisplay.edgeAnnotation.QDefined((v,w)):
            da = graphDisplay.edgeAnnotation[(v,w)]
            x,y = graphDisplay.canvas.coords(graphDisplay.edgeAnnotation[(v,w)])
            xe,ye = graphDisplay.CanvasToEmbedding(x,y)
            y -= y_add
            ye -= y_add
            x -= x_add
            xe -= x_add

            text = graphDisplay.canvas.itemcget(graphDisplay.edgeAnnotation[(v,w)],"text") 
            size = r * 0.9
            offset = 0.33 * size
            col = 'black'
            if text != "":
                ret_strs.append('<text id="ea%s" class="edge_annotation" x="%s" y="%s" text-anchor="center" '\
                           'fill="%s" font-family="Helvetica" '\
                           'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(xe),
                                                                               ye+offset,col,size,text))

    ret_strs.append('<g id="%s"></g>' % (idPrefix+'pre_vertices_group'))
    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)
        y -= y_add
        x -= x_add

        # Write Vertex
        col = graphDisplay.GetVertexColor(v)
        fw = graphDisplay.GetVertexFrameWidth(v)
        fwe,dummy = graphDisplay.CanvasToEmbedding(fw,0)
        stroke = graphDisplay.GetVertexFrameColor(v)

        ret_strs.append('<g id="%s" class="vertex_g" style="cursor: pointer">' % (idPrefix + str(v) + '_group'))
        ret_strs.append('<circle id="%s" class="vertex" cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"'\
                   ' stroke-width="%s" style="filter:url(#dropshadow)"/>\n' % (idPrefix+str(v),x,y,r,col,stroke,fwe))

        # Write Vertex Label
        col = graphDisplay.canvas.itemcget(graphDisplay.drawLabel[v], "fill")
        size = r*1.0
        offset = 0.33 * size

        ret_strs.append('<text id="vl%s" x="%s" y="%s" text-anchor="middle" fill="%s" font-family="Helvetica" '\
                   'font-size="%s" font-style="normal" font-weight="bold" >%s</text>\n' % (idPrefix+str(v),x,
                                                                                           y+offset,col,size,
                                                                                           graphDisplay.G.GetLabeling(v)))
        ret_strs.append('</g>')
        # Write vertex annotation
        #size = r*0.9
        size = 14
        text = graphDisplay.GetVertexAnnotation(v)
        col = 'black'
        if text != "":
            ret_strs.append('<text id="va%s" class="vertex_annotation" x="%s" y="%s" text-anchor="left" fill="%s" font-weight="bold" font-family="Helvetica" '\
                       'font-size="%s" font-style="normal" text_content="%s">%s</text>\n' % (idPrefix+str(v),x+r+1,y+r*1.5+2.5,col,size,text,text))

    return '\n'.join(ret_strs)
    

def compute_coord_changes(gdisp):
    has_elements = False
    x_add, y_add = 0, 0
    for v, w in gdisp.G.Edges():
        vx, vy, r = gdisp.VertexPositionAndRadius(v)
        if not has_elements:
            x_add = vx
            y_add = vy
            has_elements = True
        else:
            x_add = min(vx, x_add)
            y_add = min(vy, y_add)
    for v in gdisp.G.Vertices():
        vx, vy, r = gdisp.VertexPositionAndRadius(v)
        if not has_elements:
            x_add = vx
            y_add = vy
            has_elements = True
        else:
            x_add = min(vx, x_add)
            y_add = min(vy, y_add)
    return x_add, y_add, has_elements

def format_init_edge_infos(info_dict, idPrefix):
    ''' Formats the info_dict to a javascript object '''
    if not info_dict:
        return 'null';
    str_bits = ['{'] # List of strings to return joined at the end(faster than concatenation)
    for (v, w), info in info_dict.iteritems():
        edge_id = get_edge_id(v, w, idPrefix)
        assignment = '"{}": "{}",'.format(edge_id, info)
        str_bits.append(assignment)
    str_bits.append('}')
    return '\n'.join(str_bits)

def format_init_vertex_infos(info_dict, idPrefix):
    ''' Formats the info_dict to a javascript object '''
    if not info_dict:
        return 'null';
    str_bits = ['{'] # List of strings to return joined at the end(faster than concatenation)
    for v, info in info_dict.iteritems():
        vertex_id = idPrefix + str(v)
        assignment = '"{}": "{}",'.format(vertex_id, info)
        str_bits.append(assignment)
    str_bits.append('}')
    return '\n'.join(str_bits)
        
def ExportAlgoInfo(fileName, algorithm):
    if not os.path.exists('./svgs/infos'):
        os.makedirs('./svgs/infos')

    file = open("./svgs/infos/%s" % os.path.basename(fileName).replace("svg", "html"), "w")
    info = algorithm.About()
    soup = BeautifulSoup(info)

    # Link the CSS file
    head = soup.find('head')
    if not head:
        html = soup.find('html')
        html.insert(0, soup.new_tag('head'))
        head = soup.find('head')
    head.insert(0, soup.new_tag('link', rel='stylesheet', href='../css/info_page_style.css'))

    # Insert a div with background-color found by colordef into the <dt> elements
    for dt in soup.find_all('dt'):
        colordef = dt.find('colordef')
        if not colordef:
            continue
        color = colordef['color']
        colordef.extract()
        color_div = soup.new_tag('div')
        color_div.string = '&nbsp;&nbsp;&nbsp;&nbsp;'
        color_div['style'] = 'background-color: %s' % color
        color_div['class'] = 'color_div'
        dt.append(color_div)


    # Add a div with "clear: both" to make the next row
    for dd in soup.find_all('dd'):
        clear_div = soup.new_tag('div')
        clear_div['class'] = 'clear_div'
        dd.insert_after(clear_div)
    
    body = soup.find('body')
    if not body.contents:
        # If there isn't any content add "No algorithm info"
        body.append(soup.new_string('No algorithm info'))

    file.write(soup.prettify(formatter=None))

def format_animation(animation):
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))
    if len(animation) < 32000:
        return 'var anim_array = Array(' + ',\n'.join(animation) + ');'
    else:
        ret_str = 'var anim_array = Array(' + ',\n'.join(animation[:32000]) + ');\n'
        for chunk in chunker(animation[32000:], 32000):
            ret_str += 'anim_array = anim_array.concat(Array(' + ','.join(chunk) + '));\n'
        return ret_str

def construct_title(fileName):
    sp = fileName.split('/')[1].split('--')
    algorithm = sp[0]
    graph = sp[1].split('.')[0]
    return 'Gato -- %s algorithm on %s graph' % (algorithm, graph)

def construct_animation_name(fileName):
    sp = fileName.split('/')[1].split('--')
    algorithm = sp[0]
    graph = sp[1].split('.')[0]
    return '%s on %s graph' % (algorithm, graph)

def get_start_coordinate_diff(graphDisplay, secondaryGraphDisplay=None):
    start_g1_x_add, start_g1_y_add, start_g1_has_elements = compute_coord_changes(graphDisplay)
    start_g2_x_add, start_g2_y_add, start_g2_has_elements = 0, 0, False
    if secondaryGraphDisplay:
        start_g2_x_add, start_g2_y_add, start_g2_has_elements = compute_coord_changes(secondaryGraphDisplay)
        
    return {
        'g1_x_add': start_g1_x_add,
        'g1_y_add': start_g1_y_add,
        'g1_has_elements': start_g1_has_elements,
        'g2_x_add': start_g2_x_add,
        'g2_y_add': start_g2_y_add,
        'g2_has_elements': start_g2_has_elements
    }

def format_bubbles(bubbles):
    if not bubbles:
        return '{}'
    bubble_str = '{\n'
    for bubble_id, (offset_value, color) in bubbles.iteritems():
        bubble_str += '"%s"' % bubble_id
        bubble_str += ': ["' + offset_value + '", "' + color + '"],\n'
    bubble_str += '}'
    return bubble_str

def ExportSVG(fileName, algowin, algorithm, graphDisplay, secondaryGraphDisplay=None, 
    secondaryGraphDisplayAnimationHistory=None, showAnimation=False, 
    init_edge_infos=None, init_vertex_infos=None, init_graph_infos=None,
    write_to_png=False, chapter_number=None, algo_div=None, chapter_name=None, start_graph_coord_diff=None):
    """ Export either the current graphs or the complete animation
        (showAnimation=True) to the file fileName.

        showAnimation: We don't do anything if this is False
        init_edge_infos: list of dictionaries with keys that are tuples of form (v1, v2) where v1 and v2 are the vertices
            that an edge connects.  The values keys point to are the initial edge infos of that edge.
    """
    global algo_lines

    algo_lines = []
    file = open(fileName, 'w')

    # Figure out how much we want to pull the graph to the left and top before we reset the graph
    end_g1_x_add, end_g1_y_add, end_g1_has_elements = compute_coord_changes(graphDisplay)
    end_g2_x_add, end_g2_y_add = 0, 0
    if secondaryGraphDisplay:
        end_g2_x_add, end_g2_y_add, end_g2_has_elements = compute_coord_changes(secondaryGraphDisplay)

    if showAnimation:
        try:
            if secondaryGraphDisplayAnimationHistory:
                animation = collectAnimations([algorithm.animation_history.getHistoryOne(),
                                               secondaryGraphDisplayAnimationHistory.getHistoryTwo(),
                                               algowin.codeLineHistory],
                                              ['g1_', 'g2_', 'l_'])
            else:
                animation = collectAnimations([algorithm.animation_history.getHistoryOne(),
                                               algowin.codeLineHistory],
                                              ['g1_', 'l_'])
        except IndexError as e:
            print "Error:"
            print e
            print "Filename: ", fileName
            print "Algowin: ", algowin
            print "Algorithm: ", algorithm
            print "graphDisplay: ", graphDisplay
            return

    

    # Reload the graph and execute prolog so we can save the initial state to SVG
    # if showAnimation and not write_to_png:
    algorithm.Start(prologOnly=True)

    # If we have coord diffs passed in, then use those, otherwise recompute
    if start_graph_coord_diff:
        start_g1_x_add, start_g2_x_add = start_graph_coord_diff['g1_x_add'], start_graph_coord_diff['g2_x_add']
        start_g1_y_add, start_g2_y_add = start_graph_coord_diff['g1_y_add'], start_graph_coord_diff['g2_y_add']
        start_g1_has_elements, start_g2_has_elements = start_graph_coord_diff['g1_has_elements'], start_graph_coord_diff['g2_has_elements']
    else:
        start_g1_x_add, start_g1_y_add, start_g1_has_elements = compute_coord_changes(graphDisplay)
        start_g2_x_add, start_g2_y_add, g2_x_add, g2_y_add = 0, 0, 0, 0
        if secondaryGraphDisplay:
            start_g2_x_add, start_g2_y_add, start_g2_has_elements = compute_coord_changes(secondaryGraphDisplay)
    
    # Find final g1 and g2 x and y coord differences
    if start_g1_has_elements and end_g1_has_elements:
        g1_x_add, g1_y_add = min(start_g1_x_add, end_g1_x_add), min(start_g1_y_add, end_g1_y_add)
    elif start_g1_has_elements:
        g1_x_add, g1_y_add = start_g1_x_add, start_g1_y_add
    else:
        g1_x_add, g1_y_add = end_g1_x_add, end_g1_y_add
    if secondaryGraphDisplay:
        if start_g2_has_elements and end_g2_has_elements:
            g2_y_add, g2_x_add = min(start_g2_y_add, end_g2_y_add), min(start_g2_x_add, end_g2_x_add)
        elif start_g2_has_elements:
            g2_y_add, g2_x_add = start_g2_y_add, start_g2_x_add
        else:
            g2_y_add, g2_x_add = end_g2_y_add, end_g2_x_add


    if showAnimation and not write_to_png:
        # Build the SVG graph string
        graph_strs = []
        graph_type = "undirected" if graphDisplay.G.directed == 0 else "directed"
        graph_strs.append('<g id="g1" type="%s" style="visibility: hidden">\n' % (graph_type))

        g1_str = get_graph_as_svg_str_for_animation(graphDisplay, g1_x_add, g1_y_add, file, idPrefix=id_prefixes[0])
        graph_strs.append(g1_str)
        graph_strs.append('</g>\n')
        if secondaryGraphDisplay:
            graph_type = "undirected" if secondaryGraphDisplay.G.directed == 0 else "directed"
            graph_strs.append('<g id="g2" type="%s" style="visibility: hidden">\n' % (graph_type))
            g2_str = get_graph_as_svg_str_for_animation(secondaryGraphDisplay, g2_x_add, g2_y_add, file, idPrefix=id_prefixes[1])
            graph_strs.append(g2_str)
            graph_strs.append('</g>\n')

        # Build the Algorithm SVG string
        source = algorithm.GetSource()
        tokenize.tokenize(StringIO.StringIO(source.replace('\\', '\\\\')).readline, tokenEater)
        algowin.CommitStop()

        # Merge the animation into the HTML
        str_vars = {
            'title': construct_title(fileName),
            'animation_name': construct_animation_name(fileName),
            'chapter_number': chapter_number or 0,
            'algo_div': algo_div or '',
            'chapter_name': chapter_name or '',
            'info_file': 'infos/' + fileName[fileName.rindex('/') + 1:],
            'this_url': fileName[fileName.rindex('/') + 1:],
            'animation': format_animation(animation),
            'graph_str': '\n'.join(graph_strs), 
            'algo_str': '<g id="codelines" style="visibility: hidden">' + ''.join(algo_lines) + "</g>",
            'g1_x_add': g1_x_add,
            'g1_y_add': g1_y_add,
            'g2_x_add': g2_x_add,
            'g2_y_add': g2_y_add,
            'g1_init_edge_info': format_init_edge_infos(init_edge_infos[0], id_prefixes[0]) if init_edge_infos else 'null',
            'g2_init_edge_info': format_init_edge_infos(init_edge_infos[1], id_prefixes[1]) if init_edge_infos and len(init_edge_infos) > 1 else 'null',
            'g1_init_graph_info': '"%s"' % init_graph_infos[0] if init_graph_infos and init_graph_infos[0] else '""',
            'g2_init_graph_info': '"%s"' % init_graph_infos[1] if init_graph_infos and init_graph_infos[1] else '""',
            'g1_init_vertex_info': format_init_vertex_infos(init_vertex_infos[0], id_prefixes[0]) if init_vertex_infos else 'null',
            'g2_init_vertex_info': format_init_vertex_infos(init_vertex_infos[1], id_prefixes[1]) if init_vertex_infos else 'null',
            'g1_init_bubbles': format_bubbles(graphDisplay.bubbles),
            'g2_init_bubbles': format_bubbles(secondaryGraphDisplay.bubbles if secondaryGraphDisplay else None),
            'g1_init_moats': format_bubbles(graphDisplay.moats),
            'g2_init_moats': format_bubbles(secondaryGraphDisplay.moats if secondaryGraphDisplay else None),
        }
        file.write(animationhead % str_vars)
        file.close()

        # Export the algorithm info to its own HTML file        
        ExportAlgoInfo(fileName, algorithm)


    elif not showAnimation and not write_to_png:
        edge_padding = 5
        g1_svg_body_str, g1_width, g1_height = get_graph_as_svg_str_standalone(graphDisplay, g1_x_add, 
            g1_y_add, file, idPrefix=id_prefixes[0], translate=(edge_padding, edge_padding))
        g2_svg_body_str, g2_width, g2_height = '', 0, 0
        g2_y_padding = 0
        if secondaryGraphDisplay:
            g2_y_padding = 10
            g2_svg_body_str, g2_width, g2_height = get_graph_as_svg_str_standalone(secondaryGraphDisplay, g2_x_add, 
                g2_y_add, file, idPrefix=id_prefixes[1], translate=(edge_padding,g1_height+g2_y_padding+edge_padding))

        width = int(max(g1_width, g2_width))+edge_padding*2
        height = int(g1_height+g2_height+g2_y_padding)+edge_padding*2 
        scale = min(200.0/width, 1.0)
        
        # Put a border between the graphs
        if secondaryGraphDisplay:
            y = g1_height + g2_y_padding/2 + edge_padding
            g2_svg_body_str += '<line x1="0" x2="%d" y1="%d" y2="%d" stroke="#000" stroke-width="3.0" />' % (width, y, y)
        svg_str = '\n'.join(['<svg width="%d" height="%d">' % (width, height), svg_drop_shadow, g1_svg_body_str, g2_svg_body_str, '</svg>'])
        file.write(svg_str)
        file.close()

    elif not showAnimation and write_to_png:
        '''
        The commands on Ubuntu to get these libraries installed:
        sudo apt-get install libcairo2-dev librsvg2-dev python-rsvg
        '''
        import cairo
        import rsvg

        file.close()

        edge_padding = 15
        g1_svg_body_str, g1_width, g1_height = get_graph_as_svg_str_standalone(graphDisplay, g1_x_add, 
            g1_y_add, file, idPrefix=id_prefixes[0], translate=(edge_padding, edge_padding), skip_edge_info=True)
        g2_svg_body_str, g2_width, g2_height = '', 0, 0
        g2_y_padding = 0
        if secondaryGraphDisplay:
            g2_y_padding = 10
            g2_svg_body_str, g2_width, g2_height = get_graph_as_svg_str_standalone(secondaryGraphDisplay, g2_x_add, 
                g2_y_add, file, idPrefix=id_prefixes[1], translate=(edge_padding,g1_height+g2_y_padding+edge_padding), skip_edge_info=True)

        width = int(max(g1_width, g2_width))+edge_padding*2
        height = int(g1_height+g2_height+g2_y_padding)+edge_padding*2 
        scale = min(min(200.0/width, 1.0), min(200.0/height, 1.0))
        
        # Put a border between the graphs
        if secondaryGraphDisplay and g2_svg_body_str:
            y = g1_height + g2_y_padding/2 + edge_padding
            g2_svg_body_str += '<line x1="0" x2="%d" y1="%d" y2="%d" stroke="#aaa" stroke-width="1.0" />' % (width, y, y)
        svg_str = '\n'.join(['<svg width="%d" height="%d">' % (width, height), svg_drop_shadow, g1_svg_body_str, g2_svg_body_str, '</svg>'])

        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(ceil(width*scale)), int(ceil(height*scale)))

        ctx = cairo.Context(img)
        ctx.scale(scale, scale)
        handler= rsvg.Handle(None, svg_str)
        handler.render_cairo(ctx)
        img.write_to_png(fileName)
        return {'width': width*scale, 'height': height*scale}

