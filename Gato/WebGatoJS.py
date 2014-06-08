animationhead = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="viewport" content="user-scalable=no, initial-scale=1, maximum-scale=1, minimum-scale=1, width=device-width, height=device-height, target-densitydpi=device-dpi" />
        <link rel="stylesheet" type="text/css" href="js/subModal/subModal.css" />
        <script type="text/javascript" src="js/subModal/common.js"></script>
        <script type="text/javascript" src="js/subModal/subModal.js"></script>
        <script src="js/snap.svg.js" type="text/javascript"></script>
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
            #help_div {
                position: absolute;
                width: 100%%;
                height: 2.5em;
                top: 0px;
                left: 0px;
                background-color: white;
                border-bottom: 1px solid #aaa;
                color: #333;
            }
            .invisible {
                visibility: hidden;
            }
            .visible {
                visibility: visible;
                z-index: 1000;
            }
            .help_link {
                font-family: Helvetica;
                font-size: 1.5em;
                text-decoration: none;
                color: #87afff;
            }
            .help_link:visited {
                color: #1354D6;
            }
            .help_link:hover {
                color: #1354D6;
            }
            .left_link {
                border-right: 1px solid #aaa;
                padding-right: 15px;
                margin-right: 0px;
            }
            .right_link {
                margin-left: 0px;
                padding-left: 15px;
            }
        </style>
        <title>%(title)s</title>
    </head>
    <body>
        <div id="help_div" class="invisible">
            <div style="padding: .5em">
                <a class="help_link left_link" href="./index.html">Index</a><a class="help_link right_link" href="./help.html">Help</a>
            </div>
        </div>
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
            <filter id="tooltip_dropshadow" height="130%%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="1"/> <!-- stdDeviation is how much to blur -->
                <feOffset dx="2" dy="2" result="offsetblur"/> <!-- how much to offset -->
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

        <script type="text/javascript" src="js/util.js"></script>
        <script type="text/javascript" src="js/animation_functions.js"></script>
        <script type="text/javascript" src="js/display_functions.js"></script>
        <script type="text/javascript" src="js/webgato_main.js"></script>
        
        <script type="text/javascript">
            %(animation)s
            init();
        </script>

    </body>
</html>
'''