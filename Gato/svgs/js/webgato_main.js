var snap = Snap("svg");
var g = {}; // globals

function fill_global() {
    /*  Fills the global variable, g, with all necessary info.  
        Where we don't have info yet null values are inserted
    */
    var cont_width = window.innerWidth;
    var cont_height = window.innerHeight;
    extend(g, {
        playback_bar: null,
        code_box: null,
        animation: null,

        /* General Globals */
        // Width and height of the whole draw area
        cont_width: cont_width,
        cont_height: cont_height,
        // Location in the file system of the algorithm info file
        info_file: 'infos/%(info_file)s',
        // Number of pixels to use for padding on edges of canvas and between elements
        padding: Math.min(Math.ceil(cont_width*.02), Math.ceil(cont_height)*.02),
        // The x/y coordinate shifts we apply to any coordinates passed in from animation commands
        coord_changes: [
            {'x': g1_x_add, 'y': g1_y_add},
            {'x': g2_x_add, 'y': g2_y_add}
        ],
        // true moats are currently undergoing a growing animation.  
        // We use this to know when we've hit the first GrowMoat command in a series, so we can find the corresponding
        // Wait() command that tells us how long the animation lasts
        growing_moats: false,
        // true if we are currently jumping between animation states(we avoid blinking if we are jumping, 
        // and execute animation commands immediately if they would normally be animated).
        // At the start we are building the graph states so we set it to true
        jumping: true,

        /* Graph Related Globals */
        // The radius of vertices on the graph
        vertex_r: parseInt(snap.select('g#g1 .vertex').attr('r')),
        // Padding given to graph inside graph container
        frame_padding: 8,
        // The two containers that hold each graph
        graph_containers: [snap.group().attr({'id': 'g1_container'}),
            snap.group().attr({'id': 'g2_container'})],
        // The two containers that hold each graph info.  These are children of the graph containers above
        graph_info_containers: [snap.group().attr({'id': 'g1_info_container'}), 
            snap.group().attr({'id': 'g2_info_container'})],
        graph_frame_stroke_width: 1,
        edge_width: 4,
        edge_color: '#EEEEEE',
        graph_info_height: 20,
        // Holds the offsets for bubbles per graph.  Each bubble is indexed by id.  A bubble
        // offset is a value that is added to the radius of the bubble when resizing.
        bubble_offsets: [{}, {}],
        // Dictionary of edges that are currently blinking, indexed by ID.
        // When we set an edge's color we remove any blinks associated with that edge, if any
        blinking_edges: {},
        // Same as blinking_edges but for vertices
        blinking_vertices: {},
        // The initial information for each element type
        init_edge_infos: [g1_init_edge_info, g2_init_edge_info],
        init_graph_infos: [g1_init_graph_info, g2_init_graph_info],
        init_vertex_infos: [g1_init_vertex_info, g2_init_vertex_info],
        // The graph info text elements
        graph_infos: [],
        // Array of tooltip text elements
        tooltips: [{}, {}],
        // Dictionary of tooltips indexed by tooltip ID that points to the ToolTip javascript objects
        tooltip_objects: {},
        arrow_id_prefix: 'ea',
        // Array with a dictionary for each graph that contains the maximum width and height the graph attains.
        // The min_left attribute is the minimum x value that the graph attains throughout animation.
        // min_left is useful for things like WeightedMatching of PrimalDualKruskal which have big bubbles
        // that must be accounted for with graph translations
        max_graph_sizes: [
            {'width': null, 'height': null, 'min_left': null},
            {'width': null, 'height': null, 'min_left': null}
        ],
        // All of the different elem types that we have to keep track of the history of in animation_functions.Animation
        graph_elem_types: ['vertices', 'edges', 'code_lines', 'edge_arrows', 'highlight_boxes', 'annotations', 'moats', 'bubbles', 'highlighted_paths'],
    });

    // Set the initial graph_translate.  this might be changed in display_functions.position_graph
    var trans = g.frame_padding + g.vertex_r;
    g['graph_translate'] = [{x: trans, y:trans}, {x: trans, y: trans}];

    // Set number of graphs
    if (snap.select('g#g2') != null) {
        g.num_graphs = 2;
    } else {
        g.num_graphs = 1;
    }

    // Make one container to rule them all
    g.master_graph_container = snap.group();
    for (var i=0; i<g.graph_containers.length; i++) {
        g.master_graph_container.append(g.graph_containers[i]);
    }

    // Add containers to globals for each of the element types
    add_graph_element_globals();
}

function add_graph_element_globals() {
    extend(g, {
        vertex_groups: [{}, {}],
        vertices: [{}, {}],
        edge_groups: [{}, {}],
        edges: [{}, {}],
        edge_arrows: [{}, {}],
        graphs: [],
        highlight_boxes: [{}, {}],
        annotations: [{}, {}],
        moats: [{}, {}],
        bubbles: [{}, {}],
        highlighted_paths: [{}, {}],
        // Each graph has a pre_vertex element.  This element simply acts as a marker
        // so we can add edges immediately before it(so they will appear above other 
        // elements, such as bubbles, that we prepend to the graph)
        pre_vertex: []
    });

    // Add the initial elements to the global containers
    for (var graph_num=0; graph_num<g.num_graphs; graph_num++) {
        // Vertex Groups
        var v_g = snap.selectAll('g#g' + (graph_num+1) + ' .vertex_g');
        for (var i=0; i<v_g.length; i++) {
            g.vertex_groups[graph_num][v_g[i].attr('id')] = v_g[i];
        }

        // Vertices
        var v = snap.selectAll('g#g' + (graph_num+1) + ' .vertex');
        for (var i=0; i<v.length; i++) {
            g.vertices[graph_num][v[i].attr('id')] = v[i];
        }

        // Edges
        var e = snap.selectAll('g#g' + (graph_num+1) + ' .edge');
        for (var i=0; i<e.length; i++) {
            g.edges[graph_num][e[i].attr('id')] = e[i];
        }

        // Edge Groups
        var e_g = snap.selectAll('g#g' + (graph_num+1) + ' .edge_group');
        for (var i=0; i<e_g.length; i++) {
            g.edge_groups[graph_num][e_g[i].attr('id')] = e_g[i];
        }

        // Edge Annotations
        var ea = snap.selectAll('g#g' + (graph_num+1) + ' .arrowhead');
        for (var i=0; i<ea.length; i++) {
            g.edge_arrows[graph_num][ea[i].attr('id')] = ea[i];
        }
        
        // Vertex Annotations
        var va = snap.selectAll('g#g' + (graph_num+1) + ' .vertex_annotation');
        for (var i=0; i<va.length; i++) {
            g.annotations[graph_num][va[i].attr('id')] = va[i];
        }
        g.pre_vertex.push(snap.select('g#g' + (graph_num+1) + '_pre_vertices_group'));
    }
    
    // Take care of the codelines
    var lines = snap.selectAll('.code_line');
    g.code_lines = {};
    for (var i=0; i<lines.length; i++) { 
        g.code_lines[lines[i].attr('id')] = lines[i];
        // Mark it if the codeline is just whitespace
        var text = lines[i].attr('text');
        lines[i]['whitespace'] = text.length === 0;
    }

    // Push the graph elements in
    g['graphs'].push(snap.select('g#g1'));
    var g2 = snap.select('g#g2');
    if (g2 != null) {
        g['graphs'].push(g2);
    }
}

function save_initial_graph_dimensions() {
    // Save the initial graph dimensions so we can use them for scaling
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
    if (g.control_panel.frame_visibility === true) {
        if (!g.control_panel.cursor_in_control_panel(evt)) {
            g.control_panel.toggle_visibility();
        }
    }
    if (g.active_tooltip) {
        if (g.new_active_tooltip !== true) {
            // If this tooltip wasn't triggered by this event
            g.active_tooltip.mouseout();
            g.active_tooltip = undefined;
            g.new_active_tooltip = false;
        } else {
            // New tooltip.  Register that we've seen it and go on our way
            g.new_active_tooltip = true;
        }
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

var window_size_check = (function() {
    var notice_shown = false;
    return function() {
        if (!notice_shown) {
            if (window.innerWidth < 450 || window.innerHeight < 350) {
                alert("Gato requires a window size of at least 450px width and 350px height.  Your window is smaller than that and the application may not work as intended.");
                notice_shown = true;
            }
        }
    }
})();

function window_resize(evt) {
    window_size_check();
    g.cont_height = window.innerHeight;
    g.cont_width = window.innerWidth;
    document.getElementById('svg').setAttribute('style', 'width: ' + g.cont_width + 'px; height: ' + g.cont_height + 'px');
    g.playback_bar.resize();
    g.code_box.scale_and_translate();
    g.scaler.set_max_and_min_dimensions_of_graph_container();
    position_graph();
}

function init() {
    window_size_check();

    // Add global event handlers
    snap.mouseup(global_mouseup);
    snap.mousemove(global_mousemove);
    snap.drag(function(){}, function(){}, global_drag)
    window.onresize = window_resize;

    // Set globals and size of base_container
    fill_global();
    remove_trailing_whitespace_lines();
    document.getElementById('base_container').setAttribute('style', 'width: ' + g.cont_width + '; height: ' + g.cont_height);
    document.getElementById('svg').setAttribute('style', 'width: ' + g.cont_width + 'px; height: ' + g.cont_height + 'px');
    g.playback_bar = new PlaybackBar();
    g.code_box = new CodeBox();
    initialize_tooltips();
    add_graph_info();
    g.animation = new Animation();
    add_graph_frame();
    position_graph(true);
    add_scaler();
    save_initial_graph_dimensions();
}
