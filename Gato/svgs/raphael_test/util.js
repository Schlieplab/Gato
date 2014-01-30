
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
