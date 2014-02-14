function Animation() {
	this.do_command = function(anim) {
		if (anim.length === 3) {
			anim[1](anim[2]);
		} else if (anim.length === 4) {
			anim[1](anim[2], anim[3]);
		} else {
			anim[1](anim.slice(2));
		}
	}
	this.animator = function() {
		if (this.state !== 'animating') {
			return;
		}
		if (this.step_num >= anim_array.length) {
			this.state = 'done';
			g.button_panel.set_buttons_state('done');
			return;
		}

		var last_anim = anim_array[this.step_num-1];
		if (last_anim != null && last_anim[1] === ShowActive && g.code_box.is_line_breakpoint_active(last_anim[2])) {
			// We're at a breakpoint
			this.state = 'waiting';
			g.button_panel.set_buttons_state('waiting');
		} else {
			var anim = anim_array[this.step_num];
			this.do_command(anim);
			this.step_num ++;
			g.slider.go_to_step(this.step_num, anim[0]*this.step_ms);
			var self = this;
			this.scheduled_animation = setTimeout(function() {self.animator()}, anim[0]*this.step_ms);
		}
	}

	/* Animator that executes animation commands until 
	the given index with no timeout in between commands */
	this.animate_until = function(stop_at_ind) {
		for (var i=this.step_num; i<stop_at_ind; i++) {
			this.do_command(anim_array[i]);
			this.step_num ++;
		}
	}

	this.start = function() {
		if (this.state === 'stopped' || this.state === 'done') {
			if (this.state === 'done') {
				// If we are done then reset the animation
				this.step_num = 0;
				this.jump_to_step(this.step_num);
			}

			this.state = 'animating';
			this.animator();
		}
	}

	this.stop = function() {
		if (this.state === 'animating' || this.state === 'stopped') {
			this.state = 'stopped';
			clearTimeout(this.scheduled_animation);
			this.step_num = 0;
			g.slider.stop_animating();
			this.jump_to_step(0);
		}
	}
	
	this.continue = function() {
		if (this.state !== 'stepping' && this.state !== 'waiting') {
			return;
		}
		if (this.state === 'waiting') {
			// Get past the blocking command
			this.do_command(anim_array[this.step_num]);
			this.step_num ++;
		}
		this.state = 'animating';
		this.animator();
	}

	this.step = function() {
		if (this.state === 'animating' || this.state === 'stepping' || this.state === 'waiting') {
			this.state = 'stepping';
			clearTimeout(this.scheduled_animation);
			this.do_command(anim_array[this.step_num]);
			this.step_num ++;
		}
	}

	this.jump_to_step = function(n) {
		var state_ind = parseInt(n/this.state_interval);
		var state = this.graph_states[state_ind];
		console.log(state)

		if (n > this.step_num && n < (state_ind+1)*this.state_interval) {
			// If we are animating between now and next state then just animate until, don't go to any state
			this.animate_until(n);
		} else {
			// We are moving backwards, or past the next state.  
			// Iterate over the graph element types, and the graphs
			for (var i=0; i<g.graph_elem_types.length; i++) {
				var elem_type = g.graph_elem_types[i];
				for (var g_num=0; g_num<g.num_graphs; g_num++) {
					
					// For each graph and type retrieve the state object
					var elem_state = state[elem_type][g_num];
					for (var id in elem_state) {
						var elem = snap.select('#' + id);
						if (elem == null) {
							// We need to create the element
							if (elem_type === 'edges') {
								var e = AddEdge(id);
								elem = e[0];
								
								// Take care of the arrowhead state right now
								var arrowhead = e[1];
								var arrowhead_state = state['edge_arrows'][g_num][arrowhead.attr('id')];
								if (arrowhead_state != null) {
									for (var attr in arrowhead_state) {
										var params = {};
										params[attr] = arrowhead_state[attr];
										arrowhead.attr(params);
									}
								}
							} else if (elem_type === 'vertices') {
								AddVertex(id);
							}
						}

						// Apply the attributes to the element. 
						if ('style' in elem_state[id]) {
							// If style is present apply it first.  It will overwrite stroke-width
							elem.attr({'style': elem_state[id]['style']})
						}
						for (var attr in elem_state[id]) {
							if (attr === 'style') {
								// Skip style since we set it above
								continue;
							}
							var params = {};
							params[attr] = elem_state[id][attr];
							elem.attr(params);
						}
					}

					// Remove any elements that shouldn't be in global values
					var global_elem_state = g[elem_type][g_num];
					for (var id in global_elem_state) {
						if (!(id in elem_state)) {
							if (elem_type === 'edges') {
								DeleteEdge(id);
							} 
						}
					}

				}
			}

			// do the tooltips
			var tooltips_text = state['tooltips_text'];
			for (var id in tooltips_text) {
				g.tooltip_objects[id].change_text(tooltips_text[id]);
			}

			// do the graph infos
			var infos = state['graph_infos'];
			for (var i=0; i<infos.length; i++) {
				g.graph_infos[i].node.innerHTML = infos[i];
			}

			this.step_num = state.step_num;
			this.animate_until(n);
		}
		g.slider.go_to_step(n);
		console.log("DONE JUMPING");
	}

	/*
		Builds the Graph State array to use for playback
	*/
	this.construct_graph_states = function() {
		function collect_tooltip_text() {
			var texts = {};
			for (var key in g.tooltip_objects) {
				texts[key] = g.tooltip_objects[key].text_content;
			}
			return texts;
		}

		function collect_graph_infos() {
			var infos = [];
			for (var i=0; i<g.graph_infos.length; i++) {
				infos.push(g.graph_infos[i].node.innerHTML);
			}
			return infos;
		}

		function collect_attr(elem) {
			var our_attr = {};
			var attributes = elem.node.attributes;
			for (var i=0; i<attributes.length; i++) {
				var attr = attributes[i];
				our_attr[attr.name] = attr.value;
			}
			return our_attr;	
		}
		
		function construct_state(step_num) {
			/* Builds a single graph state.  A single state is an object of the form
			{'step_num': __, 'tooltips_text': {'id': 'text'}, 'graph_infos': [text, text],
			'edges': [{'edge_id': {'attr_name': 'attr_value', ...}, ...}, {same thing for g2}],
			'vertices':[{}, {}], another state array for each element type }
			*/
			var state = {'step_num': step_num};
			for (var i=0; i<g.graph_elem_types.length; i++) {
				var elem_type = g.graph_elem_types[i];
				//console.log(elem_type);
				state[elem_type] = [];
				for (var g_num=0; g_num<g.num_graphs; g_num++) {
					var elem_obj = g[elem_type][g_num];
					state[elem_type].push({});
					for (var key in elem_obj) {
						state[elem_type][g_num][key] = collect_attr(elem_obj[key]);
					}
				}
			}
			// Get the tooltip text
			state['tooltips_text'] = collect_tooltip_text();
			state['graph_infos'] = collect_graph_infos();
			return state;
		}
		
		var states = [];
		for (var i=0; i<anim_array.length; i++) {
			if (i % this.state_interval === 0) {
				states.push(construct_state(i))
			}
			if (anim_array[i][1] === BlinkEdge || anim_array[i][1] === BlinkVertex) {
				// Skip Blinks
				continue;
			}
			this.do_command(anim_array[i]);
		}

		this.graph_states = states;
		this.jump_to_step(0);
	}



	this.initialize_variables = function() {
		// State of animation		
		this.states = ['animating', 'stopped', 'stepping', 'waiting', 'done'];
		this.state = 'stopped';
		
		// Our step interval in milliseconds
		this.step_ms = 22;
		
		// Current step in the animation
		this.step_num = 0;

		// How many steps we take between each saved graph state
		this.state_interval = 200; 

		this.construct_graph_states();
	}
	this.initialize_variables();
}

function Slider(width, height) {
	this.track_click = function(evt) {
		/*	Triggers when the slider track is clicked.  Moves the cursor to the position of the
			mouse cursor on the track, and jumps to the corresponding step in animation
		*/
		var self = g.slider;
		var new_x = evt.x - self.cursor.transform().globalMatrix.e - parseInt(self.cursor.attr('width'))/2;
		if (new_x < 0) {
			new_x = 0;
		} else if (new_x > self.cursor_max_x) {
			new_x = self.cursor_max_x;
		}
		self.cursor.attr({'x': new_x});
		var step = parseInt(new_x / self.step_width);
		g.animation.jump_to_step(step);
	}
	this.cursor_mousedown = function(evt) {
		/*	Triggers when cursor is mousedowned.  Begins sliding process by 
			recording initial cursor and mouse positions
		*/
		g.slider.sliding = true;
		g.slider.start_cursor_x = parseInt(g.slider.cursor.attr('x'));
		g.slider.start_mouse_x = parseInt(evt.x);
	}
	this.cursor_drag = function(evt) {
		this.mouseup(evt);
	}
	this.cursor_mousemove = function(evt) {
		/*	This does the actual moving of the cursor.  Using the cursor and mouse positions
			at mousedown event this computes the new position of the cursor, and moves
			the animation to the corresponding step.
		*/
		var step = 0;
		var new_x = this.start_cursor_x + parseInt(evt.x) - g.slider.start_mouse_x;
		if (new_x > this.cursor_max_x) {
			new_x = this.cursor_max_x;
			step = anim_array.length - 1;
		} else if (new_x < this.cursor_min_x) {
			new_x = this.cursor_min_x;
			step = 0;
		} else {
			step = parseInt(new_x / this.step_width) + 1;
		}
		this.cursor.attr({'x': new_x});
		g.animation.jump_to_step(step);
	}
	this.cursor_mouseup = function(evt) {
		/* Ends cursor sliding behavior */
		this.sliding = false;
	}
	this.go_to_step = function(n, time) {
		/* Positions the cursor at the position corresponding to step number n */
		var position = this.slider_positions[n];
		console.log(n);
		console.log("going to position " + position + " with timeout " + time);
		if (time) {
			var diff = position*this.step_width - parseInt(this.cursor.attr('x'));
			this.cursor.animate({'x': position*this.step_width}, time);
		} else {
			this.cursor.attr({'x': position*this.step_width});
		}
	}
	this.compute_step_width = function() {
		var sum = 0;
		this.slider_positions = [];
		for (var i=0; i<anim_array.length; i++) {
			this.slider_positions.push(sum);
			sum += anim_array[i][0];
		}
		this.slider_positions.push(sum);
		return this.cursor_max_x / sum;
	}
	this.stop_animating = function() {
		g.slider.cursor.stop();
	}

	this.init = function () {
		this.sliding = false;
		this.width = width;
		this.height = height;
		this.g = snap.group();

		// Construct the slider track
		this.track_width = this.width;
		this.track_height = 8;
		this.track_y = this.height/2-this.track_height/2;
		this.track = snap.rect(0, this.track_y, this.width, this.track_height, 2, 2).attr({
			'fill': '#AAA',
			'cursor': 'pointer'
		}).click(this.track_click);
		this.g.append(this.track);

		// Construct the cursor
		this.cursor_height = this.height;
		this.cursor_width = 10;
		this.cursor = snap.rect(0, 0, this.cursor_width, this.cursor_height, 6, 6).attr({
			'fill': '#eee',
			'stroke': '#111',
			'stroke-width': 1,
			'cursor': 'pointer'
		}).mousedown(this.cursor_mousedown);
		this.cursor_max_x = this.width - this.cursor_width;
		this.cursor_min_x = 0;
		this.step_width = this.compute_step_width()
		//this.cursor_max_x / anim_array.length;
		this.g.append(this.cursor);
	}
	
	this.init();
}


/**
*
*	Graph Modifying Functions
*
*/

/** Sets the vertex given by vertex_id to color */
function SetVertexColor(vertex_id, color) {
	g.vertices[graph_num_from_id(vertex_id)][vertex_id].attr('fill', color);
}

function UpdateEdgeInfo(edge_id, info) {
	var graph_num = parseInt(edge_id.substring(1,2));
	var tooltip_id = edge_id + '_tooltip';
	var tooltip = g.tooltip_objects[edge_id + '_tooltip'].change_text(info);
}

function UpdateGraphInfo(graph_id, info) {
	var graph_num = parseInt(graph_id.substring(1));
	var graph_info_text_elem = g.graph_infos[graph_num-1];
	graph_info_text_elem.node.innerHTML = info;
}

/** Sets the given edge to the given color.  If the given edge
	is not found, then the reverse direction is tried, e.g. if g1_(5, 4) is
	not found we will try g1_(4, 5)
*/
function SetEdgeColor(edge_id, color) {
	function switch_edge_vertices() {
	    // Switches the edge_id vertices.  ie. g1_(5, 4) in --> g1_(4, 5) out
	    // TODO: Test me
	    var re = /\d+/g;
	    var matches = edge_id.match(re);
	    return "g" + matches[0] + "_" + matches[2] + "-" + matches[1];
	}
	var graph_num = graph_num_from_id(edge_id);
	var edge = g.edges[graph_num][edge_id];
	if (edge == null) {
		edge_id = switch_edge_vertices();
		edge = g.edges[graph_num][edge_id];
	}
	edge.attr({'stroke': color});	// For some reason if we don't set stroke-width it will go to 1 
    
    var edge_arrow = g.edge_arrows[graph_num][(g.arrow_id_prefix + edge_id)];
    if (edge_arrow !== undefined) {
    	edge_arrow.attr({'fill': color});
    }
}

/** Sets color of all vertices of a given graph to a given color.
* 	graph_id_and_color is string of form "g{graph_num}_#{hex_color}"
* 	If vertices != null, then only color the set of vertices specified by vertices
*/
function SetAllVerticesColor() {
	var graph_id_and_color = arguments[0];
	var vertex = arguments[1];
	// TODO: Modify this to use variable length args instead of vertices 
	var split = graph_id_and_color.split('_');
	var graph_num = graph_num_from_id(graph_id_and_color);
	var graph_id = split[0];
	var color = split[1];

	if (vertex == null) {
		for (var key in g.vertices[graph_num]) {
			g.vertices[graph_num][key].attr({'fill': color});
		}
	} else {
		// TODO: Is vertices always a single string?
		g.vertices[graph_num]['g' + (graph_num+1) + '_' + vertex].attr({'fill': color});
		/*for (var i=0; i<vertices.length; i++) {
			console.log(vertices[i]);
			console.log('g' + (graph_num+1) + '_' + vertices[i]);
			g.vertices[graph_num]['g' + (graph_num+1) + '_' + vertices[i]].attr({'fill': color});
		}
		*/
	}
}


/** Sets all edges of given graph to color.  param is of form: "g1_#dd3333" */
function SetAllEdgesColor(graph_id_and_color) {
    var split = graph_id_and_color.split('_');
    var graph_num = graph_num_from_id(graph_id_and_color);
    var color = split[1];
    var graph_edges = g.edges[graph_num];
    var edge_arrows = g.edge_arrows[graph_num];
    //console.log(graph_edges);
    for (var key in graph_edges) {
    	graph_edges[key].attr({'stroke': color}); // For some reason if we don't set stroke-width it will go to 1 
    	var arrowhead_id = 'ea' + key;
    	if (arrowhead_id in edge_arrows) {
    		edge_arrows[arrowhead_id].attr({'fill': color});
    	}
    }
}


/** Blinks the given vertex between black and current color 3 times */
function BlinkVertex(vertex_id, color) {
	var vertex = g.vertices[graph_num_from_id(vertex_id)][vertex_id];
    var curr_color = vertex.attr('fill');
    for (var i=0; i<6; i+=2) {
    	setTimeout(function() { vertex.attr({'fill': 'black'}); }, g.step_ms*(i));
    	setTimeout(function() { vertex.attr({'fill': curr_color}); }, g.step_ms*(i+1));
    }
}

/** Blinks the given edge between black and current color 3 times */
function BlinkEdge(edge_id, color){
	var edge = g.edges[graph_num_from_id(edge_id)][edge_id];
    var curr_color = edge.attr('stroke');
    for (var i=0; i<6; i+=2) {
    	setTimeout(function() { edge.attr({'stroke':  'black', 'stroke-width': g.edge_width}); }, g.step_ms*(i));
    	setTimeout(function() { edge.attr({'stroke': curr_color, 'stroke-width': g.edge_width}); }, g.step_ms*(i+1));
    }
}

//Blink(self, list, color=None):
//Sets the frame width of a vertex
function SetVertexFrameWidth(vertex_id, val) {
	// Take away dropshadow
    var vertex = g.vertices[graph_num_from_id(vertex_id)][vertex_id];
	if (val !== '0') {
        vertex.attr({"style": ""});
	}
    vertex.attr({'stroke-width': val});

    // Add back in dropshadow
    if (val === "0") {
        vertex.attr({"style": "filter:url(#dropshadow)"});
    }
}

//Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(v, annotation, color) //removed 'this' parameter to because 'this' parameter was assigned value of v, v of annotation, and so on.
{
}


//Line with specified id is highlighted.  Becomes current line of code.  Previous highlight is removed.
function ShowActive(line_id){
 	g.code_box.highlight_line(line_id);
}

//Creates an arrowhead on a line starting at (vx,vy) and ending at (wx,wy) and parallel to it
//Arrowhead with given id touches the outide of a vertex with cx=wx and xy=wy
function createArrowhead(vx, vy, wx, wy, stroke_width, id){
    var len = Math.sqrt(Math.pow(parseFloat(wx)-parseFloat(vx),2) + Math.pow(parseFloat(wy)-parseFloat(vy), 2));
    if (len < .001) {
        len = .001;
    }
                
    var a_width = (1 + 1.5/(1*Math.pow(Math.log(parseFloat(stroke_width))/Math.log(10), 6)));
    if(a_width > 5.0) {
        a_width = 5.0;
    }
    var cr = g.vertex_r;
    a_width = a_width * parseFloat(stroke_width);

    var p1 = [0,0];
    var p2 = [0, a_width];
    var p3 = [cr, a_width/2];
    var angle = (Math.atan2(parseInt(wy)-parseInt(vy), parseInt(wx)-parseInt(vx))) * 180/Math.PI;
    var c = (len-2*g.vertex_r)/len;
    var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
    var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
    
    var arrowhead = snap.polyline(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]).attr({
    	'fill': g.edge_color,
    	'id': id
    }).transform('t' + tmpX + ',' + (tmpY-a_width/2) + 'r' + angle + ',' + p1[0] + ',' + (a_width/2));
    return arrowhead;
}

//Directed or undirected added to graph.
function AddEdge(edge_id){
	var graph_num = graph_num_from_id(edge_id);
    var graph_id = edge_id.split("_")[0];
    var vertices = edge_id.split("_")[1].match(/\d+/g);
    var v = g.vertices[graph_num][graph_id + '_' + vertices[0]];
    var w = g.vertices[graph_num][graph_id + '_' + vertices[1]];
    
    var vx = v.attr("cx"),
    	wx = w.attr("cx"),
    	vy = v.attr("cy"),
    	wy = w.attr("cy");
    if (v == null || w == null || g.edges[graph_num][graph_id + '_' + vertices[0] + '-' + vertices[1]] != null) {
    	// Exit if one of the vertices is null or the edge already exists
    	return;
    }

    var parent_graph = g.graphs[graph_num];
    var edge = null;
    var arrowhead = null;
    if (parent_graph.attr("type") == "directed") {
        var reverse_edge = g.edges[graph_num][graph_id + "_" + vertices[1] + "-" + vertices[0]];
        if (reverse_edge != null) {  
        	// reverse edge exists.  Make this edge an arc.
            // Another directed edge.  Great... Change existing edge to arc and add new arc
            // Be sure to alter polylines as well.   
            var len = Math.sqrt(Math.pow((parseFloat(vx)-parseFloat(wx)),2) + Math.pow((parseFloat(vy)-parseFloat(wy)),2));
            if (len < 0.001) {
                len = 0.001;
            }
            var c = (len - g.vertex_r)/len - 0.001;
            var tmpX = parseFloat(vx) + c * (parseFloat(wx) - parseFloat(vx));
            var tmpY = parseFloat(vy) + c * (parseFloat(wy) - parseFloat(vy));
            var orthogonal = Orthogonal((parseFloat(wx)-parseFloat(vx)),(parseFloat(wy)-parseFloat(vy)));
            var mX = orthogonal[0];
            var mY = orthogonal[1];
            c = 1.5*g.vertex_r + len/25;
            mX = parseFloat(vx) + .5 * (parseFloat(wx) - parseFloat(vx)) + c * mX
            mY = parseFloat(vy) + .5 * (parseFloat(wy) - parseFloat(vy)) + c * mY
            arrowhead = createArrowhead(mX, mY, wx, wy, g.edge_width, "ea" + edge_id);
            
            len = Math.sqrt(Math.pow(wx-mX,2) + Math.pow(wy-mY,2));
            if (len < .001) {
                len = .001;
            }
            
            c = (len-2*g.vertex_r)/len + .01;
            tmpX = mX + c*(wx - mX);
            tmpY = mY + c*(wy - mY);
            
            var path_str = "M " + vx + "," + vy +" Q "+ mX +"," + mY + " " + tmpX + "," + tmpY;
            edge = snap.path(path_str).attr({
            	'id': edge_id,
            	'stroke': g.edge_color,
            	'stroke-width': g.edge_width,
            	'fill': 'none',
            	'class': 'edge'
            });
    
            if (arrowhead != null) {
                parent_graph.prepend(arrowhead);
            }
            parent_graph.prepend(edge);
            g.edges[graph_num][edge.attr('id')] = edge;
		    if (arrowhead != null) {
		    	g.edge_arrows[graph_num][arrowhead.attr('id')] = arrowhead;
		    }
		    add_tooltip(edge);
                
            if(reverse_edge.attr("d") == null){
                var reverse_edge_id = reverse_edge.attr('id');
                var arrowhead_id = 'ea' + reverse_edge.attr('id');
                g.edge_arrows[graph_num][arrowhead_id].remove();
                delete g.edge_arrows[graph_num][arrowhead_id];
                g.edges[graph_num][reverse_edge_id].remove();
                delete g.edges[graph_num][reverse_edge_id];
                g.tooltip_objects[reverse_edge_id + '_tooltip'].delete_self();
                AddEdge(reverse_edge_id);
            }
        }else{  
        	// No reverse edge.  Just make a straight line
            var len = Math.sqrt(Math.pow((parseFloat(wx)-parseFloat(vx)),2) + Math.pow((parseFloat(wy)-parseFloat(vy)),2));
            if (len < .001) {
                len = .001;
            }
            /* What does this math do compared to wx and wy? */
            var c = (len - 2*g.vertex_r) / len + .01;
            var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
            var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
            edge = snap.line(vx, vy, tmpX, tmpY).attr({
            	'id': edge_id,
            	'stroke': g.edge_color,
            	'stroke-width': g.edge_width,
            	'class': 'edge'
            });
            arrowhead = createArrowhead(vx, vy, wx, wy, g.edge_width, "ea" + edge_id);   
            if (arrowhead != null) {
                parent_graph.prepend(arrowhead);
            }
            parent_graph.prepend(edge);
            g.edges[graph_num][edge.attr('id')] = edge;
			if (arrowhead != null) {
				g.edge_arrows[graph_num][arrowhead.attr('id')] = arrowhead;
			}
			add_tooltip(edge);
        }
    }else{ 
    	//Undirected edge
    	edge = snap.line(vx, vy, wx, wy).attr({
    		'id': edge_id,
    		'stroke': g.edge_color,
    		'stroke-width': g.edge_width,
    		'class': 'edge'
    	});
        parent_graph.prepend(edge);
    	g.edges[graph_num][edge.attr('id')] = edge;
    	add_tooltip(edge);
    }

    return [edge, arrowhead];
}

//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id){
	var graph_num = graph_num_from_id(edge_id);
	var graph_id = edge_id.substring(0,2);
	var vertices = edge_id.split("_")[1].match(/\d+/g);
	g.edges[graph_num][edge_id].remove();
	delete g.edges[graph_num][edge_id];
	var arrowhead_id = 'ea' + edge_id;
	if (arrowhead_id in g.edge_arrows[graph_num]) {
		g.edge_arrows[graph_num][arrowhead_id].remove();
		delete g.edge_arrows[graph_num][arrowhead_id];
	}

	var reverse_edge_id = graph_id + "_" + vertices[1] + "-" + vertices[0];
    var reverse_edge = g.edges[graph_num][reverse_edge_id];
    if (reverse_edge != null) {
    	// The reverse edge needs to go from arc to straight
    	var reverse_arrow = g.edge_arrows[graph_num]['ea' + reverse_edge_id];
    	var arrow_fill = reverse_arrow.attr('fill');
    	var stroke = reverse_edge.attr('stroke');
    	var stroke_width = reverse_edge.attr('stroke-width');
    	DeleteEdge(reverse_edge.attr('id'));
    	edge_and_arrow = AddEdge(reverse_edge.attr('id'));
    	edge_and_arrow[0].attr({'stroke': stroke, 'stroke-width': stroke_width});
    	edge_and_arrow[1].attr({'fill': arrow_fill});
    }

    // Remove the tooltip if needed
	var tooltip = g.tooltip_objects[edge_id + '_tooltip'];
	tooltip.delete_self();	
}

//Adds vertex of into specified graph and coordinates in graph.  Optional id argument may be given.
function AddVertex(graph_and_coordinates, id){

}

function DeleteVertex(vertex_id) {

}