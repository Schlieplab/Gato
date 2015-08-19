/*
	Copyright 2014 Scott Merkling
    This file is part of WebGato.

    WebGato is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    WebGato is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with WebGato.  If not, see <http://www.gnu.org/licenses/>.
*/
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
			g.bubble_resize_time = get_moat_growing_time(this.step_num)*this.step_ms;
		}

		if (anim.length === 3) {
			anim[1](anim[2]);
		} else if (anim.length === 4) {
			anim[1](anim[2], anim[3]);
		} else {
			anim[1].apply(this, anim.slice(2));
		}
	};
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
			var curr_time = new Date().getTime();
			var runtime_ms = curr_time - this.start_time;	// The time the animation has been running in ms
			var offset = this.anim_schedule[this.start_at_step];
			var next_anim_time = this.anim_schedule[this.step_num] - runtime_ms - offset; 	// The offset in ms of the next animation command
			if (next_anim_time < 0) {
				if (!this.immediate_calls) {
					this.immediate_calls = 0;
				}
				this.immediate_calls += 1;
				g.slider.go_to_step(this.step_num);
				this.animator();
			} else {
				g.slider.go_to_step(this.step_num, next_anim_time);
				var self = this;
				this.scheduled_animation = setTimeout(function() {self.animator()}, next_anim_time);
			}
		}
	};

	this.compute_animation_schedules = function() {
		/*  Computes an array anim_schedule of the same length as anim_array
			where each item is the time which the corresponding command in 
			anim_array should be executed
		*/

		this.anim_schedules = {};
		var button_types = g.control_panel.speed_controls.button_types;
		for (var key in button_types) {
			var anim_schedule = [];
			var step_ms = button_types[key]['speed'];
			var curr_time = 0;
			for (var i=0; i<anim_array.length; i++) {
				anim_schedule.push(curr_time);
				curr_time += anim_array[i][0]*step_ms;
			}
			this.anim_schedules[step_ms] = anim_schedule;
		}
		this.anim_schedule = this.anim_schedules[this.step_ms];
	};

	this.change_speed = function(step_ms) {
		this.step_ms = step_ms;
		this.anim_schedule = this.anim_schedules[this.step_ms];
		this.start_at_step = this.step_num;
		this.start_time = new Date().getTime();
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
		this.start_time = new Date();
		if (this.state === 'stopped' || this.state === 'done') {
			if (this.state === 'done' && g.animation.step_num === anim_array.length) {
				// If we are done and the user hasn't moved the anim-slider then reset the animation
				this.jump_to_step(0);
			}

			this.state = 'animating';
			this.start_time = new Date().getTime();
			this.start_at_step = this.step_num;
			this.animator(this.step_num);
		}
	};

	this.stop = function() {
		if (this.state === 'animating' || this.state === 'stopped' || this.state === 'stepping' || this.state === 'waiting') {
			this.state = 'stopped';
			clearTimeout(this.scheduled_animation);
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
			g.slider.go_to_step(this.step_num);
		}
		this.state = 'animating';
		this.start_time = new Date().getTime();
		this.start_at_step = this.step_num;
		this.animator(this.step_num);
	};

	this.step = function() {
		if (this.state === 'animating' || this.state === 'stepping' || this.state === 'waiting') {
			this.state = 'stepping';
			clearTimeout(this.scheduled_animation);
			this.animate_til_next_line();
		}
	};

	this.jump_to_closest_state = function(n) {
		if (!g.jump_ready) {
			return;
		}
		var rem = n % this.state_interval;
		var new_state_ind;
		if (rem >= this.state_interval/2) {
			// Go to next state_interval
			var max_state_ind = parseInt(anim_array.length / this.state_interval);
			new_state_ind = Math.min(max_state_ind, parseInt((n + this.state_interval)/this.state_interval));
		} else {
			new_state_ind = parseInt(n / this.state_interval);
		}
		return this.jump_to_step(new_state_ind*this.state_interval, false);
	};

	this.jump_to_step = function(n, move_slider) {
		/* Tried to jump to given step_number.  Returns true/false whether jump was performe dor not */
		if (!g.jump_ready) {
			return false;
		}
		if (n === this.step_num) {
			return false;
		}
		g.jumping = true;
		var curr_state_ind = parseInt(this.step_num/this.state_interval);
		var new_state_ind = parseInt(n/this.state_interval);
		var state = this.graph_states[new_state_ind];

		// TODO: Test to see whether it is faster to jump 500 then animate 500 vs animation 1000
		if (n > this.step_num && n - this.step_num < this.state_interval) {
			// If we are animating return between now and next state then just animate until, don't go to any state
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
								elem = AddVertex(arg, elem_state[id]['id'].substring(3));
							} else if (elem_type === 'moats') {
								elem = CreateMoatWithId(id);
							} else if (elem_type === 'highlighted_paths') {
								// If vertex state hasn't been restored yet then this function will likely bomb, as the vertices it 
								// depends on for coordinates may not be on the graph
								elem = CreateHighlightedPathWithId(id, elem_state[id]['closed']);
							} else if (elem_type === 'bubbles') {
								elem = CreateBubbleWithId(id, elem_state[id]['offset']);
							} else if (elem_type === 'annotations') {
								elem = CreateVertexAnnotationWithId(id, elem_state[id]['text_content']);
							}
						}

						if (elem_type === 'annotations') {
							elem.node.textContent = elem_state[id]['text_content'];
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
							} else if (elem_type === 'highlighted_paths') {
								DeleteHighlightedPath(id);
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
				g.graph_infos[i].node.textContent = infos[i];
			}

			this.step_num = state.step_num;
			this.animate_until(n);
		}
		this.start_at_step = this.step_num;

		if (move_slider !== false) {
			g.slider.go_to_step(n);
		}
		g.jumping = false;

		g.jump_ready = false;
		setTimeout(function() {
			g.jump_ready = true;
		}, g.jump_interval);

		this.start_time = new Date().getTime();
		return true;
	};

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
				infos.push(g.graph_infos[i].node.textContent);
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
			if (i % this.state_interval === 0 || i == anim_array.length - 1) {
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
			} else if (anim_array[i][1] === UpdateGraphInfo) {
				record_max_container_size(parseInt(anim_array[i][2].substring(1,2))-1);
			}
		}

		this.graph_states = states;

		try {
			localStorage.setItem(this.storage_key_name, JSON.stringify(this.graph_states));
			localStorage.setItem(this.max_size_storage_key_name, JSON.stringify(g.max_graph_sizes));
			localStorage.setItem(this.max_size_storage_key_name+'frame', JSON.stringify(g.max_container_sizes));
		} catch(e) {
			if(e.code == 22) {
				// If we have a quota exceeded error then skip writing
				console.log("Local storage is full, skipping storage.");
				localStorage.removeItem(this.storage_key_name);
				localStorage.removeItem(this.max_size_storage_key_name);
				localStorage.removeItem(this.max_size_storage_key_name+'frame');
			}
		}

		this.jump_to_step(0);
	};

	this.retrieve_graph_states = function() {
		var states = localStorage.getItem(this.storage_key_name);
		var graph_sizes = localStorage.getItem(this.max_size_storage_key_name);
		var container_sizes = localStorage.getItem(this.max_size_storage_key_name+'frame');
		if (states && graph_sizes && container_sizes) {
			this.graph_states = JSON.parse(states);
			g.max_graph_sizes = JSON.parse(graph_sizes);
			g.max_container_sizes = JSON.parse(container_sizes);
		} else {
			this.graph_states = null;
		}
	};

	this.initialize_variables = function() {
		// State of animation		
		this.states = ['animating', 'stopped', 'stepping', 'waiting', 'done'];
		this.state = 'stopped';

		this.storage_key_name = animation_name + '_graph_states';
		this.max_size_storage_key_name = animation_name + '_max_sizes';
		
		// Our step interval in milliseconds
		this.step_ms = g.speeds['4x'];
		this.start_at_step = 0;

		// Current step in the animation
		this.step_num = 0;

		// How many steps we take between each saved graph state
		this.state_interval = Math.min(1000, parseInt(anim_array.length / 32)); 

		// Try to retrieve the graph states from local storage before constructing them anew
		this.retrieve_graph_states();
		if (!this.graph_states) {
			this.construct_graph_states();
		}
		this.compute_animation_schedules();

		g.jumping = false;	// We're done building graph state, so set this to false
	};
	this.initialize_variables();
}

function Slider(width, height) {
	this.track_click = function(evt) {
		/*	Triggers when the slider track is clicked.  Moves the cursor to the position of the
			mouse cursor on the track, and jumps to the corresponding step in animation
		*/
		var clientX = evt.clientX;
		if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
			clientX = evt.changedTouches[0].clientX;
		}
		var self = g.slider;
		var new_x = clientX - self.cursor.transform().globalMatrix.e - parseInt(self.cursor.attr('width'))/2;

		if (new_x < 0) {
			new_x = 0;
		} else if (new_x > self.cursor_max_x) {
			new_x = self.cursor_max_x;
		}
		self.cursor.attr({'x': new_x});
		var step = self.get_step_for_position(new_x / self.step_width);
		g.animation.jump_to_step(step, false);
	};
	this.cursor_mousedown = function(evt) {
		/*	Triggers when cursor is mousedowned.  Begins sliding process by 
			recording initial cursor and mouse positions
		*/
		var clientX = evt.clientX;
		if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
			clientX = evt.changedTouches[0].clientX;
		}
		g.slider.sliding = true;
		g.slider.start_cursor_x = parseInt(g.slider.cursor.attr('x'));
		g.slider.start_mouse_x = parseInt(clientX);
	};
	this.cursor_drag = function(evt) {
		this.cursor_mouseup(evt);
	};
	this.cursor_mousemove = function(evt) {
		/*	This does the actual moving of the cursor.  Using the cursor and mouse positions
			at mousedown event this computes the new position of the cursor, and moves
			the animation to the corresponding step.
		*/
		var clientX = parseInt(evt.clientX);
		if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
			clientX = parseInt(evt.changedTouches[0].clientX);
		}
		var self = g.slider;
		var step = 0;
		var new_x = this.start_cursor_x + clientX - self.start_mouse_x;
		if (new_x > this.cursor_max_x) {
			new_x = this.cursor_max_x;
			step = anim_array.length;
		} else if (new_x < this.cursor_min_x) {
			new_x = this.cursor_min_x;
			step = 0;
		} else {
			step = self.get_step_for_position(new_x / self.step_width);
		}
		// g.animation.jump_to_step(step, false);
		var jumped = g.animation.jump_to_closest_state(step);
		self.go_to_step(step);
	};
	this.cursor_mouseup = function(evt) {
		/* Ends cursor sliding behavior */
		var clientX = parseInt(evt.clientX);
		if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
			clientX = parseInt(evt.changedTouches[0].clientX);
		}
		var self = g.slider;
		var step = 0;
		var new_x = this.start_cursor_x + clientX - self.start_mouse_x;
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
		this.sliding = false;
	};
	this.go_to_step = function(n, time) {
		/* Positions the cursor at the position corresponding to step number n */
		var position = this.slider_positions[n];
		var x = position*this.step_width;
		if (time) {
			this.cursor.animate({'x': x}, time);
		} else {
			this.cursor.stop();
			this.cursor.attr({'x': x});
		}
		this.cursor_click_receiver.attr({'x': x-this.cursor_extra_click_width/2.0});
	};
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
	};
	this.stop_animating = function() {
		g.slider.cursor.stop();
	};
	this.get_step_for_position = function(position) {
		var int_pos = parseInt(position);
		for (;; int_pos += 1) {
			if (int_pos in this.position_to_step) {
				return this.position_to_step[int_pos];
			} else if (int_pos > this.slider_max_position) {
				return this.position_to_step[this.slider_max_position];
			}
		}
	};
	this.resize_width = function(new_width) {
		/* 	This function resizes the slider.  It does this
			in the GUI as well as computing new mappings of pos->coord and coord-> pos
		*/
		this.width = new_width;
		this.track_width = this.width;
		this.track.attr({'width': this.width});
		this.track_click_receiver.attr({'width': this.width});
		this.cursor_max_x = this.width - this.cursor_width;
		this.step_width = this.compute_step_width()
		this.naive_step_width = this.cursor_max_x / anim_array.length;
		this.go_to_step(g.animation.step_num, 0);
	};

	this.init = function () {
		this.min_width = 50;
		this.sliding = false;
		this.width = width;
		this.height = height;
		this.g = snap.group();
		this.slider_positions = [];
		this.position_to_step = {};

		// Construct the slider track
		this.track_width = this.width;
		this.track_height = 10;
		this.track_y = this.height/2-this.track_height/2;
		this.track = snap.rect(0, this.track_y, this.width, this.track_height, 2, 2).attr({
			'id': 'slider_track',
			'fill': '#AAA',
			'cursor': 'pointer'
		})
		.click(this.track_click)
		.touchstart(this.track_click);

		this.track_click_receiver = snap.rect(0, -10, this.width, this.height+20).attr({
			'id': 'slider_track_click_receiver',
			'opacity': 0
		})
		.click(this.track_click)
		.touchstart(this.track_click);
		this.g.append(this.track_click_receiver);
		this.g.append(this.track);

		// Construct the cursor
		this.cursor_height = this.height;
		this.cursor_width = 10;
		this.cursor = snap.rect(0, 0, this.cursor_width, this.cursor_height, 6, 6).attr({
			'id': 'slider_cursor',
			'fill': '#eee',
			'stroke': '#111',
			'stroke-width': 1,
			'cursor': 'pointer'
		}).mousedown(this.cursor_mousedown);
		
		this.cursor_extra_click_width = 40;
		this.cursor_extra_click_height = 20;
		this.cursor_click_receiver = snap.rect(this.cursor_extra_click_width/2.0*-1, 
			this.cursor_extra_click_height*-1/2.0, 
			this.cursor_width+this.cursor_extra_click_width, 
			this.cursor_height+this.cursor_extra_click_height
		).attr({
			'id': 'slider_cursor_click_receiver',
			'opacity': 0
		}).mousedown(this.cursor_mousedown);

		this.cursor_max_x = this.width - this.cursor_width;
		this.cursor_min_x = 0;

		// step_width is the width of each time unit as specified in anim_array.  Total time units are the sum of first element of all arrays
		this.step_width = this.compute_step_width()
		// naive_step_width is just the position in anim_array
		this.naive_step_width = this.cursor_max_x / anim_array.length;
		
		this.g.append(this.cursor_click_receiver);
		this.g.append(this.cursor);
	};
	
	this.init();
}


/**
*
*	Graph Modifying Functions
*
*/

function SetVertexColor(vertex_id, color) {
	// Sets the vertex given by vertex_id to color
	if (vertex_id in g.blinking_vertices) {
		remove_scheduled_vertex_blinks(vertex_id);
	}
	g.vertices[graph_num_from_id(vertex_id)][vertex_id].attr('fill', color);
}

function UpdateEdgeInfo(edge_id, info) {
	// Updates the tooltip text corresponding to the edge given by edge_id with the string "info"
	var graph_num = parseInt(edge_id.substring(1,2));
	var tooltip_id = edge_id + '_group_tooltip';
	var tooltip = g.tooltip_objects[tooltip_id];
	if (tooltip != null) {
		tooltip.change_text(info);
	}
}

function UpdateGraphInfo(graph_id, info) {
	// Updates the graph info for the given graph with the string "info"
	var graph_num = parseInt(graph_id.substring(1));
	var graph_info_text_elem = g.graph_infos[graph_num-1];
	graph_info_text_elem.node.textContent = info;
}

function UpdateVertexInfo(vertex_id, info) {
	// Updates the vertex info tooltip for the given vertex with the string "info"
	var vertex_group_id = vertex_id + '_group';
	var tooltip_id = vertex_group_id + '_tooltip';
	var tooltip = g.tooltip_objects[tooltip_id];
	if (tooltip != null) {
		tooltip.change_text(info);
	}
}

function SetEdgeColor(edge_id, color) {
	/** Sets the given edge to the given color.  If the given edge
		is not found, then the reverse direction is tried, e.g. if g1_(5, 4) is
		not found we will try g1_(4, 5).
		If there are any scheduled edge blinks for this edge then we will remove those scheduled blinks.
	*/
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

function SetAllVerticesColor() {
	/** Sets color of all vertices of a given graph to a given color.
	 	First argument is always graph_id_and_color: string of form "g{graph_num}_#{hex_color}"
	 	Optional argument afterwards is a string of vertices like "1,2,3,4"
	 	Sometimes though(see WeightedMatching algorithms) the vertices are passed in like 
	 	SetAllVerticesColor(arg_1, v1, v2, v3, v4, ...).  We account for all forms of arguments
	*/
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


function SetAllEdgesColor(graph_id_and_color) {
	// Sets all edges of given graph to color.  param is of form: "g1_#dd3333"
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


function BlinkVertex(vertex_id, color) {
	// Blinks the given vertex between black and current color 3 times
	// Adds an array of blink animations to g.blinking_vertices, and adds a task to delete those animations
	// from g.blinking_vertices when they are completed
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

function BlinkEdge(edge_id, color){
	// Blinks the given edge between black and current color 3 times
	// Adds an array of blink animations to g.blinking_edges, and adds a task to delete those animations
	// from g.blinking_edges when they are completed
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

function SetVertexFrameWidth(vertex_id, val) {
	/* Sets the stroke-width of a vertex */
    var vertex = g.vertices[graph_num_from_id(vertex_id)][vertex_id];
    var stroke_color = '';
	if (val !== '0') {
		stroke_color = vertex.attr('stroke');
        vertex.attr({"style": ""});
	}
	if (!stroke_color || stroke_color === 'none') {
		stroke_color = 'black';
	}
    vertex.attr({'stroke-width': val, 'stroke': stroke_color});

    // Add back in dropshadow
    if (val === "0") {
        vertex.attr({"style": "filter:url(#dropshadow)"});
    }
}

function SetVertexAnnotation(vertex_id, annotation, color) {
	// Sets annotation of vertex vertex_id to annotation.  Annotation's color is optionally specified
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
		'font-size': 14,
		'text_content': annotation
	});
	g.graphs[g_num-1].append(text);
	g.annotations[g_num-1][annotation_id] = text;
}

function CreateVertexAnnotationWithId(annotation_id, annotation) {
	var vertex_id = annotation_id.substring(2);
	var g_num = parseInt(annotation_id.substring(3,4));
	var vertex = g.vertices[g_num-1][vertex_id];
	delete_vertex_annotation(annotation_id);
	var text = snap.text(parseInt(vertex.attr('cx')) + g.vertex_r+1, parseInt(vertex.attr('cy')) + g.vertex_r*1.5 + 2.62, annotation).attr({
		'id': annotation_id,
		'class': 'vertex_annotation',
		'fill': 'black',
		'text-anchor': 'middle',
		'font-weight': 'bold',
		'font-family': 'Helvetica',
		'font-size': 14,
		'text_content': annotation
	});
	g.graphs[g_num-1].append(text);
	g.annotations[g_num-1][annotation_id] = text;
	return text;
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
	if (tooltip) {
		tooltip.delete_self();	
	}
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
	var tooltip = g.tooltip_objects[group_id + '_tooltip'];
	if (tooltip) {
		tooltip.delete_self();
	}
	delete_vertex_annotation('va' + vertex_id);
	delete g.vertices[g_num-1][vertex_id];
	delete g.vertex_groups[g_num-1][group_id];
}

function init_moats() {
	var initial_moats = [g1_init_moats, g2_init_moats];
	for (var i=0; i<2; i++) {
		var curr_moats = initial_moats[i];
		for (var key in curr_moats) {
			CreateMoat(key, curr_moats[key][0], curr_moats[key][1]);
		}
	}
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

function CreateMoatWithId(moat_id) {
	var g_num = parseInt(moat_id.substring(1,2));
	var moat = snap.circle(0, 0, 0).attr({
		'id': moat_id,
		'class': 'moats'
	});
	g.moats[g_num-1][moat_id] = moat;
	g.graphs[g_num-1].prepend(moat);
	return moat;
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

function init_bubbles() {
	var initial_bubbles = [g1_init_bubbles, g2_init_bubbles];
	for (var i=0; i<2; i++) {
		var curr_bubbles = initial_bubbles[i];
		var graph = "g" + (i+1) + "_()";
		for (var key in curr_bubbles) {
			CreateBubble(graph, key, curr_bubbles[key][0], curr_bubbles[key][1]);
		}
	}
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
			'fill': color,
			'offset': offset_values[i]
		});
		g.bubbles[g_num-1][bubble_id] = bubble;
		g.bubble_offsets[g_num-1][bubble_id] = offset_values[i];
		g.graphs[g_num-1].prepend(bubble);
	}
}

function CreateBubbleWithId(bubble_id, offset_value) {
	var g_num = parseInt(bubble_id.substring(1, 2));
	var sp = bubble_id.split('_bubble_');
	var vertex_id = sp[0];
	var vertex_nums = sp[1].split('-');
	var vertex = g.vertices[g_num-1][vertex_id];
	var bubble = snap.circle(vertex.attr('cx'), vertex.attr('cy'), 0).attr({
		'id': bubble_id,
		'class': 'bubbles'
	});
	g.bubbles[g_num-1][bubble_id] = bubble;
	g.bubble_offsets[g_num-1][bubble_id] = offset_value;
	g.graphs[g_num-1].prepend(bubble);
	return bubble;
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

function HighlightPath(graph_and_path, color, closed) {
	// graph_and_path example: g1_[17, 10, 3, 4].
	// if closed != 0 then we make a line back to the first item in path
	var g_num, 
		vertex_nums, 
		coords, 
		vertex, 
		path_id, 
		existing_path,
		path_str, 
		path;

	g_num = parseInt(graph_and_path.substring(1,2));
	vertex_nums = get_ints_from_str(graph_and_path.split('_')[1]);

	coords = [];	// Holds 2-tuples of coordinates
	for (var i=0; i<vertex_nums.length; i++) {
		vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[i])];
		coords.push([vertex.attr('cx'), vertex.attr('cy')]);
	}
	if (closed !== "0") {	
		vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[0])];
		coords.push([vertex.attr('cx'), vertex.attr('cy')]);
	}

	path_id = 'g' + g_num + '_' + vertex_nums.join('-') + '_highlighted_path';
	// Check for existing path with this same id
	existing_path = g.highlighted_paths[g_num-1][path_id];
	if (existing_path) {
		DeleteHighlightedPath(path_id);
	}

	path_str = 'M' + coords[0][0] + ',' + coords[0][1];
	for (var i=1; i<coords.length; i++) {
		path_str += 'L' + coords[i][0] + ',' + coords[i][1];
	}
	path = snap.path(path_str).attr({
		'id': path_id,
		'stroke': color,
		'stroke-width': 16,
		'fill': 'none',
		'closed': closed
	});
	g.graphs[g_num-1].prepend(path);
	g.highlighted_paths[g_num-1][path_id] = path;
}

function CreateHighlightedPathWithId(id, closed) {
	var g_num = parseInt(id.substring(1,2));
	var vertex_nums = get_ints_from_str(id.split('_')[1]);

	var coords = [];	// Holds 2-tuples of coordinates
	for (var i=0; i<vertex_nums.length; i++) {
		var vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[i])];
		coords.push([vertex.attr('cx'), vertex.attr('cy')]);
	}
	if (closed !== "0") {	
		var vertex = g.vertices[g_num-1][get_vertex_id(g_num, vertex_nums[0])];
		coords.push([vertex.attr('cx'), vertex.attr('cy')]);
	}

	var path_str = 'M' + coords[0][0] + ',' + coords[0][1];
	for (var i=1; i<coords.length; i++) {
		path_str += 'L' + coords[i][0] + ',' + coords[i][1];
	}
	var path = snap.path(path_str).attr({
		'id': id,
		'stroke-width': 16,
		'fill': 'none',
		'closed': closed
	});
	g.graphs[g_num-1].prepend(path);
	g.highlighted_paths[g_num-1][id] = path;
	return path;
}

function DeleteHighlightedPath(path_id) {
	var g_num = parseInt(path_id.substring(1,2));
	var path = g.highlighted_paths[g_num-1][path_id];
	path.remove();
	delete g.highlighted_paths[g_num-1][path_id];
}

function HidePath(graph_and_path) {
	/* Takes in a path_id in desktop form and deletes the path it corresponds to */
	var g_num = parseInt(graph_and_path.substring(1,2));
	var vertex_nums = get_ints_from_str(graph_and_path.split('_')[1]);
	path_id = 'g' + g_num + '_' + vertex_nums.join('-') + '_highlighted_path';
	var path = g.highlighted_paths[g_num-1][path_id];
	if (path) {
		path.remove();
	}
	delete g.highlighted_paths[g_num-1][path_id];
}