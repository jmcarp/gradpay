/*
 * @module scatter
 * @author jmcarp
 */

var scatter = (function() {

    // Initialize SVG variables
    var svg, points, tip;
    
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

        tip = d3.select("body").append("div")   
            .attr("class", "tooltip")               
            .style("opacity", 0);        

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
            var xscale = d3.scale.linear()
                .domain([xmin, xmax])
                .range([50, 250]);
            var yscale = d3.scale.linear()
                .domain([ymin, ymax])
                .range([50, 250]);
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
                .attr('r', 5)
                .on("mouseover", function(d) {      
                    tip.transition()        
                        .duration(200)      
                        .style("opacity", .9);      
                    tip.html(d.institution)
                        .style("left", (d3.event.pageX) + "px")     
                        .style("top", (d3.event.pageY - 28) + "px");    
                    })                  
                .on("mouseout", function(d) {       
                    tip.transition()        
                        .duration(500)      
                        .style("opacity", 0);   
                });

        });
        
    }

    return {
        init : init,
        scatter : scatter,
    };

})();
