animationhead = '''
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="libs/subModal/subModal.css" />
        <script type="text/javascript" src="libs/subModal/common.js"></script>
        <script type="text/javascript" src="libs/subModal/subModal.js"></script>
        <script src="libs/snap.svg.js" type="text/javascript"></script>
        <style>
            html, body {
                margin: 0 auto;
                overflow-y: hidden;
                background-image:url('img/white_wall.png')
            }
            * {
                -webkit-touch-callout: none;
                -webkit-user-select: none;
                -khtml-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }
            .edge {
                cursor: pointer;
            }
        </style>
    </head>
    <body>

        <div id="base_container">
        <svg id="svg">
            <filter id="dropshadow" height="130%%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="1"/> <!-- stdDeviation is how much to blur -->
                <feOffset dx="2.5" dy="2.5" result="offsetblur"/> <!-- how much to offset -->
                <feMerge> 
                  <feMergeNode/> <!-- this contains the offset blurred image -->
                  <feMergeNode in="SourceGraphic"/> <!-- this contains the element that the filter is applied to -->
               </feMerge>
            </filter>
            %(graph_str)s
            %(algo_str)s
        </svg>
        </div>

        <script type="text/javascript">
            var info_file = "%(info_file)s";
            var g1_x_add = %(g1_x_add)d;
            var g1_y_add = %(g1_y_add)d;
            var g2_x_add = %(g2_x_add)d;
            var g2_y_add = %(g2_y_add)d;
            var g1_init_edge_info = %(g1_init_edge_info)s;
            var g2_init_edge_info = %(g2_init_edge_info)s;
            var g1_init_graph_info = %(g1_init_graph_info)s;
            var g2_init_graph_info = %(g2_init_graph_info)s;
            var g1_init_vertex_info = %(g1_init_vertex_info)s;
            var g2_init_vertex_info = %(g2_init_vertex_info)s;
        </script>

        <script type="text/javascript" src="static_scripts/util.js"></script>
        <script type="text/javascript" src="static_scripts/animation_functions.js"></script>
        <script type="text/javascript" src="static_scripts/display_functions.js"></script>
        <script type="text/javascript" src="static_scripts/webgato_main.js"></script>
        
        <script type="text/javascript">
            %(animation)s
            init();
        </script>

    </body>
</html>
'''