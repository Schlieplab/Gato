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
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
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
from math import sqrt, pi, sin, cos, atan2, degrees, log10, floor
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
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 14*indent_stack[len(indent_stack)-1]))

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
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

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
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

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
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
            algo_lines.append('%s' % token)
        else:
            algo_lines.append('%s' % token)
    elif (type == 54): #Empty line with newline
        algo_lines.append('<text blank = "true" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal"></text>\n' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))
        line_begun = False
        line_count += 1
    else:
        if begun_line == False:
            begun_line = True
            algo_lines.append('<text blank = "false" id="%s" class="code_line" x="0" y="0" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
            algo_lines.append('%s' % token)
        else:
            algo_lines.append('%s' % token)
    
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
    
    # Special case for some animatin commands
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
    for i, cmd in enumerate(mergedCmds):
        duration = max(1,int(round((cmd[0] - currentTime) * 1000, 0)))
        currentTime = cmd[0]
        mergedCmds[i][0] = str(duration)

        # We want to change the ids to a different form
        for j in xrange(2, len(mergedCmds[i])):
            #if mergedCmds[i][1] == 'UpdateEdgeInfo' and j == 3:
            #    continue
            if 'Edge' in mergedCmds[i][1]:
                mergedCmds[i][j] = change_id_format(mergedCmds[i][j])
            #mergedCmds[i][j] = mergedCmds[i][j].replace(' ', '').replace('(', '').replace(')', '').replace(',', '-')
    return ["Array(" + ", ".join(cmd) + ")" for cmd in mergedCmds]


def get_graph_as_svg_str(graphDisplay, x_add, y_add, file, idPrefix=''):
    # Write Bubbles from weighted matching
    # XXX We make use of the fact that they have a bubble tag
    # XXX What to use as the bubble ID?
##    bubbles = graphDisplay.canvas.find_withtag("bubbles")
##    for b in bubbles:
##        col = graphDisplay.canvas.itemcget(b,"fill")
##        # Find center and convert to Embedding coordinates
##        coords = graphDisplay.canvas.coords(b)
##        x = 0.5 * (coords[2] - coords[0]) + coords[0]
##        y = 0.5 * (coords[3] - coords[1]) + coords[1]
##        r = 0.5 * (coords[2] - coords[0])
##        xe,ye = graphDisplay.CanvasToEmbedding(x,y)
##        re,dummy = graphDisplay.CanvasToEmbedding(r,0)
##        file.write('<circle cx="%s" cy="%s" r="%s" fill="%s" '\
##                   ' stroke-width="0" />\n' % (xe,ye,re,col))           


##    # Write Highlighted paths
##    # XXX What to use as the bubble ID?
##    for pathID, draw_path in graphDisplay.highlightedPath.items():
##        # XXX Need to check visibility? See HidePath
##        col = graphDisplay.canvas.itemcget(draw_path,"fill")
##        width = graphDisplay.canvas.itemcget(draw_path,"width")
##        points = ["%s,%s" % graphDisplay.VertexPositionAndRadius(v)[0:2] for v in pathID]
##        file.write('<polyline points="%s" stroke="%s" stroke-width="%s" '\
##                   'fill="None" />\n' % (" ".join(points),col,width))

    ret_strs = []

    # x_add and y_add will be added to the position of edges in order to make the leftmost edge be positioned at 0
    x_add, y_add = 0, 0
    t = False
    for v, w in graphDisplay.G.Edges():
        vx, vy, r = graphDisplay.VertexPositionAndRadius(v)
        if not t:
            x_add = vx
            y_add = vy
            #print "setting to ", vx
            t = True
        else:
            x_add = min(vx, x_add)
            y_add = min(vy, y_add)

    # Write Edges
    for v,w in graphDisplay.G.Edges():
        vx,vy,r = graphDisplay.VertexPositionAndRadius(v)
        wx,wy,r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)
        
        vy = vy - y_add
        wy = wy - y_add
        vx = vx - x_add
        wx = wx - x_add
        
        edge_id = idPrefix + '{}-{}'.format(v, w)
        if graphDisplay.G.directed == 0:
            ret_strs.append('<line id="%s" class="edge" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                       ' stroke-width="%s"/>\n' % (edge_id, vx, vy, wx, wy, col, width))
        else:
            x1,y1,x2,y2 = graphDisplay.directedDrawEdgePoints(graphDisplay.VertexPosition(v),
                                                              graphDisplay.VertexPosition(w),
                                                              0)
            
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

    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)
        y = y - y_add
        x = x - x_add
        
        # Write Vertex
        col = graphDisplay.GetVertexColor(v)
        fw = graphDisplay.GetVertexFrameWidth(v)
        fwe,dummy = graphDisplay.CanvasToEmbedding(fw,0)
        stroke = graphDisplay.GetVertexFrameColor(v)

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
        # Write vertex annotation
        #size = r*0.9
        size = 14
        text = graphDisplay.GetVertexAnnotation(v)
        col = 'black'
        if text != "":
            ret_strs.append('<text id="va%s" class="vertex_annotation" x="%s" y="%s" text-anchor="left" fill="%s" font-weight="bold" font-family="Helvetica" '\
                       'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(v),x+r+1,y+r*1.5+2.5,col,size,text))

    return '\n'.join(ret_strs)
    
        
def ExportAlgoInfo(fileName, algorithm):
    if not os.path.exists('./svgs/infos'):
        os.makedirs('./svgs/infos')

    file = open("./svgs/infos/%s" % os.path.basename(fileName).replace("svg", "html"), "w")
    info = algorithm.About()
    r = re.compile(r'colordef\s+color="[a-zA-z#]+')
    matches = r.findall(info)
    colors = [s.split('"')[1] for s in matches]
    info = re.sub(r'colordef\s+color="[a-zA-z#]+">', lambda match: 'div style="height: 10px; width: 10px; display:inline; background-color:%s">&nbsp&nbsp&nbsp&nbsp</div>&nbsp' % colors.pop(0), info, count=len(colors))
    file.write(info)

def ExportSVG(fileName, algowin, algorithm, graphDisplay,
              secondaryGraphDisplay=None,
              secondaryGraphDisplayAnimationHistory=None,
              showAnimation=False):
    """ Export either the current graphs or the complete animation
        (showAnimation=True) to the file fileName
    """
    global algo_lines
    algo_lines = []

    if showAnimation:
        try:
            if secondaryGraphDisplayAnimationHistory:
                #x_add, y_add = compute_coordinate_shifts([graphDisplay, secondaryGraphDisplay], [algorithm.animation_history.getHistoryOne(), secondaryGraphDisplayAnimationHistory.getHistoryTwo()])
                animation = collectAnimations([algorithm.animation_history.getHistoryOne(),
                                               secondaryGraphDisplayAnimationHistory.getHistoryTwo(),
                                               algowin.codeLineHistory],
                                              ['g1_','g2_','l_'])
            else:
                #x_add, y_add = compute_coordinate_shifts([graphDisplay], [algorithm.animation_history.getHistoryOne()])
                animation = collectAnimations([algorithm.animation_history.getHistoryOne(),
                                               algowin.codeLineHistory],
                                              ['g1_','l_'])
        except IndexError:
            print "Error:"
            print "Filename: ", fileName
            print "Algowin: ", algowin
            print "Algorithm: ", algorithm
            print "graphDisplay: ", graphDisplay
            return


        def compute_coord_changes(gdisp):
            t = False
            x_add, y_add = 0, 0
            for v, w in gdisp.G.Edges():
                vx, vy, r = gdisp.VertexPositionAndRadius(v)
                if not t:
                    x_add = vx
                    y_add = vy
                    t = True
                else:
                    x_add = min(vx, x_add)
                    y_add = min(vy, y_add)
            return x_add, y_add

        # Figure out how much we want to pull the graph to the left and top before we reset the graph
        g1_x_add, g1_y_add = compute_coord_changes(graphDisplay)
        g2_x_add, g2_y_add = 0, 0
        if secondaryGraphDisplay:
            g2_x_add, g2_y_add = compute_coord_changes(secondaryGraphDisplay)

        # Reload the graph and execute prolog so we can save the initial state to SVG
        algorithm.Start(prologOnly=True)
        file = open(fileName, 'w')

        # Build the SVG graph string
        graph_strs = []
        graph_type = "undirected" if graphDisplay.G.directed == 0 else "directed"
        graph_strs.append('<g id="g1" type="%s">\n' % (graph_type))

        g1_str = get_graph_as_svg_str(graphDisplay, g1_x_add, g1_y_add, file, idPrefix='g1_')
        graph_strs.append(g1_str)
        graph_strs.append('</g>\n')
        if secondaryGraphDisplay:
            graph_type = "undirected" if secondaryGraphDisplay.G.directed == 0 else "directed"
            graph_strs.append('<g id="g2" type="%s">\n' % (graph_type))
            g2_str = get_graph_as_svg_str(secondaryGraphDisplay, g2_x_add, g2_y_add, file, idPrefix='g2_')
            graph_strs.append(g2_str)
            graph_strs.append('</g>\n')

        # Build the Algorithm SVG string
        source = algorithm.GetSource()
        #print source.replace('\\', '\\\\')
        tokenize.tokenize(StringIO.StringIO(source.replace('\\', '\\\\')).readline, tokenEater)
        algowin.CommitStop()

        # Merge the animation into the HTML
        print {'g1_x_add': g1_x_add,
            'g1_y_add': g1_y_add,
            'g2_x_add': g2_x_add,
            'g2_y_add': g2_y_add
        }
        str_vars = {
            'info_file': 'infos/' + fileName[fileName.rindex('/') + 1:], 
            'animation': ',\n'.join(animation), 
            'graph_str': '\n'.join(graph_strs), 
            'algo_str': ''.join(algo_lines),
            'g1_x_add': g1_x_add,
            'g1_y_add': g1_y_add,
            'g2_x_add': g2_x_add,
            'g2_y_add': g2_y_add
        }
        file.write(animationhead % str_vars)
        file.close()

        # Export the algorithm info to its own HTML file        
        ExportAlgoInfo(fileName, algorithm)
    else:
        pass
