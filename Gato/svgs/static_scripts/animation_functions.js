function Animation() {
	this.do_command = function(anim) {
		// Handle growing of moats
		if (anim[1] === GrowMoat) {
			g.growing_moats = true;
			if (!g.moat_growing_time) {
				g.moat_growing_time = get_moat_growing_time(this.step_num);
			}
		} else if (g.growing_moats) {
			g.growing_moats = false;
			g.moat_growing_time = null;
		} 
		if (anim[1] === ResizeBubble) {
			g.bubble_resize_time = anim[0]*this.step_ms;
		}

		if (anim.length === 3) {
			anim[1](anim[2]);
		} else if (anim.length === 4) {
			anim[1](anim[2], anim[3]);
		} else {
			anim[1].apply(this, anim.slice(2));
		}
	}
	this.animator = function() {
		if (this.state !== 'animating') {
			return;
		}
		if (g.slider.sliding === true) {
			setTimeout(function() {
				g.animation.animator();
			}, 10);
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
	};

	/* Animator that executes animation commands until 
	the given index with no timeout in between commands */
	this.animate_until = function(stop_at_ind) {
		for (var i=this.step_num; i<stop_at_ind; i++) {
			this.do_command(anim_array[i]);
			this.step_num ++;
			g.slider.go_to_step(this.step_num);
		}
	};

	this.animate_til_next_line = function() {
		for (var i=this.step_num; i<anim_array.length; i++) {
			var anim = anim_array[i];
			this.do_command(anim);
			this.step_num++;
			g.slider.go_to_step(this.step_num);
			if (anim[1] === ShowActive) {
				break;
			}
		}
	};

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
	};

	this.stop = function() {
		if (this.state === 'animating' || this.state === 'stopped' || this.state === 'stepping') {
			this.state = 'stopped';
			clearTimeout(this.scheduled_animation);
			this.step_num = 0;
			g.slider.stop_animating();
			this.jump_to_step(0);
		}
	};
	
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
	};

	this.step = function() {
		if (this.state === 'animating' || this.state === 'stepping' || this.state === 'waiting') {
			this.state = 'stepping';
			clearTimeout(this.scheduled_animation);
			this.animate_til_next_line();
		}
	};

	this.jump_to_step = function(n, move_slider) {
		g.jumping = true;
		var state_ind = parseInt(n/this.state_interval);
		var state = this.graph_states[state_ind];

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
								if (g.graphs[g_num].attr("type") == "directed") {
									var arrowhead = e[1];
									var arrowhead_state = state['edge_arrows'][g_num][arrowhead.attr('id')];
									if (arrowhead_state != null) {
										for (var attr in arrowhead_state) {
											var params = {};
											params[attr] = arrowhead_state[attr];
											arrowhead.attr(params);
										}
									}
								}
							} else if (elem_type === 'vertices') {
								var arg = construct_AddVertex_argument_from_state(elem_state[id]);
								elem = AddVertex(arg, elem_state[id]['id'].substring(3,4));
							} else if (elem_type === 'moats') {

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
							} else if (elem_type === 'vertices') {
								DeleteVertex(id);
							} else if (elem_type === 'annotations') {
								delete_vertex_annotation(id);
							} else if (elem_type === 'moats') {
								DeleteMoat(id);
							} else if (elem_type === 'bubbles') {
								DeleteBubbleWithId(id);
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

		if (move_slider !== false) {
			g.slider.go_to_step(n);
		}
		g.jumping = false;
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
			this.step_num = i;
			if (i % this.state_interval === 0) {
				states.push(construct_state(i))
			}
			if (anim_array[i][1] === BlinkEdge || anim_array[i][1] === BlinkVertex) {
				// Skip Blinks
				continue;
			}
			this.do_command(anim_array[i]);
			if (anim_array[i][1] === AddVertex || anim_array[i][1] === AddEdge || anim_array[i][1] === ResizeBubble) {
				// If the graph has potentially changed sizes then record the size to use for the frame
				record_max_graph_size(parseInt(anim_array[i][2].substring(1,2))-1);
			}
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
		this.state_interval = 500; 

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
		var new_x = evt.clientX - self.cursor.transform().globalMatrix.e - parseInt(self.cursor.attr('width'))/2;
		if (new_x < 0) {
			new_x = 0;
		} else if (new_x > self.cursor_max_x) {
			new_x = self.cursor_max_x;
		}

		self.cursor.attr({'x': new_x});
		var step = self.get_step_for_position(new_x / self.step_width);
		g.animation.jump_to_step(step, false);
	}
	this.cursor_mousedown = function(evt) {
		/*	Triggers when cursor is mousedowned.  Begins sliding process by 
			recording initial cursor and mouse positions
		*/
		g.slider.sliding = true;
		g.slider.start_cursor_x = parseInt(g.slider.cursor.attr('x'));
		g.slider.start_mouse_x = parseInt(evt.clientX);
	}
	this.cursor_drag = function(evt) {
		this.cursor_mouseup(evt);
	}
	this.cursor_mousemove = function(evt) {
		/*	This does the actual moving of the cursor.  Using the cursor and mouse positions
			at mousedown event this computes the new position of the cursor, and moves
			the animation to the corresponding step.
		*/
		var self = g.slider;
		var step = 0;
		var new_x = this.start_cursor_x + parseInt(evt.clientX) - self.start_mouse_x;
		if (new_x > this.cursor_max_x) {
			new_x = this.cursor_max_x;
			step = anim_array.length;
		} else if (new_x < this.cursor_min_x) {
			new_x = this.cursor_min_x;
			step = 0;
		} else {
			step = self.get_step_for_position(new_x / self.step_width);
		}
		g.animation.jump_to_step(step, false);
		self.go_to_step(step);
	}
	this.cursor_mouseup = function(evt) {
		/* Ends cursor sliding behavior */
		this.sliding = false;
	}
	this.go_to_step = function(n, time) {
		/* Positions the cursor at the position corresponding to step number n */
		var position = this.slider_positions[n];
		if (time) {
			// var diff = position*this.step_width - parseInt(this.cursor.attr('x'));
			this.cursor.animate({'x': position*this.step_width}, time);
		} else {
			this.cursor.attr({'x': position*this.step_width});
		}
	}
	this.compute_step_width = function() {
		var sum = 0;
		this.slider_positions = [];
		this.position_to_step = {};
		for (var i=0; i<anim_array.length; i++) {
			this.position_to_step[sum] = i;
			this.slider_positions.push(sum);
			sum += anim_array[i][0];
		}
		this.position_to_step[sum] = i;
		this.slider_positions.push(sum);
		this.slider_max_position = this.slider_positions[this.slider_positions.length-1];
		return this.cursor_max_x / sum;
	}
	this.stop_animating = function() {
		g.slider.cursor.stop();
	}
	this.get_step_for_position = function(position) {
		var int_pos = parseInt(position);
		for (;; int_pos += 1) {
			if (int_pos in this.position_to_step) {
				return this.position_to_step[int_pos];
			} else if (int_pos > this.slider_max_position) {
				return this.position_to_step[this.slider_max_position];
			}
		}
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

		// step_width is the width of each time unit as specified in anim_array.  Total time units are the sum of first element of all arrays
		this.step_width = this.compute_step_width()
		// naive_step_width is just the position in anim_array
		this.naive_step_width = this.cursor_max_x / anim_array.length;
		
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
	if (vertex_id in g.blinking_vertices) {
		remove_scheduled_vertex_blinks(vertex_id);
	}
	g.vertices[graph_num_from_id(vertex_id)][vertex_id].attr('fill', color);
}

function UpdateEdgeInfo(edge_id, info) {
	var graph_num = parseInt(edge_id.substring(1,2));
	var tooltip_id = edge_id + '_group_tooltip';
	var tooltip = g.tooltip_objects[tooltip_id];
	if (tooltip != null) {
		tooltip.change_text(info);
	}
}

function UpdateGraphInfo(graph_id, info) {
	var graph_num = parseInt(graph_id.substring(1));
	var graph_info_text_elem = g.graph_infos[graph_num-1];
	graph_info_text_elem.node.innerHTML = info;
}

function UpdateVertexInfo(vertex_id, info) {
	var vertex_group_id = vertex_id + '_group';
	var tooltip_id = vertex_group_id + '_tooltip';
	var tooltip = g.tooltip_objects[tooltip_id];
	if (tooltip != null) {
		tooltip.change_text(info);
	}
}

/** Sets the given edge to the given color.  If the given edge
	is not found, then the reverse direction is tried, e.g. if g1_(5, 4) is
	not found we will try g1_(4, 5)
*/
function SetEdgeColor(edge_id, color) {
	if (edge_id in g.blinking_edges) {
		remove_scheduled_edge_blinks(edge_id);
	}

	var graph_num = graph_num_from_id(edge_id);
	var edge = g.edges[graph_num][edge_id];
	if (edge == null) {
		edge_id = switch_edge_vertices(edge_id);
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
	remove_all_scheduled_vertex_blinks();

	var graph_id_and_color = arguments[0];
	var vertex = arguments[1];
	var split = graph_id_and_color.split('_');
	var g_num = parseInt(graph_id_and_color.substring(1, 2));
	var graph_id = split[0];
	var color = split[1];

	if (!vertex) {
		for (var key in g.vertices[g_num-1]) {
			g.vertices[g_num-1][key].attr({'fill': color});
		}
	} else {
		for (var i=1; i<arguments.length; i++) {
			if (is_multiple_vertices(arguments[i])) {
				// Weighted matching sometimes passes in vertices like (v1, v2, v3...)
				var vertex_nums = get_ints_from_str(arguments[i]);
				for (var v in vertex_nums) {
					g.vertices[g_num-1]['g' + (g_num) + '_' + vertex_nums[v]].attr({'fill': color});
				}
			} else {
				g.vertices[g_num-1]['g' + (g_num) + '_' + arguments[i]].attr({'fill': color});
			}
		}
	}
}


/** Sets all edges of given graph to color.  param is of form: "g1_#dd3333" */
function SetAllEdgesColor(graph_id_and_color) {
	remove_all_scheduled_edge_blinks();
    
    var split = graph_id_and_color.split('_');
    var graph_num = graph_num_from_id(graph_id_and_color);
    var color = split[1];
    var graph_edges = g.edges[graph_num];
    var edge_arrows = g.edge_arrows[graph_num];
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
	if (g.jumping) {
		return;
	}
	/* TODO: Add timeout array in here */
	var vertex = g.vertices[graph_num_from_id(vertex_id)][vertex_id];
    var curr_color = vertex.attr('fill');
    if (color === 'None' || !color) {
    	color = 'black'
    }

    var timeout_arr = [];
    for (var i=0; i<6; i+=2) {
    	timeout_arr.push(setTimeout(function() { vertex.attr({'fill': color}); }, g.animation.step_ms*i*3));
    	timeout_arr.push(setTimeout(function() { vertex.attr({'fill': curr_color}); }, g.animation.step_ms*(i+1)*3));
    }
    timeout_arr.push(
    	setTimeout(function() {
    		delete g.blinking_vertices[vertex_id];
    	}, g.animation.step_ms*16)
    );

    g.blinking_vertices[vertex_id] = timeout_arr;
}

/** Blinks the given edge between black and current color 3 times */
function BlinkEdge(edge_id, color){
	if (g.jumping) {
		return;
	}
	var edge = g.edges[graph_num_from_id(edge_id)][edge_id];
    var curr_color = edge.attr('stroke');
    if (color === 'None' || !color) {
    	color = 'black';
    }

    var timeout_arr = [];
    for (var i=0; i<6; i+=2) {
    	timeout_arr.push(setTimeout(function() { edge.attr({'stroke':  color, 'stroke-width': g.edge_width}); }, g.animation.step_ms*i*3));
	    timeout_arr.push(setTimeout(function() { edge.attr({'stroke': curr_color, 'stroke-width': g.edge_width}); }, g.animation.step_ms*(i+1)*3));
    }
    timeout_arr.push(
    	setTimeout(function(){
    		delete g.blinking_edges[edge_id];
    	}, g.animation.step_ms*16)
    );

    g.blinking_edges[edge_id] = timeout_arr;
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

// Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(vertex_id, annotation, color) {
	if (annotation === "None") {
		return;
	}
	var g_num = vertex_id.substring(1, 2);
	var vertex = g.vertices[g_num-1][vertex_id];
	if (!color) {
		color = 'black';
	}
	var annotation_id = 'va' + vertex_id;
	delete_vertex_annotation(annotation_id);
	var text = snap.text(parseInt(vertex.attr('cx')) + g.vertex_r+1, parseInt(vertex.attr('cy')) + g.vertex_r*1.5 + 2.62, annotation).attr({
		'id': annotation_id,
		'class': 'vertex_annotation',
		'fill': 'black',
		'text-anchor': 'middle',
		'font-weight': 'bold',
		'font-family': 'Helvetica',
		'font-size': 14
	});
	g.graphs[g_num-1].append(text);
	g.annotations[g_num-1][annotation_id] = text;
}

function delete_vertex_annotation(annotation_id) {
	var g_num = annotation_id.substring(3, 4);
	if (annotation_id in g.annotations[g_num-1]) {
		var annot = g.annotations[g_num-1][annotation_id];
		annot.remove()
		delete g.annotations[g_num-1][annotation_id];
	}
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
	var graph_num = parseInt(edge_id.substring(1,2)) - 1;
    var graph_id = edge_id.split("_")[0];
    var vertices = edge_id.split("_")[1].match(/\d+/g);
    var v = g.vertices[graph_num][graph_id + '_' + vertices[0]];
    var w = g.vertices[graph_num][graph_id + '_' + vertices[1]];
    var v_group = g.vertex_groups[graph_num][graph_id + '_' + vertices[0] + '_group'];
    var w_group = g.vertex_groups[graph_num][graph_id + '_' + vertices[1] + '_group'];
    
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
    var group = snap.group().attr({
    	'class': 'edge_group',
    	'id': edge_id + '_group',
    	'cursor': 'pointer'
    });
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
                group.prepend(arrowhead);
                parent_graph.prepend(arrowhead);
            }
            group.prepend(edge);
            parent_graph.prepend(group);
            g.edges[graph_num][edge.attr('id')] = edge;
            g.edge_groups[graph_num][group.attr('id')] = group;
		    if (arrowhead != null) {
		    	g.edge_arrows[graph_num][arrowhead.attr('id')] = arrowhead;
		    }
		    add_tooltip(group, 'edge');
                
            if(reverse_edge.attr("d") == null){
                var reverse_edge_id = reverse_edge.attr('id');
                var arrowhead_id = 'ea' + reverse_edge.attr('id');
                g.edge_arrows[graph_num][arrowhead_id].remove();
                delete g.edge_arrows[graph_num][arrowhead_id];
                g.edges[graph_num][reverse_edge_id].remove();
                delete g.edges[graph_num][reverse_edge_id];
                g.edge_groups[graph_num][reverse_edge_id + '_group'].remove();
                delete g.edge_groups[graph_num][reverse_edge_id + '_group'];
                g.tooltip_objects[reverse_edge_id + '_group_tooltip'].delete_self();
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
            	group.prepend(arrowhead);
            }
            group.prepend(edge);
            parent_graph.prepend(group);
            g.edges[graph_num][edge.attr('id')] = edge;
            g.edge_groups[graph_num][group.attr('id')] = group;
			if (arrowhead != null) {
				g.edge_arrows[graph_num][arrowhead.attr('id')] = arrowhead;
			}
			add_tooltip(group, 'edge');
        }
    }else{ 
    	//Undirected edge
    	edge = snap.line(vx, vy, wx, wy).attr({
    		'id': edge_id,
    		'stroke': g.edge_color,
    		'stroke-width': g.edge_width,
    		'class': 'edge'
    	});
    	group.prepend(edge);
    	parent_graph.prepend(group);
    	g.edges[graph_num][edge.attr('id')] = edge;
    	g.edge_groups[graph_num][group.attr('id')] = group;
    	add_tooltip(group, 'edge');
    }
    group.insertBefore(g.pre_vertex[graph_num]);

    return [edge, arrowhead];
}

//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id) {
	var graph_num = graph_num_from_id(edge_id);
	var graph_id = edge_id.substring(0,2);
	var vertices = edge_id.split("_")[1].match(/\d+/g);
	g.edges[graph_num][edge_id].remove();
	delete g.edges[graph_num][edge_id];
	g.edge_groups[graph_num][edge_id + '_group'].remove();
	delete g.edge_groups[graph_num][edge_id + '_group'];
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
	var tooltip = g.tooltip_objects[edge_id + '_group_tooltip'];
	tooltip.delete_self();	
}

//Adds vertex of into specified graph and coordinates in graph
function AddVertex(graph_and_coordinates, vertex_num) {
	var graph_num = graph_and_coordinates.substring(1, 2);
	var coords = graph_and_coordinates.split("(")[1].match(/[\d\.]+/g);
	var x = parseFloat(coords[0]) - g.coord_changes[graph_num-1].x,
		y = parseFloat(coords[1]) - g.coord_changes[graph_num-1].y;
	
	var vertex_id = 'g' + graph_num + '_' + vertex_num;
	var group_id = vertex_id + '_group';
	var group = snap.group().attr({
		'id': group_id,
		'cursor': 'pointer'
	});
	g.vertex_groups[graph_num-1][group_id] = group;
	var vertex = snap.circle(x, y, g.vertex_r).attr({
		'id': vertex_id,
		'class': 'vertex',
		'fill': '#808080',
		'style': 'filter: url(#dropshadow)',
		'cursor': 'pointer'
	});
	g.vertices[graph_num-1][vertex_id] = vertex;
	//g.graphs[graph_num-1].append(vertex);
	group.append(vertex);

	// TODO: compute the 4.62, don't just use a constant
	var vertex_label = snap.text(x, y+4.62, vertex_num).attr({
		'id': 'vl' + vertex_id,
		'text-anchor': 'middle',
		'fill': 'white',
		'font-family': 'Helvetica',
		'font-size': 14.0,
		'font-weight': 'bold'
	});
	group.append(vertex_label);
	//g.graphs[graph_num-1].append(vertex_label);
	g.graphs[graph_num-1].append(group);
	add_tooltip(group, 'vertex');

	return vertex;
}

function DeleteVertex(vertex_id) {
	var g_num = parseInt(vertex_id.substring(1,2));
	var group_id = vertex_id + '_group';
	var vertex = g.vertices[g_num-1][vertex_id];
	var group = g.vertex_groups[g_num-1][group_id];
	group.remove()
	var vertex_label = snap.select('#vl' + vertex_id);
	vertex.remove()
	if (vertex_label) {
		vertex_label.remove()
	}
	delete_vertex_annotation('va' + vertex_id);
	delete g.vertices[g_num-1][vertex_id];
	delete g.vertex_groups[g_num-1][group_id];
}

function CreateMoat(moat_id, radius, color) {
	radius = parseFloat(radius);
	var g_num = parseInt(moat_id.substring(1,2));
	var v_num = get_vertex_num(moat_id);
	var vertex = g.vertices[g_num-1][get_vertex_id(g_num, v_num)];
	if (!radius) {
		radius = g.vertex_r;
	}
	var moat = snap.circle(vertex.attr('cx'), vertex.attr('cy'), radius).attr({
		'id': moat_id,
		'class': 'moats',
		'fill': color
	});
	g.moats[g_num-1][moat_id] = moat;
	g.graphs[g_num-1].prepend(moat);
}

function GrowMoat(moat_id, radius) {
	radius = parseFloat(radius);
	var g_num = parseInt(moat_id.substring(1,2));
	var moat = g.moats[g_num-1][moat_id];
	if (!g.jumping) {
		moat.animate({'r': radius}, g.moat_growing_time*g.animation.step_ms);
	} else {
		moat.attr({'r': radius});
	}
}

function DeleteMoat(moat_id) {
	var g_num = parseInt(moat_id.substring(1,2));
	var moat = g.moats[g_num-1][moat_id];
	delete g.moats[g_num-1][moat_id];
	moat.remove();
}

function CreateBubble(which_graph, vertex_nums_str, offset_values_str, color) {
	// which_graph: string of form g1_() or g2_()
	// vertex_nums_str: python list as string "[v1, v2, v3...]" that contains all of the vertices for this bubble
	// offset_values: python list as string "[v1_offset, v2_offset, ...]"
	var vertex_nums = get_ints_from_str(vertex_nums_str);
	var offset_values = get_floats_from_str(offset_values_str);
	var g_num = parseInt(which_graph.substring(1,2));
	for (var i=0; i<vertex_nums.length; i++) {
		var vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[i])];
		var bubble_id = get_bubble_id(vertex, vertex_nums);
		var bubble = snap.circle(vertex.attr('cx'), vertex.attr('cy'), 0).attr({
			'id': bubble_id,
			'class': 'bubbles',
			'fill': color
		});
		g.bubbles[g_num-1][bubble_id] = bubble;
		g.bubble_offsets[g_num-1][bubble_id] = offset_values[i];
		g.graphs[g_num-1].prepend(bubble);
	}
}

function ResizeBubble(which_graph, vertex_nums_str, new_radius) {
	var vertex_nums = get_ints_from_str(vertex_nums_str);
	var g_num = parseInt(which_graph.substring(1,2));
	for (var i=0; i<vertex_nums.length; i++) {
		var vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[i])];
		var bubble_id = get_bubble_id(vertex, vertex_nums);
		var bubble = g.bubbles[g_num-1][bubble_id];
		var our_radius = parseInt(new_radius) + parseInt(Math.floor(g.bubble_offsets[g_num-1][bubble_id]));
		if (!g.jumping) {
			bubble.animate({'r': our_radius}, g.bubble_resize_time);
		} else {
			bubble.attr('r', our_radius);
		}
	}
}

function DeleteBubble(which_graph, vertex_nums_str) {
	var vertex_nums = get_ints_from_str(vertex_nums_str);
	var g_num = parseInt(which_graph.substring(1,2));
	for (var i=0; i<vertex_nums.length; i++) {
		var vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[i])];
		var bubble_id = get_bubble_id(vertex, vertex_nums);
		var bubble = g.bubbles[g_num-1][bubble_id];
		delete g.bubbles[g_num-1][bubble_id];
		bubble.remove();
	}
}

function DeleteBubbleWithId(bubble_id) {
	var g_num = parseInt(bubble_id.substring(1,2));
	var bubble = g.bubbles[g_num-1][bubble_id];
	bubble.remove()
	delete g.bubbles[g_num-1][bubble_id];
}

function Wait(t) {

}