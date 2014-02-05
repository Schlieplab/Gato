function Scaler() {
	this.set_max_and_min_dimensions_of_graph_container = function () {
		var bbox = g.graph_containers[0].getBBox();
		var playback_bbox = g.playback_bar.g.getBBox();
		var max_height = playback_bbox.y - g.padding - bbox.y;
		var max_width = g.cont_width - g.padding - bbox.x;
		var max_scale_factor_y = max_height / bbox.height;
		var max_scale_factor_x = max_width / bbox.width;
		this.max_scale_factor = Math.min(max_scale_factor_x, max_scale_factor_y);
		this.min_scale_factor = .3;
		console.log('Max: ' + this.max_scale_factor);
		console.log('Min: ' + this.min_scale_factor)
	}
	this.mousedown = function(evt) {
		g.scaler.scaling = true;
		var bbox = g.g1_container.getBBox();
		g.scaler.start_width = bbox.width;
		g.scaler.start_mouse = {'x': parseInt(evt.x), 'y': parseInt(evt.y)};
	}
	this.drag = function(evt) {
		this.mouseup(evt);
	}
	this.mouseup = function(evt) {
		g.scaler.scaling = false;
	}
	this.mousemove = function(evt) {
		this.do_scale(evt);
	}
	this.do_scale = function(evt) {
		var dx = parseInt(evt.x) - g.scaler.start_mouse.x;
		var new_width = g.scaler.start_width + dx;
		var scale_factor = new_width / g.initial_graph_width;
		if (scale_factor > this.max_scale_factor) {
			scale_factor = this.max_scale_factor;
		} else if (scale_factor < this.min_scale_factor) {
			scale_factor = this.min_scale_factor;
		}
		g.scaler.curr_scale = scale_factor;
		g.g1_scale = 's' + g.scaler.curr_scale + ',0,0';
		var trans = 't' + g.g1_container_translate[0] + ',' + g.g1_container_translate[1] + g.g1_scale;
		g.g1_container.transform(trans);
	}

	var bbox = g.graph_containers[0].getBBox();
	this.scaling = false;
	this.curr_scale = 1;
	this.width = 10;
	this.height = 10;
	this.x = bbox.width - this.width;
	this.y = bbox.height + g.frame_padding - this.height;
	this.set_max_and_min_dimensions_of_graph_container();

	this.elem = snap.polygon([this.x, this.y, this.x+this.width, this.y, this.x+this.width, this.y-this.height, this.x, this.y]).attr({
		'fill': '#000',
		'stroke': '#000',
		'cursor': 'move'
	}).mousedown(this.mousedown);
}

function add_scaler() {
	g.scaler = new Scaler();
	g.graph_containers[1].append(g.scaler.elem);
}

function add_graph_frame() {
	g.graph_containers[0].append(g.graphs[0]);
	g.graph_containers[1].append(g.graphs[1]);

	for (var i=0; i<g.num_graphs; i++) {
		var graph_bbox = g.graphs[i].getBBox();
		var pad = g.vertex_r + g.frame_padding;
		var frame = snap.rect(0, 0, graph_bbox.width+pad, graph_bbox.height+pad).attr({
			fill: '#fff',
			stroke: '#ccc',
			strokeWidth: g.graph_frame_stroke_width,
			strokeDasharray: '5,2',
		});
		
		g.graph_containers[i].prepend(frame);
	}
}

function position_graph() {
	/*
		LEFT OFF HERE TRYING TO POSITION THE GRAPHS
	*/
	var x_trans = g.code_box.width + g.padding*2;
	g.container_translate = [{x: x_trans}, {x: x_trans}];
	g.graph_translate = [{x: g.frame_padding + g.vertex_r, y: g.frame_padding + g.vertex_r},
		{x: g.frame_padding + g.vertex_r, y: g.frame_padding + g.vertex_r}];
	for (var i=0; i<g.num_graphs; i++) {
		var this_translate = g.container_translate[i];
		if (i === 0) {
			this_translate.y = g.padding + g.graph_frame_stroke_width;
		} else {
			this_translate.y = g.container_translate[0].y + g.graph_containers[0].getBBox().height;
		}
		var this_container = g.graph_containers[i];
		var this_graph = g.graphs[i];
		this_container.transform('t' + this_translate.x + ',' + this_translate.y);
		this_graph.transform('t' + g.graph_translate[i]['x'] + ',' + g.graph_translate[i]['y']);	
	}
}


function PlaybackBar() {
	this.g = snap.group();
	this.width = g.cont_width * 3/4 - g.padding*2;
	this.height = 40;
	this.padding_y = 5;
	this.padding_x = 15;
	this.bg_color = '#676767';
	this.stroke = '#222';
	this.stroke_width = 2;

	this.frame = snap.rect(0, 0, this.width, this.height, 5, 5).attr({
		'fill': this.bg_color,
		'stroke': this.stroke,
		'stroke-width': this.stroke_width,
	});
	this.g.append(this.frame);

	g.button_panel = new ButtonPanel();
	g.button_panel.g.transform('t' + this.padding_x + ',' + this.padding_y);
	this.g.append(g.button_panel.g);

	// Implement me
	// g.control_panel = new ControlPanel();
	g.control_panel = {'width': 100}

	this.slider_width = this.width - this.padding_x*4 - g.button_panel.width - g.control_panel.width;
	this.slider_height = this.height - this.padding_y*2;
	g.slider = new Slider(this.slider_width, this.slider_height);
	var slider_x_trans = g.button_panel.width + this.padding_x*2;
	g.slider.g.transform('t' + slider_x_trans + ',' + this.padding_y)
	this.g.append(g.slider.g);

	this.x_translate = g.cont_width/8+g.padding;
	this.y_translate = g.cont_height - this.height - g.padding;
	this.g.transform('t' + this.x_translate + ',' + this.y_translate);
}

function start_click(evt) {
	var buttons = g.button_panel.buttons;
	if (buttons.start.active) {
		g.button_panel.set_buttons_state('animating');
		g.animation.start();
	}
}

function step_click(evt) {
	var buttons = g.button_panel.buttons;
	if (buttons.step.active) {
		g.button_panel.set_buttons_state('stepping');
		g.animation.step();
	}
}

function continue_click(evt) {
	var buttons = g.button_panel.buttons;
	if (buttons.continue.active) {
		g.button_panel.set_buttons_state('animating');
		g.animation.continue();
	}
}

function stop_click(evt) {
	var buttons = g.button_panel.buttons;
	if (buttons.stop.active) {
		g.button_panel.set_buttons_state('stopped');
		g.animation.stop();
	}
}

function ButtonPanel() {
	this.g = snap.group();
	this.width = 205;

	this.buttons = {};
	this.buttons['start'] = new Button(start_click, 'M0,0 0,30 20,15 Z', true, [0,0]);
	this.g.append(this.buttons['start'].button);
	this.buttons['step'] = new Button(step_click, 'M0,0 0,30 20,15 Z M20,0 20,30 30,30 30,0 Z', false, [50,0]);
	this.g.append(this.buttons['step'].button);
	this.buttons['continue'] = new Button(continue_click, 'M0,0 0,30 10,30 10,0 Z M15,0 15,30 35,15 Z', false, [110,0]);
	this.g.append(this.buttons['continue'].button);
	this.buttons['stop'] = new Button(stop_click, 'M0,0 0,30 30,30 30,0 Z', false, [175,0]);
	this.g.append(this.buttons['stop'].button);

	/*this.start_button = snap.path('M0,0 0,30 20,15 Z').attr(this.active_attr);
	
	this.step_button = snap.path('M0,0 0,30 20,15 Z M20,0 20,30 30,30 30,0 Z').attr(this.inactive_attr);
	this.step_button.transform('t50');
	this.g.append(this.step_button);

	this.continue_button = snap.path('M0,0 0,30 10,30 10,0 Z M15,0 15,30 35,15 Z').attr(this.inactive_attr);
	this.continue_button.transform('t110');
	this.g.append(this.continue_button);

	this.stop_button = snap.path('M0,0 0,30 30,30 30,0 Z').attr(this.inactive_attr);
	this.stop_button.transform('t175');
	this.g.append(this.stop_button);
	*/


	this.button_states = {
		'animating': {'step': true, 'stop': true},
		'stopped': {'start': true},
		'stepping': {'step': true, 'continue': true, 'stop': true},
		'waiting': {'step': true, 'continue': true, 'stop': true},
		'done': {'start': true},
	}
	this.set_buttons_state = function(button_state) {
		for (var type in this.buttons) {
			if (type in this.button_states[button_state]) {
				this.buttons[type].set_active();
			} else {
				this.buttons[type].set_inactive();
			}
		}
	}
}

function Button(click_handler, path_str, active, translate) {
	this.color = '#87afff';
	this.active_opacity = 1;
	this.inactive_opacity = .47;
	this.inactive_attr = {
		'fill': this.color,
		'fill-opacity': this.inactive_opacity,
		'cursor': 'default'
	};
	this.active_attr = {
		'fill': this.color,
		'fill-opacity': this.active_opacity,
		'cursor': 'pointer'
	};
	this.active = active;
	this.button = snap.path(path_str).click(click_handler);
	if (this.active) {
		this.button.attr(this.active_attr);
	} else {
		this.button.attr(this.inactive_attr);
	}
	this.button.transform('t' + translate[0] + ',' + translate[1]);

	this.set_active = function() {
		this.active = true;
		this.button.attr(this.active_attr);
	}
	this.set_inactive = function() {
		this.active = false;
		this.button.attr(this.inactive_attr);		
	}
}


function BreakPoint(width, breakpoint_num) {
	this.click = function() {
		if (this.active === true) {
			this.active = false;
			this.button.attr({'opacity': this.inactive_opacity});
		} else {
			this.active = true;
			this.button.attr({'opacity': this.active_opacity});
		}
	}
	this.g = snap.group();
	this.active = false;
	this.active_opacity = 1;
	this.inactive_opacity = .5;
	var self = this;	

	var path_str = 'M0 0 L8 0 L12 4 L8 8 L0 8 L0 0 Z';
	this.button = snap.path(path_str).attr({
		'id': 'breakpoint_' + breakpoint_num,
		'fill': 'blue',
		'opacity': this.inactive_opacity,
	}).click(function() {
		self.click();
	});
	this.g.append(this.button);
}


function CodeBox() {
	this.highlight_line = function(line_id) {
		if (this.line_bboxes === undefined) {
			// We cache the line bboxes so we make less getBBox() calls
			this.line_bboxes = {};
		}
		var line_bbox = this.line_bboxes[line_id];
		if (line_bbox == null) {
			var line = g.code_lines[line_id];
			console.log(line_id);
			line_bbox = line.getBBox();
			this.line_bboxes[line_id] = line_bbox;
		}
		this.highlight_box.attr({'opacity': this.highlight_box_opacity});
		this.highlight_box.transform('t0,' + (line_bbox.y - this.highlight_box_padding.y));
	}
	this.remove_highlighting = function() 	{
		this.highlight_box.attr({'opacity': 0});
	}
	this.add_line_numbers = function() {
		for (var key in g.code_lines) {
			var line = g.code_lines[key];
			if (line['whitespace'] === true) {
				continue;
			}
			var line_num = key.split('_')[1];
			var x = this.padding;
			var y = g.code_lines[key].attr('y');
			var elem = snap.text(x, y, line_num).attr({
				'font-family': 'Courier New',
				'font-size': 14
			});
			this.g.append(elem);
		}
	}
	this.add_break_points = function() {
		this.breakpoints = {};
		for (var key in g.code_lines) {
			var line = g.code_lines[key];
			if (line['whitespace'] === true) {
				continue;
			}
			var line_num = key.split('_')[1];
			this.breakpoints[key] = new BreakPoint(this.breakpoint_width, line_num);
			this.g.append(this.breakpoints[key].g);

			var trans_x = this.line_number_width + this.padding*2;
			var trans_y = parseInt(line.attr('y')) - line.getBBox().height/2;
			this.breakpoints[key].g.transform('t' + trans_x + ',' + trans_y);
		}
	}
	this.is_line_breakpoint_active = function(line_id) {
		return this.breakpoints[line_id].active;
	}

	this.line_padding = 18;
	this.padding = 6;
	this.breakpoint_width = 16;
	this.line_number_width = 16;
	this.line_x = this.padding*3 + this.breakpoint_width + this.line_number_width;
	
	// Set y of codelines to separate them.  Add to group.  Find widest for framing box
    var curr_y = this.line_padding;
    var min_bbox_x = 99999;
    this.widest_line = 0;
    this.g = snap.group();
    for (var key in g.code_lines) {
        var curr_line = g.code_lines[key];
        this.g.append(curr_line);
        curr_line.attr({'y': curr_y, 'x': this.line_x});
        curr_y += this.line_padding;
        
        if (curr_line['whitespace'] === false) {
        	// Don't consider whitespace in size calculation
	        var bbox = curr_line.getBBox();
	        var width = bbox.width + bbox.x;
	        min_bbox_x = Math.min(min_bbox_x, bbox.x);
	        this.widest_line = Math.max(width, this.widest_line);
        }
    }

    // Add a framing box
    this.width =  this.widest_line + this.padding;
    this.height = curr_y + this.padding*2;
    this.frame = snap.rect(0, 0, this.width, this.height, 5, 5).attr({
        fill: '#aaaaaa',
        stroke: '#333333',
        strokeWidth: 2,
    });
    this.g.prepend(this.frame);

    // Add a highlight box 
    this.highlight_box_padding = {x: 8, y: 2};
    this.highlight_box_opacity = .35;
    this.highlight_box = snap.rect(this.line_x - this.highlight_box_padding.x/2, 0, this.widest_line - min_bbox_x + this.highlight_box_padding.x, this.line_padding + this.highlight_box_padding.y*2).attr({
    	'id': 'highlight_box',
    	'fill': 'yellow',
    	'stroke': 'blue',
    	'stroke-width': 1,
    	'opacity': .35
    });
    g.highlight_boxes = {'highlight_box': this.highlight_box};
    this.g.append(this.highlight_box);
    this.remove_highlighting();

    // Add line numbers and breakpoints
    this.add_line_numbers();
    this.add_break_points();
    
    this.g.transform('t' + g.padding + ',' + g.padding);
}
