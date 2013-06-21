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
        var data, values;

        // 
        $.getJSON(
            '/scatter_json?xv=' + xv + '&yv=' + yv
        ).done(function(data) {
            var xmin = d3.min(data, function(d) {return d[xv]}),
                xmax = d3.max(data, function(d) {return d[xv]}),
                ymin = d3.min(data, function(d) {return d[yv]}),
                ymax = d3.max(data, function(d) {return d[yv]});
            var xscale = d3.scale.linear
                .domain([xmin, xmax])
                .range([0, 100]);
            var yscale = d3.scale.linear
                .domain([0, 100])
                .range([ymin, ymax]);
            points.selectAll('path')
                .data(data)
                .enter()
                .append('circle')
                .attr('cx', function(d) {
                    return xscale(d[xv]);
                })
                .attr('cy', function(d) {
                    return yscale(d[yv]);
                })
                .attr('r', 5);

        });
        
    }

    return {
        init : init,
        scatter : scatter,
    };

})();
