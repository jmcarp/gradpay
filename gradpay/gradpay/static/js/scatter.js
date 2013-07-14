/*
 * @module scatter
 * @author jmcarp
 */

var scatter = (function() {

    // Initialize SVG variables
    var svg, points, tip;
    var height = 500,
        width = 500, 
        padding = 50;
    
    /* 
     * 
     */
    function init() {
        
        // Create SVG object
        svg = d3.select('body')
            .append('svg:svg')
            .attr('width', width)
            .attr('height', height);
        
        // Create counties group
        points = svg.append('svg:g')
            .attr('id', 'points');
        
        // Create tooltip
        tip = d3.select("body").append("div")   
            .attr("class", "tooltip")               
            .style("opacity", 0);        

    }

    /**
     * @class scatter
     */
    function scatter(selector, xv, yv) {
        
        // Initialize
        var data, values;

        // 
        $.getJSON(
            '/scatter_json?xv=' + xv + '&yv=' + yv
        ).done(function(data) {

            // Get min / max values
            var xmin = d3.min(data, function(d) {return d[xv]}),
                xmax = d3.max(data, function(d) {return d[xv]}),
                ymin = d3.min(data, function(d) {return d[yv]}),
                ymax = d3.max(data, function(d) {return d[yv]});

            // Define scales
            var xscale = d3.scale.linear()
                .domain([xmin, xmax])
                .range([padding, width - padding]);
            var yscale = d3.scale.linear()
                .domain([ymin, ymax])
                .range([padding, height - padding]);
            
            // Define axes
            var xaxis = d3.svg.axis()
                .scale(xscale)
                .orient('bottom')
                .ticks(5);
            var yaxis = d3.svg.axis()
                .scale(yscale)
                .orient('left')
                .ticks(5);

            svg.selectAll('circle')
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
                .on('mouseover', function(d) {      
                    tip.transition()        
                        .duration(200)      
                        .style("opacity", .9);      
                    tip.html(d.institution)
                        .style("left", (d3.event.pageX) + "px")     
                        .style("top", (d3.event.pageY - 28) + "px");    
                    })                  
                .on('mouseout', function(d) {       
                    tip.transition()        
                        .duration(500)      
                        .style("opacity", 0);   
                });
            /*
            svg.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(0," + (height - padding) + ")")
                .call(xaxis);
            svg.append("g")
                .attr("class", "axis")
                .attr("transform", "translate(" + padding + ",0)")
                .call(yaxis);
            */

        });
        
    }

    return {
        init : init,
        scatter : scatter,
    };

})();
