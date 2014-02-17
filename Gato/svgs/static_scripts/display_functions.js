function Scaler() {
	this.set_max_and_min_dimensions_of_graph_container = function() {
		var bbox = g.master_graph_container.getBBox(),
			playback_bbox = g.playback_bar.g.getBBox();
		var max_height = playback_bbox.y + g.control_panel.height - g.padding - bbox.y,
			max_width = g.cont_width - g.padding - bbox.x,
			min_height = 50,
			min_width = 50;
		var max_scale_factor_y = max_height / bbox.height,
			max_scale_factor_x = max_width / bbox.width;
		
		this.max_scale_factor = Math.min(max_scale_factor_x, max_scale_factor_y);
		this.min_scale_factor = .3;
		
		// If the graph started too large or small then scale it appropriately
		if (this.curr_scale > this.max_scale_factor) {
			this.initial_scale = this.max_scale_factor;
			this.curr_scale = this.max_scale_factor;
			this.scale_graphs(this.curr_scale);
		} else if (this.curr_scale < this.min_scale_factor) {
			this.initial_scale = this.min_scale_factor;
			this.curr_scale = this.min_scale_factor;
			this._scale_graphs(this.curr_scale);
		}
	};

	this.mousedown = function(evt) {
		g.scaler.scaling = true;
		
		var bbox = g.master_graph_container.getBBox();
		g.scaler.start_width = bbox.width * g.scaler.initial_scale;
		g.scaler.start_mouse = {'x': parseInt(evt.x), 'y': parseInt(evt.y)};
	};
	this.drag = function(evt) {
		this.mouseup(evt);
	};
	this.mouseup = function(evt) {
		g.scaler.scaling = false;
	};
	this.mousemove = function(evt) {
		this.do_scale(evt);
	};
	this.scale_graphs = function(scale_factor) {
		/* Scales the graph to the scale factor passed in, or current scale factor.  Accomodates for translation changes */
		if (scale_factor == null) {
			scale_factor = g.scaler.curr_scale;
		}
		g.master_graph_container.transform('s' + scale_factor + ',0,0');
		for (var i=0; i<g.graph_containers.length; i++) {
			var g_cont = g.graph_containers[i],
				x_trans = g.init_container_translate[i]['x']/scale_factor,
				y_trans = 0;
			if (i == 0) {
				y_trans = g.init_container_translate[i]['y']/scale_factor;
			} else {
				y_trans = g.graph_containers[0].getBBox().y2;
			}
			g_cont.transform('t' + x_trans + ',' + y_trans);
		}
	};
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
		g.scaler.scale_graphs();
	};

	var bbox = g.graph_containers[g.num_graphs-1].getBBox();
	this.scaling = false;
	this.initial_scale = 1;
	this.curr_scale = 1;
	this.width = 20;
	this.height = 20;
	this.x = bbox.width - this.width;
	this.y = bbox.height + g.frame_padding*2 - this.height + g.graph_frame_stroke_width * 3;
	this.set_max_and_min_dimensions_of_graph_container();

	this.elem = snap.polygon([this.x, this.y, this.x+this.width, this.y, this.x+this.width, this.y-this.height, this.x, this.y]).attr({
		'fill': '#cc3333',
		'stroke': '#330000',
		'cursor': 'move'
	}).mousedown(this.mousedown);
}

function add_scaler() {
	g.scaler = new Scaler();
	g.graph_containers[g.num_graphs-1].append(g.scaler.elem);
}

function ToolTip(edge) {
	this.mouseover = function(evt) {
		// Move the tooltip to the cursor and make visible
		if (!this.frame_is_sized) {
			var text_bbox = this.text_elem.getBBox();
			this.frame_width = text_bbox.width + this.frame_padding_x;
			this.frame_height = text_bbox.height*2 + 5;
			this.frame.attr({'width': this.frame_width, 'height': this.frame_height});
		}
		this.g.attr({'visibility': 'visible'});
		this.mousemove(evt);
	};
	this.mousemove = function(evt) {
		var x_trans = evt.clientX - this.frame_width;
		var y_trans = evt.clientY + this.frame_height/2;
		this.g.transform('t' + x_trans + ',' + y_trans);
	};

	this.mouseout = function(evt) {
		this.g.attr({'visibility': 'hidden'});
	};

	this.change_text = function(text) {
		this.text_content = text;
		this.text_elem.node.innerHTML = text;
		this.frame_is_sized = false;
	};

	this.delete_self = function() {
		this.text_elem.remove();
		this.frame.remove();
		this.g.remove();
		delete g.tooltip_objects[this.id];
	}


	this.id = edge.attr('id') + '_tooltip';
	this.g = snap.group().attr({
		'id': this.id,
	});
	this.edge = edge;
	this.frame_is_sized = true; 	// True when the frame matches the text size

	// Build the tooltip
	this.text_content = 'No Edge Info Yet';
	this.text_elem = snap.text(0, 0, this.text_content);
	this.g.append(this.text_elem);

	var text_bbox = this.text_elem.getBBox();
	this.frame_padding_x = 20;
	this.frame_width = text_bbox.width + this.frame_padding_x;
	this.frame_height = text_bbox.height*2 + 5;
	this.frame = snap.rect(-1 * this.frame_padding_x/2, text_bbox.height* -1.5, this.frame_width, this.frame_height, 4, 4).attr({
		'fill': '#AABBAA',
		'stroke': '#556655',
		'stroke-width': 2
	});
	this.g.prepend(this.frame);

	this.g.attr({'visibility': 'hidden'});

	// Set the edge mouseover
	edge.hover(
		function (evt) {
			var edge_id = get_id(evt.srcElement);
			var tooltip = g.tooltip_objects[edge_id + '_tooltip'];
			tooltip.mouseover(evt);
		},
		function (evt) {
			var edge_id = get_id(evt.srcElement);
			var tooltip = g.tooltip_objects[edge_id + '_tooltip'];
			tooltip.mouseout(evt);
		}
	);
	edge.mousemove(function (evt) {
		var edge_id = get_id(evt.srcElement);
		var tooltip = g.tooltip_objects[edge_id + '_tooltip'];
		tooltip.mousemove(evt);
	});
}

function add_tooltips() {
	// Put these in the add_global variables function with a description to improve maintainability
	g.tooltips = [];
	g.tooltip_objects = {};

	for (var g_num=0; g_num<g.num_graphs; g_num++) {
		g.tooltips.push({});
		var edges = g.edges[g_num];

		for (var key in edges) {
			var tooltip = new ToolTip(edges[key]);
			g.tooltip_objects[tooltip.id] = tooltip;
			g.tooltips[g_num][tooltip.id] = tooltip.text_elem;
		}
	}
}

function add_tooltip(edge) {
	var edge_id = edge.attr('id');
	var graph_num = parseInt(edge_id.substring(1,2));
	var tooltip = new ToolTip(edge);
	g.tooltip_objects[tooltip.id] = tooltip;
	g.tooltips[graph_num-1][tooltip.id] = tooltip.text_elem;
}

function build_graph_info(group, width, height, g_num) {
	/*var rect = snap.rect(0, 0, width, height).attr({
		'fill': '#fff',
		'stroke': '#ccc',
		'stroke-width': g.graph_frame_stroke_width,
		strokeDasharray: '5,2',
	});
	group.append(rect);
	*/

	var text_elem = snap.text(5, 0, 'No Info').attr({'id': 'g' + g_num + '_info'});		// Set this to "No Info"(or any text) at first so the bbox has a height
	text_elem.attr({'y': text_elem.getBBox().height-1});
	text_elem.node.innerHTML = '';
	group.append(text_elem);
	return text_elem;
}

function add_graph_frame() {
	var pad = g.vertex_r + g.frame_padding;
	g.graph_infos = [];
	for (var i=0; i<g.num_graphs; i++) {
		g.graph_containers[i].append(g.graphs[i]);
		g.graph_containers[i].append(g.graph_info_containers[i]);
		
		var graph_bbox = g.graphs[i].getBBox();
		graph_info_text_elem = build_graph_info(g.graph_info_containers[i], graph_bbox.width/3, 20, i+1);
		g.graph_infos.push(graph_info_text_elem);
		g.graph_info_height = 20; // put me in settings
		var y_trans = graph_bbox.height + pad;
		g.graph_info_containers[i].transform('t0,' + y_trans);

		var frame = snap.rect(0, 0, graph_bbox.width+pad, graph_bbox.height+pad+g.graph_info_height).attr({
			fill: '#fff',
			stroke: '#ccc',
			strokeWidth: g.graph_frame_stroke_width,
			strokeDasharray: '5,2',
		});
		
		g.graph_containers[i].prepend(frame);
	}
}

function position_graph() {
	var x_trans = g.code_box.width + g.padding*2;
	g.init_container_translate = [{x: x_trans}, {x: x_trans}];
	g.graph_translate = [{x: g.frame_padding + g.vertex_r, y: g.frame_padding + g.vertex_r},
		{x: g.frame_padding + g.vertex_r, y: g.frame_padding + g.vertex_r}];
	for (var i=0; i<g.num_graphs; i++) {
		var this_translate = g.init_container_translate[i];
		if (i === 0) {
			this_translate.y = g.padding + g.graph_frame_stroke_width;
		} else {
			this_translate.y = g.init_container_translate[0].y + g.graph_containers[0].getBBox().height;
		}
		var this_container = g.graph_containers[i];
		var this_graph = g.graphs[i];
		this_container.transform('t' + this_translate.x + ',' + this_translate.y);
		this_graph.transform('t' + g.graph_translate[i]['x'] + ',' + g.graph_translate[i]['y']);	
	}
}

function toggle_control_panel() {
	if (g.control_panel.frame_visibility === false) {
		g.control_panel.frame_visibility = true;
		g.control_panel.frame_g.attr({'visibility': 'visible'});
	} else {
		g.control_panel.frame_visibility = false;
		g.control_panel.frame_g.attr({'visibility': 'hidden'});
	}
}

function click_speed_button(evt) {
	var id = get_id(evt.srcElement);
	var label = id.split('_')[0];
	var speed_controls = g.control_panel.speed_controls;
	var buttons = speed_controls.buttons;
	var button_types = speed_controls.button_types;
	for (var i=0; i<buttons.length; i++) {
		if (button_types[i].label === label) {
			g.animation.step_ms = button_types[i]['speed'];
			buttons[i].attr({'opacity': speed_controls.button_settings.active_opacity});
		} else {
			buttons[i].attr({'opacity': speed_controls.button_settings.inactive_opacity});
		}
	}
}

function SpeedControls(width) {
	this.width = width;
	this.g = snap.group();

	this.text_elem = snap.text(0, 0, 'Animation Speed:').attr({
		'fill': '#DDDDDD',
		'font-size': 15,
		'font-family': 'Helvetica',
		'font-weight': 'bold'
	});
	this.g.append(this.text_elem);
	
	// Set up button settings
	var text_bbox = this.text_elem.getBBox();
	this.button_types = [
		{'label': '.25x', 'speed': 200, 'default_selected': false},
		{'label': '.5x', 'speed': 37, 'default_selected': false},
		{'label': '1x', 'speed': 22, 'default_selected': true},
		{'label': '2x', 'speed': 10, 'default_selected': false},
		{'label': '4x', 'speed': .8, 'default_selected': false},
	];
	var size = (this.width - text_bbox.width)/10;
	this.button_settings = {
		'padding': size,
		'width': size,
		'height': size,
		'active_opacity': 1,
		'inactive_opacity': .5
	};

	// Create the different buttons
	var text_trans_y = 0;
	this.buttons = [];
	for (var i=0; i<this.button_types.length; i++) {
		var type = this.button_types[i];
		var button_g = snap.group().attr({
			'class': 'speed_button'
		}).click(click_speed_button);
		
		var button_text = snap.text(0, 0, type['label']).attr({
			'fill': 'white'
		});
		if (text_trans_y === 0) {
			// Set the variable that controls y translation of "Animation Speed" string
			text_trans_y = button_text.getBBox().height;
		}
		var opacity = this.button_settings.inactive_opacity;
		if (type['default_selected'] === true) {
			opacity = this.button_settings.active_opacity;
		}
		var button = snap.rect(0, 3, this.button_settings.width, this.button_settings.height, 4, 4).attr({
			'id': type['label'] + '_button',
			'fill': '#87afff',
			'stroke': '#476fb4',
			'opacity': opacity,
			'cursor': 'pointer'
		});
		var x_trans = text_bbox.width + (i+1)*this.button_settings.padding + i*this.button_settings.width;
		button_g.transform('t' + x_trans);

		button_g.append(button);
		button_g.append(button_text);
		this.buttons.push(button);
		this.g.append(button_g);
	}

	// Translate the animation text down
	this.text_elem.attr({'y': text_trans_y});

	this.height = this.g.getBBox().height;
}

function show_algo_info() {
	// Implement me
    algo_info_active = true;
    showPopWin(info_file, g.cont_width*1/2, g.cont_height*1/2);	// TODO: Change this in GatoExport.py
}

function create_algo_info_button() {
	var g = snap.group().attr({
		'cursor': 'pointer'
	}).click(show_algo_info);
	var text_elem = snap.text(5, 0, 'Show Algorithm Info');
	var text_bbox = text_elem.getBBox();
	text_elem.attr({'y': text_bbox.height});
	var rect = snap.rect(0, 0, text_bbox.width + 10, text_bbox.height + 7, 4, 4).attr({
		'fill': '#aaaaaa',
		'stroke': '#777777',
		'stroke-width': 1
	});
	g.append(rect);
	g.append(text_elem);
	return g;
}

function create_homepage_link() {
	var g = snap.group();
	var text_elem = snap.text(0, 0, 'Visit Gato Homepage').attr({
		'id': 'homepage_link',
		'fill': '#87afff',
		'text-decoration': 'underline',
		'font-size': 17,
		'font-weight': 'bold',
		'cursor': 'pointer'
	});
	text_elem.click(function() {
		window.open('http://bioinformatics.rutgers.edu/Software/Gato/');
	});
	text_elem.attr({'y': text_elem.getBBox().height});
	g.append(text_elem);
	return g;
}

function ControlPanel(cog_width, cog_height, width, height) {
	this.cog_width = cog_width;
	this.cog_height = cog_height;
	this.width = width;
	this.height = height;
	this.padding = 10;
	this.frame_visibility = false;
	this.g = snap.group();

	this.cog = snap.image('img/cog.png', 0, 0, this.cog_width, this.cog_height).click(toggle_control_panel).attr({
		'cursor': 'pointer'
	});
	this.g.append(this.cog);

	this.frame_g = snap.group().attr({'visibility': 'hidden'});
	this.frame = snap.rect(0, 0, this.width, this.height, 5, 5).attr({
		'fill': '#444',
	});
	this.frame_g.append(this.frame);

	// Create the speed controls
	this.speed_controls = new SpeedControls(this.width - this.padding*2);
	this.speed_controls.g.transform('t' + this.padding + ',' + (this.height - this.speed_controls.height + 7));
	this.frame_g.append(this.speed_controls.g);

	// Create the algorithm info button
	this.algo_info_button = create_algo_info_button();	// Returns a g element encompassing the algo info button
	var bbox = this.algo_info_button.getBBox();
	var x_trans = (this.width - this.padding*2) / 2 - bbox.width/2;
	var y_trans = this.height - this.speed_controls.height - this.padding*2 - bbox.height + bbox.y;
	this.algo_info_button.transform('t' + x_trans + ',' + y_trans);
	this.frame_g.append(this.algo_info_button);

	// Create the homepage link
	this.homepage_link = create_homepage_link(); 	// Returns a g element encompassing the homepage link
	var bbox = this.homepage_link.getBBox();
	var x_trans = (this.width - this.padding*2) / 2 - bbox.width/2;
	var y_trans = this.padding;
	this.homepage_link.transform('t' + x_trans + ',' + y_trans);
	this.frame_g.append(this.homepage_link);

	this.frame_g.transform('t' + (-1*this.width+10) + ',' + (-1*this.height-5));	// Align the right edge of the frame with the cog
	this.g.append(this.frame_g);
}

function PlaybackBar() {
	this.g = snap.group();
	this.width = g.cont_width * 3/4 - g.padding*2;
	this.height = 40;
	this.padding_y = 5;
	this.padding_x = 15;
	this.bg_color = '#606060';
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

	g.control_panel = new ControlPanel(30, 30, 360, 130);
	g.control_panel.g.transform('t' + (this.width - this.padding_x - g.control_panel.cog_width) + ',' + (this.padding_y));
	this.g.append(g.control_panel.g);

	this.slider_width = this.width - this.padding_x*4 - g.button_panel.width - g.control_panel.cog_width;
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
	this.button = snap.path(path_str).click(click_handler).touchstart(click_handler);
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
		'cursor': 'pointer'
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
	this.scale_and_translate = function() {
		/* This function accounts for the cases where there is too much code and
			the code box goes off the screen.  In those cases it is scaled down
		*/
		var bbox = this.g.getBBox(),
			playback_bbox = g.playback_bar.g.getBBox();
		var max_height = playback_bbox.y + g.control_panel.height - g.padding*2 - bbox.y;
		var max_scale_factor = max_height / bbox.height;
		this.scale_factor = 1;
		if (max_scale_factor < 1) {
			this.scale_factor = max_scale_factor;
		}
		var scale = 's' + this.scale_factor + ',0,0';
		var translate = 't' + g.padding + ',' + g.padding;
		this.g.transform(translate + scale);

    	// If some text is outside of the frame then make the frame wider
    	var new_width = this.width * this.scale_factor;
    	bbox = this.g.getBBox();
    	if (new_width < bbox.width) {
    		this.frame.attr({'width': parseInt(this.frame.attr('width')) + (bbox.width - new_width) + this.padding})
    	}
	};

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
        fill: '#ddd',
        stroke: '#333333',
        strokeWidth: 2,
    });
    this.g.prepend(this.frame);

    // Add a highlight box 
    this.highlight_box_padding = {x: 8, y: 2};
    this.highlight_box_opacity = .35;
    this.highlight_box = snap.rect(this.line_x - this.highlight_box_padding.x/2, 0, this.widest_line - min_bbox_x + this.highlight_box_padding.x, this.line_padding + this.highlight_box_padding.y).attr({
    	'id': 'highlight_box',
    	'fill': 'yellow',
    	'stroke': 'blue',
    	'stroke-width': 1,
    	'opacity': .35
    });
    g.highlight_boxes[0] = {'highlight_box': this.highlight_box};
    this.g.append(this.highlight_box);
    this.remove_highlighting();

    // Add line numbers and breakpoints
    this.add_line_numbers();
    this.add_break_points();

    this.scale_and_translate();
}
