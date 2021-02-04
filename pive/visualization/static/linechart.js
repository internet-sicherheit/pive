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

class Linechart {

	constructor(config) {
		this.config = config;
		this.serialisable_elements = [
			'width', 'height', 'padding', 'label_size', 'viewport', 'jumplength', 'xlabel', 'ylabel', 'datakeys',
			'timeformat', 'iconwidth', 'iconheight', 'iconcolor', 'iconhighlight', 'interpolation', 'iso', 'scales', 'colors',
			'div_hook', 'circleopacity', 'highlightfactor', 'minradius', 'maxradius'
		];
		this.width = config.width;
		this.height = config.height;
		this.padding	= config.padding;
		this.label_size = config.label_size;
		this.viewport = config.viewport;
		this.jumplength = config.jumplength;
		this.xlabel = config.xlabel;
		this.ylabel = config.ylabel;
		this.datakeys = config.datakeys;
		this.timeformat = config.timeformat;
		this.iconwidth = config.iconwidth;
		this.iconheight = config.iconheight;
		this.iconcolor = config.iconcolor;
		this.iconhighlight = config.iconhighlight;
		this.interpolation = config.interpolation;
		this.dataset_url = config.dataset_url;
		this.iso = d3.utcFormat(config.iso);
		this.scales = config.scales;
		this.colors = config.colors;
		this.div_hook = config.div_hook;
		this.tickrotation = -45;
		this.highlightradius = 8;
	}

	get_current_config() {
		let config = {};
		for (let element_name of this.serialisable_elements) {
			config[element_name] = this[element_name];
		}
		return config;
	}


	render() {
		var root_div = document.getElementById(this.div_hook);
		root_div.innerHTML = "";

		const css_line = `#${this.div_hook} .line { stroke: ${this.config.line_stroke}; fill: none; stroke-width: 2.5px}\n`,
			css_tooltip = `#${this.div_hook} .tooltip {color: white; line-height: 1; padding: 12px; font-weight: italic; font-family: arial; border-radius: 5px;}\n`,
			css_axis_path = `#${this.div_hook} .axis path { fill: none; stroke: ${this.config.line_stroke}; shape-rendering: crispEdges;}\n`,
			css_axis_line = `#${this.div_hook} .axis line { stroke: ${this.config.line_stroke}; shape-rendering: ${this.config.shape_rendering };}\n`,
			css_path_area = `#${this.div_hook} .path area { fill: blue; }\n`,
			css_axis_text = `#${this.div_hook} .axis text {font-family: sans-serif; font-size: ${this.config.font_size }px }\n`,
			css_xlabel_text = `#${this.div_hook} .xlabel {font-family: helvetica; font-size: ${this.label_size }px }\n`,
			css_ylabel_text = `#${this.div_hook} .ylabel {font-family: helvetica; font-size: ${this.label_size }px }\n`,
			css_x_axis_line = `#${this.div_hook} .x.axis line { stroke: grey; stroke-opacity: 0.25; stroke-width: 2.5px}\n`,
			css_y_axis_line = `#${this.div_hook} .y.axis line { stroke: grey; stroke-opacity: 0.25; stroke-width: 2.5px}`;

		var css = css_line.concat(css_tooltip).concat(css_axis_path).concat(css_axis_line).concat(css_path_area).concat(css_axis_text)
				  .concat(css_xlabel_text).concat(css_ylabel_text).concat(css_x_axis_line).concat(css_y_axis_line);

		var style = document.createElement('style');
		style.type = 'text/css';
		style.appendChild(document.createTextNode(css));
		root_div.appendChild(style);
		const chart_object = this;
		d3.json(chart_object.dataset_url).then(function (data) {

			var dataset = data;

			var current_offset = 0;
			var viewdata = dataset.slice(current_offset, current_offset + chart_object.viewport);

			var max_y = d3.max(data, function (d) {
				var datapoint_max = d.y[0];
				for (var i = 0; i < d.y.length; i++)
					if (d.y[i] > datapoint_max) {
						datapoint_max = d.y[i];
					}
				return datapoint_max;
			});

			var min_y = d3.min(data, function (d) {
				var datapoint_min = d.y[0];
				for (var i = 0; i < d.y.length; i++)
					if (d.y[i] < datapoint_min) {
						datapoint_min = d.y[i];
					}
				return datapoint_min;
			});


			var x_extent = d3.extent(viewdata, function (d) {
				return d.x
			});
			var y_extent = [min_y, max_y];

			var xScale;
			var yScale;
			var yAxisScale;
			scaleXAxis();
			scaleYAxis();

			function getDateFromTime(time) {
				try {
					return new Date(time);
				} catch (err) {
					console.log("An Error occured while parsing the date object.");
					console.log(err.message);
					return null;
				}
				;
			};

			function scaleXAxis() {
				//###################################
				//######## scale the x-axis. ########
				//###################################
				var xrange = [chart_object.padding + chart_object.label_size + chart_object.iconwidth, chart_object.width - chart_object.padding];

				if (chart_object.scales[0] == 'linear') {
					//Provide a linear scaling.
					xScale = d3.scaleLinear()
						.range(xrange)
						.domain(x_extent);

				} else if (chart_object.scales[0] == 'log') {
					if (x_extent[0] <= 0) {
						xScale = d3.scaleLinear()
							.range(xrange)
							.domain(x_extent);
					} else {
						xScale = d3.scaleLog()
							.range(xrange)
							.domain(x_extent);
					}


				} else if (chart_object.scales[0].substring(0, 3) == 'pow') {

					//The exponent of the power scale is indicated by a number
					//following the 'pow', e.g. 'pow2'.
					const exp = parseInt(chart_object.scales[0].substring(3, chart_object.scales[0].length));

					//Provide a power scaling.
					xScale = d3.scalePow()
						.exponent(exp)
						.range(xrange)
						.domain(x_extent);

				} else if (chart_object.scales[0] == 'date') {
					//Date-code to be implemented.
					var minDate = getDateFromTime(x_extent[0]);
					var maxDate = getDateFromTime(x_extent[1]);

					xScale = d3.time.scale()
						.range(xrange)
						.domain([minDate, maxDate]);
				}
				;
			};

			function scaleYAxis() {
				//###################################
				//######## scale the x-axis. ########
				//###################################
				if (chart_object.scales[1] == 'linear') {
					//Provide a linear scaling.
					yScale = d3.scaleLinear()
						.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
						.domain(y_extent);
					yAxisScale = d3.scaleLinear()
						.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
						.domain(y_extent);

				} else if (chart_object.scales[1] == 'log') {
					if (y_extent[0] <= 0) {
						yScale = d3.scaleLinear()
							.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
							.domain(y_extent);
						yAxisScale = d3.scaleLinear()
							.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
							.domain(y_extent);
					} else {
						yScale = d3.scaleLog()
							.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
							.domain(y_extent);
						yAxisScale = d3.scaleLog()
							.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
							.domain(y_extent);
					}


				} else if (chart_object.scales[1].substring(0, 3) == 'pow') {

					//The exponent of the power scale is indicated by a number
					//following the 'pow', e.g. 'pow2'.
					exp = parseInt(chart_object.scales[1].substring(3, chart_object.scales[1].length));

					//Provide a power scaling.
					yScale = d3.scalePow()
						.exponent(exp)
						.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
						.domain(y_extent);
					yAxisScale = d3.scalePow()
						.exponent(exp)
						.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
						.domain(y_extent);

				} else if (chart_object.scales[1] == 'date') {
					//Date-code to be implemented.
					var minDate = getDateFromTime(y_extent[0]);
					var maxDate = getDateFromTime(y_extent[1]);
					yScale = d3.time.scale()
						.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
						.domain([minDate, maxDate]);
					yAxisScale = d3.time.scale()
						.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
						.domain([minDate, maxDate]);
				}
				;
			};
			var svg = d3.select('#'.concat(chart_object.div_hook)).append("svg")
				.attr("width", chart_object.width)
				.attr("height", chart_object.height);

			var tooltip = d3.select('#'.concat(chart_object.div_hook)).append("div")
				.attr("class", "tooltip")
				.style("opacity", "0.0")
				.style("top", 0 + "px");

			var xaxis = d3.axisBottom();
			var yaxis = d3.axisLeft();

			function initializeXAxis() {

				if (chart_object.scales[0] == 'date') {
					xaxis.ticks(d3.time.milliseconds, 10)
						.tickFormat(d3.time.format(chart_object.timeformat))
						.tickSize(-(chart_object.height - chart_object.padding * 2 - chart_object.label_size), 0, 0)
						.scale(xScale);
				} else {

					xaxis.tickSize(-(chart_object.height - chart_object.padding * 2 - chart_object.label_size), 0, 0)
						.scale(xScale);
				}
				;
			};

			function initializeYAxis() {
				yaxis.scale(yAxisScale);
			};

			initializeXAxis();
			initializeYAxis();

			var xa = svg.append('g')
				.attr('class', 'x axis')
				.attr('transform', 'translate(0, ' + (chart_object.height - chart_object.padding - chart_object.label_size) + ')')
				.data(viewdata)
				.call(xaxis)
				.selectAll("text")
				.style("text-anchor", "end")
				.attr("dx", "-.8em")
				.attr("dy", ".15em")
				.attr("transform", function (d) {
					return "rotate(" + chart_object.tickrotation + ")"
				});

			var ya = svg.append('g')
				.attr('class', 'y axis')
				.attr('transform', 'translate(' + (chart_object.padding + chart_object.label_size + chart_object.iconwidth) + ', ' + (-chart_object.label_size) + ')')
				.data(viewdata)
				.call(yaxis);

			var bottom_label = svg.append("text")
				.attr("class", "xlabel")
				.attr("x", (chart_object.width / 2) + (chart_object.padding / 2))
				.attr("y", chart_object.height)
				.style("text-anchor", "middle")
				.text(chart_object.xlabel);

			var left_label = svg.append("text")
				.attr("class", "ylabel")
				.attr("transform", "rotate(-90)")
				.attr("x", (-chart_object.height / 2) + (chart_object.padding / 2))
				.attr("y", 0)
				.attr("dy", "1em")
				.style("text-anchor", "middle")
				.text(chart_object.ylabel);

			function drawButtons() {
				//Append the buttons.
				var buttons = svg.append("g")
					.attr("class", "button")

				var vertical_center = (chart_object.height / 2) - (chart_object.padding / 2) - (chart_object.iconheight / 2);

				//Prepare the transformation.
				var right_translation = 'translate(' + (chart_object.width - chart_object.iconwidth) + ',' + (vertical_center) + ')';
				var left_translation = 'translate(' + (chart_object.iconwidth + 10 + chart_object.label_size) + ',' + (vertical_center) + ')';

				//Append the right arrow button and apply its transformation.
				buttons.append("path")
					.attr('d', 'm 0 0 0 ' + chart_object.iconheight + ' ' + chart_object.iconwidth + ' -' + chart_object.iconheight / 2 + 'z')
					.attr('transform', right_translation)
					.attr('fill', chart_object.iconcolor)
					.on("click", function () {
						forwardData();
					})
					.on('mouseover', function () {
						d3.select(this).attr('fill', chart_object.iconhighlight);
					})
					.on('mouseout', function () {
						d3.select(this).attr('fill', chart_object.iconcolor);
					});

				//Append the left arrow button and apply its transformation.
				buttons.append("path")
					.attr('d', 'm 0 0 0 ' + chart_object.iconheight + ' -' + chart_object.iconwidth + ' -' + chart_object.iconheight / 2 + 'z')
					.attr('transform', left_translation)
					.attr('fill', chart_object.iconcolor)
					.on("click", function () {
						backwardData();
					})
					.on('mouseover', function () {
						d3.select(this).attr('fill', chart_object.iconhighlight);
					})
					.on('mouseout', function () {
						d3.select(this).attr('fill', chart_object.iconcolor);
					});

			}

			if (chart_object.viewport > viewdata.length) {
				chart_object.viewport = viewdata.length;
			} else {
				drawButtons();
			}


			function updateXAxis(new_extent) {

				if (chart_object.scales[0] == 'date') {
					var minDate = chart_object.iso(getDateFromTime(new_extent[0]));
					var maxDate = chart_object.iso(getDateFromTime(new_extent[1]));
					xScale.domain([minDate, maxDate]);
				} else {
					xScale.domain(new_extent);
				}

			}

			function forwardData() {
				current_offset += chart_object.jumplength;

				if ((current_offset + chart_object.viewport) > dataset.length) {
					viewdata = dataset.slice(current_offset, dataset.length);
					current_offset -= chart_object.jumplength;
				} else {
					viewdata = dataset.slice(current_offset, current_offset + chart_object.viewport);
				}
				;

				//Binds the new viedata to the line generation.
				lines.datum(viewdata);

				x_extent = d3.extent(viewdata, function (d) {
					return d.x
				});


				if (chart_object.scales[0] == 'date') {
					var minDate = getDateFromTime(x_extent[0]);
					var maxDate = getDateFromTime(x_extent[1]);
					xScale.domain([minDate, maxDate]);
				} else {
					xScale.domain(x_extent);
				}
				;

				updateView();

			};


			function backwardData() {
				current_offset -= chart_object.jumplength;

				if (current_offset < 0) {
					viewdata = dataset.slice(0, 0 + chart_object.viewport);
					current_offset = 0;
				} else {
					viewdata = dataset.slice(current_offset, current_offset + chart_object.viewport);
				}
				;

				//Binds the new viedata to the line generation.
				lines.datum(viewdata);

				x_extent = d3.extent(viewdata, function (d) {
					return d.x
				});


				if (chart_object.scales[0] == 'date') {
					var minDate = getDateFromTime(x_extent[0]);
					var maxDate = getDateFromTime(x_extent[1]);
					xScale.domain([minDate, maxDate]);
				} else {
					xScale.domain(x_extent);
				}
				;

				updateView();

			};


			function updateView() {

				svg.select(".x.axis")
					.transition("updateViewX")
					.duration(250)
					.call(xaxis)

				svg.select(".x.axis")
					.selectAll("text")
					.style("text-anchor", "end")
					.attr("dx", "-.8em")
					.attr("dy", ".15em")
					.attr("transform", function (d) {
						return "rotate(" + chart_object.tickrotation + ")"
					});

				svg.selectAll(".line").remove();
				svg.selectAll(".circle").remove();

				for (var i = 0; i < viewdata[0].y.length; i++)
					drawData(i);

			};


			var valueline = d3.line();
			var lines;
			var circles = svg.selectAll("circle");


			for (var i = 0; i < viewdata[0].y.length; i++)
				drawData(i);

			function getColorIndex(y_accessor) {
				var colorindex = y_accessor;
				var color;

				while (colorindex > chart_object.colors.length - 1) {
					colorindex = colorindex - chart_object.colors.length;

				}

				color = chart_object.colors[colorindex];
				return color;
			}

			function drawData(y_accessor) {
				//If no y_accessor was defined, the data is assumed to contain only one dataset.
				//the y_accessor then becomes obsolete.
				y_accessor = (typeof y_accessor == "undefined") ? "singleData" : y_accessor;
				//Describes a line for each dataset.
				valueline = d3.line()
					.curve(d3.curveLinear) //TODO: Get curvature based on variable "interpolation"
					.x(function (d) {

						if (chart_object.scales[0] == 'date') {
							d.x = getDateFromTime(d.x);
						}
						;
						return xScale(d.x);
					})
					.y(function (d) {

						var y_value;

						if (d.y instanceof Array) {
							y_value = d.y[y_accessor];
						} else {
							y_value = d.y;
						}
						;

						return chart_object.height - yScale(y_value);
					});


				//sellectAll("path") causes a path element to be added for each data array
				//member. So call the line method on each data entry in the data for this
				//one "path"-element. The d-attribute of SVG usualy contains a string with a series of path
				//descriptions.
				lines = svg.append("path")
					.datum(viewdata)
					.attr("class", "line")
					.style("stroke", getColorIndex(y_accessor))
					.attr("d", valueline);

				function drawCircleHighlights(index) {

					circles = svg.append("circle")
						.datum(viewdata)
						.attr("class", "circle")
						.transition("drawCircleHighlights")
						.duration(200)
						.attr("cx", function (d) {
							return xScale(d[index].x);
						})
						.attr("cy", function (d) {
							return chart_object.height - yScale(d[index].y[y_accessor]);
						})
						.attr("r", chart_object.highlightradius)
						//.attr("index", index)
						.attr("xvalue", function (d) {
							return d[index].x;
						})
						.attr("yvalue", function (d) {
							return d[index].y[y_accessor];
						})
						.attr("y_accessor", y_accessor)
						.attr("opacity", 0)
						.attr("fill", getColorIndex(y_accessor));
				}

				for (var i = 0; i < viewdata.length; i++)
					drawCircleHighlights(i);


				svg.selectAll("circle")
					.on("mouseover", function (d, i) {
						var xvalue = d3.select(this).attr("xvalue");
						var yvalue = d3.select(this).attr("yvalue");
						var circlex = d3.select(this).attr("cx");
						var circley = d3.select(this).attr("cy");
						var accessor = d3.select(this).attr("y_accessor");


						var values = [xvalue, yvalue];
						var position = [circlex, circley];
						var coords = d3.pointer(d)[0];

						d3.select(this).transition("circlesMouseover")
							.duration(500)
							.attr('opacity', 1)
							.on('end', showTooltip(coords, values, position, accessor));
					})
					.on("mouseout", function () {
						d3.select(this).transition("circlesMouseover").attr('opacity', 0);
						hideTooltip();
					});
			};

			function hideTooltip() {
				tooltip.transition("hideTooltip")
					.duration(200)
					.style("opacity", 0.0)
					.style("top", 0 + "px");
			}

			function showTooltip(coords, values, position, accessor) {
				var keyindex = parseInt(accessor) + 1;

				tooltip.text(chart_object.datakeys[0] + ": " + values[0] + " " + chart_object.datakeys[keyindex] + ": " + values[1])
					.style("left", (position[0] + "px"))
					.transition("showTooltip")
					.delay(600)
					.duration(400)
					.style("opacity", 1.0)
					.style("position", "absolute")
					.style("background-color", getColorIndex(accessor))
					.style("top", ((position[1] - (2 * chart_object.highlightradius)) + "px"));

			}

		});

	}
}