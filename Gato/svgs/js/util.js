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

function do_interval(func, speed_ms) {
    /*  Given speed in ms and a function to execute this 
        is the same as setInterval(), but it is more accurate
    */
    var start = (new Date()).getTime();
    var steps = 0;

    function instance()
    {
        if (g.animation.state !== 'animating') {
            return;
        }
        func();
        var now = (new Date()).getTime();
        steps += 1;
        var should_run_at = start + speed_ms*steps;
        var next_run_ms = should_run_at - now;
        window.setTimeout(instance, next_run_ms);
    }

    window.setTimeout(instance, speed_ms);
}

function isPhoneGap() {
    return (cordova || PhoneGap || phonegap) 
    && /^file:\/{3}[^\/]/i.test(window.location.href) 
    && /ios|iphone|ipod|ipad/i.test(navigator.userAgent);
}

function isiPhone(){
    /* This is poorly named, it detects mobile generally */
    return (
        //Detect iPhone
        (navigator.platform.indexOf("iPhone") != -1) ||
        //Detect iPod
        (navigator.platform.indexOf("iPod") != -1) ||
        (navigator.platform.indexOf("iPad") != -1) ||
        (navigator.userAgent.toLowerCase().indexOf('android') != -1)
    );
}

function add_scaler() {
    g.scaler = new Scaler();
    g.graph_containers[g.num_graphs-1].append(g.scaler.click_receiver);
    g.graph_containers[g.num_graphs-1].append(g.scaler.elem);
}

function get_bubble_id(vertex, vertex_nums) {
    // Given a vertex attr and the vertex numbers the bubble connects, return a bubble id
    return vertex.attr('id') + '_bubble_' + vertex_nums.join('-');
}

function get_vertex_id(g_num, vertex_num) {
    // Given a graph number and a vertex number construct an id
    return 'g' + g_num + '_' + vertex_num;
}

function is_multiple_vertices(add_vertex_str) {
    // Returns true if the add_vertex_str has multiple vertices
    var re = /\d+/g;
    var matches = add_vertex_str.match(re);
    if (matches && matches.length > 1) {
        return true;
    }
    return false;
}

function get_ints_from_str(list_str) {
    // Given a python list of ints, return a javascript array of ints
    var re = /\d+/g;
    var matches = list_str.match(re);
    if (matches) {
        return matches.map(function(x) {
            return parseInt(x);
        });
    } else {
        return null;
    }
}

function get_int_from_str(str) {
    var re = /\d+/g;
    var match = str.match(re);
    if (match) {
        return parseInt(match[0]);
    } else {
        return nil;
    }
}

function get_floats_from_str(list_str) {
    // Given a python list of floats, return a javascript array of floats
    var re = /[+-]?\d+(\.\d+)?/g;
    var matches = list_str.match(re);
    if (matches) {
        return matches.map(function(x) {
            return parseFloat(x);
        });
    } else {
        return null;
    }
}


function get_moat_growing_time(step_num) {
    // Given a step_number, this will find the first Wait() command
    // that follows that step_number and return the animation length of that Wait command
    for (var i=step_num; i<anim_array.length; i++) {
        var anim = anim_array[i];
        if (anim[1] === Wait) {
            return anim[0];
        }
    }
    return 1;
}

function switch_edge_vertices(edge_id, suffix) {
    // Switches the edge_id vertices.  ie. g1_(5, 4) in --> g1_(4, 5) out
    var re = /\d+/g;
    var matches = edge_id.match(re);
    var new_id = "g" + matches[0] + "_" + matches[2] + "-" + matches[1];
    if (suffix) {
        new_id += suffix;
    }
    return new_id;
}

function get_edge_vertices(edge_id) {
    // Returns the two vertices an edge is connecting.  If edge_id is malformed returns null
    var re = /\d+/g;
    var matches = edge_id.match(re);
    if (matches) {
        return matches.slice(1);
    }
    return null;
}

function get_vertex_num(id) {
    // Returns an int representing the number associated with the vertex
    var re = /\d+/g;
    var matches = id.match(re);
    if (matches) {
        return matches[1];
    }
    return null;
}

function get_default_edge_info(edge_g_id, graph_index) {
    // Given an edge id this will reutrn the initial edge info
    var vertices = get_edge_vertices(edge_g_id);
    var init_infos = g.init_edge_infos[graph_index];
    if (!init_infos) {
        return 'Edge (' + vertices[0] + ', ' + vertices[1] + ')';
    }
    var edge_id = edge_g_id.split('_group')[0];
    var info = init_infos[edge_id];
    if (!info) {
        info = init_infos[switch_edge_vertices(edge_id)];
    }
    if (!info) {
        if (!vertices) {
            info = '';
        } else {
            info = 'Edge (' + vertices[0] + ', ' + vertices[1] + ')';
        }
    }
    return info;
}

function get_default_vertex_info(vertex_g_id, graph_index) {
    // Given a vertex id this will return the initial info
    var init_infos = g.init_vertex_infos[graph_index];
    var vertex_num = get_vertex_num(vertex_g_id);
    if (!init_infos) {
        return 'Vertex ' + vertex_num;
    }
    var vertex_id = vertex_g_id.split('_group')[0];
    var info = init_infos[vertex_id];
    if (!info) {
        return 'Vertex ' + vertex_num;
    }
    return info;
}

// TODO: This and the next function both use the max_sizes object... that seems wrong
function record_max_graph_size(g_num) {
    // Checks to see if any of the graphs are bigger then they were before
    // If they are at a current max size we record that
    // We use this info to set the size of the graph frame to the largest size of the graphsaph
    //
    // Also finds the minimum x and y of each graph and sets the g.coord_changes to that
    for (var i=0; i<g.num_graphs; i++) {
        // Get the max sizes
        var bbox = g.graphs[i].getBBox();
        var width = bbox.width;
        var height = bbox.height;
        var x = bbox.x;
        var max_sizes = g.max_graph_sizes[i];
        if (!max_sizes.width || width > max_sizes.width) {
            max_sizes.width = width;
        }
        if (!max_sizes.height || height > max_sizes.height) {
            max_sizes.height = height;
        }
        if (!max_sizes.min_left || x < max_sizes.min_left) {
            max_sizes.min_left = x;
        }
        if (!max_sizes.min_top || bbox.y < max_sizes.min_top) {
            max_sizes.min_top = bbox.y;
        }
    }
}

function record_max_container_size(g_num) {
    for (var i=0; i<g.num_graphs; i++) {
        var bbox = g.graph_containers[i].getBBox();
        var width = bbox.width;
        var height = bbox.height;
        var x = bbox.x;
        var max_sizes = g.max_container_sizes[i];
        if (!max_sizes.width || width > max_sizes.width) {
            max_sizes.width = width;
        }
        if (!max_sizes.height || height > max_sizes.height) {
            max_sizes.height = height;
        }
        if (!max_sizes.min_left || x < max_sizes.min_left) {
            max_sizes.min_left = x;
        }
    }
}


function remove_trailing_whitespace_lines() {
    // This function will remove any line elements from the g.code_lines object 
    // and the canvas if they are trailing whitespace lines

    // Find the last line that has content 
    var last_content = 0;
    for (var key in g.code_lines) {
        var line = g.code_lines[key];
        var line_num = parseInt(key.split('_')[1]) ;
        if (line['whitespace'] !== true && line_num > last_content) {
            last_content = line_num;
        }
    }

    // Delete any lines that come after the last line with content
    for (var key in g.code_lines) {
        var line = g.code_lines[key];
        var line_num = parseInt(key.split('_')[1]) ;
        if (line_num > last_content) {
            delete g.code_lines[key];
            line.remove();
        }
    }
}

function get_evt_target(evt) {
    // Returns the target of an event.  We need this because
    // the attribute is stored in different places for different browsers
    var target = evt.srcElement;
    if (!target) {
        target = evt.target;
    }
    return target;
}

function construct_AddVertex_argument_from_state(state) {
    // Given a state object of a vertex this will create the argument
    // to AddVertex that will produce that vertex
    var g_num = parseInt(state['id'].substring(1,2));
    var x = parseFloat(state['cx']) + g.coord_changes[g_num-1].x;
    var y = parseFloat(state['cy']) + g.coord_changes[g_num-1].y;
    return 'g' + g_num + '_(' + x + ', ' + y + ')';
}

function remove_scheduled_vertex_blinks(vertex_id) {
    // Given a vertex_id this will remove any scheduled vertex blinks, if any
    var timeout_arr = g.blinking_vertices[vertex_id];
    for (var i=0; i<timeout_arr.length; i++) {
        clearTimeout(timeout_arr[i]);
    }
    delete g.blinking_vertices[vertex_id];
}

function remove_all_scheduled_vertex_blinks() {
    for (var id in g.blinking_vertices) {
        remove_scheduled_vertex_blinks(id);
    }
}

function remove_scheduled_edge_blinks(edge_id) {
    // Given an edge_id this will remove any scheduled edge blinks, if any
    var timeout_arr = g.blinking_edges[edge_id];
    for (var i=0; i<timeout_arr.length; i++) {
        clearTimeout(timeout_arr[i]);
    }
    delete g.blinking_edges[edge_id];
}

function remove_all_scheduled_edge_blinks() {
    // Need I explain?
    for (var id in g.blinking_edges) {
        remove_scheduled_edge_blinks(id);
    }
}

function get_id(node) {
    // Given a DOM node it will return the 'id' if it is present, else null.
    // We use this when getting the id of an event target
    var attributes = node.attributes;
    for (var attr in attributes) {
        var a = attributes[attr];
        if (a.name === 'id') {
            return a.value;
        }
    }
    return null;
}

function graph_num_from_id (id) {
    // Returns the index we use to reach the represented graph in all the global datastructures
    return parseInt(id.substring(1,2)) - 1;
}

function Orthogonal(dx, dy){
    // Return a 2-index array [v1,v2] which has an angle of
    // 90 degrees clockwise to the vector (dx,dy)
    // Used when creating arrowheads
    
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

function extend(a, b) {
    // Updates object a with properties in object b
    for (var key in b) {
        a[key] = b[key];
    }
}