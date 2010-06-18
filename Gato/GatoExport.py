#!/usr/bin/env python2.6
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoExport.py
#	author: Alexander Schliep (alexander@schliep.org)
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
from math import sqrt, pi, sin, cos, atan2, degrees, log10

# SVG Fileheader and JavaScript animation code
#
animationhead = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm"
onload="StartAnimation(evt)">
<defs> 
    <marker id="Arrowhead" 
      viewBox="0 0 10 10" refX="0" refY="5" 
      markerUnits="strokeWidth" 
      markerWidth="4" markerHeight="3" 
      orient="auto"> 
      <path d="M 0 0 L 10 5 L 0 10 z" /> 
    </marker> 
</defs>
<script type="text/ecmascript"><![CDATA[
var step = 0;
var v_ano_id = "va"; //ID prefix for vertex annotation
var e_arrow_id = "ea"; //ID prefix for edge arrow
var svgNS="http://www.w3.org/2000/svg";
var the_evt;
var element;
var blinkcolor;
var blinkcount;
function StartAnimation(evt) {
	the_evt = evt;	
	ShowAnimation();
}
function SetVertexColor(v, color) {
    element = the_evt.target.ownerDocument.getElementById(v);
    element.setAttribute("fill", color);
}
// Cannot map: SetAllVerticesColor(self, color, graph=None, vertices=None):
function SetEdgeColor(e, color) {
    // NOTE: Gato signature SetEdgeColor(v, w, color)
    element = the_evt.target.ownerDocument.getElementById(e);
    element.setAttribute("stroke", color);
    //added changes to color of arrowheads
    element = the_evt.target.ownerDocument.getElementById(e_arrow_id + e);
    if(element != null){
        element.setAttribute("fill", color);
    }
}
//function SetEdgesColor(edge_array, color) {
// Cannot map: SetAllEdgesColor(self, color, graph=None, leaveColors=None)
function BlinkVertex(v, color) {
    element = the_evt.target.ownerDocument.getElementById(v);
    blinkcolor = element.getAttribute("fill")
    blinkcount = 3;
    element.setAttribute("fill", "black");
    setTimeout(VertexBlinker, 3);
}
function VertexBlinker() {
    if (blinkcount %% 2 == 1) {
       element.setAttribute("fill", blinkcolor); 
    } else {
       element.setAttribute("fill", "black"); 
    }
    blinkcount = blinkcount - 1;
    if (blickcount >= 0)
       setTimeout(VertexBlinker, 3);
}




//
//BlinkEdge(self, tail, head, color=None):
//
//Blink(self, list, color=None):
function SetVertexFrameWidth(v, val) {
    var element = the_evt.target.ownerDocument.getElementById(v);
    element.setAttribute("stroke-width", val);
}
function SetVertexAnnotation(v, annotation, color) //removed 'self' parameter to because 'self' parameter was assigned value of v, v of annotation, and so on.
{
    element = the_evt.target.ownerDocument.getElementById(v);
    if(element != null){
	if(the_evt.target.ownerDocument.getElementById(v_ano_id + v) !=null){
		ano = the_evt.target.ownerDocument.getElementById(v_ano_id + v);
		ano.parentNode.removeChild(ano);
	
	}
	
	var newano = the_evt.target.ownerDocument.createElementNS(svgNS,"text");
	x_pos = parseFloat(element.getAttribute("cx")) + parseFloat(element.getAttribute("r")) + 1;
	y_pos = parseFloat(element.getAttribute("cy")) + parseFloat(element.getAttribute("r")) + 1;
	newano.setAttribute("x", x_pos);
	newano.setAttribute("y", y_pos);
	newano.setAttribute("fill",color);
	newano.setAttribute("id", v_ano_id+v);
	newano.setAttribute("text-anchor","center");
	newano.setAttribute("font-size","14.0");
	newano.setAttribute("font-family","Helvetica");
	newano.setAttribute("font-style","normal");
	newano.setAttribute("font-weight","bold");
	newano.appendChild(the_evt.target.ownerDocument.createTextNode(annotation));
	the_evt.target.ownerDocument.documentElement.appendChild(newano);
	
    }
}

//function SetEdgeAnnotation(self,tail,head,annotation,color="black"):
//def UpdateVertexLabel(self, v, blink=1, color=None):
var animation = Array(%(animation)s
);
function ShowAnimation() {
	var duration = animation[step][0] * 4;
	animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
	step = step + 1; 
	if(step < animation.length) 
		setTimeout(ShowAnimation, duration);
}
]]></script>
"""
head = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm">
<defs> 
    <marker id="Arrowhead" 
      viewBox="0 0 10 10" refX="0" refY="5" 
      markerUnits="strokeWidth" 
      markerWidth="4" markerHeight="3" 
      orient="auto"> 
      <path d="M 0 0 L 10 5 L 0 10 z" /> 
    </marker> 
</defs>
"""

footer = """
</svg>
"""






def cmd_as_javascript(cmd, currentTime = 0):
    """ Return an JavaScript array of methodname, target and args """
    def quote(s):
        return "\"%s\"" % str(s)
    if len(cmd.target) == 1:
        target = quote(cmd.target[0])
    else:
        target = quote(cmd.target)
        
    duration = max(1,int(round((cmd.time - currentTime) * 1000, 0)))
                                 
    result = [str(duration), cmd.method.__name__, target]
    for arg in cmd.args:
        result.append(quote(arg))
    return "Array(" + ", ".join(result) + ")"
    
def collectAnimation(algorithm):
    lastTime = algorithm.animation_history.history[0][0]
    result = []
    for time, command in algorithm.animation_history.history:
        result.append(cmd_as_javascript(command,lastTime))
        lastTime = time
    return result

def boundingBox(graphDisplay):
    bb = graphDisplay.canvas.bbox("all") # Bounding box of all elements on canvas
    # Give 20 pixels room to breathe
    x = max(bb[0] - 20,0)
    y = max(bb[1] - 20,0)
    width=bb[2] - bb[0] + 20
    height=bb[3] - bb[1] + 20
    return {'x':x,'y':y,'width':width,'height':height}


def WriteGraphAsSVG(graphDisplay, file):
    # Write Bubbles from weighted matching
    # XXX We make use of the fact that they have a bubble tag
    # XXX What to use as the bubble ID?
    bubbles = graphDisplay.canvas.find_withtag("bubbles")
    for b in bubbles:
        col = graphDisplay.canvas.itemcget(b,"fill")
        # Find center and convert to Embedding coordinates
        coords = graphDisplay.canvas.coords(b)
        x = 0.5 * (coords[2] - coords[0]) + coords[0]
        y = 0.5 * (coords[3] - coords[1]) + coords[1]
        r = 0.5 * (coords[2] - coords[0])
        xe,ye = graphDisplay.CanvasToEmbedding(x,y)
        re,dummy = graphDisplay.CanvasToEmbedding(r,0)
        file.write('<circle cx="%s" cy="%s" r="%s" fill="%s" '\
                   ' stroke-width="0" />\n' % (xe,ye,re,col))           


    # Write Highlighted paths
    # XXX What to use as the bubble ID?
    for pathID, draw_path in graphDisplay.highlightedPath.items():
        # XXX Need to check visibility? See HidePath
        col = graphDisplay.canvas.itemcget(draw_path,"fill")
        width = graphDisplay.canvas.itemcget(draw_path,"width")
        points = ["%s,%s" % graphDisplay.VertexPositionAndRadius(v)[0:2] for v in pathID]
        file.write('<polyline points="%s" stroke="%s" stroke-width="%s" '\
                   'fill="None" />\n' % (" ".join(points),col,width))



    # Write Edges
    for v,w in graphDisplay.G.Edges():
        vx,vy,r = graphDisplay.VertexPositionAndRadius(v)
        wx,wy,r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)

        if graphDisplay.G.directed == 0:
            file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                       ' stroke-width="%s"/>\n' % ((v,w),vx,vy,wx,wy,col,width))
        else:
            # AAARGH. SVG has a retarded way of dealing with arrowheads 
            # It is a known bug in SVG 1.1 that the color of the arrowhead is not inherited
            # Will be fixed in SVG 1.2
            # See bug 995815 in inkscape bug tracker on SF
            # However, even 1.2 will keep the totally braindead way of sticking on the arrowhead
            # to the end! of the arrow. WTF
            # Workarounds:
            # Implement arrows as closed polylines including the arrow (7 vs. 2 coordinates)
            # Q> How to do curved edges with arrows? Loops? 
            x1,y1,x2,y2 = graphDisplay.directedDrawEdgePoints(graphDisplay.VertexPosition(v),
                                                              graphDisplay.VertexPosition(w),0)
            x1e,y1e = graphDisplay.CanvasToEmbedding(x1,y1)
            x2e,y2e = graphDisplay.CanvasToEmbedding(x2,y2)


            if graphDisplay.G.QEdge(w,v): # Directed edges both ways
                file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                           ' stroke-width="%s"/>\n' % ((v,w),x1e,y1e,x2e,y2e,col,width))
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
                    if(cx == wx and cy == wy):
                        angle = atan2(int(float(wy))-int(float(vy)), int(float(wx))-int(float(vx)))
                        file.write('<line id="%s" x1="%s" y1="%s" x2="%f" y2="%f" stroke="%s"'\
                               ' stroke-width="%s" />\n' % ((v,w),vx,vy,tmpX,tmpY,col,width))
                        break

                #Temporary settings for size of polyline arrowhead
                a_width = (1 + 1.5/(1*pow(log10(float(width)), 6)))
                if(a_width > 5.0):
                    a_width = 5.0
                a_width *= float(width) 
                p1 = (0,0)
                p2 = (0, a_width) #0 + int(round(1.5*int(float(width)))))       float(wy) - (p2[1]+p1[1])/2
                p3 = (cr, a_width/2)
                angle = degrees(atan2(int(wy)-int(vy), int(wx)-int(vx)))
                c = (l-2*graphDisplay.zVertexRadius)/l
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                file.write('<polyline id="ea%s" points="%f %f %f %f %s %f" fill="%s" transform="translate(%f,%f)'\
                           ' rotate(%f %f %f)" />\n' % ((v,w), p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))


        # Write Edge Annotations
        if graphDisplay.edgeAnnotation.QDefined((v,w)):
            da = graphDisplay.edgeAnnotation[(v,w)]
            x,y = graphDisplay.canvas.coords(graphDisplay.edgeAnnotation[(v,w)])
            xe,ye = graphDisplay.CanvasToEmbedding(x,y)
            text = graphDisplay.canvas.itemcget(graphDisplay.edgeAnnotation[(v,w)],"text") 
            size = r * 0.9
            offset = 0.33 * size
            col = 'black'
            if text != "":
                file.write('<text id="ea%s" x="%s" y="%s" text-anchor="center" '\
                           'fill="%s" font-family="Helvetica" '\
                           'font-size="%s" font-style="normal">%s</text>\n' % (xe,ye+offset,col,size,text))


    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)

        # Write Vertex
        col = graphDisplay.GetVertexColor(v)
        fw = graphDisplay.GetVertexFrameWidth(v)
        fwe,dummy = graphDisplay.CanvasToEmbedding(fw,0)
        stroke = graphDisplay.GetVertexFrameColor(v)

        #print x,y,r,col,fwe,stroke
        file.write('<circle id="%s" cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"'\
                   ' stroke-width="%s" />\n' % (v,x,y,r,col,stroke,fwe))

        # Write Vertex Label
        col = graphDisplay.canvas.itemcget(graphDisplay.drawLabel[v], "fill")
        size = r*1.0
        offset = 0.33 * size

        file.write('<text id="vl%s" x="%s" y="%s" text-anchor="middle" fill="%s" font-family="Helvetica" '\
                   'font-size="%s" font-style="normal" font-weight="bold" >%s</text>\n' % (v,x,y+offset,col,size,graphDisplay.G.GetLabeling(v)))

        # Write vertex annotation
        size = r*0.9
        text = graphDisplay.GetVertexAnnotation(v)
        col = 'black'
        if text != "":
            file.write('<text id="va%s" x="%s" y="%s" text-anchor="left" fill="%s" font-family="Helvetica" '\
                       'font-size="%s" font-style="normal">%s</text>\n' % (v,x+r+1,y+r+1,col,size,text))
    
        



def ExportSVG(fileName, algowin, algorithm, graphDisplay, secondaryGraphDisplay,
              showAnimation=False):
    """ Export either the current graphs or the complete animation
        (showAnimation=True) to the file fileName
    """
    if showAnimation:
        animation = collectAnimation(algorithm)

        # Reload the graph and execute prolog so we can save the initial state
        # to SVG
        if algorithm.graphFileName is not "":
            algowin.OpenGraph(algorithm.graphFileName)
            execfile(os.path.splitext(algorithm.algoFileName)[0] + ".pro", 
                     algorithm.algoGlobals,
                     algorithm.algoGlobals)
        
        file = open(fileName,'w')
        vars = boundingBox(graphDisplay)
        vars['animation'] = ",\n".join(animation)
        file.write(animationhead % vars)
        # <g id="graph1"> </g>
        WriteGraphAsSVG(graphDisplay, file)    
        source = algorithm.GetSource()
        print source
        file.write(footer)
        file.close()
    else:
        pass
