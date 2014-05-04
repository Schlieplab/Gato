function Scaler() {
    /* This object represents the graphical and programmatical elements
        of the graph scaler.  It appears at the bottom right of the graph
        as a red triangle.
    */
    this.set_max_and_min_dimensions_of_graph_container = function() {
        /* Sets the following properties on the Scaler object:
        this.max_scale_factor: The largest value the graph can be scaled to
            before it grows too large for it's space
        this.min_scale_factor: The minimum value the graph can be scaled to.
            This one isn't as essential, but we definitely don't want negative scale values.
        */
        var bbox = g.master_graph_container.getBBox(),
            playback_bbox = g.playback_bar.g.getBBox();
        var max_height = playback_bbox.y + g.control_panel.height - g.padding - bbox.y, // control_panel height gets added in because the playback_bbox includes it
            max_width = g.cont_width - g.padding - bbox.x,
            min_height = 50,
            min_width = 50;
        var max_scale_factor_y = max_height / (bbox.height / this.curr_scale),
            max_scale_factor_x = max_width / (bbox.width / this.curr_scale);
            
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
            this.scale_graphs(this.curr_scale);
        }
    };

    this.mousedown = function(evt) {
        g.scaler.scaling = true;
        var bbox = g.master_graph_container.getBBox();
        g.scaler.start_width = bbox.width * g.scaler.initial_scale;
        g.scaler.start_mouse = {'x': parseInt(evt.clientX), 'y': parseInt(evt.clientY)};
    };
    this.drag = function(evt) {
        this.mouseup(evt);
    };
    this.mouseup = function(evt) {
        g.scaler.scaling = false;
    };
    this.mousemove = function(evt) {
        /* Computes the new scale_factor and calls scale_graphs() */
        var dx = parseInt(evt.clientX) - g.scaler.start_mouse.x;
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
    this.scale_graphs = function(scale_factor) {
        /* Scales the graph to the scale factor passed in, 
            or current scale factor.  Accomodates for translation changes(what does that mean?)
        */
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

    var bbox = g.graph_containers[g.num_graphs-1].getBBox();
    // true if the scaler is currently being manipulated
    this.scaling = false;
    // The initial scale factor of the graph
    this.initial_scale = 1;
    // The current scale factor of the graph
    this.curr_scale = 1;
    this.set_max_and_min_dimensions_of_graph_container();
    
    this.width = 20;
    this.height = 20;
    this.x = bbox.width - this.width + g.graph_frame_stroke_width;
    this.y = bbox.height;   // TODO: commit this line
    this.elem = snap.polygon([this.x, this.y, this.x+this.width, this.y, this.x+this.width, this.y-this.height, this.x, this.y]).attr({
        'fill': '#cc3333',
        'stroke': '#330000',
        'cursor': 'move'
    }).mousedown(this.mousedown);
}

function ToolTip(elem, elem_type) {
    /* Takes in an element to put the tooltip on elem_type is either 'edge' or 'vertex' */
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
        // Move the tooltip to the cursor
        var x_trans = evt.clientX - this.frame_width;
        var y_trans = evt.clientY + this.frame_height/2;
        this.g.transform('t' + x_trans + ',' + y_trans);
    };

    this.mouseout = function(evt) {
        // Hide the tooltip
        this.g.attr({'visibility': 'hidden'});
    };

    this.change_text = function(text) {
        // Change the content of the ToolTip text node
        this.text_content = text;
        this.text_elem.node.innerHTML = text;
        this.frame_is_sized = false;
    };

    this.delete_self = function() {
        // Remove the tooltip from the canvas, and from the 
        // global tooltips and tooltip_objects arrays
        for (var key in g.tooltips[this.g_num-1]) {
            if (g.tooltips[this.g_num-1][key] === this.text_elem) {
                delete g.tooltips[this.g_num-1][key];
            }
        }
        this.text_elem.remove();
        this.frame.remove();
        this.g.remove();
        delete g.tooltip_objects[this.id];
    }

    var elem_id = elem.attr('id');
    this.g_num = parseInt(elem_id.substring(1,2));
    this.id = elem_id + '_tooltip';
    this.g = snap.group().attr({
        'id': this.id,
    });
    this.elem = elem;
    this.frame_is_sized = true;     

    // Build the tooltip
    if (elem_type === 'edge') {
        this.text_content = get_default_edge_info(elem_id, this.g_num-1);
    } else {
        this.text_content = get_default_vertex_info(elem_id, this.g_num-1);
    }
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
    elem.hover(
        function (evt) {
            var elem_id = get_id(get_evt_target(evt));
            var elem = snap.select('#' + elem_id);
            var tooltip = g.tooltip_objects[elem.parent().attr('id') + '_tooltip'];
            tooltip.mouseover(evt);
        },
        function (evt) {
            var elem_id = get_id(get_evt_target(evt));
            var elem = snap.select('#' + elem_id);
            var tooltip = g.tooltip_objects[elem.parent().attr('id') + '_tooltip'];
            tooltip.mouseout(evt);
        }
    );
    elem.mousemove(function (evt) {
        var elem_id = get_id(get_evt_target(evt));
        var elem = snap.select('#' + elem_id);
        var tooltip = g.tooltip_objects[elem.parent().attr('id') + '_tooltip'];
        tooltip.mousemove(evt);
    });
}

function initialize_tooltips() {
    // This function creates tooltips for all of the vertices and edges current on the graph
    // It does not respect existing ToolTips so call at the beginning of the program run
    for (var g_num=0; g_num<g.num_graphs; g_num++) {
        var edge_groups = g.edge_groups[g_num];
        for (var key in edge_groups) {
            var tooltip = new ToolTip(edge_groups[key], 'edge');
            g.tooltip_objects[tooltip.id] = tooltip;
            g.tooltips[g_num][tooltip.id] = tooltip.text_elem;
        }
        var vertex_groups = g.vertex_groups[g_num];
        for (var key in vertex_groups) {
            var tooltip = new ToolTip(vertex_groups[key], 'vertex');
            g.tooltip_objects[tooltip.id] = tooltip;
            g.tooltips[g_num][tooltip.id] = tooltip.text_elem;
        }
    }
}

function add_tooltip(elem, element_type) {
    // Adds a tooltip to the given element(always a edge group or vertex group right now)
    // element_type is either 'edge' or 'vertex' right now-- we need to the element_type to determine default tooltip info
    var elem_id = elem.attr('id');
    var graph_num = parseInt(elem_id.substring(1,2));
    var tooltip = new ToolTip(elem, graph_num-1, element_type);
    g.tooltip_objects[tooltip.id] = tooltip;
    g.tooltips[graph_num-1][tooltip.id] = tooltip.text_elem;
}

function add_graph_info() {
    /* Adds graph info elements to the canvas */
    function build_graph_info(group, g_num) {
        var text_elem = snap.text(5, 0, 'No Info').attr({'id': 'g' + g_num + '_info'});     // Set this to "No Info"(or any text) at first so the bbox has a height
        text_elem.attr({'y': text_elem.getBBox().height-1});    
        text_elem.attr({'text': g.init_graph_infos[g_num-1]}); // TODO: commit this line    /* This line fixes the safari issue */
        group.append(text_elem);
        return text_elem;
    }

    var pad = g.vertex_r + g.frame_padding; // Padding on each edge of the graph
    
    for (var g_num=0; g_num<g.num_graphs; g_num++) {
        var graph_bbox = g.graphs[g_num].getBBox();
        // Add the graph and graph info to the graph container
        g.graph_containers[g_num].append(g.graph_info_containers[g_num]);
        // Set up the graph info
        var graph_info_text_elem = build_graph_info(g.graph_info_containers[g_num], g_num+1);
        g.graph_infos.push(graph_info_text_elem);
    }
}

function add_graph_frame() {
    // Padding on each edge of graph
    var pad = g.vertex_r + g.frame_padding;

    for (var g_num=0; g_num<g.num_graphs; g_num++) {
        var graph_bbox = g.graphs[g_num].getBBox();
        
        // Add the graph and graph info to the graph container
        g.graph_containers[g_num].prepend(g.graphs[g_num]);
        
        var max_size = g.max_graph_sizes[g_num];
        
        // reposition the graph info
        var y_trans = graph_bbox.height + pad;
        if (max_size.height) {
            y_trans = max_size.height + pad;
        }
        g.graph_info_containers[g_num].transform('t0,' + y_trans);

        // Create the frame
        var frame = null;
        //  TODO: THIS IS MESSY.  Max size should always be set here.
        if (max_size.width && max_size.height) {
            // If we added any vertices or edges then max_size will be set and we should use that
            frame = snap.rect(0, 0, max_size.width+pad, max_size.height+pad+g.graph_info_height);
        } else {
            frame = snap.rect(0, 0, graph_bbox.width+pad, graph_bbox.height+pad+g.graph_info_height);
        }
        frame.attr({
            fill: '#fff',
            stroke: '#ccc',
            strokeWidth: g.graph_frame_stroke_width,
            strokeDasharray: '5,2',
        });
        g.graph_containers[g_num].prepend(frame);
    }
}

function position_graph() {
    // Used for initial translations, and also scaling of graph
    var curr_scale = 1;
    if (g.scaler !== undefined) {
        curr_scale = g.scaler.curr_scale;
    }

    var x_trans = g.code_box.frame_width + g.padding*2;
    g['init_container_translate'] = [{x: x_trans}, {x: x_trans}];
    for (var i=0; i<g.num_graphs; i++) {
        var max_size = g.max_graph_sizes[i];
        var container_translate = g.init_container_translate[i];
        if (i === 0) {
            container_translate.y = g.padding + g.graph_frame_stroke_width;
        } else {
            container_translate.y = g.init_container_translate[0].y + g.graph_containers[0].getBBox().height;
        }

        // Adjust the translations if we have a max height and width.  
        // If we don't have one, then the original size is ok
        var graph_bbox = g.graphs[i].getBBox();
        if (max_size.height) {
            var diff = max_size.height - graph_bbox.height;
            if (diff > 0 && graph_bbox.height != 0) {
                g.graph_translate[i].y += diff/2; 
            }
        }
        if (max_size.width) {
            var diff = 0;
            if (graph_bbox.width != 0) {
                if (max_size.min_left && max_size.min_left < g.frame_padding) {
                    diff += -1*max_size.min_left;
                }
            }
            if (diff > 0) {
                g.graph_translate[i]['x'] += diff - g.vertex_r;
            }
        }

        container_translate.x = container_translate.x / curr_scale;
        container_translate.y = container_translate.y / curr_scale;
        g.graph_containers[i].transform('t' + container_translate.x + ',' + container_translate.y);
        g.graphs[i].transform('t' + g.graph_translate[i]['x'] + ',' + g.graph_translate[i]['y']);   
    }
}

function click_speed_button(evt) {
    /* Changes the animation speed based on which button was clicked */
    var target_id = get_id(get_evt_target(evt));
    var target_label = target_id.split('_')[0];
    var speed_controls = g.control_panel.speed_controls;
    var buttons = speed_controls.buttons;
    var button_types = speed_controls.button_types;
    
    // Iterate over the buttons, finding the one that was clicked
    for (var i=0; i<buttons.length; i++) {
        if (button_types[i].label === target_label) {
            g.animation.step_ms = button_types[i]['speed'];
            buttons[i].attr({'opacity': speed_controls.button_settings.active_opacity});
        } else {
            buttons[i].attr({'opacity': speed_controls.button_settings.inactive_opacity});
        }
    }
}

function SpeedControls(width) {
    /*  Object that represents the row of speed buttons in the
        menu that opens at bottom right 
    */
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
    /* Pops open the algorithm info iframe */
    algo_info_active = true;
    showPopWin(info_file, g.cont_width*1/2, g.cont_height*1/2);
}

function create_algo_info_button() {
    /* Creates the button that when clicked will show the algorithm info iframe */
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
    /*  Object that controls the control panel at the bottom right of the screen that is 
        brought up by clicking on the cog.
    */
    this.toggle_visibility = function() {
        if (g.control_panel.frame_visibility === false) {
            g.control_panel.frame_visibility = true;
            g.control_panel.frame_g.attr({'visibility': 'visible'});
        } else {
            g.control_panel.frame_visibility = false;
            g.control_panel.frame_g.attr({'visibility': 'hidden'});
        }
    };
    this.cursor_in_control_panel = function(evt) {
        var elem = Snap.getElementByPoint(evt.clientX, evt.clientY);
        while (elem !== null && elem !== snap) {
            if (elem === this.g) {
                return true;
            }
            elem = elem.parent();
        }
        return false;
    };

    this.cog_width = cog_width;
    this.cog_height = cog_height;
    this.width = width;
    this.height = height;
    this.padding = 10;
    this.frame_visibility = false;
    this.g = snap.group().attr({'id': 'control_panel_group'});

    this.cog = snap.image('img/cog.png', 0, 0, this.cog_width, this.cog_height).click(this.toggle_visibility).attr({
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
    this.algo_info_button = create_algo_info_button();  // Returns a g element encompassing the algo info button
    var bbox = this.algo_info_button.getBBox();
    var x_trans = (this.width - this.padding*2) / 2 - bbox.width/2;
    var y_trans = this.height - this.speed_controls.height - this.padding*2 - bbox.height + bbox.y;
    this.algo_info_button.transform('t' + x_trans + ',' + y_trans);
    this.frame_g.append(this.algo_info_button);

    // Create the homepage link
    this.homepage_link = create_homepage_link();    // Returns a g element encompassing the homepage link
    var bbox = this.homepage_link.getBBox();
    var x_trans = (this.width - this.padding*2) / 2 - bbox.width/2;
    var y_trans = this.padding;
    this.homepage_link.transform('t' + x_trans + ',' + y_trans);
    this.frame_g.append(this.homepage_link);

    this.frame_g.transform('t' + (-1*this.width+10) + ',' + (-1*this.height-5));    // Align the right edge of the frame with the cog
    this.g.append(this.frame_g);
}

function PlaybackBar() {
    /* Object to represent the whole playback bar at the bottom */
    this.g = snap.group();
    this.width = g.cont_width * 3/4 - g.padding*2;
    this.min_width = 350;
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
    this.control_panel_x = this.width - this.padding_x - g.control_panel.cog_width;
    g.control_panel.g.transform('t' + this.control_panel_x + ',' + this.padding_y);
    this.g.append(g.control_panel.g);

    this.slider_width = this.width - this.padding_x*4 - g.button_panel.width - g.control_panel.cog_width;
    this.slider_height = this.height - this.padding_y*2;
    g.slider = new Slider(this.slider_width, this.slider_height);
    this.slider_x_trans = g.button_panel.width + this.padding_x*2;
    g.slider.g.transform('t' + this.slider_x_trans + ',' + this.padding_y)
    this.g.append(g.slider.g);

    this.x_translate = g.cont_width/8 + g.padding;
    this.y_translate = g.cont_height - this.height - g.padding;
    this.g.transform('t' + this.x_translate + ',' + this.y_translate);
}

PlaybackBar.prototype.resize = function() {
    /* Called on window resize to redraw */
    var new_width = g.cont_width * 3/4 - g.padding*2;
    if (new_width > this.min_width) {
        this.width = g.cont_width * 3/4 - g.padding*2;
        this.frame.attr({'width': this.width});
        this.x_translate = g.cont_width/8 + g.padding;
        this.y_translate = g.cont_height - this.height - g.padding;
        this.g.transform('t' + this.x_translate + ',' + this.y_translate);

        this.control_panel_x = this.width - this.padding_x - g.control_panel.cog_width;
        g.control_panel.g.transform('t' + this.control_panel_x + ',' + this.padding_y);

        var new_slider_width = this.width - this.padding_x*4 - g.button_panel.width - g.control_panel.cog_width;
        if (new_slider_width > g.slider.min_width) {
            this.slider_width = new_slider_width;
            g.slider.resize_width(this.slider_width);
            this.slider_x_trans = g.button_panel.width + this.padding_x*2;
            g.slider.g.transform('t' + this.slider_x_trans + ',' + this.padding_y);
        }
    }
}

function start_click(evt) {
    /* This is called when the start button is clicked */
    var buttons = g.button_panel.buttons;
    if (buttons.start.active) {
        g.button_panel.set_buttons_state('animating');
        g.animation.start();
    }
}

function step_click(evt) {
    /* This is called when the step button is clicked */
    var buttons = g.button_panel.buttons;
    if (buttons.step.active) {
        g.button_panel.set_buttons_state('stepping');
        g.animation.step();
    }
}

function continue_click(evt) {
    /* This is called when the continue button is clicked */
    var buttons = g.button_panel.buttons;
    if (buttons.continue.active) {
        g.button_panel.set_buttons_state('animating');
        g.animation.continue();
    }
}

function stop_click(evt) {
    /* This is called when the stop button is clicked */
    var buttons = g.button_panel.buttons;
    if (buttons.stop.active) {
        g.button_panel.set_buttons_state('stopped');
        g.animation.stop();
    }
}

function ButtonPanel() {
    /*  This object represents the animation control buttons at 
        the left side of the playback bar
    */
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
    /*  This object represents one of the buttons that control animation
        that are located at the left side of the playback bar
    */
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
    /*  This object represents the line breakpoints */
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
    /*  This objects represents the code box at the top left */
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
    this.remove_highlighting = function()   {
        this.highlight_box.attr({'opacity': 0});
    }
    this.add_line_numbers = function() {
        var sub = 0;
        for (var key in g.code_lines) {
            var line = g.code_lines[key];
            if (line['whitespace'] === true) {
                sub ++;
                continue;
            }
            var line_num = parseInt(key.split('_')[1]) - sub;
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
    this.scale_and_translate = function(initial) {
        /* This function accounts for the cases where there is too much code and
            the code box goes off the screen.  In those cases it is scaled down
        */
        if (!this.initial_bbox) {
            this.initial_bbox = this.g.getBBox();
        }
        var playback_bbox = g.playback_bar.g.getBBox();
        var max_height = playback_bbox.y + g.control_panel.height - g.padding*2 - this.initial_bbox.y;
        var max_scale_factor = max_height / this.initial_bbox.height;
        this.scale_factor = 1;
        if (max_scale_factor < 1) {
            this.scale_factor = max_scale_factor;
        }
        var scale = 's' + this.scale_factor + ',0,0';
        var translate = 't' + g.padding + ',' + g.padding;
        this.g.transform(translate + scale);

        // Resize the frame and highlight box
        this.frame.remove();    // Remove the frame before getting the bbox, so the bbox tells us how wide the lines are
        var bbox = this.g.getBBox();
        this.frame_width = bbox.width / this.scale_factor;
        this.frame.attr({'width': this.frame_width});
        this.g.prepend(this.frame);
        this.highlight_box_width = this.frame_width - this.highlight_box_x;
        this.highlight_box.attr({'width': this.highlight_box_width});
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
    this.frame_width = this.widest_line + this.padding;
    this.initial_frame_width = this.frame_width;
    this.frame_height = curr_y + this.padding*2;

    this.frame = snap.rect(0, 0, this.frame_width, this.frame_height, 5, 5).attr({
        fill: '#ddd',
        stroke: '#333333',
        strokeWidth: 2,
    });
    this.g.prepend(this.frame);

    // Add a highlight box 
    this.highlight_box_padding = {x: 8, y: 2};
    this.highlight_box_opacity = .35;
    this.highlight_box_x = this.line_x - this.highlight_box_padding.x/2;
    this.highlight_box_width = this.frame_width - this.highlight_box_x;
    this.highlight_box = snap.rect(this.highlight_box_x, 0, this.highlight_box_width, this.line_padding + this.highlight_box_padding.y).attr({
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

    for (var key in g.code_lines) {
        var curr_line = g.code_lines[key];
        (function (codebox, closure_key) {
            curr_line.click(function() {
                codebox.breakpoints[closure_key].click();
            });
        })(this, key);
    }

    this.scale_and_translate();
}
