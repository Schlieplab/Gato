function start_animation() {
	g.running = true;
	for (var i=0; i<animation.length; i++) {	
		(function (index) {
			setTimeout(function() {
				animation[index][1](animation[index][2], animation[index][3]);
			}, g.step_ms*i);
		})(i);
	}
}

/** Sets the vertex given by vertex_id to color */
function SetVertexColor(vertex_id, color) {
	g.vertices[vertex_id].attr('fill', color);
}

function UpdateEdgeInfo(edge_id, info) {

}

function UpdateGraphInfo(graph_id, info) {

}

/** Sets the given edge to the given color.  If the given edge
	is not found, then the reverse direction is tried, e.g. if g1_(5, 4) is
	not found we will try g1_(4, 5)
*/
function SetEdgeColor(edge_id, color) {
	function switch_edge_vertices() {
	    // Switches the edge_id vertices.  ie. g1_(5, 4) in --> g1_(4, 5) out
	    // TODO: Test me
	    var re = /\d+/g;
	    var matches = edge_id.match(re);
	    return "g" + matches[0] + "_(" + matches[1] + ", " + matches[2] + ")";
	}
	var edge = g.edges[edge_id];
	if (edge === null) {
		edge_id = switch_edge_vertices();
		edge = g.edges[edge_id];
	}
	edge.attr({'stroke': color});
    
    var edge_arrow = g.edge_arrows[(g.arrow_id_prefix + edge_id)];
    if (edge_arrow !== undefined) {
    	edge_arrow.attr({'fill': color});
    }
}

/** Sets color of all vertices of a given graph to a given color.
* 	graph_id_and_color is string of form "g{graph_num}_#{hex_color}"
* 	If vertices != null, then only color the set of vertices specified by vertices
*/
function SetAllVerticesColor(graph_id_and_color, vertices) {
	var split = graph_id_and_color.split('_');
	var graph_id = split[0];
	var color = split[1];

	if (vertices == null) {
		for (var key in g.vertices) {
			g.vertices[key].attr({'fill': color});
		}
	} else {
		for (var i=0; i<vertices.length; i++) {
			g.vertices[vertices[i]].attr({'fill': color});
		}
	}
}


/** Sets all edges of given graph to color.  param is of form: "g1_#dd3333" */
function SetAllEdgesColor(graph_id_and_color) {
    var split = graph_id_and_color.split('_');
    var graph = split[0];
    var color = split[1];
    var graph_edges = g.edges[graph];
    var edge_arrows = g.edge_arrows[graph];
    for (var i=0; i<graph_edges.length; i++) {
    	graph_edges[i].attr({'stroke': color});
    	if (edge_arrows.length > i) {
    		edge_arrows[i].attr({'fill': color});
    	}
    }
}


/** Blinks the given vertex between black and current color 3 times */
function BlinkVertex(vertex_id, color) {
    var vertex = document.getElementById(vertex_id);
    var curr_color = vertex.getAttribute('fill');
    for (var i=0; i<6; i+=2) {
    	setTimeout(function() { vertex.setAttribute('fill',  'black'); }, g.step_ms*(i));
    	setTimeout(function() { vertex.setAttribute('fill', curr_color); }, g.step_ms*(i+1));
    }
}

/** Blinks the given edge between black and current color 3 times */
function BlinkEdge(edge_id, color){
    var edge = document.getElementById(edge_id);
    var curr_color = edge.getAttribute('stroke');
    for (var i=0; i<6; i+=2) {
    	setTimeout(function() { edge.setAttribute('stroke',  'black'); }, g.step_ms*(i));
    	setTimeout(function() { edge.setAttribute('stroke', curr_color); }, g.step_ms*(i+1));
    }
}

//Blink(self, list, color=None):
//Sets the frame width of a vertex
function SetVertexFrameWidth(v, val) {

}


//Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(v, annotation, color) //removed 'self' parameter to because 'self' parameter was assigned value of v, v of annotation, and so on.
{
    
}


//Line with specified id is highlighted.  Becomes current line of code.  Previous highlight is removed.
function ShowActive(line_id){
    
}


//Directed or undirected added to graph.
function AddEdge(edge_id){
    
}

//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id){

}

//Adds vertex of into specified graph and coordinates in graph.  Optional id argument may be given.
function AddVertex(graph_and_coordinates, id){

}
