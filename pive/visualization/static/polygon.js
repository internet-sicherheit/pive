/* Copyright (c) 2014 - 2015, David Bothe
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:

 1. Redistributions of source code must retain the above copyright notice,
 this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright notice,
 this list of conditions and the following disclaimer in the documentation
 and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.

*/

class Polygon {

    constructor(config, init) {
        this.config = config;

        this.serialisable_elements = [
			'width', 'height', 'dataset_url', 'map_shape_url', 'scale_extent', 'zoom_threshold', 'div_hook_map',
            'div_hook_legend', 'div_hook_tooltip', 'tooltip_div_border', 'map_fill', 'map_stroke', 'fill_opacity', 'stroke_opacity',
            'mouseover_opacity', 'mouseout_opacity', 'outer_map_fill'
		];
        this.width = config.width;
        this.height = config.height;
        this.map_shape_url = config.map_shape_url;
        this.dataset_url = config.dataset_url;
        this.city = config.city;
        this.scale_extent = config.scale_extent;
        this.transExtent = [[0,0],[config.width,config.height]];
        this.zoom_threshold = config.zoom_threshold;
        this.div_hook_map = config.div_hook_map;
        this.div_hook_tooltip = config.div_hook_tooltip;
        this.tooltip_div_border = config.tooltip_div_border;
        this.map_fill = config.map_fill;
        this.map_stroke = config.map_stroke;
        this.fill_opacity = config.fill_opacity;
        this.stroke_opacity = config.stroke_opacity;
        this.mouseover_opacity = config.mouseover_opacity;
        this.mouseout_opacity = config.mouseout_opacity;
        this.outer_map_fill = config.outer_map_fill;
        this.fontsize = 12;
        this.moveAmount = 20;

        this.init = init;
    }

    get_current_config() {
		let config = {};
		for (let element_name of this.serialisable_elements) {
			config[element_name] = this[element_name];
		}
		return config;
	}

    render() {
        this.hash_div_hook_map = '#'.concat(this.div_hook_map);
        this.hash_div_hook_legend = '#'.concat(this.div_hook_legend);

        this.root_div_hook_map = document.getElementById(this.div_hook_map);
        this.root_div_hook_map.innerHTML = "";
        this.root_div_hook_tooltip = document.getElementById(this.div_hook_tooltip);
        this.root_div_hook_tooltip.innerHTML = "";
        this.root_div_hook_tooltip.style.border = "none"

        //FIXME: Clear all 3 div hooks before rendering

        const css_pan_zoom_rect = `#${this.div_hook_map} .pan rect, .zoom rect { fill: black; opacity: 0.2; }\n`,
            css_pan_zoom_text = `#${this.div_hook_map} .pan text, .zoom text { fill: black; font-size: 18px; text-anchor: middle; }\n`,
            css_pan_zoom_hover = `#${this.div_hook_map} .pan:hover rect, .pan:hover text, .zoom:hover rect, .zoom:hover text { fill:blue; }\n`,
            css_text_label = `#${this.div_hook_map} .label { font-family: Helvetica, sans-serif; text-anchor: middle; fill: black; }\n`,
            css_tooltip = `#${this.div_hook_map} { font-family: Helvetica, sans-serif; margin-top: 10px; padding: 5px; white-space: pre-wrap; width: 590px; }\n`;

        var css = css_pan_zoom_rect.concat(css_pan_zoom_text).concat(css_pan_zoom_hover).concat(css_text_label).concat(css_tooltip);

        var style = document.createElement("style");
        style.type = "text/css";
        style.appendChild(document.createTextNode(css));
        this.root_div_hook_map.appendChild(style);
        const chart_object = this;

// Configure the map
        configMap();

// Determine and execute the method for visualization
        visualize(chart_object.map_shape_url, chart_object.dataset_url);


// Set up the map
// Parameters: Scale factor for zooming, translate extent for panning borders and translate value for starting viewpoint
        function configMap() {
            // Define map projection
            chart_object.projection = d3.geoMercator();

            // Define path generator
            chart_object.path = d3.geoPath()
                .projection(chart_object.projection);

            // Create SVG element
            chart_object.svg = d3.select(chart_object.hash_div_hook_map)
                .append("svg")
                .attr("width", chart_object.width)
                .attr("height", chart_object.height);

            // Then define the zoom behavior
            chart_object.zoom = d3.zoom()
                .scaleExtent(chart_object.scale_extent)
                .translateExtent(chart_object.transExtent)
                .on("zoom", function (event) {
                    chart_object.map.selectAll("path").attr("transform", "translate(" + event.transform.x + "," + event.transform.y + ") scale(" + event.transform.k + ")");
                    chart_object.map.selectAll("text")
                        .attr("transform", "translate(" + event.transform.x + "," + event.transform.y + ") scale(" + event.transform.k + ")")
                        .attr("font-size", chart_object.fontsize / event.transform.k)
                        .text(function (d) {
                            if (event.transform.k < chart_object.zoom_threshold) {
                                return d.properties.id;
                            } else {
                                return d.properties.name;
                            }
                        });
                })


            // Create a container in which all pan-able elements will live
            chart_object.map = chart_object.svg.append("g")
                .attr("id", "map")
                .call(chart_object.zoom);


            // Create a new, invisible background rect to catch drag events
            chart_object.map.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", chart_object.width)
                .attr("height", chart_object.height)
                .attr("opacity", 0);
        }

        function vizPolygon(json_file, inner_shape) {

            const outer_map = chart_object.map.append("g")
                .attr("id", "outer_map")

            const inner_map = chart_object.map.append("g")
                .attr("id", "inner_map")

            // Load in GeoJSON data
            d3.json(json_file, chart_object.init).then(function (json) {

                for (let feature of json.features) {
                    d3ify_polygon(feature)
                }

                chart_object.projection.fitExtent([[chart_object.width * 0.1, chart_object.height * 0.1], [chart_object.width * 0.9, chart_object.height * 0.9]], json);

                // Bind data and create one path per GeoJSON feature
                outer_map.selectAll("path")
                    .data(json.features)
                    .enter()
                    .append("path")
                    .attr("class", "json_path")
                    .attr("d", chart_object.path)
                    .style("fill", chart_object.outer_map_fill)
                    .style("stroke", chart_object.map_stroke)
                    .style("fill-opacity", chart_object.fill_opacity)
                    .style("stroke-opacity", chart_object.stroke_opacity);

                // Create a label to display its name
                outer_map.selectAll("text")
                    .data(json.features)
                    .enter()
                    .append("text")
                    .attr("class", "label")
                    .attr("x", function (d) {
                        return chart_object.path.centroid(d)[0];
                    })
                    .attr("y", function (d) {
                        return chart_object.path.centroid(d)[1];
                    })
                    .text(function (d) {
                        return d.properties.id;
                    });
            }).then(function () {
                return d3.json(inner_shape, chart_object.init)
            }).then(function (inner_json) {

                for (let feature of inner_json) {
                    d3ify_polygon(feature)
                }

                // Bind data and create one path per GeoJSON feature
                inner_map.selectAll("path")
                    .data(inner_json)
                    .enter()
                    .append("path")
                    .attr("class", "json_path")
                    .attr("d", chart_object.path)
                    .style("fill", chart_object.map_fill)
                    .style("stroke", chart_object.map_stroke)
                    .style("fill-opacity", chart_object.fill_opacity)
                    .style("stroke-opacity", chart_object.stroke_opacity)
                    // Increase opacity while hovering over a polygon
                    .on("mouseover", function () {
                        d3.select(this).style("fill-opacity", chart_object.mouseover_opacity);
                    })
                    .on("mouseout", function () {
                        d3.select(this).style("fill-opacity", chart_object.mouseout_opacity);
                    })
                    .on("click", function (event, d) {
                        var header = getHeader(d.properties);
                        showTooltip(d.properties, header);
                    })

                inner_map.selectAll("text")
                    .data(inner_json)
                    .enter()
                    .append("text")
                    .attr("class", "label")
                    .attr("x", function (d) {
                        return chart_object.path.centroid(d)[0];
                    })
                    .attr("y", function (d) {
                        return chart_object.path.centroid(d)[1];
                    })
                    .text(function (d) {
                        return d.properties.id;
                    });
            });

        }

// Determine method for visualization
// Parameters: Selected file, GeoJSON files and visualization type
        function visualize(json_file, inner_shape) {

            vizPolygon(json_file, inner_shape);

            // Call functions to initialize pan and zoom buttons
            createPanButtons();
            createZoomButtons();
        }

// Read CSV header to check if columns for lat and lon data exist
// Parameters: Header of CSV
        function getLatLon(header) {
            var latLon = [];
            var lat = ["Latitude", "Lat"];
            var latLC = [];
            var lon = ["Longitude", "Lon"];
            var lonLC = [];

            for (let i = 0; i < lat.length; i++) {
                var name = lat[i].toLowerCase();
                latLC.push(name);
            }

            for (let i = 0; i < lon.length; i++) {
                var name = lon[i].toLowerCase();
                lonLC.push(name);
            }

            for (let i = 0; i < header.length; i++) {
                var columnName = header[i];
                if (latLC.includes(columnName.toLowerCase())) {
                    latLon.push(columnName);
                    break;
                }
            }

            for (let i = 0; i < header.length; i++) {
                var columnName = header[i];
                if (lonLC.includes(columnName.toLowerCase())) {
                    latLon.push(columnName);
                    break;
                }
            }

            return latLon;
        }

// Create pan buttons
        function createPanButtons() {

            //Create the clickable groups

            //North
            var north = chart_object.svg.append("g")
                .attr("class", "pan")   //All share the 'pan' class
                .attr("id", "north");   //The ID will tell us which direction to head

            north.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", chart_object.width)
                .attr("height", 30);

            north.append("text")
                .attr("x", chart_object.width / 2)
                .attr("y", 20)
                .html("&uarr;");

            //South
            var south = chart_object.svg.append("g")
                .attr("class", "pan")
                .attr("id", "south");

            south.append("rect")
                .attr("x", 0)
                .attr("y", chart_object.height - 30)
                .attr("width", chart_object.width)
                .attr("height", 30);

            south.append("text")
                .attr("x", chart_object.width / 2)
                .attr("y", chart_object.height - 10)
                .html("&darr;");

            //West
            var west = chart_object.svg.append("g")
                .attr("class", "pan")
                .attr("id", "west");

            west.append("rect")
                .attr("x", 0)
                .attr("y", 30)
                .attr("width", 30)
                .attr("height", chart_object.height - 60);

            west.append("text")
                .attr("x", 15)
                .attr("y", chart_object.height / 2)
                .html("&larr;");

            //East
            var east = chart_object.svg.append("g")
                .attr("class", "pan")
                .attr("id", "east");

            east.append("rect")
                .attr("x", chart_object.width - 30)
                .attr("y", 30)
                .attr("width", 30)
                .attr("height", chart_object.height - 60);

            east.append("text")
                .attr("x", chart_object.width - 15)
                .attr("y", chart_object.height / 2)
                .html("&rarr;");


            // Panning interaction

            d3.selectAll(".pan")
                .on("click", function () {

                    // Set x/y to zero for now
                    var x = 0;
                    var y = 0;

                    // Which way are we headed?
                    var direction = d3.select(this).attr("id");

                    // Modify the offset, depending on the direction
                    switch (direction) {
                        case "north":
                            y += chart_object.moveAmount;
                            break;
                        case "south":
                            y -= chart_object.moveAmount;
                            break;
                        case "west":
                            x += chart_object.moveAmount;
                            break;
                        case "east":
                            x -= chart_object.moveAmount;
                            break;
                        default:
                            break;
                    }

                    // This triggers a zoom event, translating by x, y
                    chart_object.map.transition()
                        .call(chart_object.zoom.translateBy, x, y);
                });
        };

// Create zoom buttons
        function createZoomButtons() {

            // Create the clickable groups

            // Zoom in button
            var zoomIn = chart_object.svg.append("g")
                .attr("class", "zoom")
                .attr("id", "in")
                .attr("transform", "translate(" + (chart_object.width - 110) + "," + (chart_object.height - 70) + ")");

            zoomIn.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 30)
                .attr("height", 30)
                .attr("rx", 5)
                .attr("ry", 5);

            zoomIn.append("text")
                .attr("x", 15)
                .attr("y", 20)
                .text("+");

            // Zoom out button
            var zoomOut = chart_object.svg.append("g")
                .attr("class", "zoom")
                .attr("id", "out")
                .attr("transform", "translate(" + (chart_object.width - 70) + "," + (chart_object.height - 70) + ")");

            zoomOut.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 30)
                .attr("height", 30)
                .attr("rx", 5)
                .attr("ry", 5);

            zoomOut.append("text")
                .attr("x", 15)
                .attr("y", 20)
                .html("&ndash;");

            // Zooming interaction
            d3.selectAll(".zoom")
                .on("click", function () {

                    // Set how much to scale on each click
                    var scaleFactor;

                    // Which way are we headed?
                    var direction = d3.select(this).attr("id");

                    // Modify the k scale value, depending on the direction
                    switch (direction) {
                        case "in":
                            scaleFactor = 1.5;
                            break;
                        case "out":
                            scaleFactor = 0.75;
                            break;
                        default:
                            break;
                    }

                    // This triggers a zoom event, scaling by 'scaleFactor'
                    chart_object.map.transition()
                        .call(chart_object.zoom.scaleBy, scaleFactor);
                });
        };

// Display tooltip for heatmap or POIs showing the explicit values
// Parameter: Selected district or point of interest to show tooltip for and header names
        function showTooltip(data, header) {
            // Get column names for lat and lon data to hide these columns in the tooltip
            var latLon = getLatLon(header);
            var lat = latLon[0];
            var lon = latLon[1];
            var div = chart_object.root_div_hook_tooltip;
            var text = "";

            for (let i = 0; i < header.length; i++) {
                var name = header[i];
                if (name != lat && name != lon && name != "id") {
                    var value = data[name];
                    if (text) {
                        text = text + "\n" + name + ": " + value;
                    } else {
                        text = name + ": " + value;
                    }
                }
            }
            if (div.innerHTML != text) {
                div.style.border = chart_object.tooltip_div_border;
                div.innerHTML = text;
            } else {
                div.style.border = "none";
                div.innerHTML = "";
            }
        }

// Access data to get column names/names of properties
// Parameter: Data of CSV or JSON file
        function getHeader(data) {
            var header = [];

            for (let key in data) {
                if (Array.isArray(data)) {
                    header.push(data[key]);
                } else {
                    header.push(key);
                }

            }

            return header;
        }


        function is_clockwise(coordinates) {
            let summed_orientation = 0;
            for (let index = 0; index < coordinates.length; index++) {
                const p1 = coordinates[index];
                const p2 = coordinates[(index + 1) % coordinates.length];
                summed_orientation += ((p2[0] - p1[0]) * (p2[1] + p1[1]));
            }
            return summed_orientation > 0.0;
        }

        function d3ify_polygon(polygon) {
            /* GeoJSON objects have the wrong winding order (RFC7946) and need to be wound the clockwise for outer rings
            */
            if (polygon["geometry"]["type"] == "Polygon") {
                for (let index in polygon["geometry"]["coordinates"]) {
                    if (index == 0) {
                        if (!is_clockwise(polygon["geometry"]["coordinates"][index])) {
                            polygon["geometry"]["coordinates"][index].reverse()
                        }
                    } else {
                        if (is_clockwise(polygon["geometry"]["coordinates"][index])) {
                            polygon["geometry"]["coordinates"][index].reverse()
                        }
                    }
                }
            } else {
                if (polygon["geometry"]["type"] == "MultiPolygon") {
                    for (let polygon_index in polygon["geometry"]["coordinates"]) {
                        for (let index in polygon["geometry"]["coordinates"][polygon_index]) {
                            if (index == 0) {
                                if (!is_clockwise(polygon["geometry"]["coordinates"][polygon_index][index])) {
                                    polygon["geometry"]["coordinates"][polygon_index][index].reverse()
                                }
                            } else {
                                if (is_clockwise(polygon["geometry"]["coordinates"][polygon_index][index])) {
                                    polygon["geometry"]["coordinates"][polygon_index][index].reverse()
                                }
                            }
                        }
                    }
                }
            }
            return polygon
        }

    }
}

pive.addChartVersion("polygon", "0.3.4", Polygon);