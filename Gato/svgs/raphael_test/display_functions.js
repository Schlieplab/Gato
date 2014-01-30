function Scaler() {
	function scaled_to_max() {
		var bbox = g.g1_container.getBBox();
		var playback_bbox = g.playback_bar.g.getBBox();
		if (bbox.y + bbox.height + g.padding > playback_bbox.y) {
			return true;
		}
		return false;
	}

	this.mousedown = function(evt) {
		g.scaler.scaling = true;
		g.scaler.start_width = g.g1_container.getBBox().width;
		console.log(g.scaler.start_width);
		g.scaler.start_mouse = {'x': parseInt(evt.x), 'y': parseInt(evt.y)};
	}
	this.mouseup = function(evt) {
		g.scaler.scaling = false;
	}
	this.do_scale = function(evt) {
		var dx = parseInt(evt.x) - g.scaler.start_mouse.x;
		var dy = parseInt(evt.y) - g.scaler.start_mouse.y;

		var new_width = g.scaler.start_width + dx;
		var scale_factor = new_width / g.initial_graph_width;
		if (scale_factor < g.min_scale_factor) {
			return;
		}

		if (scale_factor < g.scaler.curr_scale || !scaled_to_max()) {
			console.log("Curr scale is " + g.scaler.curr_scale + '. Moving to ' + scale_factor);
			g.scaler.curr_scale = scale_factor;
			g.g1_scale = 's' + g.scaler.curr_scale + ',0,0';
			var trans = 't' + g.g1_container_translate[0] + ',' + g.g1_container_translate[1] + g.g1_scale;
			g.g1_container.transform(trans);
		}
	}

	var bbox = g.g1_container.getBBox();
	this.scaling = false;
	this.curr_scale = 1;
	this.width = 10;
	this.height = 10;
	this.x = bbox.width - this.width;
	this.y = bbox.height + g.frame_padding - this.height;

	this.elem = snap.polygon([this.x, this.y, this.x+this.width, this.y, this.x+this.width, this.y-this.height, this.x, this.y]).attr({
		'fill': '#000',
		'stroke': '#000',
		'cursor': 'pointer'
	}).mousedown(this.mousedown).
	mouseup(this.mouseup);
}

function add_scaler() {
	g.scaler = new Scaler();
	g.g1_container.append(g.scaler.elem);
}

function add_graph_frame() {
	g.g1_container.append(g.g1);
	g.g2_container.append(g.g2);

	var graph_bbox = g.g1.getBBox();
	var pad = g.vertex_r + g.frame_padding;
	var frame = snap.rect(0, 0, graph_bbox.width+pad, graph_bbox.height+pad).attr({
		fill: '#fff',
		stroke: '#ccc',
		strokeWidth: g.graph_frame_stroke_width,
		strokeDasharray: '5,2',
	});
	
	g.g1_container.prepend(frame);
}

function position_graph() {
	var cont_x_trans = g.code_box_width + g.padding*2;
	var cont_y_trans = g.padding + g.graph_frame_stroke_width;
	var x_trans = g.frame_padding + g.vertex_r;
	var y_trans = x_trans;
	g.g1_container_translate = [cont_x_trans, cont_y_trans];
	g.g1_translate = [x_trans, y_trans];
	g.g1_container.transform('t' + g.g1_container_translate[0] + ',' + g.g1_container_translate[1]);
	g.g1.transform('t' + (g.g1_translate[0]) + ',' + g.g1_translate[1]);
}

function format_code_lines() {
    // Set y of codelines to separate them.  Add to group.  Find widest for framing box
    var curr_y = g.line_padding;
    var widest = 0;
    g.line_g = snap.group();
    for (var key in g.code_lines) {
        var curr_line = g.code_lines[key];
        g.line_g.append(curr_line);
        curr_line.attr({'y': curr_y, 'x': g.code_box_padding + g.breakpoint_width + g.line_number_width});
        curr_y += g.line_padding;
        
        var bbox = curr_line.getBBox();
        var width = bbox.width + bbox.x;
        if (width > widest) {
            widest = width;
        }
    }

    // Add a framing box
    g.code_box_width =  widest+g.code_box_padding;
    g.code_box_height = curr_y+g.code_box_padding*2;
    g.code_box = snap.rect(0, 0, g.code_box_width, g.code_box_height, 5, 5).attr({
        fill: '#aaaaaa',
        stroke: '#333333',
        strokeWidth: 2,
    });
    g.line_g.prepend(g.code_box);
    g.line_g.transform('t' + g.padding + ',' + g.padding);
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

	this.x_translate = g.cont_width/8+g.padding;
	this.y_translate = g.cont_height - this.height - g.padding;
	this.g.transform('t' + this.x_translate + ',' + this.y_translate);
}

function start_click(evt) {
	var buttons = g.button_panel.buttons;
	if (buttons.start.active) {
		g.button_panel.set_buttons_state('animating');
		start_animation();
	}
}

function step_click(evt) {
	// TODO: fill me in
}

function ButtonPanel() {
	this.g = snap.group();

	this.buttons = {};
	this.buttons['start'] = new Button(start_click, 'M0,0 0,30 20,15 Z', true, [0,0]);
	this.g.append(this.buttons['start'].button);
	this.buttons['step'] = new Button(step_click, 'M0,0 0,30 20,15 Z M20,0 20,30 30,30 30,0 Z', false, [50,0]);
	this.g.append(this.buttons['step'].button);


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

