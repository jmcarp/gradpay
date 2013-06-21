/*
 * @module scatter
 * @author jmcarp
 */

var scatter = (function() {

    // Initialize SVG variables
    var svg, points;
    
    /* 
     * 
     */
    function init() {
        
        // Create SVG object
        svg = d3.select('body')
            .append('svg:svg');
        
        // Create counties group
        points = svg.append('svg:g')
            .attr('id', 'points');
        
    }

    /* 
     * @class choro
     * @static
     * @param selector
     * @param iv
     * @param dv
     */
    function scatter(selector, xv, yv) {
        
        // Initialize
        var data, values, cscale;

        // 
        $.getJSON(
            '/scatter_json?xv=' + xv + '&yv=' + yv
        ).done(function(data) {
            points.selectAll('path')
                .data(data)
                .enter()
                .append('circle')
                .attr('cx', function(d) {
                    return d[xv]
                })
                .attr('cy', function(d) {
                    return d[yv]
                })
                .attr('r', 5);

        });
        
    }

    return {
        init : init,
        scatter : scatter,
    };

})();
