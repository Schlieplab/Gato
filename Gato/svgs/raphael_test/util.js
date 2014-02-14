function time_of_last_animation() {
    return anim_array[g.animation.step_num-1][0] * g.animation.step_ms;
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
