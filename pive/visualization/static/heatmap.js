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

class Heatmap {
    constructor(config, init) {

        this.serialisable_elements = [
			'width', 'height', 'scale_extent', 'zoom_threshold', 'div_hook_map',
            'div_hook_legend', 'div_hook_tooltip', 'tooltip_div_border', 'map_stroke', 'fill_opacity', 'stroke_opacity',
            'mouseover_opacity', 'mouseout_opacity', 'legendwidth', 'legendheight', 'legendmargin', 'legendticksize',
            'legendborder', 'headers', 'colors'
		];
        this.width = config.width;
        this.height = config.height;
        this.dataset_url = config.dataset_url;
        this.map_shape_url = config.map_shape_url;
        this.city = config.city;  //Should this be serialisable too?
        this.scale_extent = config.scale_extent;
        this.transExtent = [[0, 0], [config.width, config.height]]
        this.zoom_threshold = config.zoom_threshold;
        this.div_hook_map = config.div_hook_map;
        this.div_hook_legend = config.div_hook_legend;
        this.div_hook_tooltip = config.div_hook_tooltip;
        this.tooltip_div_border = config.tooltip_div_border;
        this.map_stroke = config.map_stroke;
        this.fill_opacity = config.fill_opacity;
        this.stroke_opacity = config.stroke_opacity;
        this.mouseover_opacity = config.mouseover_opacity;
        this.mouseout_opacity = config.mouseout_opacity;
        this.legendwidth = config.legendwidth;
        this.legendheight = config.legendheight;
        this.legendmargin = config.legendmargin;
        this.legendticksize = config.legendticksize;
        this.legendborder = config.legendborder;
        this.headers = config.headers;
        this.fontsize = 12;
        this.moveAmount = 20;

        this.colors = d3.scaleQuantize().range(config.colors);

        this.svg = null;
        this.map = null;
        this.path = null;
        this.projection = null;
        this.zoom = null;

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
        // Configure the map
        this.configMap();

        // Determine and execute the method for visualization
        this.visualize(this.dataset_url, this.map_shape_url);

    }


// Set up the map
// Parameters: Scale factor for zooming, translate extent for panning borders and translate value for starting viewpoint
    function

    configMap() {
        const chart_object = this;
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
            .duration(10)
            .translateExtent(chart_object.transExtent)
            .on("zoom", function (event) {
                chart_object.map.selectAll("path").attr("transform", "translate(" + event.transform.x + "," + event.transform.y + ") scale(" + event.transform.k + ")");
                chart_object.map.selectAll("text").attr("transform", "translate(" + event.transform.x + "," + event.transform.y + ") scale(" + event.transform.k + ")");
                chart_object.svg.selectAll(".label").attr("font-size", chart_object.fontsize / event.transform.k)
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
            //.call(drag)
            .call(chart_object.zoom)


        // Create a new, invisible background rect to catch drag events
        chart_object.map.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", chart_object.width)
            .attr("height", chart_object.height)
            .attr("opacity", 0);
    }


// Heatmap method selected
// Parameters: CSV file, GeoJSON file
    vizHeatmap(filename, json_file) {
        const chart_object = this;
        // Load in JSON data
        d3.json(filename, chart_object.init).then(async function (data) {
            // Read header from CSV
            var header = chart_object.getHeader();


            // Parse min and max from data to int for d3 min/max function
            var min = d3.min(data, function (d) {
                return parseInt(d[header[1]]);
            });
            var max = d3.max(data, function (d) {
                return parseInt(d[header[1]]);
            });

            // Set input domain for color scale
            chart_object.colors.domain([min, max]);
            // color.domain(d3.extent(data));
            let json = await d3.json(json_file, chart_object.init)

            for (let feature of json.features) {
                Heatmap.d3ify_polygon(feature)
            }

            chart_object.projection.fitExtent([[chart_object.width * 0.1, chart_object.height * 0.1], [chart_object.width * 0.9, chart_object.height * 0.9]], json);

            // Merge the CSV data and GeoJSON
            // Loop through once for each CSV data value
            for (var i = 0; i < data.length; i++) {

                var dataDistrict = data[i][header[0]];
                var dataValue = data[i][header[1]];

                // Find the corresponding district inside the GeoJSON
                for (var j = 0; j < json.features.length; j++) {

                    var jsonDistrict = json.features[j].properties.name;

                    if (dataDistrict == jsonDistrict) {

                        // Copy the data value into the JSON
                        json.features[j].properties.value = dataValue;

                        // Stop looking through the JSON
                        break;
                    }
                }
            }

            // Bind data and create one path per GeoJSON feature
            chart_object.map.selectAll("path")
                .data(json.features)
                .enter()
                .append("path")
                .attr("class", "json_path")
                .attr("d", chart_object.path)
                .style("fill", function (d) {
                    // Get data value
                    var value = d.properties.value;

                    if (value) {
                        return chart_object.colors(value);
                    } else {
                        return "#ccc";
                    }
                })
                .style("stroke", chart_object.map_stroke)
                .style("fill-opacity", chart_object.fill_opacity)
                .style("stroke-opacity", chart_object.stroke_opacity)
                // Increase opacity while hovering over a district, and show a tooltip after clicking it
                .on("mouseover", function () {
                    d3.select(this).style("fill-opacity", chart_object.mouseover_opacity);
                })
                .on("mouseout", function () {
                    d3.select(this).style("fill-opacity", chart_object.mouseout_opacity);
                })
                .on("click", function (event, d) {
                    var header = chart_object.getHeader();
                    chart_object.showTooltip(d.properties, header);
                });

            // Create one label per district to display its name
            chart_object.map.selectAll("text")
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
                    if (d.properties.name) {
                        return d.properties.id;
                    }
                });

            // Call function to initialize the color legend
            chart_object.continuousLegend();
        });
    }


// Determine method for visualization
// Parameters: Selected file, GeoJSON files and visualization type
    visualize(filename, json_file) {

        this.vizHeatmap(filename, json_file);

        // Call functions to initialize pan and zoom buttons
        this.createPanButtons();
        this.createZoomButtons();
    }


// Read CSV header to check if columns for lat and lon data exist
// Parameters: Header of CSV
    static getLatLon(header) {
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
    createPanButtons() {
        const chart_object = this;
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
    createZoomButtons() {
        const chart_object = this;
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
    showTooltip(data, header) {
        const chart_object = this;
        // Get column names for lat and lon data to hide these columns in the tooltip
        var latLon = Heatmap.getLatLon(header);
        var lat = latLon[0];
        var lon = latLon[1];
        var div = chart_object.root_div_hook_tooltip;
        var text = "";

        text += header[0] + ": " + data.name + "\n";
        text += header[1] + ": " + data.value;
        for (let i = 2; i < header.length; i++) {
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

// Create continous color legend
    continuousLegend() {
        const chart_object = this;
        var canvas = d3.select(chart_object.hash_div_hook_legend)
            // Width, height and position of div element
            .style("height", chart_object.legendheight + "px")
            .style("width", chart_object.legendwidth + "px")
            .style("position", "relative")
            .append("canvas")
            // Dimension of pixels in canvas element
            .attr("height", chart_object.legendheight - chart_object.legendmargin.top - chart_object.legendmargin.bottom)
            .attr("width", 1)
            // Display size of canvas element
            .style("height", (chart_object.legendheight - chart_object.legendmargin.top - chart_object.legendmargin.bottom) + "px")
            .style("width", (chart_object.legendwidth - chart_object.legendmargin.left - chart_object.legendmargin.right) + "px")
            // Border and position with margin of canvas element
            .style("border", chart_object.legendborder)
            .style("position", "absolute")
            .style("top", (chart_object.legendmargin.top) + "px")
            .style("left", (chart_object.legendmargin.left) + "px")
            // Get the canvas element of this selection
            .node();

        // Get a two-dimensional rendering context for canvas element (CanvasRenderingContext2D object)
        var ctx = canvas.getContext("2d");

        // Set range and domain for the linear color scale
        var legendscale = d3.scaleLinear()
            .range([1, chart_object.legendheight - chart_object.legendmargin.top - chart_object.legendmargin.bottom])
            .domain(chart_object.colors.domain());

        // image data hackery based on http://bl.ocks.org/mbostock/048d21cf747371b11884f75ad896e5a5
        // Create ImageData object with specified dimensions
        var image = ctx.createImageData(1, chart_object.legendheight);
        // Determine the color for each pixel within the height of the legend
        d3.range(chart_object.legendheight).forEach(function (i) {
            // Based on the number of each pixel within the range give the RGB color for the corresponding value of the domain
            var c = d3.rgb(chart_object.colors(legendscale.invert(i)));
            // Store four values for each pixel in the data array of the image
            image.data[4 * i] = c.r;
            image.data[4 * i + 1] = c.g;
            image.data[4 * i + 2] = c.b;
            //RGBa, alpha value, opacity
            image.data[4 * i + 3] = 200;
        });
        // Paint image data onto the canvas element
        ctx.putImageData(image, 0, 0);

        // Store tick values for the axis of the legend in array
        var tickVal = [];
        // Determine min and max of domain and calculate values where the color changes
        var tickMin = chart_object.colors.domain()[0];
        var tickMax = chart_object.colors.domain()[1];
        var tickIncrement = (tickMax - tickMin) / chart_object.colors.range().length;
        // Start with minimum value
        var n = tickMin;
        // Ticks for min and max values of the domain and one tick for each color change in the legend
        for (let i = 0; i <= chart_object.colors.range().length; i++) {
            // Push value to array
            tickVal.push(parseInt(n));
            // Increase by increment value
            n += tickIncrement;
        }

        // Construct a right-oriented axis generator for the given scale with specified tick values
        var legendaxis = d3.axisRight()
            .scale(legendscale)
            .tickSize(chart_object.legendticksize)
            .tickValues(tickVal);

        // Append SVG element to DIV element for the legend
        var legendSvg = d3.select(chart_object.hash_div_hook_legend)
            .append("svg")
            .attr("height", (chart_object.legendheight) + "px")
            .attr("width", (chart_object.legendwidth) + "px")
            .style("position", "absolute")
            .style("left", "0px")
            .style("top", "0px")

        // Append group element to SVG and position legendaxis in the group element
        legendSvg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(" + (chart_object.legendwidth - chart_object.legendmargin.left - chart_object.legendmargin.right + 3) + "," + (chart_object.legendmargin.top) + ")")
            .call(legendaxis);
    };

// Access data to get column names/names of properties
// Parameter: Data of CSV or JSON file
    getHeader() {
        const chart_object = this;
        return chart_object.headers;
    }
    static is_clockwise(coordinates) {
        let summed_orientation = 0;
        for (let index = 0; index < coordinates.length; index++) {
            const p1 = coordinates[index];
            const p2 = coordinates[(index + 1) % coordinates.length];
            summed_orientation += ((p2[0] - p1[0]) * (p2[1] + p1[1]));
        }
        return summed_orientation > 0.0;
    }
    static d3ify_polygon(polygon) {
        /* GeoJSON objects have the wrong winding order (RFC7946) and need to be wound the clockwise for outer rings
        */
        if (polygon["geometry"]["type"] == "Polygon") {
            for (let index in polygon["geometry"]["coordinates"]) {
                if (index == 0) {
                    if (!Heatmap.is_clockwise(polygon["geometry"]["coordinates"][index])) {
                        polygon["geometry"]["coordinates"][index].reverse()
                    }
                } else {
                    if (Heatmap.is_clockwise(polygon["geometry"]["coordinates"][index])) {
                        polygon["geometry"]["coordinates"][index].reverse()
                    }
                }
            }
        } else {
            if (polygon["geometry"]["type"] == "MultiPolygon") {
                for (let polygon_index in polygon["geometry"]["coordinates"]) {
                    for (let index in polygon["geometry"]["coordinates"][polygon_index]) {
                        if (index == 0) {
                            if (!Heatmap.is_clockwise(polygon["geometry"]["coordinates"][polygon_index][index])) {
                                polygon["geometry"]["coordinates"][polygon_index][index].reverse()
                            }
                        } else {
                            if (Heatmap.is_clockwise(polygon["geometry"]["coordinates"][polygon_index][index])) {
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