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

    <linearGradient id="button_bg1" x1="0" y1="0" x2="0" y2="1">
	<stop offset="0" stop-color="turquoise">
	</stop>						
	<stop offset="1" stop-color="navy">	
	</stop>	
    </linearGradient>
    <linearGradient id="button_light1" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="white">
		</stop>					
		<stop offset="1" stop-color="white" stop-opacity="0">	
		</stop>								
	
    </linearGradient>
    <linearGradient id="button_light2" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="black" stop-opacity="0">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    <filter id="button_gb">
		<feGaussianBlur stdDeviation="3">
		</feGaussianBlur>	
    </filter>
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
var code;    //tracks HTB of code
var init_graph;  //initial graph, for restarting
var action_panel;   //tracks buttons
var state;	//tracks state of animation
var timer;	//variable for timer for AnimateLoop
var timeout = 4;  //timeout
var horiz_layout;
var verti_layout;


function getTranslate(str){
	var x;
	var y;
	
	if(str == null){
		return new Array(0, 0);
	}
	
	var to_parse = str.slice(str.indexOf("translate") + "translate".length);
	
	if(to_parse == null){
		return new Array(0, 0);
	}
	
	
	var r = to_parse.match(/\d+/g);
	
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


function setTranslate(component, x, y){
	var transformation = component.getAttribute("transform");
	
	if(transformation != null){
		var header = transformation.substring(0, transformation.indexOf("translate") + "translate".length);
		if(transformation.indexOf("translate") == -1){
			component.setAttribute("transform", transformation + " translate(" + x + " " + y + ")");
		}else{

			var trailer = transformation.slice(transformation.indexOf("translate") + "translate".length);
			trailer = trailer.slice(trailer.indexOf(")"));
		
			var newattr = header + "(" + x + " " + y + trailer;

			component.setAttribute("transform", newattr);
		}

	}else{
		component.setAttribute("transform", "translate(" + x + " " + y + ")");
	}
}



function HighlightableTextBlock(hp, vp, i, font_size, layout){
	this.line_llc = new LinearLayoutComponent(hp, vp, i, layout);
	this.line_llc.group.setAttribute("font-size", font_size);
	this.highlight_group = the_evt.target.ownerDocument.createElementNS(svgNS,"g");
	this.highlight_group.setAttribute("id", i + "_hg");
	the_evt.target.ownerDocument.documentElement.insertBefore(this.highlight_group, this.line_llc.group);	
}

function HTB_prototypeInit(){
	var htb = new HighlightableTextBlock(2,2,"foo",14, "vertical");
	HighlightableTextBlock.prototype.insertLine = HTB_insertLine;
	HighlightableTextBlock.prototype.deleteLine = HTB_deleteLine;
	HighlightableTextBlock.prototype.highlightLine = HTB_highlightLine;
	HighlightableTextBlock.prototype.removeHighlight = HTB_removeHighlight;

	htb = the_evt.target.ownerDocument.getElementById("foo");
	htb.parentNode.removeChild(htb);
	htb = the_evt.target.ownerDocument.getElementById("foo_hg");
	htb.parentNode.removeChild(htb);
}



//insert line into nth slot.  0-based indexing.  May also be used to rearrange lines
function HTB_insertLine(id, n){

	this.line_llc.insertComponent(id, n);
}


//delete nth line
function HTB_deleteLine(n){
	this.line_llc.deleteComponent(n);
	this.removeHighlight(this.line_llc.group.childNodes.length);
}



//highlight nth line
function HTB_highlightLine(n){

	if(n < this.line_llc.group.childNodes.length && n >= 0){

		if(the_evt.target.ownerDocument.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + n) == null){

			var line = this.line_llc.group.childNodes.item(n);
			var htb_bbox = this.line_llc.group.getBBox();
			var line_bbox = line.getBBox();
			var line_translation = getTranslate(this.line_llc.group.childNodes.item(n).getAttribute("transform"));
			var m = 1;

			var background = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
			
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
			
			//setTranslate(background, line_translation[0] , line_translation[1]-this.line_llc.v_padding);
			background.setAttribute("x", line_bbox.x + line_translation[0] - this.line_llc.h_padding - dx);
			background.setAttribute("y", line_bbox.y + line_translation[1] - this.line_llc.v_padding - dy);
			background.setAttribute("width", htb_bbox.width + 2*this.line_llc.h_padding);
			background.setAttribute("height", line_bbox.height + 2*this.line_llc.v_padding);

			background.setAttribute("stroke", "blue");
			background.setAttribute("fill", "yellow");
			background.setAttribute("id", this.line_llc.group.getAttribute("id") + "_hl" + n);
			
			this.highlight_group.appendChild(background);
		}
	}
}

function HTB_removeHighlight(n){
	var hl = the_evt.target.ownerDocument.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + n);
	if(hl != null){
		this.highlight_group.removeChild(hl);
	}
}



function LinearLayoutComponent(hp, vp, i, layout){
	this.h_padding = hp;  //Number of pixels padding the top and bottom of each line
	this.v_padding = vp;  //Number of pixels padding the left and right of each line
	this.id = i;           //ID of group that is abstracted by this HTB instance
	
	//Create new group element to place all lines of code
	this.group = the_evt.target.ownerDocument.createElementNS(svgNS,"g");
	this.group.setAttribute("id", i);
	the_evt.target.ownerDocument.documentElement.appendChild(this.group);
	this.layout = layout;  //'horizontal' or 'vertical'
}

function LLC_prototypeInit(){
	var llc = new LinearLayoutComponent(0,0,"foo","horizontal");
	LinearLayoutComponent.prototype.insertComponent = LLC_insertComponent;
	LinearLayoutComponent.prototype.deleteComponent = LLC_deleteComponent;
	LinearLayoutComponent.prototype.resnapComponent = LLC_resnapComponent;
	llc.group.parentNode.removeChild(llc.group);
}



//insert line into nth slot.  0-based indexing.  May also be used to rearrange lines
function LLC_insertComponent(id, n){

	var new_c = the_evt.target.ownerDocument.getElementById(id);
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
		
			if(n == 0){
				setTranslate(new_c, 0, 0);
			}else{
				bbox = this.group.childNodes.item(n-1).getBBox();
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


//delete nth line
function LLC_resnapComponent(n){
	var children = this.group.childNodes;
	var child = children.item(n);
	
	child.parentNode.removeChild(n);
	the_evt.target.ownerDocument.documentElement.appendChild(child);
	this.insertComponent(child.getAttribute("id"), n);
}


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






function ButtonPanel(hp, vp, i, layout){
	this.llc = new LinearLayoutComponent(hp, vp, i, layout);
}



function BP_prototypeInit(){
	var bp = new ButtonPanel(0,0,"baz","horizontal");
	ButtonPanel.prototype.createButton = BP_createButton;
	ButtonPanel.prototype.deleteButton = BP_deleteButton;
	ButtonPanel.prototype.deleteButtonById = BP_deleteButtonById;
	ButtonPanel.prototype.activateButton = BP_activateButton;
	ButtonPanel.prototype.deactivateButton = BP_deactivateButton;
	bp.llc.group.parentNode.removeChild(bp.llc.group);
}

function BP_createButton(id, text, index, action){  //Create button with corresponding id, text, and action into slot #index
	if(the_evt.target.ownerDocument.getElementById(id) == null){
		var button_group = the_evt.target.ownerDocument.createElementNS(svgNS, "g");
		button_group.setAttribute("id", id);
		
		
		var element1 = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
		element1.setAttribute("x", 5);
		element1.setAttribute("y", 5);
		element1.setAttribute("width", 150);
		element1.setAttribute("height", 30);
		element1.setAttribute("rx", 10);
		element1.setAttribute("ry", 10);
		element1.setAttribute("fill", "grey");
		element1.setAttribute("filter", "url(#button_gb)");
		button_group.appendChild(element1);
	
		element1 = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
		element1.setAttribute("x", 0);
		element1.setAttribute("y", 0);
		element1.setAttribute("width", 150);
		element1.setAttribute("height", 30);
		element1.setAttribute("rx", 10);
		element1.setAttribute("ry", 10);
		element1.setAttribute("fill", "url(#button_bg1)");
		button_group.appendChild(element1);
	
		
		element1 = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
		element1.setAttribute("x", 2);
		element1.setAttribute("y", 2);
		element1.setAttribute("width", 146);
		element1.setAttribute("height", 17);
		element1.setAttribute("rx", 8);
		element1.setAttribute("ry", 8);
		element1.setAttribute("fill", "url(#button_light1)");
		button_group.appendChild(element1);
		
		element1 = the_evt.target.ownerDocument.createElementNS(svgNS, "rect");
		element1.setAttribute("x", 4);
		element1.setAttribute("y", 21);
		element1.setAttribute("width", 142);
		element1.setAttribute("height", 7);
		element1.setAttribute("rx", 8);
		element1.setAttribute("ry", 8);
		element1.setAttribute("fill", "url(#button_light2)");
		button_group.appendChild(element1);
		
		element1 = the_evt.target.ownerDocument.createElementNS(svgNS, "text");
		element1.setAttribute("x", 75);
		element1.setAttribute("y", 19);
		element1.setAttribute("text-anchor", "middle");
		element1.setAttribute("fill", "yellow");
		element1.setAttribute("font-weight", 900);
		element1.setAttribute("id", id + "_text");
		element1.appendChild(the_evt.target.ownerDocument.createTextNode(text));
		button_group.appendChild(element1);
		
		
		button_group.setAttribute("onclick", action);
		button_group.setAttribute("cursor", "pointer");
		the_evt.target.ownerDocument.documentElement.appendChild(button_group);
		this.llc.insertComponent(button_group.getAttribute("id"), index);

	}else{
		this.llc.insertComponent(id, index);

	}
	

	

}

function BP_deleteButton(n){
	this.llc.deleteComponent(n);
}

function BP_deleteButtonById(id){
	var children = this.llc.group.childNodes;
	
	for(i = 0; i < children.length; i++){
		if(children.item(i).getAttribute("id") == id){
			this.deleteButton(i);
			break;
		}
	}
}

function BP_activateButton(id, action){
	var children = this.llc.group.childNodes;


	for(i = 0; i < children.length; i++){
		if(children.item(i).getAttribute("id") == id){
			children.item(i).setAttribute("onclick", action);
			children.item(i).setAttribute("cursor", "pointer");
			var grandchildren = children.item(i).childNodes;
			for(j = 0; j < grandchildren.length; j++){
				if(grandchildren.item(j).getAttribute("id") == (id + "_text")){
					grandchildren.item(j).setAttribute("fill", "yellow");
					break;
				}
			}
			break;
		}
	}
}

function BP_deactivateButton(id){
	var children = this.llc.group.childNodes;

	for(i = 0; i < children.length; i++){
		if(children.item(i).getAttribute("id") == id){
			children.item(i).setAttribute("onclick", "");
			children.item(i).setAttribute("cursor", "default");
			var grandchildren = children.item(i).childNodes;
			for(j = 0; j < grandchildren.length; j++){
				if(grandchildren.item(j).getAttribute("id") == id + "_text"){
					grandchildren.item(j).setAttribute("fill", "grey");
					break;
				}
			}			
			break;
		}
	}
}











function Initialize(evt) {
	the_evt = evt;
	HTB_prototypeInit();
	LLC_prototypeInit();
	BP_prototypeInit();


        /*
        I commented out this part for now, so nothing will display.  I wanted to wait until I saw
        what the final product looked like (i.e. how the elements are actually listed at the bottom of the document)
        */
	/*code = new HighlightableTextBlock(2, 2, "code", 14, "vertical");

	for(i = 0; i < 5; i++){
		code.insertLine("cl" + i, i);
	}
	for(i = 0; i < 5; i++){
		code.insertLine("foocl" + i, i+5);
	}	
	
	
	init_graph = the_evt.target.ownerDocument.getElementById("graph1").cloneNode(true);
	
	action_panel = new ButtonPanel(2, 2, "actions", "horizontal");
	action_panel.createButton("start_button", "Start", 0, "StartAnimation(evt)");
	action_panel.createButton("step_button", "Step", 1, "StepAnimation(evt)");
	action_panel.createButton("continue_button", "Continue", 2, "ContinueAnimation(evt)");
	action_panel.createButton("stop_button", "Stop", 3, "StopAnimation(evt)");

	horiz_layout = new LinearLayoutComponent(2, 2, "horizontal_layout", "horizontal");	
	vert_layout = new Array(new LinearLayoutComponent(2, 2, "vert_layout_0", "vertical"), new LinearLayoutComponent(2, 2, "vert_layout_1", "vertical"));

	vert_layout[0].insertComponent(code.line_llc.group.getAttribute("id"), 0);
	vert_layout[0].insertComponent(action_panel.llc.group.getAttribute("id"), 1);
	vert_layout[1].insertComponent(the_evt.target.ownerDocument.getElementById("graph1").getAttribute("id"), 0);
	horiz_layout.insertComponent(vert_layout[0].group.getAttribute("id"), 0);
	horiz_layout.insertComponent(vert_layout[1].group.getAttribute("id"), 1);
	var bbox1 = vert_layout[0].group.getBBox();
	var bbox2 = vert_layout[1].group.getBBox();*/

}




function StartAnimation(evt){

	if(evt.target.getAttribute("id") == "start_button" || evt.target.parentNode.getAttribute("id") == "start_button"){
	
		if(state != null){
			horiz_layout.deleteComponent(1);
			vert_layout[1] = new LinearLayoutComponent(2, 2, "vert_layout_1", "vertical");
			
			var new_graph = init_graph.cloneNode(true);
			the_evt.target.ownerDocument.documentElement.appendChild(new_graph);
			
			vert_layout[1].insertComponent(the_evt.target.ownerDocument.getElementById("graph1").getAttribute("id"), 0);
			horiz_layout.insertComponent(vert_layout[1].group.getAttribute("id"), 1);

		}
	
	
	
		state = "running";
		action_panel.activateButton("stop_button", "StopAnimation(evt)");
		action_panel.activateButton("continue_button", "ContinueAnimation(evt)");
		action_panel.activateButton("step_button", "StepAnimation(evt)");
		action_panel.deactivateButton("start_button");

		AnimateLoop();
	}
}



function AnimateLoop(){
	var duration = animation[step][0] * timeout;
	animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
	step = step + 1; 
	if(step < animation.length) 
		timer = setTimeout(AnimateLoop, duration);

}

function ContinueAnimation(evt){
	if(evt.target.getAttribute("id") == "continue_button" || evt.target.parentNode.getAttribute("id") == "continue_button" ){
		if(state != "running"){
			state = "running";
			AnimateLoop();
		}
	}
}

function StepAnimation(evt){
	if(evt.target.getAttribute("id") == "step_button" || evt.target.parentNode.getAttribute("id") == "step_button"){
		animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
		step = step + 1;

	}
	
}

function StopAnimation(evt){
	if(evt.target.getAttribute("id") == "stop_button" || evt.target.parentNode.getAttribute("id") == "stop_button"){
		clearTimeout(timer);
		
		
		state = "stopped";
		action_panel.activateButton("start_button", "StartAnimation(evt)");
		action_panel.deactivateButton("continue_button");
		action_panel.deactivateButton("stop_button");
		action_panel.deactivateButton("step_button");
		step = 0;
	}
}



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
	element.parentNode.appendChild(newano);
	
    }
}

//function SetEdgeAnnotation(self,tail,head,annotation,color="black"):
//def UpdateVertexLabel(self, v, blink=1, color=None):
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
    <marker id="Arrowhead" 
      viewBox="0 0 10 10" refX="0" refY="5" 
      markerUnits="strokeWidth" 
      markerWidth="4" markerHeight="3" 
      orient="auto"> 
      <path d="M 0 0 L 10 5 L 0 10 z" /> 
    </marker>
    
    <linearGradient id="button_bg1" x1="0" y1="0" x2="0" y2="1">
	<stop offset="0" stop-color="turquoise">
	</stop>						
	<stop offset="1" stop-color="navy">	
	</stop>	
    </linearGradient>
    <linearGradient id="button_light1" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="white">
		</stop>					
		<stop offset="1" stop-color="white" stop-opacity="0">	
		</stop>								
	
    </linearGradient>
    <linearGradient id="button_light2" x1="0" y1="0" x2="0" y2="1">
		<stop offset="0" stop-color="black" stop-opacity="0">
		</stop>
		<stop offset="1" stop-color="black">
		</stop>
    </linearGradient>
    <filter id="button_gb">
		<feGaussianBlur stdDeviation="3">
		</feGaussianBlur>	
    </filter>
</defs>
"""

footer = """
</svg>
"""






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

def boundingBox(graphDisplay):
    bb = graphDisplay.canvas.bbox("all") # Bounding box of all elements on canvas
    # Give 10 pixels room to breathe
    x = max(bb[0] - 10,0)
    y = max(bb[1] - 10,0)
    width=bb[2] - bb[0] + 10
    height=bb[3] - bb[1] + 10
    return {'x':x,'y':y,'width':width,'height':height}


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



    # Write Edges
    for v,w in graphDisplay.G.Edges():
        vx,vy,r = graphDisplay.VertexPositionAndRadius(v)
        wx,wy,r = graphDisplay.VertexPositionAndRadius(w)
        col = graphDisplay.GetEdgeColor(v,w)
        width = graphDisplay.GetEdgeWidth(v,w)

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
                               ' stroke-width="%s" />\n' % (idPrefix+str((v,w)),vx,vy,tmpX,tmpY,
                                                            col,width))
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
                           ' rotate(%f %f %f)" />\n' % (idPrefix+str((v,w)), p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                                        col, tmpX, tmpY - a_width/2, angle, p1[0], a_width/2))


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
                           'font-size="%s" font-style="normal">%s</text>\n' % (idPrefix+str(xe),
                                                                               ye+offset,col,size,text))


    for v in graphDisplay.G.Vertices():
        x,y,r = graphDisplay.VertexPositionAndRadius(v)

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
    print algowin.codeLineHistory
    
    if showAnimation:
        animation = collectAnimations([algorithm.animation_history.history,
                                       secondaryGraphDisplayAnimationHistory.history,
                                       algowin.codeLineHistory],
                                      ['g1_','g2_','l_'])

        # Reload the graph and execute prolog so we can save the initial state
        # to SVG
        algorithm.Start(prologOnly=True)
        
        file = open(fileName,'w')

        # We need to change the coordinates and sizes of the SVG
        # to accomodate two graphs. How do we deal with various
        # browser window sizes???
        vars = {'x':0,'y':0,'width':1024,'height':768}

        # Merge animation commands from the graph windows and the algo window
        vars['animation'] = ",\n".join(animation)
        file.write(animationhead % vars)

        # Write out first graph as group and translate it
        bbg1 = boundingBox(graphDisplay)
        file.write('<g id="g1" transform="translate(%d,%d)">\n' % (200,0))
        WriteGraphAsSVG(graphDisplay, file, idPrefix='g1_')    
        file.write('</g>\n')

        if secondaryGraphDisplay:
            # Write out second graph as group and translate it
            bbg2 = boundingBox(secondaryGraphDisplay)
            file.write('<g id="g2" transform="translate(%d,%d)">\n' % (200,bbg1['height']))
            WriteGraphAsSVG(secondaryGraphDisplay, file, idPrefix='g2_')    
            file.write('</g>\n')

        algowin.CommitStop()
        # Write algorithm to SVG    
        source = algorithm.GetSource()
        print source
        file.write(footer)
        file.close()
    else:
        pass