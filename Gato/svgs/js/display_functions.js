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
        var max_height = g.cont_height - g.padding*3 - g.playback_bar.frame.attr('height');
        if (isiPhone()) {
            max_height = g.cont_height - g.padding*2 - g.playback_bar.frame.attr('height');
        }
        if (this.min_scale_factor) {
            // If this isn't the first computation then add the click_receiver extra height to the max_height
            max_height += this.click_receiver_extra_height;
        }
        var max_width = g.cont_width - g.padding - get_graph_x_trans(),
            min_height = 50,
            min_width = 50;
        var max_scale_factor_y = max_height / (bbox.height / this.curr_scale),
            max_scale_factor_x = max_width / (bbox.width / this.curr_scale);

        this.max_scale_factor = Math.min(max_scale_factor_x, max_scale_factor_y);
        if (isiPhone()) {
            this.min_scale_factor = Math.min(.5, Math.max(this.max_scale_factor-.1, .15));
        } else {
            this.min_scale_factor = .15;    
        }
        
        if (this.initial_scale) {
            if (this.curr_scale > this.max_scale_factor) {
                // If this isn't the first time we're calling this function then 
                // the window is being resized and we should maximize the graph size if need be
                this.curr_scale = this.max_scale_factor;
                this.scale_graphs(this.curr_scale);
            }
        }
        if (this.initial_scale === undefined) {
            // If this is the first time this is run then adjust the graph to fit appropriately
            // If the graph started too large or small then scale it appropriately
            if (this.curr_scale > this.max_scale_factor) {
                this.curr_scale = this.max_scale_factor;
                this.scale_graphs(this.curr_scale);
            } 
            if (this.curr_scale < this.min_scale_factor) {
                this.curr_scale = this.min_scale_factor;
                this.scale_graphs(this.curr_scale);
            }
        }
    };

    this.mousedown = function(evt) {
        g.scaler.scaling = true;
        var bbox = g.master_graph_container.getBBox();
        g.scaler.start_width = bbox.width * g.scaler.initial_scale;
        var start_x = parseInt(evt.clientX),
            start_y = parseInt(evt.clientY);
        if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
            start_x = parseInt(evt.changedTouches[0].clientX);
            start_y = parseInt(evt.changedTouches[0].clientY);
        }
        g.scaler.start_mouse = {'x': start_x, 'y': start_y};
    };
    this.drag = function(evt) {
        this.mouseup(evt);
    };
    this.mouseup = function(evt) {
        g.scaler.scaling = false;
    };
    this.mousemove = function(evt) {
        /* Computes the new scale_factor and calls scale_graphs() */
        var clientX = evt.clientX;
        if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
            clientX = evt.changedTouches[0].clientX;
        }
        var dx = parseInt(clientX) - g.scaler.start_mouse.x;
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
                x_trans = get_graph_x_trans() / scale_factor,
                y_trans = 0;
            if (i === 0) {
                y_trans = g.init_container_translate[i]['y']/scale_factor;
            } else {
                y_trans = g.graph_containers[0].getBBox().y2;
            }
            g_cont.transform('t' + x_trans + ',' + y_trans);
        }
        this.curr_scale = scale_factor;
    };

    var bbox = g.graph_containers[g.num_graphs-1].getBBox();
    // true if the scaler is currently being manipulated
    this.scaling = false;
    // The current scale factor of the graph
    this.curr_scale = 1;
    this.set_max_and_min_dimensions_of_graph_container();
    // The initial scale factor of the graph
    this.initial_scale = this.curr_scale;
    
    this.width = 20;
    this.height = 20;
    this.x = bbox.width - this.width + g.graph_frame_stroke_width;
    this.y = bbox.height;   // TODO: commit this line
    this.elem = snap.polygon([this.x, this.y, this.x+this.width, this.y, this.x+this.width, this.y-this.height, this.x, this.y]).attr(
    {
        'fill': '#cc3333',
        'cursor': 'move'
    }).mousedown(this.mousedown);
    var w = 15;
    var h = 15;
    var e = 15;
    this.click_receiver = snap.polygon([this.x-w-e, this.y+h, this.x+this.width+w, this.y+h, this.x+this.width+w, this.y-this.height-h-e, this.x-w-e, this.y+h]).attr(
    {
        'opacity': 0,
    }).mousedown(this.mousedown);
    this.click_receiver_extra_height = 7.5;
}

function ToolTip(elem, elem_type) {
    /* Takes in an element to put the tooltip on elem_type is either 'edge' or 'vertex' */
    this.mouseover = function(evt) {
        // Move the tooltip to the cursor and make visible
        if (!this.frame_is_sized) {
            this.size_frame();
        }
        this.g.attr({'visibility': 'visible'});
        this.visible = true;
        this.mousemove(evt);
    };

    this.size_frame = function() {
        var text_bbox = this.text_elem.getBBox();
        this.frame_width = text_bbox.width + this.frame_padding_x;
        this.frame_height = text_bbox.height*2 + 5;
        this.frame.attr({'width': this.frame_width, 'height': this.frame_height});
    };

    this.mousemove = function(evt) {
        // Move the tooltip to the cursor
        var clientX = parseInt(evt.clientX),
            clientY = parseInt(evt.clientY);
        if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
            clientX = parseInt(evt.changedTouches[0].clientX);
            clientY = parseInt(evt.changedTouches[0].clientY);
        }
        var x_trans = clientX - this.frame_width;
        var y_trans = clientY + this.frame_height/2 - g.navbar_height;
        this.g.transform('t' + x_trans + ',' + y_trans);
    };

    this.mouseout = function(evt) {
        // Hide the tooltip
        this.visible = false;
        this.g.attr({'visibility': 'hidden'});
    };
    this.change_text = function(text) {
        // Change the content of the ToolTip text node
        this.text_content = text;
        this.text_elem.node.textContent = text;
        if (this.visible) {
            this.size_frame();
        } else {
            this.frame_is_sized = false;
        }
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
    };

    var elem_id = elem.attr('id');
    this.g_num = parseInt(elem_id.substring(1,2));
    this.id = elem_id + '_tooltip';
    this.g = snap.group().attr({
        'id': this.id,
    });
    this.elem = elem;
    this.frame_is_sized = true;
    this.visible = false;

    // Build the tooltip
    if (elem_type === 'edge') {
        this.text_content = get_default_edge_info(elem_id, this.g_num-1);
    } else if (elem_type === 'vertex') {
        this.text_content = get_default_vertex_info(elem_id, this.g_num-1);
    }
    this.text_elem = snap.text(0, 0, this.text_content).attr({
        'font-family': 'Helvetica'
    });
    this.g.append(this.text_elem);

    var text_bbox = this.text_elem.getBBox();
    this.frame_padding_x = 20;
    this.frame_width = text_bbox.width + this.frame_padding_x;
    this.frame_height = text_bbox.height*2 + 5;
    this.frame = snap.rect(-1 * this.frame_padding_x/2, text_bbox.height* -1.5, this.frame_width, this.frame_height, g.rect_r, g.rect_r).attr({
        'fill': g.codebox_fill,
        'stroke': g.playback_bar_stroke,
        'stroke-width': 1,
        'filter' : 'url(#tooltip_dropshadow)',
    });
    this.g.prepend(this.frame);
    this.g.attr({'visibility': 'hidden'});

    // Set the mouseover and mousemove
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
    elem.touchstart(function (evt) {
        var elem_id = get_id(get_evt_target(evt));
        var elem = snap.select('#' + elem_id);
        var tooltip = g.tooltip_objects[elem.parent().attr('id') + '_tooltip'];
        tooltip.mouseover(evt);
        g.new_active_tooltip = true;
        if (g.active_tooltip !== undefined) {
            g.active_tooltip.mouseout();
        }
        g.active_tooltip = tooltip;
    });
    elem.mousemove(function (evt) {
        if (isiPhone()) {
            return;
        }
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
    var tooltip = new ToolTip(elem, element_type);
    g.tooltip_objects[tooltip.id] = tooltip;
    g.tooltips[graph_num-1][tooltip.id] = tooltip.text_elem;
}

function add_graph_info() {
    /* Adds graph info elements to the canvas */
    function build_graph_info(group, g_num) {
        var text_elem = snap.text(5, 0, 'No Info').attr({
            'id': 'g' + g_num + '_info',
            'font-family': 'Helvetica',
            'visibility': 'hidden'
        });     // Set this to "No Info"(or any text) at first so the bbox has a height
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

    // Compute the dimensions of each graph frame
    var graph_frame_dim = [{'width': null, 'height': null}, {'width': null, 'height': null}];
    for (var g_num=0; g_num<g.num_graphs; g_num++) {
        var graph_bbox = g.graphs[g_num].getBBox();
        
        // Add the graph and graph info to the graph container
        g.graph_containers[g_num].prepend(g.graphs[g_num]);
        
        var max_graph_size = g.max_graph_sizes[g_num];
        var max_container_size = g.max_container_sizes[g_num];
        
        // reposition the graph info
        var y_trans = graph_bbox.height + pad;
        if (max_graph_size.height) {
            y_trans = max_graph_size.height + pad;
        }
        g.graph_info_containers[g_num].transform('t0,' + y_trans);

        // Create the frame
        var frame = null;
        //  TODO: THIS IS MESSY.  Max size should always be set here.
        if (max_graph_size.width && max_graph_size.height) {
            // If we added any vertices or edges then max_size will be set and we should use that
            if (max_container_size.width && max_container_size.height) {
                graph_frame_dim[g_num] = {
                    'width': Math.max(max_graph_size.width, max_container_size.width) + pad, 
                    'height':  Math.max(max_graph_size.height, max_container_size.height) + pad + g.graph_info_height};
            } else {
                graph_frame_dim[g_num] = {
                    'width': max_graph_size.width + pad, 
                    'height': max_graph_size.height + pad + g.graph_info_height};
            }
        } else if (max_container_size.width && max_container_size.height) {
            graph_frame_dim[g_num] = {
                'width': Math.max(graph_bbox.width, max_container_size.width)+pad, 
                'height': Math.max(graph_bbox.height, max_container_size.height)+pad+g.graph_info_height};
        } else {
            graph_frame_dim[g_num] = {'width': graph_bbox.width+pad, 'height': graph_bbox.height+pad+g.graph_info_height};
        }
    }

    // Normalize the frame width.  If there is only a small discrepancy in widths between graphs then make them the same
    if (graph_frame_dim[0]['width'] && graph_frame_dim[1]['width']) {
        if (Math.abs(graph_frame_dim[0]['width'] - graph_frame_dim[1]['width']) < g.graph_frame_normalize_diff) {
            var same_width = Math.max(graph_frame_dim[0]['width'], graph_frame_dim[1]['width']);
            graph_frame_dim[0]['width'] = same_width;
            graph_frame_dim[1]['width'] = same_width;
        }
    }

    // Create the frames
    for (var g_num=0; g_num<g.num_graphs; g_num++) {
        var frame_dim = graph_frame_dim[g_num];
        if (frame_dim['width'] && frame_dim['height']) {
            var frame = snap.rect(0, 0, frame_dim['width'], frame_dim['height'])
            .attr({
                id: 'g' + (g_num+1) + '_frame',
                fill: '#fff',
                
            });
            g.graph_containers[g_num].prepend(frame);
        }
    }
}

function get_graph_x_trans() {
    return (g.code_box.frame_width * g.code_box.scale_factor) + g.padding*2;
}

function position_graph(initial) {
    /* Used for initial translations, and also scaling of graph */
    
    // Record the current scale
    var curr_scale = 1;
    if (g.scaler !== undefined) {
        curr_scale = g.scaler.curr_scale;
    }

    // If the initial translation has not been set then set it
    var x_trans = get_graph_x_trans();
    if (g.init_container_translate === undefined) {
        g['init_container_translate'] = [{x: x_trans, y: g.padding + g.graph_frame_stroke_width}, {x: x_trans, y: g.padding + g.graph_frame_stroke_width}];
    }

    for (var i=0; i<g.num_graphs; i++) {
        var max_size = g.max_graph_sizes[i];
        var container_translate = null;
        
        if (initial === true) {
            // If this is the first time we are calling this function then we want to keep track of the initial translation of the containers
            container_translate = g.init_container_translate[i];
        } else {
            container_translate = {x: x_trans, y: g.padding + g.graph_frame_stroke_width};
        }

        container_translate.y = container_translate.y / curr_scale;
        if (i === 1) {
            container_translate.y = g.graph_containers[0].getBBox().y2;
        }

        // Adjust the translations if we have a max height and width.  
        // If we don't have one, then the original size is ok
        if (initial === true) {
            var graph_bbox = g.graphs[i].getBBox();
            if (max_size.height) {
                var diff = 0;
                if (graph_bbox.height != 0) {
                    if (max_size.min_top && max_size.min_top < g.frame_padding) {
                        diff -= max_size.min_top;
                    }
                }
                if (diff > 0) {
                    g.graph_translate[i]['y'] += diff - g.vertex_r;
                }
            }
            if (max_size.width) {
                var diff = 0;
                if (graph_bbox.width != 0) {
                    if (max_size.min_left && max_size.min_left < g.frame_padding) {
                        diff -= max_size.min_left;
                    }
                }
                if (diff > 0) {
                    g.graph_translate[i]['x'] += diff - g.vertex_r;
                }
            }
        }

        container_translate.x = container_translate.x / curr_scale;
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
            g.animation.change_speed(button_types[i]['speed']);
            buttons[i].attr({'opacity': speed_controls.button_settings.active_opacity});
            g.control_panel.set_text(target_label);
        } else {
            buttons[i].attr({'opacity': speed_controls.button_settings.inactive_opacity});
        }
    }
    g.control_panel.start_speed_menu_close_timeout();
}

function HelpPanel(y_trans, padding, button_panel_height) {
    this.padding = padding;
    this.button_panel_height = button_panel_height;
    this.g = snap.group().attr({'id': 'help_panel_group', 'cursor': 'pointer'})
    .click(show_algo_info);
    this.width = 24;

    this.text_elem = snap.text(0, 0, '?')
    .attr({
        'fill': 'white',
        'font-size': 16,
        'font-family': 'Helvetica',
        'font-weight': 'bold',
        'text-anchor': 'middle',
    });
    var text_bbox = this.text_elem.getBBox();
    this.text_elem.attr({'x': this.width/2, 'y': text_bbox.height + 5})
    this.g.append(this.text_elem);
    this.frame = snap.rect(0, -1*y_trans, this.width, button_panel_height)
    .attr({
        'fill': g.playback_bar_fill,
        'stroke': g.playback_bar_stroke,
        'stroke-width': 1
    });
    
    this.g.prepend(this.frame);
}

function SpeedControls(width, height) {
    /*  Object that represents the row of speed buttons in the
        menu that opens at bottom right 
    */
    this.width = width;
    this.height = height;
    this.g = snap.group();

    this.button_types = [
        {'label': '.25x', 'speed': g.speeds['.25x'], 'default_selected': false},
        {'label': '.5x', 'speed': g.speeds['.5x'], 'default_selected': false},
        {'label': '1x', 'speed': g.speeds['1x'], 'default_selected': false},
        {'label': '2x', 'speed': g.speeds['2x'], 'default_selected': false},
        {'label': '4x', 'speed': g.speeds['4x'], 'default_selected': true},
    ];
    
    this.button_settings = {
        'width': this.width,
        'height': this.height / this.button_types.length,
        'active_opacity': 1,
        'inactive_opacity': .5
    };

    // Create the different buttons
    this.buttons = [];
    for (var i=0; i<this.button_types.length; i++) {
        var type = this.button_types[i];
        var button_g = snap.group()
        .attr({
            'id': type['label'] + '_g',
            'class': 'speed_button',
            'cursor': 'pointer'
        })
        .click(click_speed_button)
        .touchstart(click_speed_button);
        
        var button_text = snap.text(this.button_settings.width/2, 0, type['label']).attr({
            'id': type['label'] + '_button_label',
            'fill': 'white',
            'font-family': 'Helvetica',
            'font-size': 16,
            'text-anchor': 'middle'
        });

        var opacity = this.button_settings.inactive_opacity;
        if (type['default_selected'] === true) {
            opacity = this.button_settings.active_opacity;
        }
        var button = snap.rect(0, 0, this.button_settings.width, this.button_settings.height).attr({
            'id': type['label'] + '_button',
            'fill': '#87afff',
            'stroke': '#476fb4',
            'opacity': opacity,
        });
        button_text.transform('t0,' + (button_text.getBBox().height+5));
        var y_trans = i*this.button_settings.height;
        button_g.transform('t0,' + y_trans);

        button_g.append(button);
        button_g.append(button_text);
        this.buttons.push(button);
        this.g.append(button_g);
    }

    this.height = this.g.getBBox().height;
}

function show_algo_info() {
    /* Pops open the algorithm info iframe */
    g.algo_info_active = true;
    if (!isiPhone()) {
        showPopWin(info_file, g.cont_width*1/2, g.cont_height*1/2, null, false);
        document.getElementById('help_div').className = 'visible';
    } else {
        showPopWin(info_file, g.cont_width*1/2, g.cont_height*1/2, function() {g.algo_info_active = false;}, false);
    }
}

function create_algo_info_button() {
    /* Creates the button that when clicked will show the algorithm info iframe */
    var g = snap.group().attr({
        'cursor': 'pointer'
    })
    .click(show_algo_info)
    .touchstart(show_algo_info);
    var text_elem = snap.text(5, 0, 'Show Algorithm Info');
    var text_bbox = text_elem.getBBox();
    text_elem.attr({'y': text_bbox.height});
    var rect = snap.rect(0, 0, text_bbox.width + 10, text_bbox.height + 7, g.rect_r, g.rect_r).attr({
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
    var link_func = function() {
        window.open('http://bioinformatics.rutgers.edu/Software/Gato/');
    };
    text_elem.click(link_func).touchstart(link_func);
    text_elem.attr({'y': text_elem.getBBox().height});
    g.append(text_elem);
    return g;
}

function ControlPanel(button_panel_height, y_trans) {
    /*  Object that controls the control panel at the bottom right of the screen that is 
        brought up by clicking on the cog.
    */
    this.cursor_in_control_panel = function(evt) {
        var clientX = parseInt(evt.clientX),
            clientY = parseInt(evt.clientY);
        if (Object.prototype.toString.call(evt) === '[object TouchEvent]') {
            clientX = parseInt(evt.changedTouches[0].clientX);
            clientY = parseInt(evt.changedTouches[0].clientY);
        }
        var elem = Snap.getElementByPoint(clientX, clientY);
        while (elem !== null && elem !== snap) {
            if (elem === this.g) {
                return true;
            }
            elem = elem.parent();
        }
        return false;
    };
    this.set_text = function(txt) {
        this.speed_menu_text_content = txt;
        this.speed_menu_text_elem.node.textContent = txt;
    };
    this.start_speed_menu_close_timeout = function() {
        if (g.control_panel.close_timeout) {
            clearTimeout(g.control_panel.close_timeout);
        }
        this.close_timeout = setTimeout(g.control_panel.close, g.speed_menu_close_timeout);
    };

    this.button_panel_height = button_panel_height;
    this.padding = 5;
    this.frame_visibility = false;
    this.g = snap.group().attr({'id': 'control_panel_group', 'cursor': 'pointer'});
    
    this.open_group = snap.group().attr({'id': 'open_group'});
    this.speed_menu_text_content = '.25x';
    this.speed_menu_text_elem = snap.text(0, 20, this.speed_menu_text_content).attr({
        'fill': 'white',
        'font-family': 'Helvetica',
        'font-size': 16,
        'font-weight': 'bold'
    });
    var text_bbox = this.speed_menu_text_elem.getBBox();
    this.text_height = text_bbox.height;
    this.text_width = text_bbox.width;

    this.triang_padding = 9;
    this.triang_x = this.text_width + this.triang_padding;
    this.triang_y = 12;
    this.triang_height = 8;
    this.triang_width = 7;
    this.speed_triang = snap.polygon([this.triang_x-this.triang_width,this.triang_y, this.triang_x,this.triang_y+this.triang_height, this.triang_x+this.triang_width,this.triang_y])
    .attr({'fill': '#87afff'});
    this.open_group.append(this.speed_triang);
    this.open_group.append(this.speed_menu_text_elem);
    this.g.append(this.open_group);

    this.width = this.g.getBBox().width;
    this.set_text('4x');
    this.speed_frame_width = this.width + this.padding*2;
    this.speed_frame_height_closed = this.button_panel_height;
    this.speed_frame_height_open = 200;
    this.speed_frame_x = -1*this.padding;
    this.speed_frame_y_closed = -1*y_trans;
    this.speed_frame_y_open = -1*y_trans - (this.speed_frame_height_open - this.button_panel_height);
    this.speed_frame_open = false;
    this.speed_frame = snap.rect(
        this.speed_frame_x, 
        this.speed_frame_y_closed, 
        this.speed_frame_width, 
        this.speed_frame_height_open)
    .attr({
        'fill': g.playback_bar_fill,
        'stroke': g.playback_bar_stroke,
        'stroke-width': 1
    });
    
    this.open_group.prepend(this.speed_frame);
    this.height = this.g.getBBox().height;  // Get the height with the open height
    this.speed_frame.attr({'height': this.speed_frame_height_closed});
    
    this.speed_controls = new SpeedControls(this.speed_frame_width, this.speed_frame_height_open - this.button_panel_height);
    this.speed_controls.g.attr({'visibility': 'hidden'});
    this.speed_controls.g.transform('t' + this.speed_frame_x + ',' + (-1*(this.speed_frame_height_open - this.button_panel_height + this.padding)));
    this.g.append(this.speed_controls.g);
    if (isiPhone()) {
        this.width = this.speed_controls.width;
    } else {
        // If it isn't an iPad or iPhone then we want to display the HelpPanel at the bottom of the screen
        this.help_panel = new HelpPanel(y_trans, this.padding, button_panel_height);
        this.g.append(this.help_panel.g);
        this.help_panel.g.transform('t' + (this.speed_controls.width-this.padding) + ',0');
        this.width = this.speed_controls.width + this.help_panel.width-this.padding;
    }

    this.close_timeout = null;
    this.toggle_visibility = (function(self) {
        return function() {
            self.speed_frame_open = !self.speed_frame_open;
            if (self.speed_frame_open) {
                g.control_panel.speed_controls.g.attr({'visibility': 'visible'});
                self.speed_frame.attr({'y': self.speed_frame_y_open, 'height': self.speed_frame_height_open});
                self.frame_visibility = true;
            } else {
                g.control_panel.speed_controls.g.attr({'visibility': 'hidden'});
                self.speed_frame.attr({'y': self.speed_frame_y_closed, 'height': self.speed_frame_height_closed});
                self.frame_visibility = false;
                if (self.close_timeout) {
                    clearTimeout(self.close_timeout);
                    self.close_timeout = null;
                }
            }
        }
    })(this);
    this.close = (function(self) {
        return function() {
            self.speed_frame_open = false;
            g.control_panel.speed_controls.g.attr({'visibility': 'hidden'});
            self.speed_frame.attr({'y': self.speed_frame_y_closed, 'height': self.speed_frame_height_closed});
            self.frame_visibility = false;
            if (self.close_timeout) {
                clearTimeout(self.close_timeout);
                self.close_timeout = null;
            }
        }
    })(this);
    this.open_group.click(this.toggle_visibility)
        .touchstart(this.toggle_visibility)
        .click(this.start_speed_menu_close_timeout)
        .touchstart(this.start_speed_menu_close_timeout);
}

function PlaybackBar() {
    /* Object to represent the whole playback bar at the bottom */
    this.g = snap.group().attr({'visibility': 'hidden'}); // hide the playback bar at start
    if (isiPhone()) {
        this.width = g.cont_width;
    } else {
        this.width = g.cont_width * 3/4 - g.padding*2;
    }
    this.min_width = 350;
    this.height = 40;
    this.padding_y = 5;
    this.padding_x = 15;
    this.bg_color = g.playback_bar_fill;
    this.stroke = g.playback_bar_stroke;
    this.stroke_width = g.playback_bar_stroke_width;

    this.frame = snap.rect(0, 0, this.width, this.height, g.rect_r, g.rect_r).attr({
        'fill': this.bg_color,
        'stroke': this.stroke,
        'stroke-width': this.stroke_width,
    });
    this.g.append(this.frame);

    g.button_panel = new ButtonPanel();
    g.button_panel.g.transform('t' + this.padding_x + ',' + this.padding_y);
    this.g.append(g.button_panel.g);

    g.control_panel = new ControlPanel(this.height, this.padding_y);
    this.control_panel_x = this.width - this.padding_x - g.control_panel.width;
    g.control_panel.g.transform('t' + this.control_panel_x + ',' + this.padding_y);
    this.g.append(g.control_panel.g);

    this.slider_width = this.width - this.padding_x*4 - g.button_panel.width - g.control_panel.width;
    this.slider_height = this.height - this.padding_y*2;
    g.slider = new Slider(this.slider_width, this.slider_height);
    this.slider_x_trans = g.button_panel.width + this.padding_x*2;
    g.slider.g.transform('t' + this.slider_x_trans + ',' + this.padding_y)
    this.g.append(g.slider.g);

    this.compute_translate = function() {
        if (isiPhone()) {
            this.x_translate = 0;
            this.y_translate = g.cont_height - this.height;
        } else {
            this.x_translate = g.cont_width/8 + g.padding;
            this.y_translate = g.cont_height - this.height - g.padding;
        }
    };
    this.compute_translate();
    this.g.transform('t' + this.x_translate + ',' + this.y_translate);
}

PlaybackBar.prototype.resize = function() {
    /* Called on window resize to redraw */
    var new_width = g.cont_width * 3/4 - g.padding*2;
    if (isiPhone()) {
        new_width = g.cont_width;
    }
    if (new_width > this.min_width) {
        this.width = new_width;
        this.frame.attr({'width': this.width});
        this.compute_translate();
        this.g.transform('t' + this.x_translate + ',' + this.y_translate);

        this.control_panel_x = this.width - this.padding_x - g.control_panel.width;
        g.control_panel.g.transform('t' + this.control_panel_x + ',' + this.padding_y);

        var new_slider_width = this.width - this.padding_x*4 - g.button_panel.width - g.control_panel.width;
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
        buttons.step.pulsate();
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
    this.g = snap.group().attr({'visibility': 'hidden'});
    this.width = 205;

    this.buttons = {};
    this.buttons['start'] = new Button(start_click, 'M0,0 0,30 20,15 Z', true, [0,0], [20, 30]);
    this.g.append(this.buttons['start'].click_receiver);
    this.g.append(this.buttons['start'].button);
    this.buttons['step'] = new Button(step_click, 'M0,0 0,30 20,15 Z M20,0 20,30 30,30 30,0 Z', false, [50,0], [30, 30]);
    this.g.append(this.buttons['step'].click_receiver);
    this.g.append(this.buttons['step'].button);
    this.buttons['continue'] = new Button(continue_click, 'M0,0 0,30 10,30 10,0 Z M15,0 15,30 35,15 Z', false, [110,0], [35, 30]);
    this.g.append(this.buttons['continue'].click_receiver);
    this.g.append(this.buttons['continue'].button);
    this.buttons['stop'] = new Button(stop_click, 'M0,0 0,30 30,30 30,0 Z', false, [175,0], [30, 30]);
    this.g.append(this.buttons['stop'].click_receiver);
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

function Button(click_handler, path_str, active, translate, dim) {
    /*  This object represents one of the buttons that control animation
        that are located at the left side of the playback bar.
        click_handler: the function to be called on click
        path_str: the path string to pass to snap
        active: true/false whether or not the button is active
        translate: [x, y] array representing translation
        dim: [width, height] array representing the width and height of the button, to be used for making a larger click handler
    */
    this.color = '#87afff';
    this.pulse_color = '#547ccc';
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
    var extra_width = 20;
    var extra_height = 20;
    this.click_receiver = snap.rect(extra_width/2.0*-1, extra_height/2.0*-1, dim[0]+extra_width, dim[1]+extra_height).attr(
    {
        'opacity': 0,
    }).click(click_handler).touchstart(click_handler);
    if (this.active) {
        this.button.attr(this.active_attr);
    } else {
        this.button.attr(this.inactive_attr);
    }
    this.button.transform('t' + translate[0] + ',' + translate[1]);
    this.click_receiver.transform('t' + translate[0] + ',' + translate[1]);

    this.set_active = function() {
        this.active = true;
        this.button.animate({'fill-opacity': this.active_opacity}, 250);
        this.button.attr({'cursor': 'pointer'});
    };
    this.set_inactive = function() {
        this.active = false;
        this.button.animate({'fill-opacity': this.inactive_opacity}, 250);  
        this.button.attr({'cursor': 'default'});    
    };
    this.pulsate = function() {
        this.button.animate({'fill': this.pulse_color}, 125);
        var self = this;
        setTimeout(function() {
            self.button.animate({'fill': self.color}, 125);
        }, 125);
    };
}


function BreakPoint(width, breakpoint_num) {
    /*  This object represents the line breakpoints */
    this.click = function() {
        if (this.active === true) {
            this.active = false;
            this.button.attr({'opacity': this.inactive_opacity, 'fill': this.inactive_fill});
        } else {
            this.active = true;
            this.button.attr({'opacity': this.active_opacity, 'fill': this.active_fill});
        }
    };
    this.g = snap.group();
    this.active = false;
    this.active_opacity = .9;
    this.inactive_opacity = .3;
    this.inactive_fill = 'blue';
    this.active_fill = '#E30000';

    var path_str = 'M0 0 L8 0 L12 4 L8 8 L0 8 L0 0 Z';
    var self = this;    
    var click_func = function() {
        self.click();
    };
    this.button = snap.path(path_str)
    .attr({
        'id': 'breakpoint_' + breakpoint_num,
        'fill': this.inactive_fill,
        'opacity': this.inactive_opacity,
        'cursor': 'pointer'
    })
    .mousedown(click_func);
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

        // Set the click handler of highlight_box to the line it is covering
        if (this.current_highlight_box_click !== undefined) {
            this.highlight_box.unclick(this.current_highlight_box_click).untouchstart(this.current_highlight_box_click);
        }
        this.current_highlight_box_click = function() {
            g.code_box.breakpoints[line_id].click();
        };
        this.highlight_box.click(this.current_highlight_box_click).touchstart(this.current_highlight_box_click);
    };
    this.remove_highlighting = function()   {
        this.highlight_box.attr({'opacity': 0});
    };
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
                'font-size': 14,
                'cursor': 'pointer'
            });
            // Bind breakpoint click to the line number click
            (function (e, line_key) {
                var line_num_click = function() {
                    g.code_box.breakpoints[line_key].click();
                };
                e.mousedown(line_num_click);
            })(elem, key);
            this.g.append(elem);
        }
    };
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
    };
    this.is_line_breakpoint_active = function(line_id) {
        return this.breakpoints[line_id].active;
    };
    this.scale_and_translate = function() {
        /*  This function is called at the beginning of the program and will
            scale the codebox based on vertical and horizontal dimensions
        */
        if (!this.initial_bbox) {
            this.initial_bbox = this.g.getBBox();
        }
        var playback_bbox = g.playback_bar.g.getBBox();
        var max_height = playback_bbox.y + g.control_panel.height - g.playback_bar.height - g.padding*2 - this.initial_bbox.y - g.navbar_height;
        var max_scale_factor_y = max_height / this.initial_bbox.height;
        var max_width = g.cont_width * .5;
        var max_scale_factor_x = max_width / this.initial_bbox.width;
        var max_scale_factor = Math.min(max_scale_factor_y, max_scale_factor_x);
        this.scale_factor = 1;
        if (max_scale_factor < 1) {
            this.scale_factor = max_scale_factor;
        }
        var scale = 's' + this.scale_factor + ',0,0';
        var translate = 't' + g.padding + ',' + g.padding;
        this.g.transform(translate + scale);

        // Resize the frame and highlight box
        // Remove the frame and highlight_box before getting the bbox, so the bbox tells us how wide the lines are
        this.frame.remove();    
        this.highlight_box.remove();
        var bbox = this.g.getBBox();
        this.frame_width = bbox.width / this.scale_factor + this.padding;
        this.frame.attr({'width': this.frame_width});
        this.highlight_box_width = this.frame_width - this.highlight_box_x;
        this.highlight_box.attr({'width': this.highlight_box_width});
        this.g.prepend(this.frame);
        this.g.append(this.highlight_box);
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
    this.g = snap.group().attr({'visibility': 'hidden'}); // hide the codebox at start
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

    this.frame = snap.rect(0, 0, this.frame_width, this.frame_height, g.rect_r, g.rect_r).attr({
        fill: g.codebox_fill,
        stroke: g.playback_bar_stroke,
        strokeWidth: g.codebox_stroke_width,
    });
    this.g.prepend(this.frame);

    // Add a highlight box 
    this.highlight_box_padding = {x: 8, y: 2};
    this.highlight_box_opacity = .35;
    this.highlight_box_x = this.line_x - this.highlight_box_padding.x/2;
    this.highlight_box_width = this.frame_width - this.highlight_box_x;
    this.highlight_box = snap.rect(this.highlight_box_x, 0, this.highlight_box_width, this.line_padding + this.highlight_box_padding.y, g.rect_r, g.rect_r).attr({
        'id': 'highlight_box',
        'fill': 'yellow',
        'stroke': 'blue',
        'stroke-width': 1,
        'opacity': .35,
        'cursor': 'pointer'
    });
    var line_id = "";
    for (var key in g.code_lines) {
        line_id = key;
        break;
    }
    this.current_highlight_box_click = function() {
        g.code_box.breakpoints[line_id].click();
    };
    this.highlight_box.click(this.current_highlight_box_click).touchstart(this.current_highlight_box_click);
    g.highlight_boxes[0] = {'highlight_box': this.highlight_box};
    this.g.append(this.highlight_box);
    this.remove_highlighting();

    // Add line numbers and breakpoints
    this.add_line_numbers();
    this.add_break_points();

    for (var key in g.code_lines) {
        var curr_line = g.code_lines[key];
        (function (codebox, closure_key) {
            var line_click_func = function() {
                codebox.breakpoints[closure_key].click();
            };
            curr_line.mousedown(line_click_func);
        })(this, key);
    }

    this.scale_and_translate();
}


function NavBar() {
    this.padding = g.navbar_padding;
    this.width = g.cont_width - g.padding*2;
    this.height = g.navbar_height;
    this.font_size = 15;

    this.g = nav_snap.group().attr({'id': 'navbar_g'});

    // Create backlink
    this.backlink_g = nav_snap.group().attr({'id': 'backlink_g', 'cursor': 'pointer'});
    var h = this.height - this.padding*2 - g.ios_statusbar_height;
    var p = 5.0;
    var k = Math.sqrt(2.0*Math.pow(p, 2));
    var f = Math.pow(p,2) / k;
    this.backlink_poly = nav_snap.polygon([
        0, h/2.0,
        h/2.0, h,
        h/2.0 + k/2.0, h - Math.pow(p,2)/k,
        k, h/2.0,
        h/2.0 + k/2.0, Math.pow(p,2) / k,
        h/2.0, 0
    ]).attr({
        'fill': '#ccc'
    });
    this.backlink_g.append(this.backlink_poly);
    this.backlink_text = nav_snap.text(h/2.0 + k/2.0 + this.padding, h/2.0 + 5, "Index").attr({
        'fill': '#ccc',
        'font-family': 'Helvetica',
        'font-size': this.font_size,
    });
    this.backlink_g.append(this.backlink_text);
    var backlink_bbox = this.backlink_g.getBBox();
    this.backlink_rect = nav_snap.rect(0, 0, backlink_bbox.width, backlink_bbox.height).attr({
        'fill': 'white'
    });
    this.backlink_g.prepend(this.backlink_rect);
    this.backlink_g.click(
        function() {
            window.location = 'index.html#' + algo_div;
        }
    );
    this.g.append(this.backlink_g);

    // Create the title and chapter name
    this.chapter_title = nav_snap.text(this.width/2, h/2.0 + 5, chapter_name + ': ').attr({
        'fill': '#333',
        'font-family': 'Helvetica',
        'font-size': this.font_size,
        'text-anchor': 'start',
        'font-weight': 'bold'
    });
    this.g.append(this.chapter_title);
    this.anim_title = nav_snap.text(this.width/2 + this.chapter_title.getBBox().width/2, h/2.0 + 5, animation_name).attr({
        'fill': '#333',
        'font-family': 'Helvetica',
        'font-size': this.font_size,
        'text-anchor': 'start'
    });
    this.g.append(this.anim_title);
    this.chapter_title_width = this.chapter_title.getBBox().width;
    this.anim_title_width = this.anim_title.getBBox().width;
    this.chapter_title.attr({'x': this.width/2 - (this.chapter_title_width + this.anim_title_width)/2});
    this.anim_title.attr({'x': this.width/2 + 3 - ((this.chapter_title_width + this.anim_title_width)/2 - this.chapter_title_width)});

    this.info_link = nav_snap.text(this.width - this.padding, h/2.0 + 5, 'Legend').attr({
        'fill': '#ccc',
        'font-family': 'Helvetica',
        'font-size': this.font_size,
        'text-anchor': 'end',
        'cursor': 'pointer'
    }).click(show_algo_info);
    this.g.append(this.info_link);
    this.info_link_width = this.info_link.getBBox().width;

    this.help_link = nav_snap.text(0, h/2.0 + 5, "Help").attr({
        'fill': '#ccc',
        'font-family': 'Helvetica', 
        'font-size': this.font_size,
        'text-anchor': 'middle',
        'cursor': 'pointer'
    }).click(function() {
        window.location = 'help.html?last_page=' + g.this_url;
    });
    this.help_link.attr({'x': this.width - this.info_link_width - this.help_link.getBBox().width - 5});
    this.g.append(this.help_link);

    this.g.transform('t' + g.padding + ',' + (g.ios_statusbar_height+g.navbar_padding));

    this.resize = function() {
        this.width = g.cont_width - g.padding*2;
        this.chapter_title.attr({'x': this.width/2 - (this.chapter_title_width + this.anim_title_width)/2});
        this.anim_title.attr({'x': this.width/2 + 3 - ((this.chapter_title_width + this.anim_title_width)/2 - this.chapter_title_width)});

        // this.cog.attr({'x': this.width - this.cog_dim});
        this.info_link.attr({'x': this.width - this.padding});
        this.help_link.attr({'x': this.width - this.info_link_width - this.help_link.getBBox().width - 5});
    };
}