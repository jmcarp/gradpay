/**
 * @module choro
 * @author jmcarp
 */

var choro = (function() {

    // Initialize SVG variables
    var svg, counties, states;
    var height = 500,
        width = 960, 
        padding = 50;
    
    // Initialize underlay data
    var state_info, county_info;
    
    /* 
     * 
     */
    function init(selector) {
        
        // Create SVG object
        svg = d3.select(selector)
            .append('svg:svg').
            .attr('height', height)
            .attr('width', width);
        
        // Create counties group
        counties = svg.append('svg:g')
            .attr('id', 'counties');
        
        // Create states group
        states = svg.append('svg:g')
            .attr('id', 'states');

    }

    /* 
     * @class choro
     * @static
     * @param selector
     * @param iv
     * @param dv
     */
    function choro(iv, dv) {
        
        // Initialize
        var data, values, cscale;

        // Initialize deferred list
        var deferred = [];
        
        // Start request for overlay data
        deferred.push($.getJSON('/choro_json?iv=' + iv + '_code&dv=' + dv));
        
        // Start request for state choropleth data
        deferred.push(state_info || $.getJSON('/static/geo/us-states.json'));

        // Optionally start request for county choropleth data
        if (iv == 'county') {
            deferred.push(county_info || $.getJSON('/static/geo/us-counties.json'))
        }
        
        // Wait for AJAX requests to finish
        $.when.apply(this, deferred).done(function() {
            
            // Update globals
            state_info = arguments[1];
            county_info = arguments[2] || county_info;
            
            // Draw counties
            if (iv == 'county') {
                counties.selectAll('path')
                    .data(county_info[0].features)
                    .enter().append('path')
                    .attr('d', d3.geo.path());
                states.selectAll('path')
                    .style('fill', 'none');
            }
            
            // Draw states
            states.selectAll('path')
                .data(state_info[0].features)
                .enter().append('path')
                .attr('d', d3.geo.path());
            if (iv == 'state_code') {
                states.selectAll('path')
                    .style('fill', '#000');
            }

            // Set up color scale
            data = arguments[0][0];
            values = d3.values(data);
            cscale = d3.scale.linear()
                .domain([d3.min(values), d3.max(values)])
                .range(['blue', 'red']);
            function quantize(d) {
                return cscale(data[d.id]);
            }

            // Draw overlay
            if (iv == 'county') {
                counties.selectAll('path')
                    .transition()
                    .style('fill', quantize);
            } else {
                states.selectAll('path')
                    .transition()
                    .style('fill', quantize);
            }

        });

    }

    return {
        init : init,
        choro : choro,
    };

})();
