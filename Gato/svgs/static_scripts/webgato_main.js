var snap = Snap("svg");
var g = {}; // globals

function add_snap_vars() {
    g.graph_elem_types = ['vertices', 'edges', 'code_lines', 'edge_arrows', 'highlight_boxes'];
    g.graph_elem_ids = ['vertex', 'edge', 'code_line', 'arrowhead'];
    // TODO: update this code to be mroe generic
    extend(g, {
        vertices: [{}, {}],
        edges: [{}, {}],
        edge_arrows: [{}, {}],
        graphs: [],
        highlight_boxes: [{}, {}],
    });
    var vertices = {}, edges = {}, edge_arrows = {}, code_lines = {};
    for (var graph_num=0; graph_num<g.num_graphs; graph_num++) {
        
        var v = snap.selectAll('g#g' + (graph_num+1) + ' .vertex');
        for (var i=0; i<v.length; i++) {
            g.vertices[graph_num][v[i].attr('id')] = v[i];
        }
        var e = snap.selectAll('g#g' + (graph_num+1) + ' .edge');
        for (var i=0; i<e.length; i++) {
            g.edges[graph_num][e[i].attr('id')] = e[i];
        }
        var ea = snap.selectAll('g#g' + (graph_num+1) + ' .arrowhead');
        for (var i=0; i<ea.length; i++) {
            g.edge_arrows[graph_num][ea[i].attr('id')] = ea[i];
        }
    }
    var lines = snap.selectAll('.code_line');
    g.code_lines = {};
    for (var i=0; i<lines.length; i++) { 
        g.code_lines[lines[i].attr('id')] = lines[i];
        // Mark it if the codeline is just whitespace
        var text = lines[i].attr('text');
        lines[i]['whitespace'] = text.length === 0;
    }
    g['graphs'].push(snap.select('g#g1'));
    var g2 = snap.select('g#g2');
    if (g2 != null) {
        g['graphs'].push(g2);
    }
}

function extend(a, b) {
    for (var key in b) {
        a[key] = b[key];
    }
}

function fill_global() {
    var cont_width = window.innerWidth;
    var cont_height = window.innerHeight;
    extend(g, {
        // Global 
        cont_width: cont_width,
        cont_height: cont_height,
        info_file: 'infos/%(info_file)s',
        padding: Math.min(Math.ceil(cont_width*.02), Math.ceil(cont_height)*.02),

        // Graph 
        vertex_r: parseInt(snap.select('g#g1 .vertex').attr('r')),
        frame_padding: 8,
        graph_containers: [snap.group().attr({'id': 'g1_container'}),
            snap.group().attr({'id': 'g2_container'})],
        graph_info_containers: [snap.group().attr({'id': 'g1_info_container'}), 
            snap.group().attr({'id': 'g2_info_container'})],
        graph_frame_stroke_width: 1,
        edge_width: 4,
        edge_color: '#EEEEEE',

        // General
        arrow_id_prefix: 'ea',
    });
    if (snap.select('g#g2') != null) {
        g.num_graphs = 2;
    } else {
        g.num_graphs = 1;
    }
    g.master_graph_container = snap.group();
    for (var i=0; i<g.graph_containers.length; i++) {
        g.master_graph_container.append(g.graph_containers[i]);
    }

    add_snap_vars();
}

function save_initial_graph_dimensions() {
    var bbox = g.master_graph_container.getBBox();
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
    // Add global event handlers
    snap.mouseup(global_mouseup);
    snap.mousemove(global_mousemove);
    snap.drag(function(){}, function(){}, global_drag)

    // Set globals and size of base_container
    fill_global();
    document.getElementById('base_container').setAttribute('style', 'width: ' + g.cont_width + '; height: ' + g.cont_height);
    document.getElementById('svg').setAttribute('style', 'width: ' + g.cont_width + 'px; height: ' + g.cont_height + 'px');
    // Initialize graphical elements
    g.playback_bar = new PlaybackBar();
    g.code_box = new CodeBox();
    add_graph_frame();
    position_graph();
    add_scaler();
    add_tooltips();
    save_initial_graph_dimensions();

    // Build the GraphState array
    g.animation = new Animation();
}
