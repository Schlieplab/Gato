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
from math import sqrt, pi, sin, cos, atan2, degrees, log10, floor

# SVG Fileheader and JavaScript animation code
#
animationhead = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
style="position:absolute; width:100%%; height:100%%"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
preserveAspectRatio="xMinYMin meet"
viewBox="%(x)d %(y)d %(width)d %(height)d"
onload="Initialize(evt)">

<style type="text/css">
<![CDATA[
    * {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    }
]]>
</style>

<defs>     
    <linearGradient id="slider_bar_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="skyblue" ></stop>
		<stop offset="1" stop-color="black"></stop>
    </linearGradient>
    
    <linearGradient id="slider_thumb_lg" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="skyblue"></stop>
		<stop offset="1" stop-color="black"></stop>
    </linearGradient>
    
    <linearGradient id="code_box_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fcfcfc"></stop>
        <stop offset="1" stop-color="#cbcbcb"></stop>
    </linearGradient>
    
    <linearGradient id="speed_box_lg" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0" stop-color="#fcfcfc"></stop>
        <stop offset="1" stop-color="#cbcbcb"></stop>
    </linearGradient>
    
    <linearGradient id="control_box_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fcfcfc"></stop>
        <stop offset="1" stop-color="#999999"></stop>
    </linearGradient>
</defs>

<script type="text/ecmascript"><![CDATA[
var step = 0;
var v_ano_id = "va"; //ID prefix for vertex annotation
var e_arrow_id = "ea"; //ID prefix for edge arrow
var svgNS="http://www.w3.org/2000/svg";
var the_evt_target;     
var the_target;
var the_evt_target_ownerDocument;
var element;
var blinkcolor;
var blinkcount;
var e_blinkcolor;
var e_blinkcount;
var code;    //HTB of code in a vertical layout
var init_graphs;  //initial graphs used for restarting animation
var edges;	//Array of all edges used for SetAllEdgesColor
var action_panel;   //ButtonPanel object for start, step, continue, and stop buttons
var speed_select;	//SpeedSelector object for controlling the speed
var state = null;  //tracks animation state ("running", "stopped", "stepping", "moving")
var movie_slider;       //Slider that controls the point in time of the graph
var timer;  //timer for AnimateLoop
var timeout = 1000;  //Multiplicative factor for timeout
var horiz_layout;  //horizontal LLC for visible elements
var vert_layout;   //vertical LLC for visible elements
var left_vert_layout;   //Layout for code and speed select
var right_vert_layout;  //Layout for graphs
var current_line = 0;  //Currently 'executing' line of code in program.  While running, in range [1, infinity).  0 otherwise.
var default_vertex_radius = 14.0; //Default vertex radius
var default_line_width = 4.0; //Default line width
var x_offset = 25;  //Distance the layout is translated horizontally, in pixels
var y_offset = 45;  //Distance layout is translated vertically, in pixels
var translate_buffer = []; //Global buffer for translating graphs.
var blinking = false; //True iff blinking animation is commencing.  Prevents premature stepping
var step_pressed = false;  //Whether the step button was pressed.  Used to emulate an interrupt.
var step_evt;
var continue_pressed = false;
var continue_evt;

// Triangular scaler at bottom right of graph
var scaler;            

// Current scale factor of the graph
var g_scale_factor = {"x":1, "y":1 };

// Coordinates of mouse start when scaling
var mouse_start = undefined;        

// SVGPoint for converting browser space to svg space
var pt;             

// Interval between saved graph states
var STEP_INTERVAL = 200;

// Array of GraphState objects representing the state of the graph at every STEP_INTERVAL
var graph_states = new Array();      

// Array of attributes that are in use on the elements.  Check to make sure differnet graphs don't introduce new attributes.
var attr_array;                     

// Width and height of the browser after initialize
var browser_width;                  
var browser_height;                 

//Coordiante transformation matrix of the screen
var screen_ctm;                     

// Option dropdown box
var option_dropdown;                

// Viewbox values of the containing svg
var viewbox_x;
var viewbox_y;

// Minimum scale factor for the graph
var MIN_SCALE_FACTOR = .2;          

// Graph width(considering scaling) at the time of a mouse click on the scaler
var scale_graph_width = undefined;  

// Holds the bounding box maximum width and height, to which it will always be set
var G_BBOX_WIDTH;   
var G_BBOX_HEIGHT;

// Graph width(considering scaling) at the time of a mouse click on the scaler
var scale_graph_width = undefined;  

// Boolean variable that is set to true when the graph states are being filled at the start of execution
var filling_states;     

// Max width and height that the graph bounding box is throughout the animation
var MAX_GBBOX_WIDTH = 0;
var MAX_GBBOX_HEIGHT = 0;

var deleted_elements;
var added_elements;  

var two_graph = false;      // True if it is a two-graph animation
var init_height_g1;
var init_transy_g2;         // The initial translate-y value for g2.  Used for scaling smoothly


/**
*
*
*
* Helper functions
*
*
**/
//Accepts a string of the form "...translate(x y)..." and returns x and y in a 2-index array
function getTranslate(str){
    var x;
    var y;
    
    if(str == null || str.indexOf("translate") == -1){
        return new Array(0, 0);
    }
    
    var to_parse = str.slice(str.indexOf("translate") + "translate".length);
    
    if(to_parse == null){
        return new Array(0, 0);
    }
    
    
    var r = to_parse.match(/[^,\(\)\sA-Za-z]+/g);;
    
    if(r[0] != null){
        x = parseFloat(r[0]);
    }
    
    if(r[1] != null){
        y = parseFloat(r[1]);
    }
    
    if(r[1] == null || (to_parse.indexOf(")") < to_parse.indexOf(r[1]))){
        return new Array(x, 0);
    }
    
    return new Array(x, y);

}


//Sets the first instance of "translate" in components "transform" attribute to "translate(x y)"
//Creates one if none exists.
function setTranslate(component, x, y){
    var transformation = component.getAttribute("transform");
    
    if(transformation != null){
        if(transformation.indexOf("translate") == -1){
            component.setAttribute("transform", transformation + " translate(" + x + " " + y + ")");
        }else{
                        var header = transformation.substring(0, transformation.indexOf("translate") + "translate".length);
            var trailer = transformation.slice(transformation.indexOf("translate") + "translate".length);
            trailer = trailer.slice(trailer.indexOf(")"));
        
            var newattr = header + "(" + x + " " + y + trailer;

            component.setAttribute("transform", newattr);
        }

    }else{
        component.setAttribute("transform", "translate(" + x + " " + y + ")");
    }
}


//Accepts a string of the form "...scale(x y)..." and returns x and y in a 2-index array
function getScale(str){
    var x;
    var y;
    
    if(str == null || str.indexOf("scale") == -1){
        return new Array(1, 1);
    }
    
    var to_parse = str.slice(str.indexOf("scale") + "scale".length);
    
    if(to_parse == null){
        return new Array(1, 1);
    }
    
    
    var r = to_parse.match(/[^,\(\)\sA-Za-z]+/g);
    
    if(r[0] != null){
        x = parseFloat(r[0]);
    }
    
    if(r[1] != null){
        y = x;              //This line doesn't make sense?
    }
    
    if(r[1] == null || (to_parse.indexOf(")") < to_parse.indexOf(r[1]))){
        return new Array(x, x);
    }
    
    return new Array(x, y);

}


//Sets the first instance of "scale" in components "transform" attribute to "scale(x y)"
//Creates one if none exists
function setScale(component, x, y){
    var transformation = component.getAttribute("transform");
    
    if(transformation != null){
        if(transformation.indexOf("scale") == -1){
            component.setAttribute("transform", transformation + " scale(" + x + " " + y + ")");
        }else{
                        var header = transformation.substring(0, transformation.indexOf("scale") + "scale".length);
            var trailer = transformation.slice(transformation.indexOf("scale") + "scale".length);
            trailer = trailer.slice(trailer.indexOf(")"));
        
            var newattr = header + "(" + x + " " + y + trailer;

            component.setAttribute("transform", newattr);
        }

    }else{
        component.setAttribute("transform", "scale(" + x + " " + y + ")");
    }
}


// Resizes and positions the graph bounding box based on the size and position of the graph,
// or the MAX_GBBOX_WIDTH/HEIGHT variables if not filling_states
// Additionally, it positions the scaler at the bottom right of the box
function sizeGraphBBox(graph) {
    var rect = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");

    // Set the size of the bounding box
    if (filling_states) {
        rect.setAttribute("width",graph.getBBox().width+10);
        rect.setAttribute("height",graph.getBBox().height+10);

        // Update MAX_GBBOX values if needed
        if ((graph.getBBox().width+10) > MAX_GBBOX_WIDTH)
            MAX_GBBOX_WIDTH = graph.getBBox().width+10;
        if ((graph.getBBox().height+10) > MAX_GBBOX_HEIGHT)
            MAX_GBBOX_HEIGHT = graph.getBBox().height+10;

    } else {
        rect.setAttribute("width", MAX_GBBOX_WIDTH);
        rect.setAttribute("height", MAX_GBBOX_HEIGHT);
    }

    repositionScaler(graph.getBBox().x, graph.getBBox().y);

    // Reposition the bounding box
    rect.setAttribute("x", graph.getBBox().x-10);
    rect.setAttribute("y", graph.getBBox().y-10);
}


//Creates a textnode with the given text
function createLabel(id, text) {
    var label = the_evt_target_ownerDocument.createElementNS(svgNS, "text");
    label.setAttribute("id", id);
    label.setAttribute("x", 0);
    label.setAttribute("y", 14);
    label.setAttribute("font-size", "15px");
    var textNode = document.createTextNode(text);
    label.appendChild(textNode);
    the_evt_target_ownerDocument.documentElement.appendChild(label);
    return label;
}


//Return a 2-index array [v1,v2] which has an angle of
//90 degrees clockwise to the vector (dx,dy)
function Orthogonal(dx, dy){

    var u1 = dx;
    var u2 = dy;
    
    var length = Math.sqrt(Math.pow(u1,2) + Math.pow(u2,2));
    
    if(length < 0.001){
        length = 0.001;
    }
    
    u1 /= length;
    u2 /= length;
    return [-1*u2, u1];
}


//Fills the edges array with all the edges that are currently active on the graph
function fillEdgesArray() {
    edges = new Array();
    var highestNode = 1;
    while (the_evt_target_ownerDocument.getElementById("g1_" + highestNode) != null)
        highestNode++;
    highestNode--;

    //See if it is a two graph algo also, have 2nd edges array declared just in case
    for (var i=0; i<=highestNode; i++) {
        for (var j=0; j<=highestNode; j++) {
            var element = the_evt_target_ownerDocument.getElementById("g1_("+i+", "+j+")");
            if (element != null) 
                edges.push(element);
        }
    }
}


//Creates an arrowhead on a line starting at (vx,vy) and ending at (wx,wy) and parallel to it
//Arrowhead with given id touches the outide of a vertex with cx=wx and xy=wy
function createArrowhead(vx, vy, wx, wy, stroke_width, id){

        var l = Math.sqrt(Math.pow(parseFloat(wx)-parseFloat(vx),2) + Math.pow(parseFloat(wy)-parseFloat(vy), 2));
        
        
                if (l < .001)
                    l = .001;
                
        var a_width = (1 + 1.5/(1*Math.pow(Math.log(parseFloat(stroke_width))/Math.log(10), 6)));

                if(a_width > 5.0)
                    a_width = 5.0;
            
        var cr = default_vertex_radius;
        
                a_width = a_width * parseFloat(stroke_width);

                var p1 = [0,0];
                var p2 = [0, a_width];
                var p3 = [cr, a_width/2];
                var angle = (Math.atan2(parseInt(wy)-parseInt(vy), parseInt(wx)-parseInt(vx))) * 180/Math.PI;
                var c = (l-2*default_vertex_radius)/l;
                var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
                var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
        
        var arrowhead = the_evt_target_ownerDocument.createElementNS(svgNS, "polyline");
        arrowhead.setAttribute("points", p1[0] + " " + p1[1] + " " + p2[0] + " " + p2[1] + " " + p3[0] + " " + p3[1]);
        arrowhead.setAttribute("fill", "#EEEEEE");
        arrowhead.setAttribute("transform", "translate(" + tmpX + " " + (tmpY-a_width/2) + ") rotate(" + angle + " " + p1[0] + " " + a_width/2 + ")");
        arrowhead.setAttribute("id", id);

                return arrowhead;
}


/**
*
*
*
* Classes for visible components
*
*
*/
//Highlightable block of text
//Parameters: horizontal and vertical padding between lines, id, font size of text, and layout mode (horizontal or vertical)
function HighlightableTextBlock(hp, vp, id, font_size, layout){
    this.line_llc = new LinearLayoutComponent(hp, vp, id, layout);
    this.line_llc.group.setAttribute("font-size", font_size);
    this.highlight_group = the_evt_target_ownerDocument.createElementNS(svgNS,"g");
    this.highlight_group.setAttribute("id", id + "_hg");
    the_evt_target_ownerDocument.documentElement.insertBefore(this.highlight_group, this.line_llc.group);   
}


//Initializes prototype, to call object.function
function HTB_prototypeInit(){
    var htb = new HighlightableTextBlock(2,2,"foo",14, "vertical");
    HighlightableTextBlock.prototype.insertLine = HTB_insertLine;
    HighlightableTextBlock.prototype.deleteLine = HTB_deleteLine;
    HighlightableTextBlock.prototype.highlightLine = HTB_highlightLine;
    HighlightableTextBlock.prototype.removeHighlight = HTB_removeHighlight;
    HighlightableTextBlock.prototype.addBoundingBox = HTB_addBoundingBox;
    htb = the_evt_target_ownerDocument.getElementById("foo");
    htb.parentNode.removeChild(htb);
    htb = the_evt_target_ownerDocument.getElementById("foo_hg");
    htb.parentNode.removeChild(htb);
}


//Adds a rectangular box around the code section
function HTB_addBoundingBox(color) {
    var bbox = this.line_llc.group.getBBox();
    var line = this.line_llc.group.childNodes.item(0);
    var line_bbox = line.getBBox();
    var rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    var line_translation = getTranslate(this.line_llc.group.childNodes.item(0).getAttribute("transform"));
    var dx = line.getAttribute("dx");
    if(dx == null)
        dx = 0;
    else
        dx = parseFloat(dx);
    
    rect.setAttribute("id", "codeBox");
    rect.setAttribute("width", bbox.width + this.line_llc.h_padding*2);
    rect.setAttribute("height", bbox.height + this.line_llc.v_padding*2 + 10);
    rect.setAttribute("x", line_bbox.x + line_translation[0] - this.line_llc.h_padding - dx);
    rect.setAttribute("y", bbox.y - this.line_llc.v_padding - 5);
    rect.setAttribute("fill", "url(#code_box_lg)");
    rect.setAttribute("stroke", color);
    rect.setAttribute("stroke-width", "3px");
    rect.setAttribute("rx", 5);
    rect.setAttribute("ry", 5);
    this.highlight_group.insertBefore(rect, this.highlight_group.firstChild);
}


//Insert line with respective into nth slot.  0-based indexing.  If line already exists in HTB, line is shifted to respective spot.
function HTB_insertLine(id, n){
    var to_insert = the_evt_target_ownerDocument.getElementById(id);
    if(to_insert != null && to_insert.getAttribute("blank") != null && to_insert.getAttribute("blank") == "true"){ // Empty Text  Replace with Rectangle
        var new_rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
        var children = this.line_llc.group.childNodes;
        for(i = 0; i < children.length; i++){
            if(children.item(i).getAttribute("blank") == "false"){
                new_rect.setAttribute("x", children.item(i).getAttribute("x"));
                new_rect.setAttribute("y", children.item(i).getAttribute("y"));
                new_rect.setAttribute("height", children.item(i).getBBox().height);
                new_rect.setAttribute("width", this.line_llc.group.getBBox().width);
                to_insert.parentNode.removeChild(to_insert);
                new_rect.setAttribute("id", to_insert.getAttribute("id"));
                new_rect.setAttribute("fill", "white");
                new_rect.setAttribute("fill-opacity", 0);
                the_evt_target_ownerDocument.documentElement.appendChild(new_rect);
                break;
            }
        }
    }
    this.line_llc.insertComponent(id, n);
}


//Deletes nth line, using 0-based indexing
function HTB_deleteLine(n){
    this.line_llc.deleteComponent(n);
    this.removeHighlight(this.line_llc.group.childNodes.length);
}


//highlight nth line, using 0-based indexing
function HTB_highlightLine(n){
    if(n < this.line_llc.group.childNodes.length && n >= 0){
        if(the_evt_target_ownerDocument.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + (n+1)) == null){
            var line = this.line_llc.group.childNodes.item(n);
            var htb_bbox = this.line_llc.group.getBBox();
            var line_bbox = line.getBBox();
            var line_translation = getTranslate(this.line_llc.group.childNodes.item(n).getAttribute("transform"));

            
            var dx = line.getAttribute("dx");
            var dy = line.getAttribute("dy");
            if(dx == null){
                dx = 0;
            }else{
                dx = parseFloat(dx);
            }
            if(dy == null){
                dy = 0;
            }else{
                dy = parseFloat(dy);
            }

            var background = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
            background.setAttribute("x", line_bbox.x + line_translation[0] - this.line_llc.h_padding - dx);
            background.setAttribute("y", line_bbox.y + line_translation[1] - this.line_llc.v_padding - dy);
            background.setAttribute("width", htb_bbox.width + 2*this.line_llc.h_padding);
            background.setAttribute("height", line_bbox.height + 2*this.line_llc.v_padding);
            background.setAttribute("style", "opacity:.35");
            background.setAttribute("stroke", "blue");
            background.setAttribute("fill", "yellow");
            background.setAttribute("id", this.line_llc.group.getAttribute("id") + "_hl" + (n+1));
            
            this.highlight_group.appendChild(background);
        }
    }
}


//Removes the highlight of the nth line, using 0-based indexing.
function HTB_removeHighlight(n){
    var hl = the_evt_target_ownerDocument.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + (n+1));
    if(hl != null){
        hl.parentNode.removeChild(hl);
    }
}


//Layout for components
//Lays out components linearly either 'horizontal' or 'vertical' as specified by layout
//With hp pixels of horizontal padding and vp pixels of vertical padding
function LinearLayoutComponent(hp, vp, id, layout){
    this.h_padding = hp;  //Number of pixels padding the top and bottom of each line
    this.v_padding = vp;  //Number of pixels padding the left and right of each line
    this.id = id;           //ID of group that is abstracted by this HTB instance
    
    //Create new group element to place all lines of code
    this.group = the_evt_target_ownerDocument.createElementNS(svgNS,"g");
    this.group.setAttribute("id", id);
    the_evt_target_ownerDocument.documentElement.appendChild(this.group);
    this.layout = layout;  //'horizontal' or 'vertical'
}


//Initializes prototype to call methods of the form object.function
function LLC_prototypeInit(){
    var llc = new LinearLayoutComponent(0,0,"foo","horizontal");
    LinearLayoutComponent.prototype.insertComponent = LLC_insertComponent;
    LinearLayoutComponent.prototype.deleteComponent = LLC_deleteComponent;
    LinearLayoutComponent.prototype.resnapComponent = LLC_resnapComponent;
    llc.group.parentNode.removeChild(llc.group);
}


//Insert element of specified id into nth slot, using 0-based indexing.
//If element is already in LLC, element is moved to nth slot
function LLC_insertComponent(id, n){
    var new_c = the_evt_target_ownerDocument.getElementById(id);
    var padding = 0;
    if(this.layout == "horizontal"){
        padding = this.h_padding;
    }else{
        padding = this.v_padding;
    }
    var bbox = null;
    var translation = null;
    var shift = 0;
    
    if(new_c != null){   //Component exists
        if((new_c.parentNode != this.group) && (n <= this.group.childNodes.length) && (n >=0)){ //Component is not in group.  Insert and shift if necessary
        
            if(n == 0){ //inserting as first element
                setTranslate(new_c, 0, 0);
            }else{  //not inserting as first element
                bbox = this.group.childNodes.item(n-1).getBBox();
                //translation of previous element
                translation = getTranslate(this.group.childNodes.item(n-1).getAttribute("transform"));
                
                if(this.layout == "horizontal"){
                    shift = translation[0] + bbox.width + 2*padding;
                    setTranslate(new_c, shift, 0);

                }else{      
                    shift = translation[1] + bbox.height + 2*padding;
                    setTranslate(new_c, 0, shift);
                }
            }
            
            if(n == this.group.childNodes.length){
                this.group.appendChild(new_c);
            }else{  
                var children = this.group.childNodes;
                this.group.insertBefore(new_c, children.item(n));
                for(i = n+1; i < children.length; i++){
                    bbox = children.item(i-1).getBBox();
                    translation = getTranslate(children.item(i-1).getAttribute("transform"));
                    if(this.layout == "horizontal"){
                        shift = translation[0] + bbox.width + 2*padding;
                        setTranslate(children.item(i), shift, 0);
                    }else{      
                        shift = translation[1] + bbox.height + 2*padding;
                        setTranslate(children.item(i), 0, shift);
                    }
                    
                }
            }
        }else if(n <= this.group.childNodes.length && (n >= 0)){ //Component is in group.  Move it and shift necessary lines
            var children = this.group.childNodes;
            var old_index = 0;
            for(; old_index < children.length; old_index++){
                if(children.item(old_index) === new_c){
                    break;
                }
            }
            if(old_index > n){
                this.group.insertBefore(new_c, children.item(n));
                
                for(i = n; i <= old_index; i++){
                    if(i == 0){
                        setTranslate(children.item(i), 0, 0);
                    }else{
                        bbox = children.item(i-1).getBBox();    
                        translation = getTranslate(children.item(i-1).getAttribute("transform"));
                        if(this.layout == "horizontal"){
                            shift = translation[0] + bbox.width + 2*padding;
                            setTranslate(children.item(i), shift, 0);
                        }else{      
                            shift = translation[1] + bbox.height + 2*padding;
                            setTranslate(children.item(i), 0, shift);
                        }
                    }
                }
            }else if(old_index < n){
                if(n == children.length){
                    this.group.appendChild(new_c);
                }else{  
                    this.group.insertBefore(new_c, children.item(n+1));
                }
                for(i = old_index; i <= n; i++){            
                    if(i == 0){
                        setTranslate(children.item(i), 0, 0);

                    }else{
                        bbox = children.item(i-1).getBBox();
                        translation = getTranslate(children.item(i-1).getAttribute("transform"));
                        if(this.layout == "horizontal"){
                            shift = translation[0] + bbox.width + 2*padding;
                            setTranslate(children.item(i), shift, 0);
                        }else{      
                            shift = translation[1] + bbox.height + 2*padding;
                            setTranslate(children.item(i), 0, shift);
                        }
                    }
                }
            }
        }
    }
}


//Refits the nth element, to fit according to specs
function LLC_resnapComponent(n){
    var children = this.group.childNodes;
    var child = children.item(n);
    child.parentNode.removeChild(child);
    
    the_evt_target_ownerDocument.documentElement.appendChild(child);
    this.insertComponent(child.getAttribute("id"), n);
}


//Deletes the nth element, using 0-based indexing, and refits components if necessary
function LLC_deleteComponent(n){
    var padding = 0;
    var children = this.group.childNodes;
    var bbox = null;
    var translation = null;
    var shift = 0;
    
    if(this.layout == "horizontal"){
        padding = this.h_padding;
    }else{
        padding = this.v_padding;
    }
    
    if(this.group.childNodes.length == 0){
        return;
    }   

    var removed_element = this.group.removeChild(this.group.childNodes.item(n));
    
    for(i = n; i < children.length; i++){

        if(i == 0){

            setTranslate(children.item(i), 0, 0);


        }else{
            bbox = children.item(i-1).getBBox();


            translation = getTranslate(children.item(i-1).getAttribute("transform"));

            if(this.layout == "horizontal"){
                shift = translation[0] + bbox.width + 2*padding;
                setTranslate(children.item(i), shift, 0);
            }else{      
                shift = translation[1] + bbox.height + 2*padding;

                setTranslate(children.item(i), 0, shift);
            }
        }
    }
}


//Button Panel
//Buttons are padded by hp and vp pixels.
//Button panel's id given by id, and layout of buttons is given by layout
function ButtonPanel(hp, vp, id, layout){
    this.llc = new LinearLayoutComponent(hp, vp, id, layout);
}


//Initializes prototype for button panel
function BP_prototypeInit(){
    var bp = new ButtonPanel(0,0,"baz","horizontal");
    ButtonPanel.prototype.createButton = BP_createButton;
    ButtonPanel.prototype.deleteButton = BP_deleteButton;
    ButtonPanel.prototype.deleteButtonById = BP_deleteButtonById;
    ButtonPanel.prototype.activateButton = BP_activateButton;
    ButtonPanel.prototype.deactivateButton = BP_deactivateButton;
    bp.llc.group.parentNode.removeChild(bp.llc.group);
}


//Creates a button
//Parameters:  button id, shape (path), color, index in button panel, button action
//Inserts button into specified and assigns specifieds action
function BP_createButton(id, draw_path, color, index, action){  //Create button with corresponding id, text, and action into slot #index
    if(the_evt_target_ownerDocument.getElementById(id) == null){
        var button_group = the_evt_target_ownerDocument.createElementNS(svgNS, "path");
        button_group.setAttribute("id", id);
        button_group.setAttribute("d", draw_path);
        button_group.setAttribute("fill", color);
        button_group.setAttribute("cursor", "pointer");
        button_group.setAttribute("onclick", action);
                button_group.setAttribute("fill-opacity", 1);
        the_evt_target_ownerDocument.documentElement.appendChild(button_group);
        this.llc.insertComponent(button_group.getAttribute("id"), index);
    }else{
        this.llc.insertComponent(id, index);
    }
}


//Deletes the nth button from panel (0-based indexing)
function BP_deleteButton(n){
    this.llc.deleteComponent(n);
}


//Deletes button of given id from the panel
function BP_deleteButtonById(id){
    var children = this.llc.group.childNodes;
    
    for(i = 0; i < children.length; i++){
        if(children.item(i).getAttribute("id") == id){
            this.deleteButton(i);
            break;
        }
    }
}


//Activates button with corresponding id and assigns a specified action
function BP_activateButton(id, action){
    var children = this.llc.group.childNodes;
    for(i = 0; i < children.length; i++){
        if(children.item(i).getAttribute("id") == id){
            children.item(i).setAttribute("onclick", action);
            children.item(i).setAttribute("cursor", "pointer");
            children.item(i).setAttribute("fill-opacity", 1);
            break;
        }
    }
}


//Deactivates button with corresponding id
function BP_deactivateButton(id){
    var children = this.llc.group.childNodes;

    for(i = 0; i < children.length; i++){
        if(children.item(i).getAttribute("id") == id){
            children.item(i).setAttribute("onclick", "");
            children.item(i).setAttribute("cursor", "default");
            children.item(i).setAttribute("fill-opacity", "0.5");
            break;
        }
    }
}


/**
*
*
*
* Slider
*
*
*/
//Creates a simple slider
//Parameters: slider id, height of slider thumb, x-offset from edge of canvas (pixels), 2-index array, specifying the upper and lower bounds of the slider,
//start value of slider, array of strings specifying  labels distributed along slider
//title of slider, and an array of 2-index arrays of ['attribute', 'action'] pairs
function Slider(id, slider_width, thumb_height, offset, range, start_value, labels, title, actions){    
    this.slider = null;
    this.slider_bar = null;
    this.slider_thumb = null;
    this.low_bound = range[0];
    this.up_bound = range[1];
    this.thumb_active = false;
    this.current_setting = range[0];
    this.offset = offset;
    
    this.default_thickness = 10;
    var font_size = 10;
    
    this.slider = the_evt_target_ownerDocument.createElementNS(svgNS, "g"); 
    this.slider.setAttribute("id", id);
    
    this.slider_bar = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    this.slider_bar.setAttribute("width", slider_width);
    this.slider_bar.setAttribute("height", this.default_thickness);
    this.slider_bar.setAttribute("x", this.default_thickness/2);
    this.slider_bar.setAttribute("y",(thumb_height-this.default_thickness)/2);
    this.slider_bar.setAttribute("rx", this.default_thickness/2);
    this.slider_bar.setAttribute("ry", this.default_thickness/2);
    this.slider_bar.setAttribute("stroke", "black");
    this.slider_bar.setAttribute("fill", "url(#slider_bar_lg)");
    this.slider_bar.setAttribute("stroke-width", 1);
    this.slider_bar.setAttribute("cursor", "pointer");
    this.slider_bar.setAttribute("id", id + "_slider_bar");
    this.slider.appendChild(this.slider_bar);
    
    this.slider_thumb = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    this.slider_thumb = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    this.slider_thumb.setAttribute("width", this.default_thickness);
    this.slider_thumb.setAttribute("height", thumb_height);
    this.slider_thumb.setAttribute("rx", this.default_thickness/2);
    this.slider_thumb.setAttribute("ry", this.default_thickness/2);
    this.slider_thumb.setAttribute("stroke", "black");
    this.slider_thumb.setAttribute("fill", "url(#slider_thumb_lg)");
    this.slider_thumb.setAttribute("stroke-width", 1);
    this.slider_thumb.setAttribute("cursor", "pointer");
    this.slider_thumb.setAttribute("id", id + "_slider_thumb");
    this.slider.appendChild(this.slider_thumb);
    
    //create labels below slider
    for(i in labels){
        var text = the_evt_target_ownerDocument.createElementNS(svgNS, "text");
        text.setAttribute("x", this.default_thickness/2 + i*(slider_width/(labels.length-1)));
        text.setAttribute("y", thumb_height+ font_size);
        text.setAttribute("text-anchor","middle");
        text.setAttribute("font-size", font_size);
        text.setAttribute("font-family","Helvetica");
        text.setAttribute("font-style","normal");
        text.appendChild(the_evt_target_ownerDocument.createTextNode(labels[i]));
        this.slider.appendChild(text);
    }
    
    //create slider title
    
    var header = the_evt_target_ownerDocument.createElementNS(svgNS, "text");
    header.setAttribute("x", (this.default_thickness + slider_width)/2);
    header.setAttribute("y", 0);
    header.setAttribute("text-anchor","middle");
    header.setAttribute("font-size", font_size);
    header.setAttribute("font-family","Helvetica");
    header.setAttribute("font-style","normal");
    header.appendChild(the_evt_target_ownerDocument.createTextNode(title));
    this.slider.appendChild(header);
        
    for(i in actions){
        this.slider.setAttribute(actions[i][0], actions[i][1]);
    }
    
    the_evt_target_ownerDocument.documentElement.appendChild(this.slider);
}

/**
*
*
* Speed Slider functions
*
*
*/
//Drags or moves thumb when slider is clicked
function Click_SSlider(evt){
    if(evt.target.getAttribute("id") == "speed_slider_slider_thumb"){  //Drag thumb
        speed_slider.thumb_active = true;
    } else if(evt.target.getAttribute("id") == "speed_slider_slider_bar"){  //Move thumb.
        Move_SSlider(evt);
    }
}

//Stops thumb movement
function Deactivate_SSlider(evt){
    speed_slider.thumb_active=false;
}

//Moves thumb and changes associated values
function Move_SSlider(evt){
    var bbox = speed_slider.slider_bar.getBBox();
    var x_pos = evt.clientX;
    if(evt.clientX == undefined)
        x_pos = evt.touches[0].clientX;
        
    speed_slider.slider_thumb.setAttribute("x", x_pos-speed_slider.offset-(speed_slider.default_thickness/2));

    speed_slider.current_setting = speed_slider.low_bound + (speed_slider.up_bound-speed_slider.low_bound)*(speed_slider.slider_thumb.getAttribute("x")/speed_slider.slider_bar.getAttribute("width"));
    //timeout = Math.log(speed_slider.current_setting) * Math.log(speed_slider.current_setting);
        timeout = speed_slider.current_setting/20;
}

//Drag slider and change associated values
function Drag_SSlider(evt){
    if(speed_slider.thumb_active){
        var x_pos = evt.clientX;
        
        if(x_pos==undefined){
            x_pos = evt.touches[0].clientX;
        }
        if(x_pos >= speed_slider.slider_bar.getBBox().x+speed_slider.offset && x_pos <= (speed_slider.slider_bar.getBBox().x + speed_slider.offset + speed_slider.slider_bar.getBBox().width)){
            speed_slider.slider_thumb.setAttribute("x", x_pos-speed_slider.offset-(speed_slider.default_thickness/2));
            speed_slider.current_setting = speed_slider.low_bound + (speed_slider.up_bound-speed_slider.low_bound)*(speed_slider.slider_thumb.getAttribute("x")/speed_slider.slider_bar.getAttribute("width"));
            //timeout = Math.log(speed_slider.current_setting) * Math.log(speed_slider.current_setting);
                        timeout = speed_slider.current_setting/20;
        }
    }
}

/* Constructor that creates a speed selector group.  Currently color and selectColor are
hardcoded into the box functions. */
function SpeedSelector(id, boxWidth, color, selectColor) {
    this.llc = new LinearLayoutComponent(8,4,id, "horizontal");
    this.color = color;
    this.boxWidth = boxWidth;
    this.selectColor = selectColor;
    this.label = createLabel("speedLabel", "Animation Speed:");
    this.llc.insertComponent(this.label.getAttribute("id"),0);
    this.lo = createSpeedSelect("lo", "0", "0", boxWidth, ".25x", this.color);
    this.lomid = createSpeedSelect("lomid", "0", "0", boxWidth, ".5x", this.color);
    this.mid = createSpeedSelect("mid", "0", "0", boxWidth, "1x", this.color);
    this.midhi = createSpeedSelect("midhi", "0", "0", boxWidth, "2x", this.color);
    this.hi = createSpeedSelect("hi", "0", "0", boxWidth, "4x", this.color);
    this.llc.insertComponent(this.lo.getAttribute("id"),1);
    this.llc.insertComponent(this.lomid.getAttribute("id"), 2);
    this.llc.insertComponent(this.mid.getAttribute("id"), 3);
    this.llc.insertComponent(this.midhi.getAttribute("id"), 4);
    this.llc.insertComponent(this.hi.getAttribute("id"), 5);
    
    setTranslate(this.llc.group, 100, 0);
    
    this.boxSelected(this.lo.firstChild);
}

function SS_prototypeInit() {
    SpeedSelector.prototype.boxSelected = SS_boxSelected;
    SpeedSelector.prototype.addBoundingBox = SS_addBoundingBox;
}

function SS_boxSelected(box) {
    var boxId = box.getAttribute("id");
    var groups = this.llc.group.childNodes;     

    //Change box colors
    //Start at i=2 to skip the label, and the bounding box
    for ( i=2; i<groups.length; i++) {
        var currBox = groups.item(i).firstChild;
        
        if (boxId === currBox.getAttribute("id"))
            currBox.setAttribute("fill-opacity", 1);
        else
            currBox.setAttribute("fill-opacity", .5);
    }
    
    //Change animation speed
    if (boxId === "lo") 
        timeout = 200;
    else if (boxId === "lomid") 
        timeout = 37;
    else if (boxId === "mid") 
        timeout = 22;
    else if (boxId === "midhi") 
        timeout = 10;
    else if (boxId === "hi") 
        timeout = .8;
    
}

/*
var bbox = this.line_llc.group.getBBox();
    var line = this.line_llc.group.childNodes.item(0);
    var line_bbox = line.getBBox();
    var rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    var line_translation = getTranslate(this.line_llc.group.childNodes.item(0).getAttribute("transform"));
    var dx = line.getAttribute("dx");
    if(dx == null)
        dx = 0;
    else
        dx = parseFloat(dx);
    
    rect.setAttribute("id", "codeBox");
    rect.setAttribute("width", bbox.width + this.line_llc.h_padding*2);
    rect.setAttribute("height", bbox.height + this.line_llc.v_padding*2 + 10);
    rect.setAttribute("x", line_bbox.x + line_translation[0] - this.line_llc.h_padding - dx);
    rect.setAttribute("y", bbox.y - this.line_llc.v_padding - 5);
    rect.setAttribute("fill", "none");
    rect.setAttribute("stroke", color);
    rect.setAttribute("stroke-width", "4px");
    //setScale(rect, .5, .5);
    this.highlight_group.appendChild(rect);
    */

function SS_addBoundingBox(color) {
    var this_bbox = this.llc.group.getBBox();
    var llc_bbox = left_vert_layout.group.getBBox();
    var rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    
    rect.setAttribute("id", "speedBox");
    rect.setAttribute("width", this_bbox.width + this.llc.h_padding*3);
    rect.setAttribute("height", this_bbox.height + this.llc.v_padding*2 + 10);
    rect.setAttribute("x", llc_bbox.x - left_vert_layout.h_padding);
    rect.setAttribute("y", this_bbox.y - this.llc.v_padding);
    rect.setAttribute("rx", 5);
    rect.setAttribute("ry", 5);
    rect.setAttribute("fill", "url(#speed_box_lg)");
    rect.setAttribute("stroke", color);
    rect.setAttribute("stroke-width", "2px");
    this.llc.group.insertBefore(rect, the_evt_target.getElementById('speedLabel'));
}

//Creates a speed selector box with the given parameters
function createSpeedSelect(id, x, y, boxWidth, text, color) {
    var group = the_evt_target_ownerDocument.createElementNS(svgNS, "g");
    var rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    var label = the_evt_target_ownerDocument.createElementNS(svgNS, "text");
    
    group.setAttribute("id", id + "_g");
    
    rect.setAttribute("id", id);
    rect.setAttribute("x", x);
    rect.setAttribute("y", y);
    rect.setAttribute("rx", 4);
    rect.setAttribute("ry", 4);
    rect.setAttribute("width", boxWidth);
    rect.setAttribute("height", boxWidth);
    rect.setAttribute("fill", "blue");
    rect.setAttribute("stroke", "#0000B2");
    rect.setAttribute("stroke-width", "1px");
    rect.setAttribute("cursor", "pointer");
    rect.setAttribute("onclick", "speed_select.boxSelected(this)");
    
    label.setAttribute("x", x + boxWidth/8);
    label.setAttribute("y", y-4);
    label.setAttribute("font-size", "10px");
    var textNode = document.createTextNode(text);
    label.appendChild(textNode);
    
    group.appendChild(rect);
    group.appendChild(label);
    
    the_evt_target_ownerDocument.documentElement.appendChild(group);
    return group;
}

// OptionDropdown Object constructor.  Creates the cog dropdown that controls animation speed
function OptionDropdown(id, height, width) {
    
    this.height = height + 4;
    this.width = width;
    this.x_trans = null;
    this.y_trans = null;
    this.speed_shown = false;
    
    //The g-element containing all other pieces
    this.dropdown = null;
    
    //The g-element containing the button always displayed
    this.button = null;
    
    //The button rectangle
    this.rect = null;
    
    //Cog image
    this.cog = null;
    
    //Triangle dropdown icon
    this.triang = null;
    
    //Options to go in the dropdown menu
    this.options = new Array("This is an option");
    //g-element containing the actual dropdown menu
    this.menu = null;   
    //Array of g-elements containing a rect, and text element 
    this.menu_items = null;
    
    this.rect_fill = '#ffffff';
    this.rect_selected_fill = '#aaaaaa';
    
    this.dropdown = the_evt_target_ownerDocument.createElementNS(svgNS, 'g');
    this.dropdown.setAttribute("id", id);
    
    this.button = the_evt_target_ownerDocument.createElementNS(svgNS, 'g');
    this.button.setAttribute('id', id + "_button");
    this.button.setAttribute("cursor", "pointer");
    this.dropdown.appendChild(this.button);
    
    this.rect = the_evt_target_ownerDocument.createElementNS(svgNS, 'rect');
    this.rect.setAttribute('id', 'dropdown_rect');
    this.rect.setAttribute("width", this.width);
    this.rect.setAttribute("height", this.height);
    this.rect.setAttribute("rx", '4');
    this.rect.setAttribute("ry", '4');
    this.rect.setAttribute('x', 0);
    this.rect.setAttribute('y', 0);
    this.rect.setAttribute('stroke', '#cbcbcb');
    this.rect.setAttribute('stroke-width', '2px');
    this.rect.setAttribute('fill', this.rect_fill);
    this.button.appendChild(this.rect);
    
    this.cog = the_evt_target_ownerDocument.createElementNS(svgNS, "image");
    this.cog.setAttribute("id", "dropdown_cog");
    this.cog.setAttributeNS('http://www.w3.org/1999/xlink','href', "cog.png");
    this.cog.setAttribute("x", 0);
    this.cog.setAttribute("y", 2);
    this.cog.setAttribute('width', this.width*2/3 + this.width/12);
    this.cog.setAttribute('height', height);
    this.button.appendChild(this.cog);
    
    this.triang = the_evt_target_ownerDocument.createElementNS(svgNS, "polygon");
    this.triang.setAttribute("id", "dropdown_triang");
    var x1 = width*2/3 + width/12 - 1;
    var x2 = width - 3;
    var x3 = (x1 + x2)/2;
    this.triang.setAttribute("points",  String(x1 + "," + height/2 + " " + x2 + "," + height/2 + " " + x3 + "," + (height-2)));
    this.triang.setAttribute("fill", "#888888");
    this.button.appendChild(this.triang);
    
    this.position_dropdown();
    this.build_dropdown();
    
    //Put mouseover and mouseout effects here
    this.dropdown.setAttribute("onmouseover", "OD_mouseover(evt)");
    this.dropdown.setAttribute("onmouseout", "OD_mouseout(evt)");
    this.button.setAttribute("onmousedown", "OD_mouseclick(evt)");
    
    the_evt_target_ownerDocument.documentElement.appendChild(this.dropdown);
}


// OptionDropdown initialization function
function OD_build_dropdown() {
    
    this.menu = the_evt_target_ownerDocument.createElementNS(svgNS, "g");
    
    var x_trans = -1*speed_select.llc.group.getBBox().width + speed_select.llc.h_padding*8;
    var y_trans = speed_select.llc.group.getBBox().height - speed_select.llc.v_padding*2;
    setTranslate(speed_select.llc.group, x_trans, y_trans);
    
    this.menu.setAttribute("visibility", "hidden");
    this.menu.appendChild(speed_select.llc.group);
    this.dropdown.appendChild(this.menu);
}


//Positions the option dropdown at the top right of the screen
function OD_position_dropdown() {
    this.y_trans = 10;
    //var x_trans = right_vert_layout.group.getBBox().x + right_vert_layout.group.getBBox().width;
    this.x_trans = (browser_width - 50)/screen_ctm.a;
    var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
    var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
    var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
    var translation3 = getTranslate(graph.getAttribute("transform"));
    
    this.x_trans = translation1[0] + translation2[0] + translation3[0] + graph.getBBox().width;
    setTranslate(this.dropdown, this.x_trans, this.y_trans);
}


//Changes the appearance of the dropdown when the mouse is over it
function OD_mouseover(evt) {
    var pieces = new Array(option_dropdown.rect, option_dropdown.triang);
    
    for (i in pieces) 
        pieces[i].setAttribute("opacity", .5);
}


//reverses the change in appearance of mouseover, and closes dropdown menu
function OD_mouseout(evt) {
    var pieces = new Array(option_dropdown.rect, option_dropdown.triang);
    
    for (i in pieces) 
        pieces[i].setAttribute("opacity", 1);
        
}


//Pops open the dropdown menu
function OD_mouseclick(evt) {

    if (option_dropdown.speed_shown === false) 
        option_dropdown.menu.setAttribute('visibility', 'visible');
    else 
        option_dropdown.menu.setAttribute('visibility', 'hidden');
        
    if (option_dropdown.speed_shown)
        option_dropdown.speed_shown = false;
    else
        option_dropdown.speed_shown = true;
}


// Initialize the functions for the OptionDropdown
function Option_prototypeInit() {
    OptionDropdown.prototype.position_dropdown = OD_position_dropdown;
    OptionDropdown.prototype.build_dropdown = OD_build_dropdown;
}

/**
*
*
*
* Animation control functions
*
*
*/
//Starts animation loop.  If called more than once, resets display and begins loop
function StartAnimation(evt){
    console.log("id: " + evt.target.getAttribute("id"));
    if(evt.target.getAttribute("id") == "start_button"){
        if(state != null){ //Graph must be refreshed
            //console.log("refreshing graph state: " + state);
            jumpToStep(step);
        }

        // If previous animation completed, then reset elements to beginning state
        // Don't reset when the step is not 0 though(user can move playback bar then start animation)
        if (state == "stopped" && step == 0) {
            setGraphState(graph_states[0]);
        }
    
        state = "running";
        action_panel.activateButton("stop_button", "StopAnimation(evt)");
        action_panel.activateButton("continue_button", "ContinueAnimation(evt)");
        action_panel.activateButton("step_button", "StepAnimation(evt)");
        action_panel.deactivateButton("start_button");
        console.log('afsdfasdf');
        //Begin animation loop
        AnimateLoop();
    }
}


//Loop of animation.  Performs actions in animation array at specified intervals
function AnimateLoop(){
    
    //Without this block, edges/vertices may be black
    //on the fastest speed.  Comment this out to verify
    if(blinking){
        setTimeout(AnimateLoop, 1);
        return;
    }
    
    if (state === "stopped" || state === 'waiting') {
        //console.log("returning because stopped");
        setTimeout(AnimateLoop, 1);
        return;
    }
    
    if (movie_slider.thumb_active === true || scaler.scaler_active === true) {
        //console.log('returning because something is active');
        setTimeout(AnimateLoop, 1);
        return;
    }
    
    //Do next command
    //Special case for SetAllVertices Color
    if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
        var vertexArray = new Array();
        for(i = 3; i < animation[step].length; i++){
            vertexArray[i-3] = animation[step][i];
        }
        animation[step][1](animation[step][2],vertexArray);
    }else{
        animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
    }       
    step = step + 1;
    Refresh_MovieSlider(step);
    
    //Realign components
    the_evt_target_ownerDocument.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    the_evt_target_ownerDocument.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
    
    //Check if steps remain
    if(step < animation.length) { //If steps remain
        
        if(animation[step-1][1] == ShowActive && ( the_evt_target_ownerDocument.getElementById(code.line_llc.group.getAttribute("id") + "_bp" + animation[step-1][2].split("_")[1] + "_act") != null 
                || step_pressed) ){ //If the line was a show_active and the line is a breakpoint or the step button was pressed, wait
                
                state = "waiting";
                clearTimeout(timer);
                //If waiting because step pressed, then step animation
                if (step_pressed) {
                    step_pressed = false;
                    StepAnimation(step_evt);
                } else {
                    step_pressed = false;
                }
        }else{
            //Otherwise, execute the next command
            var duration = animation[step][0] * timeout;
            timer = setTimeout(AnimateLoop, duration);
        }
        
    }else{  //If no steps left, stop
        
                state = "stopped";
        action_panel.activateButton("start_button", "StartAnimation(evt)");
        action_panel.deactivateButton("continue_button");
        action_panel.deactivateButton("stop_button");
        action_panel.deactivateButton("step_button");
        step = 0;
        code.removeHighlight(current_line-1);
                current_line = 0;
    }
    
}


//Resumes execution of animation loop if paused by pressing step button
function ContinueAnimation(evt){
    if(evt.target.getAttribute("id") == "continue_button"){
        if(state == "waiting"){
            state = "running";
            continue_pressed = false;
            AnimateLoop();
        }else{
            continue_pressed = true;
            continue_evt = evt;
        }
    }
}


//Stops execution of animation loop and plays next animation on press of step button
function StepAnimation(evt){
        if(state == "running"){
            step_evt = evt;
        step_pressed = true;
        return;
    }

    
    if(evt.target.getAttribute("id") == "step_button" || evt.target.getAttribute("id") == "start_button"){ //see StartAnimation to see why start button is here                
                if(blinking){
                    if(state == "stepping"){
                        setTimeout(StepAnimation,1, evt);
                    }
                        return; //prevent buggy behavior
                }
        state = "stepping";

        
        if(animation[step][1] != ShowActive && step < animation.length){
            if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
                var vertexArray = new Array();
                for(i = 3; i < animation[step].length; i++){
                    vertexArray[i-3] = animation[step][i];
                }
                animation[step][1](animation[step][2],vertexArray);
            }else{
                animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
            }       
            step = step + 1;
            
            if(blinking){
                        setTimeout(StepAnimation,1, evt);
                return;
            }
            the_evt_target_ownerDocument.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
            the_evt_target_ownerDocument.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
            setTimeout(StepAnimation,1,evt);
            return;
        }
        
        
        if(step < animation.length){
            if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
                var vertexArray = new Array();
                for(i = 3; i < animation[step].length; i++){
                    vertexArray[i-3] = animation[step][i];
                }
                    animation[step][1](animation[step][2],vertexArray);
            }else{
                animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
            }
            step = step + 1;
            the_evt_target_ownerDocument.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
            the_evt_target_ownerDocument.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
            state = "waiting";
            if(continue_pressed){
                continue_pressed = false;
                ContinueAnimation(continue_evt);
            }
        }else{
                    state = "stopped";
                    action_panel.activateButton("start_button", "StartAnimation(evt)");
                    action_panel.deactivateButton("continue_button");
                    action_panel.deactivateButton("stop_button");
                    action_panel.deactivateButton("step_button");
                    step = 0;
                    code.removeHighlight(current_line-1);
                    current_line = 0;
                }
    }
}


//Stops animation and clears code highlights.  To resume animation, it must be restarted
function StopAnimation(evt){
    
    clearTimeout(timer);
    state = "stopped";
    action_panel.activateButton("start_button", "StartAnimation(evt)");
    action_panel.deactivateButton("continue_button");
    action_panel.deactivateButton("stop_button");
    action_panel.deactivateButton("step_button");
    step = 0;
    code.removeHighlight(current_line-1);
    current_line = 0;
    Refresh_MovieSlider(step);
    setGraphState(graph_states[0]);
    
    //StopAnimation only ever called from stop button, or at end of fillGraphStates
    /*if(evt.target.getAttribute("id") == "stop_button"){
        clearTimeout(timer);
        state = "stopped";
        action_panel.activateButton("start_button", "StartAnimation(evt)");
        action_panel.deactivateButton("continue_button");
        action_panel.deactivateButton("stop_button");
        action_panel.deactivateButton("step_button");
        step = 0;
        code.removeHighlight(current_line-1);
                current_line = 0;
    }*/
}


//Inserts a breakpoint by creating a grey highlight
function SetBreakpoint(evt){            
    var line = evt.target;
    
    if(line.nodeName == "tspan"){
        line = line.parentNode;
    }

    if(line.nodeName == "path"){
        var id = "";
        if(line.getAttribute("id").indexOf("_bp") != -1){
            var target_id = evt.target.getAttribute("id");
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_bp".length);
        }else if(line.getAttribute("id").indexOf("_hl") != -1){
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_hl".length);
            line.setAttribute("cursor", "default");
            line.setAttribute("onclick", "");
        }else return;
        console.log("new line id: " + id);
        line = the_evt_target_ownerDocument.getElementById(id);
    }

    //put breakpoint functionality on highligt if it is over highlighted text
    var hl_num = line.getAttribute("id").split("_")[1];
    var hl = the_evt_target_ownerDocument.getElementById("code_hl" + hl_num);
    if(hl != null){
        hl.setAttribute("cursor", "pointer");
        hl.setAttribute("onclick", "RemoveBreakpoint(evt)");
    }
    
    var htb_bbox = code.line_llc.group.getBBox();
    var line_bbox = line.getBBox();
    var line_translation = getTranslate(line.getAttribute("transform"));

    var dx = line.getAttribute("dx");
    var dy = line.getAttribute("dy");
    if(dx == null){
        dx = 0;
    }else{
            dx = parseFloat(dx);
    }
    if(dy == null){
            dy = 0;
    }else{
            dy = parseFloat(dy);
    }
    
    //var indicator = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    //indicator.setAttribute("x", line_bbox.x + line_translation[0] - code.line_llc.h_padding - dx);
    //indicator.setAttribute("y", line_bbox.y + line_translation[1] - code.line_llc.v_padding - dy);
    //indicator.setAttribute("width", htb_bbox.width + 2*code.line_llc.h_padding);
    //indicator.setAttribute("height", line_bbox.height + 2*code.line_llc.v_padding);
    /*var y_start = line_bbox.y + line_translation[1] - code.line_llc.v_padding - dy + line_bbox.height/4;
    var x_start = -6;
    var indicator = the_evt_target_ownerDocument.createElementNS(svgNS, "path");
    indicator.setAttribute("d", String("M" + x_start + " " + y_start + " L" + (x_start+8) + " " + y_start + " L" + (x_start+12) + " " + (y_start+4) + " L" + (x_start+8) + " " + (y_start+8) + " L" + x_start + " " + (y_start+8) + " L" + x_start + " " + y_start + " Z"));
    console.log(String("M" + x_start + " " + y_start + " L" + (x_start+10) + " " + y_start + " L" + x_start + " " + y_start + " Z"));
    //indicator.setAttribute("x", -8);
    //indicator.setAttribute("y", line_bbox.y + line_translation[1] - code.line_llc.v_padding - dy + 2);
    //indicator.setAttribute("width", 12);
   // indicator.setAttribute("height", line_bbox.height + 2*code.line_llc.v_padding - 4);
    indicator.setAttribute("stroke", "blue");
    indicator.setAttribute("fill", "blue");
    indicator.setAttribute("id", code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1]);
    indicator.setAttribute("transform", "translate(" + x_offset + " " + y_offset + ")");
    indicator.setAttribute("onclick", "RemoveBreakpoint(evt)");
    indicator.setAttribute("cursor", "pointer");*/
    //code.highlight_group.parentNode.insertBefore(indicator, code.highlight_group);
    //code.highlight_group.parentNode.appendChild(indicator);
    var indicator = the_evt_target.getElementById(code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1]);
    var new_id = indicator.getAttribute("id") + "_act";
    indicator.setAttribute("id", new_id);
    console.log("new_id: " + new_id);
    indicator.setAttribute("opacity", 1);
    indicator.setAttribute("onclick", "RemoveBreakpoint(evt)");
    line.setAttribute("onclick", "RemoveBreakpoint(evt)");
}


// Add transparent breakpoints to codebox to indicate the breakpoint capability
function AddBreakpoints(code) {
    var lines = code.line_llc.group.childNodes;
    for (l in lines) {
        var line = lines[l];
        //console.log(line);
        if(line.nodeName == "tspan"){
            line = line.parentNode;
        }
        if (line.nodeName != "text")
            continue;
        var line_bbox = line.getBBox();
        var line_translation = getTranslate(line.getAttribute("transform"));
        var dx = line.getAttribute("dx");
        var dy = line.getAttribute("dy");
        if(dx == null){
            dx = 0;
        }else{
                dx = parseFloat(dx);
        }
        if(dy == null){
                dy = 0;
        }else{
                dy = parseFloat(dy);
        }
        var y_start = line_bbox.y + line_translation[1] - code.line_llc.v_padding - dy + line_bbox.height/4;
        var x_start = -6;
        var indicator = the_evt_target_ownerDocument.createElementNS(svgNS, "path");
        indicator.setAttribute("d", String("M" + x_start + " " + y_start + " L" + (x_start+8) + " " + y_start + " L" + (x_start+12) + " " + (y_start+4) + " L" + (x_start+8) + " " + (y_start+8) + " L" + x_start + " " + (y_start+8) + " L" + x_start + " " + y_start + " Z"));
        indicator.setAttribute("stroke", "blue");
        indicator.setAttribute("fill", "blue");
        indicator.setAttribute("id", code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1]);
        indicator.setAttribute("transform", "translate(" + x_offset + " " + y_offset + ")");
        indicator.setAttribute("onclick", "SetBreakpoint(evt)");
        indicator.setAttribute("cursor", "pointer");
        indicator.setAttribute("opacity", .15);
        code.highlight_group.parentNode.appendChild(indicator);
    }
}


//Removes a highlight by removing a grey highlight
function RemoveBreakpoint(evt){
    var line = evt.target;
    console.log(line);
    if(line.nodeName == "path"){
        var id = "";
        if(line.getAttribute("id").indexOf("_bp") != -1){
            var target_id = evt.target.getAttribute("id");
            evt.target.setAttribute("onclick", "SetBreakpoint(evt)");
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_bp".length, target_id.length-4);
        }else if(line.getAttribute("id").indexOf("_hl") != -1){
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_hl".length);
            line.setAttribute("cursor", "default");
            console.log("blargasdgasd");
            line.setAttribute("onclick", "");
        }else return;
        console.log("searching id: " + id);
        line = the_evt_target_ownerDocument.getElementById(id);
    }
    
    if(line.nodeName == "tspan"){
        line = line.parentNode;
    }
    
    if(line.nodeName == "text"){
        var background = the_evt_target_ownerDocument.getElementById(code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1] + "_act");
        if(background != null){
            //background.parentNode.removeChild(background);
            background.setAttribute("opacity", .15);
            var new_id = background.getAttribute("id");
            new_id = new_id.substring(0, new_id.length-4);
            console.log("new_id: " + new_id);
            background.setAttribute("id", new_id);
            line.setAttribute("onclick", "SetBreakpoint(evt)");
        }   
    }
}


/**
*
*
*
* Graph animation functions
*
*
*/
//Sets color of vertex with id given by v to specified color
function SetVertexColor(v, color) {
    element = the_evt_target_ownerDocument.getElementById(v);
    element.setAttribute("fill", color);
}


//Colors edge with id given by e
function SetEdgeColor(e, color) {
    // NOTE: Gato signature SetEdgeColor(v, w, color)
    element = the_evt_target_ownerDocument.getElementById(e);
    if (element == null) {
        e = switch_edge_vertices(e);
        element = the_evt_target_ownerDocument.getElementById(e);
    }
    element.setAttribute("stroke", color);
    //added changes to color of arrowheads
    element = the_evt_target_ownerDocument.getElementById(e_arrow_id + e);
    if(element != null){
        element.setAttribute("fill", color);
    }
}


//Takes in an edge and switches the vertices to accomodate for directed graphs.
//Usual form of edge is g1_(1, 2) or g2_(2, 1) etc.
function switch_edge_vertices(e){
    var prefix = e.split('(')[0];
    var split = e.split(',');
    var losplit = split[0].split('(');
    var v1 = losplit[1].substring(0, losplit[1].length);
    //var v1 = split[0].split[0].length-1);
    var v2 = split[1].substring(1, split[1].length-1);
    var new_e = prefix + "(" + v2 + ", " + v1 + ")";
    return new_e;
}


//Sets color of all vertices of a given graph to a given color
//If vertices != null, then only color the set of vertices specified by vertices
function SetAllVerticesColor(graph_id_and_color, vertices) {

    var graph_id = graph_id_and_color.split("_")[0];
    var color = graph_id_and_color.split("_")[1];
    var children = the_evt_target_ownerDocument.getElementById(graph_id).childNodes;

    if(vertices != null){
        for(i = 0; i < children.length; i++){
        for(j = 0; j < vertices.length; j++){
            if(children.item(i).nodeName == "circle" && children.item(i).getAttribute("id") == graph_id + "_" + vertices[j]){
                children.item(i).setAttribute("fill", color);
                break;
            }
        }
    }
    }else{
        for(i = 0; i < children.length; i++){
        if(children.item(i).nodeName == "circle"){
            children.item(i).setAttribute("fill", color);
        }
    }
    }
    
}


// Sets all the edges of one of the graphs to color given.  sample param: "g1_#dd3333"
function SetAllEdgesColor(graphColor) {
    var graph = graphColor.substring(0, 2);
    graphColor = graphColor.substring(3);

    for (var i=0; i<edges.length; i++) {
        var id = edges[i].getAttribute("id");
        if (id.substring(0, 2) !== graph)
            continue;
        var element = the_evt_target_ownerDocument.getElementById(id);
        element.setAttribute("stroke", graphColor);
        element = the_evt_target_ownerDocument.getElementById(e_arrow_id + id);
        if (element != null) {
            element.setAttribute("fill", graphColor);
        }
    }
}


//Vertex blinks between black and current color
function BlinkVertex(v, color) {

    // Return if doing the initial filling of graph states
    if (filling_states)
        return;

    blinking = true;
    element = the_evt_target_ownerDocument.getElementById(v);
    blinkcolor = element.getAttribute("fill")
    blinkcount = 3;
    element.setAttribute("fill", "black");
    setTimeout(VertexBlinker, 3*timeout);
}

//Helper for BlinkVertex
function VertexBlinker() {
    if (blinkcount %% 2 == 1) {
       element.setAttribute("fill", "black"); 
    } else {
       element.setAttribute("fill", blinkcolor); 
    }
    blinkcount = blinkcount - 1;
    if (blinkcount >= 0)
       setTimeout(VertexBlinker, 3*timeout);
    else
        blinking = false;
}


//Edge blinks between black and current color
function BlinkEdge(e, color){

    // Return if doing the initial filling of graph states
    if (filling_states)
        return;

    blinking = true;
    e_element = the_evt_target_ownerDocument.getElementById(e);
    e_blinkcolor = e_element.getAttribute("stroke");
    e_blinkcount = 3;
    e_element.setAttribute("stroke", "black");
    var element2 = the_evt_target_ownerDocument.getElementById(e_arrow_id + e);
    if(element2 != null){
        element2.setAttribute("fill", "black");
    }
    setTimeout(EdgeBlinker, 3*timeout);
    
}

//Helper for BlinkEdge
function EdgeBlinker(){
    var element2;
    if (e_blinkcount %% 2 == 1) {
       e_element.setAttribute("stroke", "black");
       element2 = the_evt_target_ownerDocument.getElementById(e_arrow_id + e_element.getAttribute("id"));
       if(element2 != null){
           element2.setAttribute("fill", "black");
       }
    } else {
       e_element.setAttribute("stroke", e_blinkcolor);
       element2 = the_evt_target_ownerDocument.getElementById(e_arrow_id + e_element.getAttribute("id"));
       if(element2 != null){
           element2.setAttribute("fill", e_blinkcolor);
       }
    }
    e_blinkcount = e_blinkcount - 1;
    if (e_blinkcount >= 0)
       setTimeout(EdgeBlinker, 3*timeout);
    else
        blinking = false;
}


//Blink(self, list, color=None):
//Sets the frame width of a vertex
function SetVertexFrameWidth(v, val) {
    var element = the_evt_target_ownerDocument.getElementById(v);
    element.setAttribute("stroke-width", val);
    var graph = the_evt_target_ownerDocument.getElementById(v).parentNode;
    sizeGraphBBox(graph);
}


//Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(v, annotation, color) //removed 'self' parameter to because 'self' parameter was assigned value of v, v of annotation, and so on.
{
    element = the_evt_target_ownerDocument.getElementById(v);
    
    if(element != null){
        if(typeof color == "undefined")
        color = "black";        
        
    if(the_evt_target_ownerDocument.getElementById(v_ano_id + v) != null){
        ano = the_evt_target_ownerDocument.getElementById(v_ano_id + v);
        ano.parentNode.removeChild(ano);
    
    }
    
    var newano = the_evt_target_ownerDocument.createElementNS(svgNS,"text");
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
    newano.appendChild(the_evt_target_ownerDocument.createTextNode(annotation));
    element.parentNode.appendChild(newano);

    var graph = the_evt_target_ownerDocument.getElementById(v).parentNode;
    sizeGraphBBox(graph);
    }
}


//Line with specified id is highlighted.  Becomes current line of code.  Previous highlight is removed.
function ShowActive(line_id){
    for(i = 0; i < code.line_llc.group.childNodes.length; i++){
        if(code.line_llc.group.childNodes.item(i).getAttribute("id") == line_id){
            code.removeHighlight(current_line-1);
            code.highlightLine(i);
            current_line = i+1;
            if(the_evt_target_ownerDocument.getElementById("code_bp" + current_line) != null){
                var hl = the_evt_target_ownerDocument.getElementById("code_hl" + current_line);
                hl.setAttribute("cursor", "pointer");
                hl.setAttribute("onclick", "RemoveBreakpoint(evt)");
            }
            break;
        }
    }
}


//Directed or undirected added to graph.
function AddEdge(edge_id){
    var graph_id = edge_id.split("_")[0];
    var vertices = edge_id.split("_")[1].match(/[^,\(\)\s]+/g);
    var v = the_evt_target_ownerDocument.getElementById(graph_id + "_" + vertices[0]);
    var w = the_evt_target_ownerDocument.getElementById(graph_id + "_" + vertices[1]);
    
    var vx = v.getAttribute("cx");
    var wx = w.getAttribute("cx");
    var vy = v.getAttribute("cy");
    var wy = w.getAttribute("cy");
    
    if(v != null && w != null && the_evt_target_ownerDocument.getElementById(graph_id + "_(" + vertices[0] + ", " + vertices[1] + ")") == null){
        var parent_graph = the_evt_target_ownerDocument.getElementById(graph_id);
        var arrowhead = null;
        var edge = null;
        
        if(parent_graph.getAttribute("type") == "directed"){
            var reverse_edge = the_evt_target_ownerDocument.getElementById(graph_id + "_(" + vertices[1] + ", " + vertices[0] + ")");
            if(reverse_edge != null){  //reverse edge exists.  Make this edge an arc.
                //Another directed edge.  Great... Change existing edge to arc and add new arc
                //Be sure to alter polylines as well.   
                var l = Math.sqrt(Math.pow((parseFloat(vx)-parseFloat(wx)),2) + Math.pow((parseFloat(vy)-parseFloat(wy)),2));
                
                if(l < 0.001)
                    l = 0.001;
                
                var c = (l - default_vertex_radius)/l - 0.001;
                var tmpX = parseFloat(vx) + c * (parseFloat(wx) - parseFloat(vx));
                var tmpY = parseFloat(vy) + c * (parseFloat(wy) - parseFloat(vy));
                
                
                var orthogonal = Orthogonal((parseFloat(wx)-parseFloat(vx)),(parseFloat(wy)-parseFloat(vy)));
                
                var mX = orthogonal[0];
                var mY = orthogonal[1];
                c = 1.5*default_vertex_radius + l/25;
                mX = parseFloat(vx) + .5 * (parseFloat(wx) - parseFloat(vx)) + c * mX
                mY = parseFloat(vy) + .5 * (parseFloat(wy) - parseFloat(vy)) + c * mY
                
                
                
                arrowhead = createArrowhead(mX, mY, wx, wy, 4.0, "ea" + edge_id);
                
                
                l = Math.sqrt(Math.pow(wx-mX,2) + Math.pow(wy-mY,2));
               
                if (l < .001)
                    l = .001;
                

                c = (l-2*default_vertex_radius)/l + .01;
                tmpX = mX + c*(wx - mX);
                tmpY = mY + c*(wy - mY);
                
                
                edge = the_evt_target_ownerDocument.createElementNS(svgNS,"path");
                edge.setAttribute("id", edge_id);
                edge.setAttribute("stroke", "#EEEEEE");
                edge.setAttribute("stroke-width", 4.0);
                edge.setAttribute("fill", "none");
                edge.setAttribute("d", "M " + vx +"," + vy +" Q "+ mX +"," + mY + " " + tmpX + "," + tmpY);
        
                parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
                if(arrowhead != null)
                    parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
                    
                    
                if(reverse_edge.getAttribute("d") == null){
                    reverse_edge.parentNode.removeChild(the_evt_target_ownerDocument.getElementById("ea" + reverse_edge.getAttribute("id")));
                    reverse_edge.parentNode.removeChild(reverse_edge);
                    AddEdge(reverse_edge.getAttribute("id"));
                }
                the_evt_target_ownerDocument.getElementById(reverse_edge.getAttribute("id")).setAttribute("stroke", reverse_edge.getAttribute("stroke"));
                the_evt_target_ownerDocument.getElementById("ea" + reverse_edge.getAttribute("id")).setAttribute("fill", reverse_edge.getAttribute("stroke"));
            }else{  //No reverse edge.  Just make a straight line
                                edge = the_evt_target_ownerDocument.createElementNS(svgNS,"line");
                                edge.setAttribute("id", edge_id);
                                edge.setAttribute("stroke", "#EEEEEE");
                                edge.setAttribute("stroke-width", 4.0);
                edge.setAttribute("x1", vx);
                edge.setAttribute("y1", vy);

                var l = Math.sqrt(Math.pow((parseFloat(wx)-parseFloat(vx)),2) + Math.pow((parseFloat(wy)-parseFloat(vy)),2));
               
                if (l < .001)
                    l = .001;

                var c = (l-2*default_vertex_radius)/l + .01;
                var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
                var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
                                
                edge.setAttribute("x2", tmpX);
                edge.setAttribute("y2", tmpY);

                arrowhead = createArrowhead(vx, vy, wx, wy, 4.0, "ea" + edge_id);   
                
                parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
                if(arrowhead != null)
                    parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
            }
        }else{ //Undirected edge
                        edge = the_evt_target_ownerDocument.createElementNS(svgNS,"line");
                    edge.setAttribute("id", edge_id);
                    edge.setAttribute("stroke", "#EEEEEE");
                    edge.setAttribute("stroke-width", 4.0);
            edge.setAttribute("x1", vx);
            edge.setAttribute("y1", vy);
            edge.setAttribute("x2", wx);
            edge.setAttribute("y2", wy);
            
            parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
            if(arrowhead != null)
                parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
        }

        var graph = the_evt_target_ownerDocument.getElementById(edge_id).parentNode;
        sizeGraphBBox(graph);
    }
    fillEdgesArray();
}


//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id){
    var edge =  the_evt_target_ownerDocument.getElementById(edge_id);
    if(edge != null){
        edge.parentNode.removeChild(edge);
    }
    var arrowhead = the_evt_target_ownerDocument.getElementById("ea" + edge_id);
    
    if(arrowhead != null){
        arrowhead.parentNode.removeChild(arrowhead);
    }

    var graph_id = edge_id.split("_")[0];
    var vertices = edge_id.split("_")[1].match(/[^,\(\)\s]+/g);
    var reverse_edge = the_evt_target_ownerDocument.getElementById(graph_id + "_(" + vertices[1] + ", " + vertices[0] + ")");
    if(reverse_edge != null){
            DeleteEdge(reverse_edge.getAttribute("id"));
            AddEdge(reverse_edge.getAttribute("id"));
            var new_edge = the_evt_target_ownerDocument.getElementById(reverse_edge.getAttribute("id"));
            new_edge.setAttribute("stroke", reverse_edge.getAttribute("stroke"));
            new_edge.setAttribute("stroke-width", reverse_edge.getAttribute("stroke-width"));
            var arrowhead = the_evt_target_ownerDocument.getElementById("ea" + new_edge.getAttribute("id"));
            if(arrowhead != null){
                arrowhead.setAttribute("fill", new_edge.getAttribute("stroke"));
            }
    }

    var graph = the_evt_target_ownerDocument.getElementById(graph_id);
    sizeGraphBBox(graph);
    fillEdgesArray();
}


//Adds vertex of into specified graph and coordinates in graph.  Optional id argument may be given.
function AddVertex(graph_and_coordinates, id){

    var graph = the_evt_target_ownerDocument.getElementById(graph_and_coordinates.split("_")[0]);
    var next_vertex = 1;
    while(true){
        if(the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_" + next_vertex) == null){
            break;
        }
        next_vertex++;
    }

    
    var coords = graph_and_coordinates.split("(")[1].match(/[\d\.]+/g);
    
    var new_vertex = the_evt_target_ownerDocument.createElementNS(svgNS,"circle");
    new_vertex.setAttribute("cx", coords[0]);
    new_vertex.setAttribute("cy", coords[1]);
    new_vertex.setAttribute("r", default_vertex_radius);
    new_vertex.setAttribute("fill", "#000099");
    new_vertex.setAttribute("stroke", "black");
    new_vertex.setAttribute("stroke-width", 0.0);

    if(id != null){
        new_vertex.setAttribute("id", graph.getAttribute("id") + "_" + id);
        if(the_evt_target_ownerDocument.getElementById(new_vertex.getAttribute("id")) != null)
            return;
    }else{
        new_vertex.setAttribute("id", graph.getAttribute("id") + "_" + next_vertex);
    }

    graph.appendChild(new_vertex);
    

    var new_label = the_evt_target_ownerDocument.createElementNS(svgNS,"text");
    new_label.setAttribute("x", coords[0]);
    new_label.setAttribute("y", parseFloat(coords[1]) + .33*parseFloat(new_vertex.getAttribute("r")));
    new_label.setAttribute("text-anchor", "middle");
    new_label.setAttribute("fill", "white");
    new_label.setAttribute("font-family", "Helvetica");
    new_label.setAttribute("font-size", 14.0);
    new_label.setAttribute("font-style", "normal");
    new_label.setAttribute("font-weight", "bold");
    new_label.setAttribute("id", "vl" + new_vertex.getAttribute("id"));

    if(id != null){
        new_label.appendChild(the_evt_target_ownerDocument.createTextNode(id));
    }else{
        new_label.appendChild(the_evt_target_ownerDocument.createTextNode(next_vertex + ""));
    }
    graph.appendChild(new_label);


        //resnap graph to fit   

    for(k = 0; k < vert_layout[1].group.childNodes.length; k++){
        vert_layout[1].resnapComponent(k);
    
        if(vert_layout[1].group.childNodes.item(x).nodeName == "g"){
            var graph = vert_layout[1].group.childNodes.item(k);
            sizeGraphBBox(graph);
            var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
            var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
            var translation3 = getTranslate(graph.getAttribute("transform"));
            setTranslate(rect, translation1[0] + translation2[0] + translation3[0], translation1[1] + translation2[1] + translation3[1]);
        }
    }
}


//function SetEdgeAnnotation(self,tail,head,annotation,color="black"):
//def UpdateVertexLabel(self, v, blink=1, color=None):
/**
*
*
*
* iPad functions
*
*
*
*/
//iPad-specific slider event handling
function TouchDrag_SSlider(evt){
    evt.preventDefault();
    Drag_SSlider(evt);
}


function TouchStart_SSlider(evt){
    evt.preventDefault();
    Click_SSlider(evt);
}


function TouchDeactivate_SSlider(evt){
    evt.preventDefault();
    Deactivate_SSlider(evt);
}


//iPad-specific graph translations
function TouchDrag_Graph(evt){
    if(evt.touches == undefined || evt.touches.length != 1)
        return;

    evt.preventDefault();
    TranslateGraph(evt);
}


function TouchStart_Graph(evt){
    if(evt.touches == undefined || evt.touches.length != 1)
        return;
    evt.preventDefault();
    translate_buffer = [evt.touches[0].clientX, evt.touches[0].clientY];
}


function TouchDeactivate_Graph(evt){
    if(evt.touches == undefined || evt.touches.length != 1)
        return;
    evt.preventDefault();
    translate_buffer = [];
}


function TranslateGraph(evt){
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
    }
    
    var x = evt.clientX;
    if(x == undefined)
        x = evt.touches[0].clientX;
    var y = evt.clientX;
    if(y == undefined)
        y = evt.touches[0].clientY;
    
    var translation = getTranslate(graph.getAttribute("transform"));
    var bg_translation = getTranslate(graph_bg.getAttribute("transform"));
    setTranslate(graph, translation[0] + (x-translate_buffer[0]), translation[1] + (y - translate_buffer[1]));
    setTranslate(graph_bg, bg_translation[0] + (x-translate_buffer[0]), bg_translation[1] + (y - translate_buffer[1]));
    graph.setAttribute("transform_buffer", graph.getAttribute("transform"));
    graph_bg.setAttribute("transform_buffer", graph_bg.getAttribute("transform"));
    translate_buffer[0] = x;
    translate_buffer[1] = y;


    the_evt_target_ownerDocument.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    the_evt_target_ownerDocument.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
}


//iPad-specific functions for rotating and scaling graphs
function GestureStart_TransformGraph(evt){      
    if(evt.touches != undefined)
        return;
    evt.preventDefault();
    
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
    }
    
    
    if(graph.getAttribute("transform_buffer") == null){     
        graph.setAttribute("transform_buffer", graph.getAttribute("transform"));
        graph_bg.setAttribute("transform_buffer", graph_bg.getAttribute("transform"));
    }
    
}


function GestureChange_TransformGraph(evt){
    if(evt.touches != undefined)
        return;
    evt.preventDefault();
    
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
    }

    TransformGraph(graph, graph_bg, evt);
}


function GestureEnd_TransformGraph(evt){
    if(evt.touches != undefined)
        return;
        
    evt.preventDefault();
    
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
    }

    graph.setAttribute("transform_buffer", graph.getAttribute("transform"));
    graph_bg.setAttribute("transform_buffer", graph_bg.getAttribute("transform"));
}


function TransformGraph(graph, graph_bg, evt){
    var scale = evt.scale;
    
    var graph_scale = getScale(graph.getAttribute("transform_buffer"));
    var gbg_scale = getScale(graph_bg.getAttribute("transform_buffer"));
    var graph_scaling_factor = 1 - scale;
    var gbg_scaling_factor = 1 - scale;
    
    var gscf_width = graph_scaling_factor* graph.getBBox().width*graph_scale[0];
    var gscf_height = graph_scaling_factor* graph.getBBox().height*graph_scale[1];  
    var gbgscf_width = gbg_scaling_factor * graph_bg.getBBox().width*gbg_scale[0];
    var gbgscf_height = gbg_scaling_factor * graph_bg.getBBox().height*gbg_scale[1];
    
    setScale(graph, scale * graph_scale[0], scale * graph_scale[1]);
    setScale(graph_bg, scale * gbg_scale[0], scale * gbg_scale[1]);
    
    graph_translation = getTranslate(graph.getAttribute("transform_buffer"));
    gbg_translation = getTranslate(graph_bg.getAttribute("transform_buffer"));
    
    setTranslate(graph, graph_translation[0] + gscf_width/2, graph_translation[1] + gscf_height/2);
    setTranslate(graph_bg, gbg_translation[0] + gbgscf_width/2, gbg_translation[1] + gbgscf_height/2);
    
    the_evt_target_ownerDocument.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    the_evt_target_ownerDocument.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
}


/*
//
// SCALING FUNCTIONS
//
//
*/
function Scaler(points, width) {
    this.triang_scaler = the_evt_target.getElementById("triangle_scaler");

    // Property that controls whether the scaler will alter the graph or not
    this.scaler_active = false;    
    this.points = points;
    this.scaler_width = width;
    
    this.triang_scaler.setAttribute("points", points);
    this.triang_scaler.setAttribute("cursor", "move");
    this.triang_scaler.setAttribute("onmousedown", "click_scaler(evt)");
    this.triang_scaler.setAttribute("onmouseup", "deactivate_scaler(evt)");
    this.triang_scaler.setAttribute("onmousemove", "drag_scaler(evt)");
}


// Repositions the scaler to match the 
function repositionScaler(x, y) {
    var scaler_x = x + MAX_GBBOX_WIDTH - 10;
    var scaler_y = y + MAX_GBBOX_HEIGHT - 10;
    var points_val = String(scaler_x) + "," + String(scaler_y) + " " + String(scaler_x-20) + "," + String(scaler_y) + " " + String(scaler_x) + "," + String(scaler_y-20);
    scaler.triang_scaler.setAttribute("points", points_val);
}


// Click-handler for scaler.  Sets scaler_active to true to enable scaling with drags,
// and sets mouse_start to the current cursor position
function click_scaler(evt) {
    scaler.scaler_active = true;
    var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
    scale_graph_width = graph.getBBox().width * g_scale_factor.x;
    mouse_start = cursorPoint(evt, null);
}


// Global-mouseup handler that deactivates scaler_active
function deactivate_scaler(evt) {
    if (scaler.scaler_active === false)
        return;
    
    scaler.scaler_active = false;
}

 
// Global-mousemove handler that calls scaleGraph with the current evt if scaler_active is True
function drag_scaler(evt) {
    if (scaler.scaler_active === false)
        return;
        
    var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
    var graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
    scaleGraph( graph, graph_bg, evt, false);
}


// Moves the second graph down in y direction to make room for the top graph scaling
function slide_down_bottom() {
    var graph_one = the_evt_target.getElementById(init_graphs[0].getAttribute("id"));
    var new_height = init_height_g1 * g_scale_factor.y;
    var diff = new_height - init_height_g1;

    var graph_two = the_evt_target.getElementById(init_graphs[1].getAttribute("id"));
    var trans = getTranslate(graph_two.getAttribute("transform"));
    setTranslate(graph_two, trans[0], init_transy_g2.graph + diff);

    // Move down the bounding box as well
    var g2_bg = the_evt_target.getElementById("g2_bg");
    var trans = getTranslate(g2_bg.getAttribute("transform"));
    setTranslate(g2_bg, trans[0], init_transy_g2.bg + diff);
}

 
 // Scales the graph and background.  If use_curr_sf is true then it uses the current
 // g_scale_factor, otherwise it computes one based on scaler position
function scaleGraph(graph, graph_bg, evt, use_curr_sf) {
    
    if (use_curr_sf) {
        setScale(graph, g_scale_factor.x, g_scale_factor.y);
        setScale(graph_bg, g_scale_factor.x, g_scale_factor.y);
        return;
    }

    // Factor the graph_width is multiplied by to get the actual width
    var width_factor = 1;
    if (max_scale_factor < 1)
        width_factor = max_scale_factor;
    
    cursor_point = cursorPoint(evt);

    //console.log('Cursor_point: (' + cursor_point.x + ', ' + cursor_point.y + ')');
    //console.log('Mouse_start: (' + mouse_start.x + ', ' + mouse_start.y + ')');

    var graph_width = graph.getBBox().width * width_factor;
    var cursor_delta = cursor_point.x - mouse_start.x;
    if (cursor_delta === 0)
        return;

    var new_width = scale_graph_width + cursor_delta;
    var temp_scale_factor = new_width / graph_width;

    //console.log("temp_scale_factor: " + temp_scale_factor);
    
    //Scale factor used to compute size of graph
   // var temp_scale_factor = (graph_width + cursor_delta)/graph_width;

    // If temp_scale_factor is too small then do not do the scaling
    if (temp_scale_factor < MIN_SCALE_FACTOR)
        return;
    
    g_scale_factor.x = temp_scale_factor * width_factor;
    g_scale_factor.y = temp_scale_factor * width_factor;

    //Limit scaling to the maximum scale_factor
    if (g_scale_factor.x > max_scale_factor) {
        g_scale_factor.x = max_scale_factor;
        g_scale_factor.y = max_scale_factor;
    }

    if (two_graph === true) 
            slide_down_bottom();
    
    for (x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        var graph_bg = the_evt_target.getElementById(graph_bgs[x]);
        setScale(graph, g_scale_factor.x, g_scale_factor.y);
        setScale(graph_bg, g_scale_factor.x, g_scale_factor.y);
    }
}

//Translate client coordinates to svg coordinates.  If given element then translates to coordinates
//in that elements coordinate system
function cursorPoint(evt, element){
    pt.x = evt.clientX; 
    pt.y = evt.clientY;
    if (element === null || element === undefined)
        return pt.matrixTransform(the_evt_target.getScreenCTM().inverse());
    else
        return pt.matrixTransform(element.getScreenCTM().inverse());
}

//This pushes the graph background too far to the left for some reason
function realignScaler(scaler_x, scaler_y){
    var tri_scaler = the_evt_target.getElementById("triangle_scaler");
    tri_scaler.setAttribute("points", String(scaler_x) + "," + String(scaler_y) + " " + String(scaler_x-20) + "," + String(scaler_y) + " " + String(scaler_x) + "," + String(scaler_y-20));
}

/*
//
//
// "MOVIE" PLAYBACK
//
//
//
*/

function GraphState(graph, step) {
    // An array tuple of (state, elements_present_at_that_time)
    this.state = buildStateArray(graph);
    this.step = step;
}

//Builds a state array representation of the graph
//A state array is an array representing the state of the graph at any point during animation, and is of the form
// Array( Array( tag_type_1st_element, attr1, val1, attr2, val2, attr3...), Array( tag_type_2nd_element, attr1, val1, attr2, val2, ...), ...)
// attribute1 and value1 will always pertain to id and its value
function buildStateArray(graph) {

    var graph_elems = graph.childNodes;

    // The total state entity
    var state_holder = new Array(); 

    // The states of the elements that are present
    var states = new Array();

    // The elements that are present at that point in the animation(ie. haven't been deleted)
    var elems_present = new Array();
    
    var i;
    //Start at one to avoid first, empty element
    for ( i=0; i<graph_elems.length; i++) {
        var elem = graph_elems[i];
        
        //If the element doesn't have any attributes, continue.  For some reason elements are making it in here like [object Text] that have no significance(whitespace maybe?)
        if (elem.attributes === null)
            continue;
        var attributes = elem.attributes;
        
        var elem_array = new Array();
        elem_array.push(elem.tagName);
        var id = elem.getAttribute("id");
        
        // Add to elems_present if not seen already
        if (elems_present.indexOf("id") === -1)
            elems_present.push(id);

        elem_array.push(id);
        
        if(the_evt_target_ownerDocument.getElementById(v_ano_id + id) != null){
            ano = the_evt_target_ownerDocument.getElementById(v_ano_id + id);
            elem_array.push(ano.firstChild.nodeValue);
        } else {
            elem_array.push("");
        }
        
        //Loop over all attributes of the element
        for ( ind in attr_array) {
            attr = attr_array[ind];
            //If the attribute is defined and not id(already added), then add it to the array
            if (elem.getAttribute(attr) != null && attr != 'id') {
                elem_array.push(attr);
                elem_array.push(elem.getAttribute(attr));
            }
        }
        states.push(elem_array);
    }
    
    state_holder.push(states);
    state_holder.push(elems_present);
    //console.log(elems_present);
    //console.log(elems_present.length);

    return state_holder;
}


/* Model this off of AnimateLoop, except translate the graph off the screen before 
doing the animations.  Save the graph state every STEP_INTERVAL commands, and in between
there save the commands */
function fillGraphStates() {
    
    filling_states = true;

    var graphs = new Array();  
    for (g in init_graphs) 
        graphs.push(the_evt_target.getElementById(init_graphs[g].getAttribute("id")));

    // Keep track of added and deleted elements for restoration to initial state
    deleted_elements = new Array();
    added_elements = new Array();

    var numAnims = animation.length;
    for ( var step=0; step<numAnims; step++) {
        if ( step %% STEP_INTERVAL === 0) {
            if (two_graph)
                graph_states.push(new Array(new GraphState(graphs[0], step), new GraphState(graphs[1], step)));
            else
                graph_states.push(new Array(new GraphState(graphs[0], step)));
        }
        
        //Do the next command, special case for SetAllVerticesColor
        if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
            var vertexArray = new Array();
            for(i = 3; i < animation[step].length; i++){
                vertexArray[i-3] = animation[step][i];
            }
            animation[step][1](animation[step][2],vertexArray);
        }else{
            // If an edge is going to be deleted save it for later restoration
            var graph_num = 1;

            if (animation[step][1] == DeleteEdge) {
                var add_ind = added_elements.indexOf(animation[step][2]);
                
                if (add_ind !== -1)
                    delete added_elements(add_ind); 
                else
                    deleted_elements.push(animation[step][2]);
                
            } else if (animation[step][1] == AddEdge) {
                var del_ind = deleted_elements.indexOf(animation[step][2]);
                
                // If the added element is in deleted_elements then just remove from deleted_elements.  Otherwise, add to added_elements
                if (del_ind !== -1)
                    delete deleted_elements[del_ind]; 
                else
                    added_elements.push(animation[step][2]);
                
            }

            animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
        }       
        //Need to realign components here??
        
    }

    console.log(graph_states);

    console.log("Deleted elements:");
    console.log(deleted_elements);
    console.log("Added elements:");
    console.log(added_elements);
    
    //Restore graph back to original state
    console.log("Setting graph state back to 0");
    //reset_elements(deleted_elements, added_elements);
    setGraphState(graph_states[0]);
    StopAnimation(undefined);

    filling_states = false;
}


/* Sets the attributes of the graph to that of the given graph_state */
/* Sets the attributes of the graph to that of the given graph_state */
function setGraphState(graph_state) {
    
    if (graph_state === undefined)
        return;

    //console.log("In setgrpahstate");
   // console.log(graph_state);

    // Keep track of elements found on graph.  
    // The ones not found on graph that are in state_array must be added
    var elements_found = new Array();
    
    for (x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        //var child = graph.firstChild;
        var state_array = graph_state[x].state;

        if (x == 1) {
          //  console.log(graph);
          //  console.log(state_array[1]);
        }

        var temp = new Array(state_array[1].length);
        for (var i=0; i<state_array[1].length; i++)
            temp[i] = false;
        
        elements_found.push(temp);
        
        var children = graph.childNodes;
        var found = 0;
        for (var i=0; i<children.length; i++) {
            var child = children.item(i);
            if (child.attributes == null) {
                child = child.nextSibling;
                continue;
            }
            
            var child_id = child.getAttribute("id");

            //console.log("Looking at " + child_id);
            
            var ind = state_array[1].indexOf(child_id);
            
            if (ind == -1) {
                // The element on graph isn't in state array, get rid of it
                var elem_type = is_edge_or_vert(child_id);
                if (elem_type === 0)
                    DeleteEdge(child_id);
                else {
                    //alert("We got a non-edge id: " + child_id);
                    SetVertexAnnotation(1, "s", "black");
                }
            } else {
                // The element on graph is in state array
                found ++;
                elements_found[x][ind] = true;
            }
            
            child = child.nextSibling;
            ind++;
        }
       // console.log("Found " + found);
        /*while (child != null) {
            if (child.attributes == null) {
                child = child.nextSibling;
                continue;
            }
            
            var child_id = child.getAttribute("id");

            console.log("Looking at " + child_id);
            
            var ind = state_array[1].indexOf(child_id);
            
            if (ind == -1) {
                // The element on graph isn't in state array, get rid of it
                var elem_type = is_edge_or_vert(child_id);
                if (elem_type === 0)
                    DeleteEdge(child_id);
                else {
                    //alert("We got a non-edge id: " + child_id);
                    SetVertexAnnotation(1, "s", "black");
                }
            } else {
                // The element on graph is in state array
                elements_found[x][ind] = true;
            }
            
            child = child.nextSibling;
            ind++;
        }*/
       // console.log(elements_found[x]);
        console.log("x = " + x);
        
        // Go over the elements that haven't been found and add them to the graph
        for (var i=0; i<state_array[1].length; i++) {
            //console.log("Looking an edge to add");
            if (elements_found[x][i] == false) {
                // The element in state_array wasn't found-- add it in
                /*if (state_array[1][i] === "g2_(1, 3)")
                    console.log("Here it is...");
                */
               // console.log("We didn't find " + state_array[1][i] + " on the graph");
                var type = is_edge_or_vert(state_array[1][i]);
                if (type === 0) {
                  //  console.log("Adding edge: " + state_array[1][i]);
                    AddEdge(state_array[1][i]);
                    elements_found[x][ind] = true;
                } else {
                    //alert("We got a non-edge!! " + state_array[1][i]);
                }
            }
        }
    
    }
    

    //
    for (g in graph_state) {
        var state_array = graph_state[g].state;

        //Set attributes of elements one at a time
        for ( var i=0; i<state_array[0].length; i++) {
            id = state_array[0][i][1];
            var elem = the_evt_target.getElementById(id);
            if (elem === null) {
                //console.log("Elem is null with id: " + id);
                continue;
            }
            
            //Check for vertex annotation
            if (state_array[0][i][2] != "") {
                SetVertexAnnotation(id, state_array[0][i][2], undefined);
            } else if (the_evt_target.getElementById(v_ano_id + id) != null)  {
                var ano = the_evt_target.getElementById(v_ano_id + id);
                ano.parentNode.removeChild(ano);
            }
            
            for ( var j=3; j<state_array[0][i].length; j+=2) {
                elem.setAttribute(state_array[0][i][j], state_array[0][i][j+1]);
            }
        }
    }

    for (x in init_graphs) {
        var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
        var graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
        scaleGraph(graph, graph_bg, undefined, true);   
    }
}


function fillAttributeArray() {
    attr_array = new Array("tagName", "id", "x1", "y1", "x2", "y2", "stroke", 
                        "stroke-width", "fill", "x", "y", "cx", "cy", "r",
                        "text-anchor", "font-family", "font-size", "font-style",
                        "font-weight", "nodeValue", "points", "style", "blank", "dx");
}


function jumpToStep(n) {
    //graph state to which animations will be applied
    var base_state;     
    step = n;

    console.log("Jumping to step " + n);
    
    //Find the graph_state to build off of
    for ( i in graph_states) {
        if (graph_states[i][0].step > n) {
            base_state = graph_states[i-1];
            break;
        }
    }
    if (base_state === undefined)
        base_state = graph_states[graph_states.length-1];
    
    setGraphState(base_state);
        
    //Apply steps base_state.step -> n
    for ( var i=base_state[0].step; i<n; i++) {
    
        //Do the next command, special case for SetAllVerticesColor
        if(animation[i][1] == SetAllVerticesColor && animation[i].length > 3){
            var vertexArray = new Array();
            
            for(i = 3; i < animation[i].length; i++)
                vertexArray[i-3] = animation[i][i];
            
                animation[i][1](animation[i][2],vertexArray);
        }else{
            animation[i][1](animation[i][2],animation[i][3],animation[i][4]);
        }    
         
    }// end for
}



/*
//
//Movie Slider
//
*/
// Creates a simple slider that controls the position of the animation in the full "movie"
function MovieSlider(id, slider_width, thumb_height, offset, end_step, labels, title, actions) {

    this.slider = null;
    this.slider_bar = null;
    this.slider_thumb = null;
    this.low_bound = 0;
    this.up_bound = end_step;
    this.thumb_active = false;
    this.current_setting = 0;
    this.offset = offset;
    
    this.thumb_width = 10;
    var font_size = 10;
    
    this.slider = the_evt_target_ownerDocument.createElementNS(svgNS, 'g');
    this.slider.setAttribute("id", id);
    
    this.slider_bar = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    this.slider_bar.setAttribute("width", slider_width);
    this.slider_bar.setAttribute("height", this.thumb_width);
    this.slider_bar.setAttribute("x", this.thumb_width/2);
    this.slider_bar.setAttribute("y",(thumb_height-this.thumb_width)/2);
    this.slider_bar.setAttribute("rx", this.thumb_width/2);
    this.slider_bar.setAttribute("ry", this.thumb_width/2);
    this.slider_bar.setAttribute("stroke", "black");
    this.slider_bar.setAttribute("fill", "url(#slider_bar_lg)");
    this.slider_bar.setAttribute("stroke-width", 1);
    this.slider_bar.setAttribute("cursor", "pointer");
    this.slider_bar.setAttribute("id", id + "_slider_bar");
    this.slider.appendChild(this.slider_bar);
    
    this.slider_thumb = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    this.slider_thumb.setAttribute("width", this.thumb_width);
    this.slider_thumb.setAttribute("height", thumb_height);
    this.slider_thumb.setAttribute("rx", this.thumb_width/2);
    this.slider_thumb.setAttribute("ry", this.thumb_width/2);
    this.slider_thumb.setAttribute("x", 0);
    this.slider_thumb.setAttribute("stroke", "black");
    this.slider_thumb.setAttribute("fill", "url(#slider_thumb_lg)");
    this.slider_thumb.setAttribute("stroke-width", 1);
    this.slider_thumb.setAttribute("cursor", "pointer");
    this.slider_thumb.setAttribute("id", id + "_slider_thumb");
    this.slider.appendChild(this.slider_thumb);
    
    //create labels below slider
    for(i in labels){
        var text = the_evt_target_ownerDocument.createElementNS(svgNS, "text");
        text.setAttribute("x", this.thumb_width/2 + i*(slider_width/(labels.length-1)));
        text.setAttribute("y", thumb_height+ font_size);
        text.setAttribute("text-anchor","middle");
        text.setAttribute("font-size", font_size);
        text.setAttribute("font-family","Helvetica");
        text.setAttribute("font-style","normal");
        text.appendChild(the_evt_target_ownerDocument.createTextNode(labels[i]));
        this.slider.appendChild(text);
    }
    
    //create slider title
    var header = the_evt_target_ownerDocument.createElementNS(svgNS, "text");
    header.setAttribute("x", (this.thumb_width + slider_width)/2);
    header.setAttribute("y", 0);
    header.setAttribute("text-anchor","middle");
    header.setAttribute("font-size", font_size);
    header.setAttribute("font-family","Helvetica");
    header.setAttribute("font-style","normal");
    header.appendChild(the_evt_target_ownerDocument.createTextNode(title));
    this.slider.appendChild(header);
        
    for(i in actions){
        this.slider.setAttribute(actions[i][0], actions[i][1]);
    }
    
    the_evt_target_ownerDocument.documentElement.appendChild(this.slider);
}


// Click-handler for movie_slider, sets thumb_active if there's a drag, or calls Move_MovieSlider if there is only a click
function Click_MovieSlider(evt) {
    if (evt.target.getAttribute("id") === "movie_slider_slider_thumb")
        movie_slider.thumb_active = true;
    else if (evt.target.getAttribute("id") === "movie_slider_slider_bar") 
        Move_MovieSlider(evt);
}


// Called on mouse-up, deactivates movie_slider from any use
function Deactivate_MovieSlider(evt){
    movie_slider.thumb_active = false;
}


// Click-handler for the movie_slider.
// Changes the position and step setting of the movie_slider when the mouse is clicked on a given position
function Move_MovieSlider(evt) {
    var bbox = movie_slider.slider_bar.getBBox();
    var x_pos = cursorPoint(evt, movie_slider.slider_thumb).x;

    if (evt.clientX == undefined)
        x_pos = evt.touches[0].clientX;


    movie_slider.slider_thumb.setAttribute("x", x_pos - movie_slider.thumb_width/2);

    //movie_slider.slider_thumb.setAttribute("x", x_pos - (movie_slider.thumb_width/2) - getTranslate(movie_slider.slider.getAttribute("transform"))[0] - getTranslate(horiz_layout[1].group.getAttribute("transform"))[0]);
    movie_slider.current_setting = movie_slider.low_bound + (movie_slider.up_bound - movie_slider.low_bound)*(movie_slider.slider_thumb.getAttribute("x")/movie_slider.slider_bar.getAttribute("width"));
    movie_slider.current_setting = Math.floor(movie_slider.current_setting);
    jumpToStep(movie_slider.current_setting);
}


// Drag-handler for movie_slider
// Changes the position of the movie_slider bar and the current step when the bar is dragged
function Drag_MovieSlider(evt) {
    if (movie_slider.thumb_active) {
        var x_pos = cursorPoint(evt, movie_slider.slider_bar).x;
        
        if (x_pos === undefined) 
            x_pos = evt.touches[0].clientX;

        if (x_pos >= movie_slider.slider_bar.getBBox().x && x_pos < (movie_slider.slider_bar.getBBox().width + movie_slider.thumb_width/2)){
            movie_slider.slider_thumb.setAttribute("x", x_pos - movie_slider.thumb_width/2);
            movie_slider.current_setting = movie_slider.low_bound + (movie_slider.up_bound - movie_slider.low_bound)*(movie_slider.slider_thumb.getAttribute("x")/movie_slider.slider_bar.getAttribute("width"));
        } else if (x_pos >= (movie_slider.slider_bar.getBBox().width + movie_slider.thumb_width/2)) {
            console.log("At els if");
            //If slider bar is all the way to right set to up_bound-1
           movie_slider.current_setting = movie_slider.up_bound-1;
        } else {
            //If slider bar is all the way to left set to 0
            movie_slider.current_setting = 0;
        }
    
        movie_slider.current_setting = Math.floor(movie_slider.current_setting);
        jumpToStep(movie_slider.current_setting);
    }
}


// Changes the position of the movie slider handle to reflect the given step_num
function Refresh_MovieSlider(step_num) {
    movie_slider.current_setting = step_num;
    var thumb_pos = (movie_slider.current_setting/movie_slider.up_bound) * movie_slider.slider_bar.getAttribute("width");
    movie_slider.slider_thumb.setAttribute('x', thumb_pos);
}


// Adds a bounding box to the action controls at the bottom of the screen
function addControlBoundingBox(color) {
    var llc_box = horiz_layout[1].group.getBBox();
    
    var rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
    
    rect.setAttribute("id", "controlBBox");
    rect.setAttribute("width", llc_box.width + 20);
    rect.setAttribute("height", llc_box.height + 10);
    rect.setAttribute("x", llc_box.x - 10);
    rect.setAttribute("y", llc_box.y - 5);
    rect.setAttribute("rx", "4");
    rect.setAttribute("ry", "4");
    rect.setAttribute("fill", "url(#control_box_lg)");
    rect.setAttribute("stroke", color);
    rect.setAttribute("stroke-width", "3px");
    
    horiz_layout[1].group.insertBefore(rect, action_panel.llc.group);
}


// Position the action_panel and movie_slider controls at the bottom-center of the screen
function positionControls() {
    var bbox = horiz_layout[1].group.getBBox();
    var panel_width = screen_ctm.a * bbox.width;
    
    //TODO: Check if the value subtracted(75) is stable, or needs to be computed
    //setTranslate(horiz_layout[1].group, ((browser_width - panel_width)/4)/screen_ctm.a, (browser_height - 40)/screen_ctm.d - screen_ctm.f/screen_ctm.d - y_offset);
    //console.log('theoretical end of browser: ' + browser_height/screen_ctm.d 
    //trans = horiz_layout[1].group.getBBox().y + horiz_layout[1].group.getBBox().height + getTranslate(vert_layout.group.getAttribute("transform"))[1] + getTranslate(horiz_layout[1].group.getAttribute("transform"))[1];   
    trans = viewbox_y - horiz_layout[1].group.getBBox().height*2;
    setTranslate(horiz_layout[1].group, 0, trans); 
    
}


// Retrieve the viewbox value set in the svg document
function getViewboxVals() {
    viewbox_str = the_evt_target.getAttribute("viewBox").split(" ");
    viewbox_x = viewbox_str[2];
    viewbox_y = viewbox_str[3];
}


// Sets the maximum scale factor the graph can apply before going off the screen
// Sets the maximum scale factor the graph can apply before going off the screen
function set_max_scale_factor() {
    
    function max_factor_y(graph) {
        // Graph Dimensions
        var height = graph.getBBox().height;
        var graph_y = graph.getBBox().y;

        // Translation of right_vert_layout, the vert_layout, and the graph itself
        var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
        var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
        var translation3 = getTranslate(graph.getAttribute("transform"));
        var translate = translation1[1] + translation2[1] + translation3[1];

        var bottom_height = horiz_layout[1].group.getBBox().height + 30;    // Height of the bottom action bar
        if (two_graph)
            bottom_height += 10;

        var total_sans_height = y_offset + graph_y + translate + bottom_height;

        // Find how much larger the graph could be before the total becomes greater than the viewbox_y
        var max_height = viewbox_y - total_sans_height;
        var max_factor_y = max_height / height;
        return max_factor_y;
    }

    function max_factor_x(graph) {
        // Graph Dimensions
        var width = graph.getBBox().width;
        var graph_x = graph.getBBox().x;

        // Translation of right_vert_layout, the vert_layout, and the graph itself
        var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
        var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
        var translation3 = getTranslate(graph.getAttribute("transform"));
        var translate = translation1[0] + translation2[0] + translation3[0];

        var total_sans_width = x_offset + graph_x + translate;

        // Find how much larger the graph could be before the total becomes greater than the viewbox_x
        var max_width = viewbox_x - total_sans_width;
        var max_factor_x = max_width / width;
        return max_factor_x;
    }

    var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
    max_scale_factor = Math.min(max_factor_y(graph), max_factor_x(graph));
}


// Scales the graph to fit the screen.  
// Only really matters in cases where the graph is too large for the screen initially
function scale_to_fit() {
    var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
    var graph_bg = the_evt_target_ownerDocument.getElementById(graph.getAttribute("id") + "_bg");
    if (max_scale_factor < 1) {
        g_scale_factor.x = max_scale_factor;
        scaleGraph(graph, graph_bg, undefined, true);
    }
}

function fill_initArrays() {
    init_edges = new Array();
    init_verts = new Array();

    // Put in as many arrays as there are graphs
    for (g in init_graphs) {
        init_edges.push(new Array());
        init_verts.push(new Array());
    }

    for (g in init_graphs) {
        var child = the_evt_target.getElementById(init_graphs[g].getAttribute("id")).firstChild;

        while (child != null) {
            // Skip over textnodes and other such nonsense
            if (child.attributes === null) {
                child = child.nextSibling;
                continue;
            }

            var id = child.getAttribute("id");
            
            var type = is_edge_or_vert(id);
            
            if (type === 0) {
                // It's an edge
                init_edges[g].push(id);
            } else if (type === 1) {
                // It's an edge
                init_verts[g].push(id);
            }

            child = child.nextSibling;
        }
    }
}

// Returns -1 if neither, 0 for edge, 1 for vertex
function is_edge_or_vert(id) {
    var prefixes = new Array("g1", "g2");
    if (prefixes.indexOf(id.substring(0,2)) != -1) {
        if (id.charAt(3) === '(') {
            // It's an edge    
            return 0;
        } else {
            // It's a vertex
            return 1;
        }
    }
    return -1;
}

/**
*
*
*
* Main program
*
*
*/
function Initialize(evt) {
    the_evt = evt;
    the_evt_target = evt.target;
    the_evt_target_ownerDocument = evt.target.ownerDocument;

    // Object Prototype initialization
    HTB_prototypeInit();
    LLC_prototypeInit();
    BP_prototypeInit();
    SS_prototypeInit();
    Option_prototypeInit();

    fillAttributeArray();   // Fills the array of attributes that svg elements may contain
    getViewboxVals();       // Set the viewbox_x and viewbox_y global vars
    
    pt = the_evt_target.createSVGPoint();       //Create a point for translating svg coords to mouse coords
    

    // Set global event handlers
    the_evt_target.addEventListener("mousemove", drag_scaler, false);
    the_evt_target.addEventListener("mouseup", deactivate_scaler, false);
    the_evt_target.addEventListener("mouseup", Deactivate_MovieSlider, false);
    the_evt_target.addEventListener("mousemove", Drag_MovieSlider, false);
    
    //Create code layout
    code = new HighlightableTextBlock(20, 0, "code", 14, "vertical");

    // Insert lines of code into the HighlightableTextBlock
    var linenum = 1;
    while(the_evt_target_ownerDocument.getElementById("l_" + linenum) != null){
        code.insertLine("l_" + linenum, linenum-1);
        linenum++;
    }

    // Add transparent breakpoints
    AddBreakpoints(code);

    code.addBoundingBox("#8888AA");
    
    speed_select = new SpeedSelector("speedSelect", 20, "blue", "red");

    //Make code lines interactive
    var code_lines = code.line_llc.group.childNodes;
    for(i = 0; i < code_lines.length; i++){
            if(code_lines.item(i).nodeName == "text"){
                code_lines.item(i).setAttribute("cursor", "pointer");
                code_lines.item(i).setAttribute("onclick", "SetBreakpoint(evt)");
            }
    }

    fillEdgesArray();

    //Clone initial graphs and keep references to them
    init_graphs = new Array();
    var i = 1;
    var tree = the_evt_target_ownerDocument.getElementById("g" + i);
    while(tree != null){
        if (i === 2)
            two_graph = true;

        init_graphs[i-1] = tree.cloneNode(true);
        i++;
        tree = the_evt_target_ownerDocument.getElementById("g" + i);
    }
        
    //Create buttons
    action_panel = new ButtonPanel(15, 2, "actions", "horizontal");
    action_panel.createButton("start_button", "M0,0 0,40 30,20 Z", "blue", 0, "StartAnimation(evt)");
    action_panel.createButton("step_button", "M0,0 0,40 30,20 Z M30,0 30,40 40,40 40,0 Z", "blue", 1, "StepAnimation(evt)");
    action_panel.createButton("continue_button", "M0,0 0,40 10,40 10,0 Z M20,0 20,40 50,20 Z", "blue", 2, "ContinueAnimation(evt)");
    action_panel.createButton("stop_button", "M0,0 0,40 40,40 40,0 Z", "blue", 3, "StopAnimation(evt)");
    action_panel.deactivateButton("continue_button");
    action_panel.deactivateButton("stop_button");
    action_panel.deactivateButton("step_button");
    
    var graph = the_evt_target_ownerDocument.getElementById("g1");
    movie_slider = new MovieSlider('movie_slider', 1300-x_offset-getTranslate(action_panel.llc.group.getAttribute("transform"))[0]-action_panel.llc.group.getBBox().width, 30, x_offset, animation.length, ["Start", "End"], "Scene", [['onmousedown', 'Click_MovieSlider(evt)']]);

    timeout = 200;

    //Lay out code, speed slider, and graphs 
    vert_layout = new LinearLayoutComponent(20, 30, "vert_layout", "vertical");
    horiz_layout = new Array(new LinearLayoutComponent(20, 10, "horiz_layout_0", "horizontal"), new LinearLayoutComponent(20, 10, "horiz_layout_1", "horizontal"));
    
    left_vert_layout = new LinearLayoutComponent(20, 10, "vert_layout_left", "vertical");
    left_vert_layout.insertComponent(code.line_llc.group.getAttribute("id"), 0);
    right_vert_layout = new LinearLayoutComponent(20, 10, "right_vert_layout", "vertical");
    horiz_layout[1].insertComponent(action_panel.llc.group.getAttribute("id"), 0);
    horiz_layout[1].insertComponent('movie_slider', 1);
    horiz_layout[0].insertComponent(left_vert_layout.group.getAttribute("id"), 0);
    
    
    speed_select.addBoundingBox("#8888AA");

    for(x in init_graphs){
            right_vert_layout.insertComponent(init_graphs[x].getAttribute("id"), x);
    }
    
    horiz_layout[0].insertComponent(right_vert_layout.group.getAttribute("id"), 1);
    vert_layout.insertComponent(horiz_layout[0].group.getAttribute("id"), 0);
    vert_layout.insertComponent(horiz_layout[1].group.getAttribute("id"), 1);
    
    //offset to make everything visible
    vert_layout.group.setAttribute("transform", "translate(" + x_offset + " " + y_offset + ")");
    code.highlight_group.setAttribute("transform","translate(" + x_offset + " " + y_offset + ")");

    var scaler_y, scaler_x;

    graph_bgs = new Array();
    //Make rectangles behind graphs, for intuitive iPad usage
    for(x in init_graphs){
        var rect = the_evt_target_ownerDocument.createElementNS(svgNS, "rect");
        var graph = the_evt_target_ownerDocument.getElementById(init_graphs[x].getAttribute("id"));
        var bg_id = graph.getAttribute("id") + "_bg";

        graph_bgs.push(bg_id);
        init_height_g1 = graph.getBBox().height;

        rect.setAttribute("id", bg_id);
        rect.setAttribute("width",graph.getBBox().width+10);
        rect.setAttribute("height",graph.getBBox().height+10);
        rect.setAttribute("fill", "white");
        rect.setAttribute("fill-opacity", 1);
        rect.setAttribute("stroke-width",1);
        rect.setAttribute("stroke",  "#bcbcbc");
        rect.setAttribute("stroke-dasharray", "5 2");
        rect.setAttribute("x", graph.getBBox().x-10);
        rect.setAttribute("y", graph.getBBox().y-10);
        rect.setAttribute("ongesturestart", "GestureStart_TransformGraph(evt)");
        rect.setAttribute("ongesturechange","GestureChange_TransformGraph(evt)");
        rect.setAttribute("ongestureend","GestureEnd_TransformGraph(evt)");
        rect.setAttribute("ontouchstart", "TouchStart_Graph(evt)");
        rect.setAttribute("ontouchmove", "TouchDrag_Graph(evt)");
        rect.setAttribute("ontouchend", "TouchDeactivate_Graph(evt)");

        var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
        var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
        var translation3 = getTranslate(graph.getAttribute("transform"));
        setTranslate(rect, translation1[0] + translation2[0] + translation3[0], translation1[1] + translation2[1] + translation3[1]);
        the_evt_target_ownerDocument.documentElement.insertBefore(rect, the_evt_target_ownerDocument.documentElement.childNodes.item(0));
        scaler_x = graph.getBBox().x + graph.getBBox().width + 10;
        scaler_y = graph.getBBox().y + graph.getBBox().height + 10;

        if (x == 1) 
            init_transy_g2 = {"graph":getTranslate(graph.getAttribute("transform"))[1], "bg":(translation1[1] + translation2[1] + translation3[1])};
    } 
    
    set_max_scale_factor();
    scale_to_fit();

    var points_val = String(scaler_x) + "," + String(scaler_y) + " " + String(scaler_x-20) + "," + String(scaler_y) + " " + String(scaler_x) + "," + String(scaler_y-20);
    scaler = new Scaler(points_val, 20);

    fill_initArrays();

    fillGraphStates();

    the_evt_target_ownerDocument.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    the_evt_target_ownerDocument.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
    
    browser_width = window.innerWidth;
    browser_height = window.innerHeight;
    
    //Position action controls at bottom-center of the screen
    screen_ctm = the_evt_target.getScreenCTM();
    positionControls();
    
    //Create the option dropdown that will be positioned at top right of screen
    option_dropdown = new OptionDropdown('option_dropdown', 20, 35);
   
    //Add bounding box to action controls
    addControlBoundingBox("#8888aa");
    
    console.log("innerwidth: " + window.innerWidth);
    console.log("outerWidth: " + window.outerWidth);
    
}



var animation = Array(%(animation)s
);

]]></script>
"""

head = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm">
<defs>  
    <linearGradient id="slider_bar_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="skyblue" >
        </stop>
        <stop offset="1" stop-color="black">
        </stop>
    </linearGradient>
    
    <linearGradient id="slider_thumb_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#C0C0C0">
        </stop>
        <stop offset="1" stop-color="black">
        </stop>
    </linearGradient>
</defs>
"""

footer = """
</svg>
"""

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
SVG_Animation = None
prev = ["",-1]
indent_stack = [0]

def tokenEater(type, token, (srow, scol), (erow, ecol), line):
    global line_count
    global prev
    global begun_line
    global num_spaces
    global SVG_Animation
    global indent_stack

    #print("'%s'" % token + " of " + str((srow,scol)) + " , " + str((erow, ecol)) + " - type: " + str(type) + "line: " + str(line) + "len=" + str(len(token)))
    #print(prev)
    #print(indent_stack[len(indent_stack)-1])
    if (type == 0): #EOF.  Reset globals
        line_count = 1
        num_spaces = 0.0
        indent_stack = [0]
        begun_line = False
        SVG_Animation = None
        prev = ["",-1]
    elif (type == 1): #Word.  Potential keyword.  Must check keywordsList
        if begun_line == False:
            begun_line = True
            SVG_Animation.write('<text blank = "false" id="%s" x="10" y="10" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if token in keywordsList:
            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                SVG_Animation.write('<tspan font-weight="bold" dx="%d">%s</tspan>' % (7*indent_stack[len(indent_stack)-1], token))
            elif (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
                SVG_Animation.write('<tspan font-weight="bold">%s</tspan>' % token)
            else:
                SVG_Animation.write('<tspan font-weight="bold" dx="7">%s</tspan>' % token)
        else:
            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                SVG_Animation.write('<tspan dx = "%d">%s</tspan>' % (7*indent_stack[len(indent_stack)-1], token))
            elif (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
                SVG_Animation.write('<tspan>%s</tspan>' % token)
            else:
                SVG_Animation.write('<tspan dx="7">%s</tspan>' % token)
    elif (type == 4): #Newline on nonempty line
        SVG_Animation.write('</text>\n')
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
            SVG_Animation.write('<text blank = "false" id="%s" x="10" y="10" dx="%d" text-anchor="start" '\
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
                SVG_Animation.write('<tspan dx="%d">%s</tspan>' % (7*indent_stack[len(indent_stack)-1], token))
            else:
                SVG_Animation.write('<tspan dx="7">%s</tspan>' % token)
        else:
            if (prev[1] == -1 or prev[1] == 5 or prev[1] == 4 or prev[1] == 54 or prev[1] == 6): #first word
                SVG_Animation.write('<tspan dx="%d">%s</tspan>' % (7*indent_stack[len(indent_stack)-1], token))
            elif prev[0] in operatorsList:
                SVG_Animation.write('<tspan dx="7">%s</tspan>' % token)
            else:
                SVG_Animation.write('<tspan>%s</tspan>' % token)
    elif (type == 53): #Comment
        if begun_line == False:
            begun_line = True
            SVG_Animation.write('<text blank = "false" id="%s" x="10" y="10" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
            SVG_Animation.write('<tspan>%s</tspan>' % token)
        else:
            SVG_Animation.write('<tspan dx="7">%s</tspan>' % token)
    elif (type == 54): #Empty line with newline
        SVG_Animation.write('<text blank = "true" id="%s" x="10" y="10" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal"></text>\n' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))
        line_begun = False
        line_count += 1
    else:
        if begun_line == False:
            begun_line = True
            SVG_Animation.write('<text blank = "false" id="%s" x="10" y="10" dx="%d" text-anchor="start" '\
                       'fill="black" font-family="Courier New" font-size="14.0" font-style="normal">' % ("l_" + str(line_count), 7*indent_stack[len(indent_stack)-1]))

        if (prev[0] in specialList and (prev[0] != "]" and prev[0] != ")")):
            SVG_Animation.write('<tspan>%s</tspan>' % token)
        else:
            SVG_Animation.write('<tspan dx="7">%s</tspan>' % token)
                
    
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
    return ["Array(" + ", ".join(cmd) + ")" for cmd in mergedCmds]

def boundingBox(graphDisplay, resultForEmptyCanvas=None):
    """ If there are no elements on the canvas, a bounding box
        cannot be computed and bb is indeed None. In that case
        we use resultForEmptyCanvas.
    """
    bb = graphDisplay.canvas.bbox("all") # Bounding box of all elements on canvas
    if bb:
        # Give 10 pixels room to breathe
        x = max(bb[0] - 10,0)
        y = max(bb[1] - 10,0)
        width=bb[2] - bb[0] + 10
        height=bb[3] - bb[1] + 10
        return {'x':x,'y':y,'width':width,'height':height}
    else:
        return resultForEmptyCanvas

def WriteGraphAsSVG(graphDisplay, file, idPrefix=''):
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

    min_y = 9999
    
    for v,w in graphDisplay.G.Edges():
        vx, vy, r = graphDisplay.VertexPositionAndRadius(v)
        if vy < min_y:
            min_y = vy
			
	# Subtract y_normalizer from all y-values to move closer to the top of the screen.  Give 18px padding
    y_normalizer = min_y - 18
    #y_normalizer = 0
    
    # Write Edges
    for v,w in graphDisplay.G.Edges():
        vx,vy,r = graphDisplay.VertexPositionAndRadius(v)
        wx,wy,r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)
        
        vy = vy - y_normalizer
        wy = wy - y_normalizer
        
        if graphDisplay.G.directed == 0:
            file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                       ' stroke-width="%s"/>\n' % (idPrefix+str((v,w)),vx,vy,wx,wy,col,width))
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
                                                              graphDisplay.VertexPosition(w),
                                                              0)
            
            x1e,y1e = graphDisplay.CanvasToEmbedding(x1,y1)
            x2e,y2e = graphDisplay.CanvasToEmbedding(x2,y2)
            y1e -= y_normalizer
            y2e -= y_normalizer

            if graphDisplay.G.QEdge(w,v): # Directed edges both ways
                file.write('<line id="%s" x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s"'\
                           ' stroke-width="%s"/>\n' % (idPrefix+str((v,w)),x1e,y1e,x2e,y2e,col,width))
            else: # Just one directed edge
                # XXX How to color arrowhead?
                l = sqrt((float(wx)-float(vx))**2 + (float(wy)-float(vy))**2)
                if (l < .001):
                    l = .001

                c = (l-2*graphDisplay.zVertexRadius)/l + .01
                tmpX = float(vx) + c*(float(wx) - float(vx))
                tmpY = float(vy) + c*(float(wy) - float(vy))
                
                #tmpY -= y_normalizer


                #dx = 0 #offset of wx to make room for arrow
                #dy = 0 #offset of wy
                cr = 0
                #Took out marker-end="url(#Arrowhead)" and added polyline
                #Shrink line to make room for arrow
                for z in graphDisplay.G.Vertices():
                    cx,cy,cr = graphDisplay.VertexPositionAndRadius(z)
                    cy -= y_normalizer
                    if(cx == wx and cy == wy):
                        angle = atan2(int(float(wy))-int(float(vy)), int(float(wx))-int(float(vx)))
                        file.write('<line id="%s" x1="%s" y1="%s" x2="%f" y2="%f" stroke="%s"'\
                               ' stroke-width="%s" />\n' % (idPrefix+str((v,w)),vx,vy,tmpX,tmpY,
                                                            col,width))
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
                file.write('<polyline id="ea%s" points="%f %f %f %f %s %f" fill="%s" transform="translate(%f,%f)'\
                           ' rotate(%f %f %f)" />\n' % (idPrefix+str((v,w)), p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                                        col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))


        # Write Edge Annotations
        if graphDisplay.edgeAnnotation.QDefined((v,w)):
            da = graphDisplay.edgeAnnotation[(v,w)]
            x,y = graphDisplay.canvas.coords(graphDisplay.edgeAnnotation[(v,w)])
            xe,ye = graphDisplay.CanvasToEmbedding(x,y)
            y -= y_normalizer
            ye -= y_normalizer
            text = graphDisplay.canvas.itemcget(graphDisplay.edgeAnnotation[(v,w)],"text") 
            size = r * 0.9
            offset = 0.33 * size
            col = 'black'
            if text != "":
                file.write('<text id="ea%s" x="%s" y="%s" text-anchor="center" '\
                           'fill="%s" font-family="Helvetica" '\
                           'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(xe),
                                                                               ye+offset,col,size,text))


    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)
        
        y = y - y_normalizer
        
        # Write Vertex
        col = graphDisplay.GetVertexColor(v)
        fw = graphDisplay.GetVertexFrameWidth(v)
        fwe,dummy = graphDisplay.CanvasToEmbedding(fw,0)
        stroke = graphDisplay.GetVertexFrameColor(v)

        #print x,y,r,col,fwe,stroke
        file.write('<circle id="%s" cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"'\
                   ' stroke-width="%s" />\n' % (idPrefix+str(v),x,y,r,col,stroke,fwe))

        # Write Vertex Label
        col = graphDisplay.canvas.itemcget(graphDisplay.drawLabel[v], "fill")
        size = r*1.0
        offset = 0.33 * size

        file.write('<text id="vl%s" x="%s" y="%s" text-anchor="middle" fill="%s" font-family="Helvetica" '\
                   'font-size="%s" font-style="normal" font-weight="bold" >%s</text>\n' % (idPrefix+str(v),x,
                                                                                           y+offset,col,size,
                                                                                           graphDisplay.G.GetLabeling(v)))
        # Write vertex annotation
        size = r*0.9
        text = graphDisplay.GetVertexAnnotation(v)
        col = 'black'
        if text != "":
            file.write('<text id="va%s" x="%s" y="%s" text-anchor="left" fill="%s" font-family="Helvetica" '\
                       'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(v),x+r+1,y+r+1,col,size,text))
    
        



def ExportSVG(fileName, algowin, algorithm, graphDisplay,
              secondaryGraphDisplay=None,
              secondaryGraphDisplayAnimationHistory=None,
              showAnimation=False):
    """ Export either the current graphs or the complete animation
        (showAnimation=True) to the file fileName
    """

    global SVG_Animation
    if showAnimation:
        if secondaryGraphDisplayAnimationHistory:
            animation = collectAnimations([algorithm.animation_history.getHistoryOne(),
                                           secondaryGraphDisplayAnimationHistory.getHistoryTwo(),
                                           algowin.codeLineHistory],
                                          ['g1_','g2_','l_'])
        else:
            animation = collectAnimations([algorithm.animation_history.getHistoryOne(),
                                           algowin.codeLineHistory],
                                          ['g1_','l_'])
            

        # Reload the graph and execute prolog so we can save the initial state
        # to SVG
        algorithm.Start(prologOnly=True)
        
        file = open(fileName,'w')
        SVG_Animation = file
        # We need to change the coordinates and sizes of the SVG
        # to accomodate two graphs. How do we deal with various
        # browser window sizes???
        vars = {'x':0,'y':0,'width':1400,'height':700}

        # Merge animation commands from the graph windows and the algo window
        vars['animation'] = ",\n".join(animation)
        # print "vars", vars
        # print "animationhead", animationhead
        file.write(animationhead % vars)

        # Write out first graph as group and translate it
        bbg1 = boundingBox(graphDisplay)
        print fileName
        print bbg1
        graph_type = ""
        if(graphDisplay.G.directed == 0):
                graph_type = "undirected"
        else:
                graph_type = "directed"
        file.write('<g id="g1" transform="translate(%d,%d)" type="%s" ongesturestart="GestureStart_TransformGraph(evt)" '\
                   'ongesturechange="GestureChange_TransformGraph(evt)" ongestureend="GestureEnd_TransformGraph(evt)" '\
                   'ontouchstart="TouchStart_Graph(evt)" ontouchmove="TouchDrag_Graph(evt)" ontouchend="TouchDeactivate_Graph(evt)">\n' % (200,0, graph_type))
        WriteGraphAsSVG(graphDisplay, file, idPrefix='g1_')    
        file.write('<polygon id="triangle_scaler" points="150,150  150,150  150,150" style="stroke:#660000; fill:#cc3333;"/>')
        file.write('</g>\n')

        if secondaryGraphDisplay:
            # Write out second graph as group and translate it using the primary graphs
            # bounding box for empty graphs on the second display
            bbg2 = boundingBox(secondaryGraphDisplay, bbg1)
            if(secondaryGraphDisplay.G.directed == 0):
                graph_type = "undirected"
            else:
                graph_type = "directed"
            file.write('<g id="g2" transform="translate(%d,%d)" type="%s" ongesturestart="GestureStart_TransformGraph(evt)" '\
                       'ongesturechange="GestureChange_TransformGraph(evt)" ongestureend="GestureEnd_TransformGraph(evt)" '\
                       'ontouchstart="TouchStart_Graph(evt)" ontouchmove="TouchDrag_Graph(evt)" ontouchend="TouchDeactivate_Graph(evt)">\n' % (200,bbg1['height'], graph_type))
            WriteGraphAsSVG(secondaryGraphDisplay, file, idPrefix='g2_')    
            file.write('</g>\n')
        algowin.CommitStop()
        # Write algorithm to SVG    
        source = algorithm.GetSource()
        #Call tokenEater
        tokenize.tokenize(StringIO.StringIO(source).readline, 
                              tokenEater)
        file.write(footer)
        file.close()
    else:
        pass
