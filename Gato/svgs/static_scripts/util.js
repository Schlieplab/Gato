function switch_edge_vertices(edge_id) {
    // Switches the edge_id vertices.  ie. g1_(5, 4) in --> g1_(4, 5) out
    var re = /\d+/g;
    var matches = edge_id.match(re);
    return "g" + matches[0] + "_" + matches[2] + "-" + matches[1];
}

function get_edge_vertices(edge_id) {
    /* Returns the two vertices an edge is connecting.  If edge_id is malformed returns null */
    var re = /\d+/g;
    var matches = edge_id.match(re);
    if (matches) {
        return matches.slice(1);
    }
    return null;
}

function get_default_edge_info(edge_id) {
    var graph_index = parseInt(edge_id.substring(1,2))-1;
    var init_infos = g.init_edge_infos[graph_index];
    var info = init_infos[edge_id];
    if (!info) {
        info = init_infos[switch_edge_vertices(edge_id)];
    }
    if (!info) {
        var vertices = get_edge_vertices(edge_id);
        if (!vertices) {
            info = '';
        } else {
            info = 'Edge (' + vertices[0] + ', ' + vertices[1] + ')';
        }
    }
    return info    
}

function fix_coord_changes() {
    // 
    for (var g_num=0; g_num<g.num_graphs; g_num++) {
        var coords = g.coord_changes[g_num];
        if (g.min_x[g_num] !== null) {
            coords.x = Math.max(coords.x, g.min_x[g_num]);
        }
        if (g.min_y[g_num] !== null) {
            coords.y = Math.max(coords.y, g.min_y[g_num]);
        }
    }
}

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
        var max_sizes = g.max_graph_sizes[i];
        if (width > max_sizes.width) {
            max_sizes.width = width;
        }
        if (height > max_sizes.height) {
            max_sizes.height = height;
        }
    }
}


function remove_trailing_whitespace_lines() {
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
    var target = evt.srcElement;
    if (!target) {
        target = evt.target;
    }
    return target;
}

function remove_all_scheduled_vertex_blinks() {
    for (var id in g.blinking_vertices) {
        remove_scheduled_vertex_blinks(id);
    }
}

function remove_scheduled_vertex_blinks(vertex_id) {
    var timeout_arr = g.blinking_vertices[vertex_id];
    for (var i=0; i<timeout_arr.length; i++) {
        clearTimeout(timeout_arr[i]);
    }
    delete g.blinking_vertices[vertex_id];
}

function remove_all_scheduled_edge_blinks() {
    for (var id in g.blinking_edges) {
        remove_scheduled_edge_blinks(id);
    }
}

function construct_AddVertex_argument_from_state(state) {
    var g_num = parseInt(state['id'].substring(1,2));
    var x = parseFloat(state['cx']) + g.coord_changes[g_num-1].x;
    var y = parseFloat(state['cy']) + g.coord_changes[g_num-1].y;
    return 'g' + g_num + '_(' + x + ', ' + y + ')';
}

function remove_scheduled_edge_blinks(edge_id) {
    var timeout_arr = g.blinking_edges[edge_id];
    for (var i=0; i<timeout_arr.length; i++) {
        clearTimeout(timeout_arr[i]);
    }
    delete g.blinking_edges[edge_id];
}

function get_id(node) {
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
    return parseInt(id.substring(1,2)) - 1;
}

function exit( status ) {
    // http://kevin.vanzonneveld.net
    // +   original by: Brett Zamir (http://brettz9.blogspot.com)
    // +      input by: Paul
    // +   bugfixed by: Hyam Singer (http://www.impact-computing.com/)
    // +   improved by: Philip Peterson
    // +   bugfixed by: Brett Zamir (http://brettz9.blogspot.com)
    // %        note 1: Should be considered expirimental. Please comment on this function.
    // *     example 1: exit();
    // *     returns 1: null

    var i;

    if (typeof status === 'string') {
        alert(status);
    }

    window.addEventListener('error', function (e) {e.preventDefault();e.stopPropagation();}, false);

    var handlers = [
        'copy', 'cut', 'paste',
        'beforeunload', 'blur', 'change', 'click', 'contextmenu', 'dblclick', 'focus', 'keydown', 'keypress', 'keyup', 'mousedown', 'mousemove', 'mouseout', 'mouseover', 'mouseup', 'resize', 'scroll',
        'DOMNodeInserted', 'DOMNodeRemoved', 'DOMNodeRemovedFromDocument', 'DOMNodeInsertedIntoDocument', 'DOMAttrModified', 'DOMCharacterDataModified', 'DOMElementNameChanged', 'DOMAttributeNameChanged', 'DOMActivate', 'DOMFocusIn', 'DOMFocusOut', 'online', 'offline', 'textInput',
        'abort', 'close', 'dragdrop', 'load', 'paint', 'reset', 'select', 'submit', 'unload'
    ];

    function stopPropagation (e) {
        e.stopPropagation();
        // e.preventDefault(); // Stop for the form controls, etc., too?
    }
    for (i=0; i < handlers.length; i++) {
        window.addEventListener(handlers[i], function (e) {stopPropagation(e);}, true);
    }

    if (window.stop) {
        window.stop();
    }

    throw '';
}

//Return a 2-index array [v1,v2] which has an angle of
//90 degrees clockwise to the vector (dx,dy)
function Orthogonal(dx, dy){

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


//Translate client coordinates to svg coordinates.  If given element then translates to coordinates
//in that elements coordinate system
function cursorPoint(evt, element){
    pt = {x: evt.clientX, y: evt.clientY};
    if (element === null || element === undefined)
        return pt.matrixTransform(document.getScreenCTM().inverse());
    else
        return pt.matrixTransform(document.getScreenCTM().inverse());
}


function get_translate(elem) {
    var trans = document.getElementById(elem.attr('id')).getAttribute('transform');
    var l_paren_split = trans.split('(');
    var found = false;
    var x_tran = 0, y_tran = 0;
    for (var i=0; i<l_paren_split.length; i++) {
        if (found === true) {
            var r_paren_split = l_paren_split[i].split(')');
            if (r_paren_split[0].indexOf(',') === -1) {
                x_tran = parseInt(r_paren_split[0]);
            } else {
                var comma_split = r_paren_split[0].split(',');
                x_tran = parseInt(comma_split[0]);
                y_tran = parseInt(comma_split[1]);
            }
            found = false;
        }
        if (l_paren_split[i].indexOf('translate') !== -1) {
            found = true;
        }
    }
    return [x_tran, y_tran];
}

function set_translate(elem, x, y){
    var transformation = document.getElementById(elem.attr('id')).getAttribute('transform');

    if(transformation != null){
        if(transformation.indexOf("translate") == -1){
            elem.transform(transformation + " translate(" + x + " " + y + ")");
        }else{
            var header = transformation.substring(0, transformation.indexOf("translate") + "translate".length);
            var trailer = transformation.slice(transformation.indexOf("translate") + "translate".length);
            trailer = trailer.slice(trailer.indexOf(")"));
            var newattr = header + "(" + x + " " + y + trailer;
            elem.transform(newattr);
        }
    }else{
        elem.transform("translate(" + x + " " + y + ")");
    }
}
