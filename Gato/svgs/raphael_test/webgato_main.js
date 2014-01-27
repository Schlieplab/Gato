/*
TODO: Change the coordinates of the graph frame to start at 0,0 instead of having negative coordinates.  This will make scaling work

*/


var snap = Snap("svg");
var g = {}; // globals

function add_snap_vars(obj) {
    var vertices = {}, edges = {}, edge_arrows = {}, code_lines = {};
    for (var graph_num=0; graph_num<obj.num_graphs; graph_num++) {
        var v = snap.selectAll('g#g' + graph_num + ' .vertex');
        for (var i=0; i<v.length; i++) {
            vertices[v[i].attr('id')] = v[i]
        }
        var e = snap.selectAll('g#g' + graph_num + ' .edge');
        for (var i=0; i<e.length; i++) {
            edges[e[i].attr('id')] = e[i]
        }
        var ea = snap.selectAll('g#g' + graph_num + ' .arrowhead');
        for (var i=0; i<ea.length; i++) {
            edge_arrows[ea[i].attr('id')] = edge_arrows[i]
        }
        var lines = snap.selectAll('.code_line');
        for (var i=0; i<lines.length; i++) {
            code_lines[lines[i].attr('id')] = lines[i];
        }
    }
    obj['vertices'] = vertices;
    obj['edges'] = edges;
    obj['edge_arrows'] = edge_arrows;
    obj['code_lines'] = code_lines;
    obj['g1'] = snap.select('g#g1');
    obj['g2'] = snap.select('g#g2');
}

function fill_global() {
	var cont_width = $(window).width();
	var cont_height = $(window).height();

	$.extend(g, {
		// Animation variables
		step_ms: 5,		// Time in ms of a single step

		// Global 
		cont_width: cont_width,
		cont_height: cont_height,
        padding: Math.min(Math.ceil(cont_width*.02), Math.ceil(cont_height)*.02),
		
		// Code Box
		line_padding: 16,
		code_box_padding: 6,
		breakpoint_width: 16,
		line_number_width: 16,
		
		// Graph 
		vertex_r: parseInt(snap.select('g#g1 .vertex').attr('r')),
        frame_padding: 8,
        g1_container: snap.group().attr({'id': 'g1_container'}),
        g2_container: snap.group().attr({'id': 'g2_container'}),
        graph_frame_stroke_width: 1,

        // General
        num_graphs: 2,
    	arrow_id_prefix: 'ea',
	});
    add_snap_vars(g);
}

function Scaler() {
	this.mousedown = function(evt) {
		g.scaler.scaling = true;
		g.scaler.start_mouse = [parseInt(evt.x), parseInt(evt.y)];
	}
	this.mouseup = function(evt) {
		g.scaler.scaling = false;
	}
	this.do_scale = function(evt) {
		var dx = parseInt(evt.x) - g.scaler.start_mouse[0];
		var dy = parseInt(evt.y) - g.scaler.start_mouse[1];
		console.log(dx);
		console.log(dy);

		var graph_bbox = g.g1.getBBox();
		var curr_width = graph_bbox.width;
		var new_width = curr_width + dx;
		console.log(new_width);
		var scale_factor = new_width / curr_width;
		g.scaler.curr_scale = scale_factor;
		g.g1_scale = 's' + g.scaler.curr_scale + ',0,0';
		var trans = 't' + g.g1_container_translate[0] + ',' + g.g1_container_translate[1] + g.g1_scale;
		g.g1_container.transform(trans);
	}

	var bbox = g.g1_container.getBBox();
	this.scaling = false;
	this.width = 10;
	this.height = 10;
	this.x = bbox.width - this.width;
	this.y = bbox.height + g.frame_padding - this.height;

	this.elem = snap.polygon([this.x, this.y, this.x+this.width, this.y, this.x+this.width, this.y-this.height, this.x, this.y]).attr({
		'fill': '#000',
		'stroke': '#000'
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
	var cont_x_trans = g.code_box_width + g.padding*2 + g.frame_padding + g.vertex_r;
	var cont_y_trans = g.padding + g.graph_frame_stroke_width;
	var x_trans = g.frame_padding + g.vertex_r;
	var y_trans = x_trans;
	g.g1_container_translate = [cont_x_trans, cont_y_trans];
	g.g1_translate = [x_trans, y_trans];
	g.g1_container.transform('t' + g.g1_container_translate[0] + ',' + g.g1_container_translate[1]);
	g.g1.transform('t' + (g.g1_translate[0]) + ',' + g.g1_translate[1]);
}

function get_line_arrow(x_start, y_start) {
    return snap.path(String("M" + x_start + " " + y_start + " L" + (x_start+8) + " " + y_start + " L" + (x_start+12) + " " + (y_start+4) + " L" + (x_start+8) + " " + (y_start+8) + " L" + x_start + " " + (y_start+8) + " L" + x_start + " " + y_start + " Z"));
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

function global_mouseup(evt) {
	if (g.scaler.scaling === true) {
		g.scaler.mouseup(evt);
	}
}

function global_mousemove(evt) {
	if (g.scaler.scaling === true) {
		g.scaler.do_scale(evt);
	}
}

function init() {
	var run = function() {
    for (var i=0; i<animation.length; i++) {
		(function (index) {
			setTimeout(function() {
				animation[index][1](animation[index][2], animation[index][3]);
			}, g.step_ms*i);
		})(i);
	}};
    // Set globals and size of base_container
    snap.mouseup(global_mouseup);
    snap.mousemove(global_mousemove);

    fill_global();
    $('#base_container').css({'width': g.cont_width, 'height': g.cont_height});
    format_code_lines();
    add_graph_frame();
    position_graph();
    add_scaler();
    //run();
}

var animation = Array(Array(1, SetAllVerticesColor, "g1_#EEEEEE"),
	Array(7, SetVertexAnnotation, "g1_1", "None"),
	Array(11, SetVertexAnnotation, "g1_2", "None"),
	Array(7, SetVertexAnnotation, "g1_3", "None"),
	Array(5, SetVertexAnnotation, "g1_4", "None"),
	Array(5, SetVertexAnnotation, "g1_5", "None"),
	Array(5, SetVertexAnnotation, "g1_6", "None"),
	Array(5, SetVertexAnnotation, "g1_7", "None"),
	Array(5, SetVertexAnnotation, "g1_8", "None"),
	Array(5, SetVertexAnnotation, "g1_9", "None"),
	Array(3, SetVertexAnnotation, "g1_10", "None"),
	Array(4, SetVertexAnnotation, "g1_11", "None"),
	Array(3, SetVertexAnnotation, "g1_12", "None"),
	Array(3, SetVertexAnnotation, "g1_13", "None"),
	Array(3, SetVertexAnnotation, "g1_14", "None"),
	Array(3, SetVertexAnnotation, "g1_15", "None"),
	Array(5, ShowActive, "l_1"),
	Array(1, UpdateEdgeInfo, "g1_(1, 3)", "Edge (1,3)"),
	Array(1, UpdateEdgeInfo, "g1_(10, 11)", "Edge (10,11)"),
	Array(1, UpdateEdgeInfo, "g1_(4, 8)", "Edge (4,8)"),
	Array(1, UpdateEdgeInfo, "g1_(1, 15)", "Edge (1,15)"),
	Array(1, UpdateEdgeInfo, "g1_(8, 9)", "Edge (8,9)"),
	Array(1, UpdateEdgeInfo, "g1_(6, 12)", "Edge (6,12)"),
	Array(1, UpdateEdgeInfo, "g1_(3, 7)", "Edge (3,7)"),
	Array(1, UpdateEdgeInfo, "g1_(2, 5)", "Edge (2,5)"),
	Array(1, UpdateEdgeInfo, "g1_(15, 5)", "Edge (15,5)"),
	Array(1, UpdateEdgeInfo, "g1_(6, 7)", "Edge (6,7)"),
	Array(1, UpdateEdgeInfo, "g1_(12, 13)", "Edge (12,13)"),
	Array(1, UpdateEdgeInfo, "g1_(4, 10)", "Edge (4,10)"),
	Array(1, UpdateEdgeInfo, "g1_(12, 14)", "Edge (12,14)"),
	Array(1, UpdateEdgeInfo, "g1_(5, 11)", "Edge (5,11)"),
	Array(1, UpdateEdgeInfo, "g1_(4, 9)", "Edge (4,9)"),
	Array(1, UpdateEdgeInfo, "g1_(11, 12)", "Edge (11,12)"),
	Array(1, UpdateEdgeInfo, "g1_(5, 10)", "Edge (5,10)"),
	Array(1, UpdateEdgeInfo, "g1_(7, 13)", "Edge (7,13)"),
	Array(1, UpdateEdgeInfo, "g1_(15, 6)", "Edge (15,6)"),
	Array(1, UpdateEdgeInfo, "g1_(2, 15)", "Edge (2,15)"),
	Array(1, UpdateEdgeInfo, "g1_(2, 4)", "Edge (2,4)"),
	Array(1, UpdateEdgeInfo, "g1_(11, 6)", "Edge (11,6)"),
	Array(10, ShowActive, "l_2"),
	Array(9, SetVertexColor, "g1_1", "blue"),
	Array(2, ShowActive, "l_3"),
	Array(10, ShowActive, "l_4"),
	Array(10, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_1", "red"),
	Array(2, SetVertexFrameWidth, "g1_1", "6"),
	Array(2, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_1", "1"),
	Array(5, ShowActive, "l_9"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_1", "6"),
	Array(2, SetEdgeColor, "g1_(1, 2)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_2", "blue"),
	Array(2, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(1, 2)", "red"),
	Array(6, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(1, 15)", "yellow"),
	Array(7, ShowActive, "l_11"),
	Array(13, ShowActive, "l_12"),
	Array(13, SetVertexColor, "g1_15", "blue"),
	Array(7, ShowActive, "l_13"),
	Array(10, SetEdgeColor, "g1_(1, 15)", "red"),
	Array(15, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(1, 3)", "yellow"),
	Array(6, ShowActive, "l_11"),
	Array(14, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_3", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(1, 3)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_1", "0"),
	Array(3, ShowActive, "l_6"),
	Array(9, ShowActive, "l_7"),
	Array(10, SetVertexColor, "g1_2", "red"),
	Array(2, SetVertexFrameWidth, "g1_1", "0"),
	Array(1, SetVertexFrameWidth, "g1_2", "6"),
	Array(1, ShowActive, "l_8"),
	Array(10, SetVertexAnnotation, "g1_2", "2"),
	Array(5, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_2", "6"),
	Array(1, SetEdgeColor, "g1_(1, 2)", "yellow"),
	Array(3, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(1, 2)", "red"),
	Array(1, SetEdgeColor, "g1_(2, 4)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_4", "blue"),
	Array(3, ShowActive, "l_13"),
	Array(10, SetEdgeColor, "g1_(2, 4)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(2, 5)", "yellow"),
	Array(4, ShowActive, "l_11"),
	Array(12, ShowActive, "l_12"),
	Array(11, SetVertexColor, "g1_5", "blue"),
	Array(11, ShowActive, "l_13"),
	Array(11, SetEdgeColor, "g1_(2, 5)", "red"),
	Array(4, ShowActive, "l_10"),
	Array(11, SetEdgeColor, "g1_(2, 15)", "yellow"),
	Array(6, ShowActive, "l_11"),
	Array(14, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(2, 15)", "grey"),
	Array(9, SetVertexFrameWidth, "g1_2", "0"),
	Array(9, ShowActive, "l_6"),
	Array(11, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_15", "red"),
	Array(2, SetVertexFrameWidth, "g1_2", "0"),
	Array(3, SetVertexFrameWidth, "g1_15", "6"),
	Array(3, ShowActive, "l_8"),
	Array(10, SetVertexAnnotation, "g1_15", "3"),
	Array(5, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(10, SetVertexFrameWidth, "g1_15", "6"),
	Array(1, SetEdgeColor, "g1_(1, 15)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(1, 15)", "red"),
	Array(2, SetEdgeColor, "g1_(2, 15)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(2, 15)", "grey"),
	Array(1, SetEdgeColor, "g1_(15, 5)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(15, 5)", "grey"),
	Array(1, SetEdgeColor, "g1_(15, 6)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_6", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(8, SetEdgeColor, "g1_(15, 6)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_15", "0"),
	Array(2, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_3", "red"),
	Array(2, SetVertexFrameWidth, "g1_15", "0"),
	Array(2, SetVertexFrameWidth, "g1_3", "6"),
	Array(4, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_3", "4"),
	Array(10, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_3", "6"),
	Array(1, SetEdgeColor, "g1_(1, 3)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(1, 3)", "red"),
	Array(1, SetEdgeColor, "g1_(3, 6)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(3, 6)", "grey"),
	Array(1, SetEdgeColor, "g1_(3, 7)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(23, ShowActive, "l_12"),
	Array(10, SetVertexColor, "g1_7", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(3, 7)", "red"),
	Array(3, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_3", "0"),
	Array(4, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_4", "red"),
	Array(1, SetVertexFrameWidth, "g1_3", "0"),
	Array(1, SetVertexFrameWidth, "g1_4", "6"),
	Array(1, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_4", "5"),
	Array(4, ShowActive, "l_9"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_4", "6"),
	Array(1, SetEdgeColor, "g1_(2, 4)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(11, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(2, 4)", "red"),
	Array(1, SetEdgeColor, "g1_(4, 8)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(11, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_8", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(10, SetEdgeColor, "g1_(4, 8)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(4, 9)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_9", "blue"),
	Array(3, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(4, 9)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(4, 10)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_10", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(4, 10)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_4", "0"),
	Array(3, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_5", "red"),
	Array(1, SetVertexFrameWidth, "g1_4", "0"),
	Array(1, SetVertexFrameWidth, "g1_5", "6"),
	Array(2, ShowActive, "l_8"),
	Array(8, SetVertexAnnotation, "g1_5", "6"),
	Array(7, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(8, SetVertexFrameWidth, "g1_5", "6"),
	Array(2, SetEdgeColor, "g1_(2, 5)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(2, 5)", "red"),
	Array(1, SetEdgeColor, "g1_(15, 5)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(15, 5)", "grey"),
	Array(1, SetEdgeColor, "g1_(5, 11)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_11", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(5, 11)", "red"),
	Array(2, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(5, 10)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(5, 10)", "grey"),
	Array(1, SetVertexFrameWidth, "g1_5", "0"),
	Array(4, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(10, SetVertexColor, "g1_6", "red"),
	Array(1, SetVertexFrameWidth, "g1_5", "0"),
	Array(1, SetVertexFrameWidth, "g1_6", "6"),
	Array(2, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_6", "7"),
	Array(5, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_6", "6"),
	Array(2, SetEdgeColor, "g1_(3, 6)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(3, 6)", "grey"),
	Array(3, SetEdgeColor, "g1_(11, 6)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(11, 6)", "grey"),
	Array(2, SetEdgeColor, "g1_(15, 6)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(15, 6)", "red"),
	Array(1, SetEdgeColor, "g1_(6, 7)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(6, 7)", "grey"),
	Array(1, SetEdgeColor, "g1_(6, 12)", "yellow"),
	Array(3, ShowActive, "l_11"),
	Array(10, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_12", "blue"),
	Array(5, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(6, 12)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_6", "0"),
	Array(2, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_7", "red"),
	Array(1, SetVertexFrameWidth, "g1_6", "0"),
	Array(7, SetVertexFrameWidth, "g1_7", "6"),
	Array(6, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_7", "8"),
	Array(20, ShowActive, "l_9"),
	Array(15, ShowActive, "l_10"),
	Array(10, SetVertexFrameWidth, "g1_7", "6"),
	Array(1, SetEdgeColor, "g1_(3, 7)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(3, 7)", "red"),
	Array(1, SetEdgeColor, "g1_(6, 7)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(6, 7)", "grey"),
	Array(1, SetEdgeColor, "g1_(7, 13)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_13", "blue"),
	Array(6, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(7, 13)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(7, 14)", "yellow"),
	Array(3, ShowActive, "l_11"),
	Array(9, ShowActive, "l_12"),
	Array(9, SetVertexColor, "g1_14", "blue"),
	Array(1, ShowActive, "l_13"),
	Array(9, SetEdgeColor, "g1_(7, 14)", "red"),
	Array(1, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_7", "0"),
	Array(2, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_8", "red"),
	Array(1, SetVertexFrameWidth, "g1_7", "0"),
	Array(1, SetVertexFrameWidth, "g1_8", "6"),
	Array(1, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_8", "9"),
	Array(5, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_8", "6"),
	Array(1, SetEdgeColor, "g1_(4, 8)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(4, 8)", "red"),
	Array(1, SetEdgeColor, "g1_(8, 9)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(8, 9)", "grey"),
	Array(1, SetVertexFrameWidth, "g1_8", "0"),
	Array(2, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_9", "red"),
	Array(1, SetVertexFrameWidth, "g1_8", "0"),
	Array(1, SetVertexFrameWidth, "g1_9", "6"),
	Array(2, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_9", "10"),
	Array(4, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_9", "6"),
	Array(2, SetEdgeColor, "g1_(4, 9)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(4, 9)", "red"),
	Array(3, SetEdgeColor, "g1_(8, 9)", "yellow"),
	Array(5, ShowActive, "l_11"),
	Array(16, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(8, 9)", "grey"),
	Array(2, SetVertexFrameWidth, "g1_9", "0"),
	Array(3, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_10", "red"),
	Array(1, SetVertexFrameWidth, "g1_9", "0"),
	Array(3, SetVertexFrameWidth, "g1_10", "6"),
	Array(2, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_10", "11"),
	Array(8, ShowActive, "l_9"),
	Array(11, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_10", "6"),
	Array(4, SetEdgeColor, "g1_(4, 10)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(4, 10)", "red"),
	Array(1, SetEdgeColor, "g1_(5, 10)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(13, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(5, 10)", "grey"),
	Array(3, SetEdgeColor, "g1_(10, 11)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(13, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(10, 11)", "grey"),
	Array(5, SetVertexFrameWidth, "g1_10", "0"),
	Array(4, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_11", "red"),
	Array(3, SetVertexFrameWidth, "g1_10", "0"),
	Array(2, SetVertexFrameWidth, "g1_11", "6"),
	Array(9, ShowActive, "l_8"),
	Array(10, SetVertexAnnotation, "g1_11", "12"),
	Array(7, ShowActive, "l_9"),
	Array(12, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_11", "6"),
	Array(1, SetEdgeColor, "g1_(5, 11)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(5, 11)", "red"),
	Array(2, SetEdgeColor, "g1_(10, 11)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(10, 11)", "grey"),
	Array(1, SetEdgeColor, "g1_(11, 6)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(11, 6)", "grey"),
	Array(1, SetEdgeColor, "g1_(11, 12)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(11, 12)", "grey"),
	Array(1, SetVertexFrameWidth, "g1_11", "0"),
	Array(1, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(8, SetVertexColor, "g1_12", "red"),
	Array(1, SetVertexFrameWidth, "g1_11", "0"),
	Array(1, SetVertexFrameWidth, "g1_12", "6"),
	Array(1, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_12", "13"),
	Array(4, ShowActive, "l_9"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_12", "6"),
	Array(4, SetEdgeColor, "g1_(6, 12)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(6, 12)", "red"),
	Array(1, SetEdgeColor, "g1_(11, 12)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(11, 12)", "grey"),
	Array(1, SetEdgeColor, "g1_(12, 13)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(12, 13)", "grey"),
	Array(1, SetEdgeColor, "g1_(12, 14)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(12, 14)", "grey"),
	Array(1, SetVertexFrameWidth, "g1_12", "0"),
	Array(2, ShowActive, "l_6"),
	Array(11, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_13", "red"),
	Array(1, SetVertexFrameWidth, "g1_12", "0"),
	Array(1, SetVertexFrameWidth, "g1_13", "6"),
	Array(2, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_13", "14"),
	Array(16, ShowActive, "l_9"),
	Array(11, ShowActive, "l_10"),
	Array(10, SetVertexFrameWidth, "g1_13", "6"),
	Array(3, SetEdgeColor, "g1_(7, 13)", "yellow"),
	Array(3, ShowActive, "l_11"),
	Array(11, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(7, 13)", "red"),
	Array(2, SetEdgeColor, "g1_(12, 13)", "yellow"),
	Array(11, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(12, 13)", "grey"),
	Array(1, SetVertexFrameWidth, "g1_13", "0"),
	Array(2, ShowActive, "l_6"),
	Array(10, ShowActive, "l_7"),
	Array(9, SetVertexColor, "g1_14", "red"),
	Array(1, SetVertexFrameWidth, "g1_13", "0"),
	Array(1, SetVertexFrameWidth, "g1_14", "6"),
	Array(2, ShowActive, "l_8"),
	Array(9, SetVertexAnnotation, "g1_14", "15"),
	Array(4, ShowActive, "l_9"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetVertexFrameWidth, "g1_14", "6"),
	Array(4, SetEdgeColor, "g1_(7, 14)", "yellow"),
	Array(2, ShowActive, "l_11"),
	Array(10, ShowActive, "l_10"),
	Array(10, SetEdgeColor, "g1_(7, 14)", "red"),
	Array(1, SetEdgeColor, "g1_(12, 14)", "yellow"),
	Array(1, ShowActive, "l_11"),
	Array(9, ShowActive, "l_10"),
	Array(9, SetEdgeColor, "g1_(12, 14)", "grey"),
	Array(1, SetVertexFrameWidth, "g1_14", "0"),
	Array(2, ShowActive, "l_6")
);

init();
