/*
	WISHLIST:
1) Back-step button

*/

var snap = Snap("svg");
var g = {}; // globals


function add_snap_vars() {
	g.graph_elem_types = ['vertices', 'edges', 'code_lines', 'edge_arrows', 'highlight_boxes'];
	g.graph_elem_ids = ['vertex', 'edge', 'code_line', 'arrowhead'];
	// TODO: update this code to be mroe generic

    var vertices = {}, edges = {}, edge_arrows = {}, code_lines = {};
    for (var graph_num=0; graph_num<g.num_graphs; graph_num++) {
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
    g['vertices'] = vertices;
    g['edges'] = edges;
    g['edge_arrows'] = edge_arrows;
    g['code_lines'] = code_lines;
    g['g1'] = snap.select('g#g1');
    g['g2'] = snap.select('g#g2');
}

function extend(a, b) {
	for (var key in b) {
		a[key] = b[key];
	}
}

function fill_global() {
	//$.extend(g, {
	var cont_width = window.innerWidth;
	var cont_height = window.innerHeight;
	extend(g, {
		// Global 
		cont_width: cont_width,
		cont_height: cont_height,
        padding: Math.min(Math.ceil(cont_width*.02), Math.ceil(cont_height)*.02),

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

    add_snap_vars();
}

function save_initial_graph_dimensions() {
    var bbox = g.g1_container.getBBox();
    g.initial_graph_width = bbox.width;
    g.initial_graph_height = bbox.height;
}

function global_mouseup(evt) {
    if (g.scaler.scaling === true) {
        g.scaler.mouseup(evt);
    }
    if (g.slider.sliding === true) {
        g.slider.cursor_mouseup(evt);
    }
}

function global_mousemove(evt) {
	if (g.scaler.scaling === true) {
		g.scaler.mousemove(evt);
	}
	if (g.slider.sliding === true) {
		g.slider.cursor_mousemove(evt);
	}
}

function global_drag(evt) {
	if (g.scaler.scaling === true) {
		g.scaler.drag(evt);
	}
	if (g.slider.sliding === true) {
		g.slider.cursor_drag(evt);
	}
}

function init() {
	var run = function() {
	    for (var i=0; i<animation.length; i++) {
			(function (index) {
				setTimeout(function() {
					animation[index][1](animation[index][2], animation[index][3]);
				}, g.animation.step_ms*i);
		})(i);
	}};
    // Add global event handlers
    snap.mouseup(global_mouseup);
    snap.mousemove(global_mousemove);
    snap.drag(function(){}, function(){}, global_drag)

    // Set globals and size of base_container
    fill_global();
    document.getElementById('base_container').setAttribute('style', 'width: ' + g.cont_width + '; height: ' + g.cont_height);
    
    // Initialize graphical elements
    g.playback_bar = new PlaybackBar();
    g.code_box = new CodeBox();
    add_graph_frame();
    position_graph();
    add_scaler();
    save_initial_graph_dimensions();

    // Build the GraphState array
    g.animation = new Animation();
 	
    //run();
}

// TODO: Change my name in GatoExport
var anim_array = Array(Array(1, SetAllVerticesColor, "g1_#EEEEEE"),
Array(2, SetVertexAnnotation, "g1_1", "None"),
Array(2, SetVertexAnnotation, "g1_2", "None"),
Array(2, SetVertexAnnotation, "g1_3", "None"),
Array(2, SetVertexAnnotation, "g1_4", "None"),
Array(2, SetVertexAnnotation, "g1_5", "None"),
Array(2, SetVertexAnnotation, "g1_6", "None"),
Array(2, SetVertexAnnotation, "g1_7", "None"),
Array(2, SetVertexAnnotation, "g1_8", "None"),
Array(2, SetVertexAnnotation, "g1_9", "None"),
Array(2, SetVertexAnnotation, "g1_10", "None"),
Array(2, SetVertexAnnotation, "g1_11", "None"),
Array(2, SetVertexAnnotation, "g1_12", "None"),
Array(2, SetVertexAnnotation, "g1_13", "None"),
Array(2, SetVertexAnnotation, "g1_14", "None"),
Array(2, SetVertexAnnotation, "g1_15", "None"),
Array(4, ShowActive, "l_1"),
Array(1, UpdateGraphInfo, "g1_", ""),
Array(1, UpdateEdgeInfo, "g1_1-3", "Edge1-3"),
Array(1, UpdateEdgeInfo, "g1_10-11", "Edge10-11"),
Array(1, UpdateEdgeInfo, "g1_4-8", "Edge4-8"),
Array(1, UpdateEdgeInfo, "g1_1-15", "Edge1-15"),
Array(1, UpdateEdgeInfo, "g1_8-9", "Edge8-9"),
Array(1, UpdateEdgeInfo, "g1_6-12", "Edge6-12"),
Array(1, UpdateEdgeInfo, "g1_3-7", "Edge3-7"),
Array(1, UpdateEdgeInfo, "g1_2-5", "Edge2-5"),
Array(1, UpdateEdgeInfo, "g1_15-5", "Edge15-5"),
Array(1, UpdateEdgeInfo, "g1_1-2", "Edge1-2"),
Array(1, UpdateEdgeInfo, "g1_6-7", "Edge6-7"),
Array(1, UpdateEdgeInfo, "g1_12-13", "Edge12-13"),
Array(1, UpdateEdgeInfo, "g1_3-6", "Edge3-6"),
Array(1, UpdateEdgeInfo, "g1_4-10", "Edge4-10"),
Array(1, UpdateEdgeInfo, "g1_7-14", "Edge7-14"),
Array(1, UpdateEdgeInfo, "g1_12-14", "Edge12-14"),
Array(1, UpdateEdgeInfo, "g1_5-11", "Edge5-11"),
Array(1, UpdateEdgeInfo, "g1_4-9", "Edge4-9"),
Array(1, UpdateEdgeInfo, "g1_11-12", "Edge11-12"),
Array(1, UpdateEdgeInfo, "g1_5-10", "Edge5-10"),
Array(1, UpdateEdgeInfo, "g1_7-13", "Edge7-13"),
Array(1, UpdateEdgeInfo, "g1_15-6", "Edge15-6"),
Array(1, UpdateEdgeInfo, "g1_2-15", "Edge2-15"),
Array(1, UpdateEdgeInfo, "g1_2-4", "Edge2-4"),
Array(1, UpdateEdgeInfo, "g1_11-6", "Edge11-6"),
Array(9, ShowActive, "l_2"),
Array(8, SetVertexColor, "g1_1", "blue"),
Array(1, ShowActive, "l_3"),
Array(9, ShowActive, "l_4"),
Array(9, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_1", "red"),
Array(1, SetVertexFrameWidth, "g1_1", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_1", "1"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_1", "6"),
Array(4, SetEdgeColor, "g1_1-2", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_2", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_1-2", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_1-15", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_15", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_1-15", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_1-3", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_3", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_1-3", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_1", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_2", "red"),
Array(1, SetVertexFrameWidth, "g1_1", "0"),
Array(1, SetVertexFrameWidth, "g1_2", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_2", "2"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_2", "6"),
Array(1, SetEdgeColor, "g1_1-2", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_1-2", "red"),
Array(1, SetEdgeColor, "g1_2-4", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_4", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_2-4", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_2-5", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_5", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_2-5", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_2-15", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(9, SetEdgeColor, "g1_2-15", "grey"),
Array(1, SetVertexFrameWidth, "g1_2", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_15", "red"),
Array(1, SetVertexFrameWidth, "g1_2", "0"),
Array(1, SetVertexFrameWidth, "g1_15", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_15", "3"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_15", "6"),
Array(1, SetEdgeColor, "g1_1-15", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_1-15", "red"),
Array(1, SetEdgeColor, "g1_2-15", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_2-15", "grey"),
Array(1, SetEdgeColor, "g1_15-5", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_15-5", "grey"),
Array(1, SetEdgeColor, "g1_15-6", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_6", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_15-6", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_15", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_3", "red"),
Array(1, SetVertexFrameWidth, "g1_15", "0"),
Array(1, SetVertexFrameWidth, "g1_3", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_3", "4"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_3", "6"),
Array(1, SetEdgeColor, "g1_1-3", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_1-3", "red"),
Array(1, SetEdgeColor, "g1_3-6", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_3-6", "grey"),
Array(1, SetEdgeColor, "g1_3-7", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_7", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_3-7", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_3", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_4", "red"),
Array(1, SetVertexFrameWidth, "g1_3", "0"),
Array(1, SetVertexFrameWidth, "g1_4", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_4", "5"),
Array(4, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_4", "6"),
Array(1, SetEdgeColor, "g1_2-4", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_2-4", "red"),
Array(1, SetEdgeColor, "g1_4-8", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_8", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_4-8", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_4-9", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_9", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_4-9", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_4-10", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_10", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_4-10", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_4", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_5", "red"),
Array(1, SetVertexFrameWidth, "g1_4", "0"),
Array(1, SetVertexFrameWidth, "g1_5", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_5", "6"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_5", "6"),
Array(1, SetEdgeColor, "g1_2-5", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_2-5", "red"),
Array(1, SetEdgeColor, "g1_15-5", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_15-5", "grey"),
Array(1, SetEdgeColor, "g1_5-11", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_11", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_5-11", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_5-10", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_5-10", "grey"),
Array(1, SetVertexFrameWidth, "g1_5", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_6", "red"),
Array(1, SetVertexFrameWidth, "g1_5", "0"),
Array(1, SetVertexFrameWidth, "g1_6", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_6", "7"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_6", "6"),
Array(1, SetEdgeColor, "g1_3-6", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_3-6", "grey"),
Array(1, SetEdgeColor, "g1_11-6", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_11-6", "grey"),
Array(1, SetEdgeColor, "g1_15-6", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_15-6", "red"),
Array(1, SetEdgeColor, "g1_6-7", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_6-7", "grey"),
Array(2, SetEdgeColor, "g1_6-12", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_12", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_6-12", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_6", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_7", "red"),
Array(1, SetVertexFrameWidth, "g1_6", "0"),
Array(1, SetVertexFrameWidth, "g1_7", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_7", "8"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_7", "6"),
Array(1, SetEdgeColor, "g1_3-7", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_3-7", "red"),
Array(1, SetEdgeColor, "g1_6-7", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_6-7", "grey"),
Array(1, SetEdgeColor, "g1_7-13", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_13", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_7-13", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_7-14", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_12"),
Array(8, SetVertexColor, "g1_14", "blue"),
Array(1, ShowActive, "l_13"),
Array(8, SetEdgeColor, "g1_7-14", "red"),
Array(1, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_7", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_8", "red"),
Array(1, SetVertexFrameWidth, "g1_7", "0"),
Array(1, SetVertexFrameWidth, "g1_8", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_8", "9"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_8", "6"),
Array(1, SetEdgeColor, "g1_4-8", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_4-8", "red"),
Array(1, SetEdgeColor, "g1_8-9", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_8-9", "grey"),
Array(1, SetVertexFrameWidth, "g1_8", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_9", "red"),
Array(1, SetVertexFrameWidth, "g1_8", "0"),
Array(1, SetVertexFrameWidth, "g1_9", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_9", "10"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_9", "6"),
Array(1, SetEdgeColor, "g1_4-9", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_4-9", "red"),
Array(1, SetEdgeColor, "g1_8-9", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_8-9", "grey"),
Array(1, SetVertexFrameWidth, "g1_9", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_10", "red"),
Array(1, SetVertexFrameWidth, "g1_9", "0"),
Array(1, SetVertexFrameWidth, "g1_10", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_10", "11"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_10", "6"),
Array(1, SetEdgeColor, "g1_4-10", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_4-10", "red"),
Array(1, SetEdgeColor, "g1_5-10", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_5-10", "grey"),
Array(1, SetEdgeColor, "g1_10-11", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_10-11", "grey"),
Array(1, SetVertexFrameWidth, "g1_10", "0"),
Array(2, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_11", "red"),
Array(1, SetVertexFrameWidth, "g1_10", "0"),
Array(1, SetVertexFrameWidth, "g1_11", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_11", "12"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_11", "6"),
Array(1, SetEdgeColor, "g1_5-11", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_5-11", "red"),
Array(1, SetEdgeColor, "g1_10-11", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_10-11", "grey"),
Array(1, SetEdgeColor, "g1_11-6", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_11-6", "grey"),
Array(1, SetEdgeColor, "g1_11-12", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_11-12", "grey"),
Array(1, SetVertexFrameWidth, "g1_11", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_12", "red"),
Array(1, SetVertexFrameWidth, "g1_11", "0"),
Array(1, SetVertexFrameWidth, "g1_12", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_12", "13"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_12", "6"),
Array(1, SetEdgeColor, "g1_6-12", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_6-12", "red"),
Array(1, SetEdgeColor, "g1_11-12", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_11-12", "grey"),
Array(1, SetEdgeColor, "g1_12-13", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_12-13", "grey"),
Array(1, SetEdgeColor, "g1_12-14", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_12-14", "grey"),
Array(1, SetVertexFrameWidth, "g1_12", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_13", "red"),
Array(1, SetVertexFrameWidth, "g1_12", "0"),
Array(1, SetVertexFrameWidth, "g1_13", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_13", "14"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_13", "6"),
Array(1, SetEdgeColor, "g1_7-13", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_7-13", "red"),
Array(1, SetEdgeColor, "g1_12-13", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_12-13", "grey"),
Array(1, SetVertexFrameWidth, "g1_13", "0"),
Array(1, ShowActive, "l_6"),
Array(9, ShowActive, "l_7"),
Array(8, SetVertexColor, "g1_14", "red"),
Array(1, SetVertexFrameWidth, "g1_13", "0"),
Array(1, SetVertexFrameWidth, "g1_14", "6"),
Array(1, ShowActive, "l_8"),
Array(8, SetVertexAnnotation, "g1_14", "15"),
Array(3, ShowActive, "l_9"),
Array(9, ShowActive, "l_10"),
Array(8, SetVertexFrameWidth, "g1_14", "6"),
Array(1, SetEdgeColor, "g1_7-14", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_7-14", "red"),
Array(1, SetEdgeColor, "g1_12-14", "yellow"),
Array(1, ShowActive, "l_11"),
Array(9, ShowActive, "l_10"),
Array(8, SetEdgeColor, "g1_12-14", "grey"),
Array(1, SetVertexFrameWidth, "g1_14", "0"),
Array(1, ShowActive, "l_6")
);
init();
