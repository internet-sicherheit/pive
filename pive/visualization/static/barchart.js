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


class Barchart {

	constructor(config, init) {
		this.config = config
		this.serialisable_elements = [
			'width', 'height', 'padding', 'label_size', 'viewport', 'jumplength', 'xlabel', 'ylabel', 'datakeys',
			'timeformat', 'iconwidth', 'iconheight', 'iconcolor', 'iconhighlight', 'verticalscale', 'colors', 'div_hook'
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
		this.verticalscale = config.verticalscale;
		this.barbreak = 0.2;
		this.div_hook = config.div_hook;

		this.dataset_url = config.dataset_url;
		this.threshold = config.threshold;
		this.filter;

		this.init = init;

		if ((this.width / this.viewport) < this.threshold){
			this.filter = parseInt(this.threshold * (this.viewport / this.width));
		};

		this.colors = config.colors;
		this.tickrotation = -45;
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
		d3.json(this.dataset_url, this.init).then(function (data) {
			//The complete dataset.
			var dataset = data;
			//The current offset starting at zero.
			var current_offset = 0;
			//Define the viewport of the data. Only a slice of the full dataset is currently shown.
			var viewdata = dataset.slice(current_offset, current_offset + chart_object.viewport);

			var vertical_extent = d3.extent(dataset, function (d) {
				return d.value
			});

			var yScale;
			var yAxisScale;

			var barScale = d3.scaleBand()
				.domain(d3.range(viewdata.length))
				.rangeRound([chart_object.padding + chart_object.iconwidth + chart_object.label_size, chart_object.width - chart_object.padding - chart_object.iconwidth])
				.padding(chart_object.barbreak);

			barScale.domain(viewdata.map(function (d) {
				return d.label;
			}));

			scaleYAxis();

			function scaleYAxis() {
				//###################################
				//######## scale the x-axis. ########
				//###################################
				if (chart_object.verticalscale == 'linear') {
					//Provide a linear scaling.
					yScale = d3.scaleLinear()
						.range([chart_object.padding + chart_object.label_size, chart_object.height - ((2 * chart_object.padding) + chart_object.label_size)])
						.domain(vertical_extent);
					yAxisScale = d3.scaleLinear()
						.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
						.domain(vertical_extent);

				} else if (chart_object.verticalscale == 'log') {
					if (vertical_extent[0] <= 0) {
						yScale = d3.scaleLinear()
							.range([chart_object.padding + chart_object.label_size, chart_object.height - ((2 * chart_object.padding) + chart_object.label_size)])
							.domain(vertical_extent);
						yAxisScale = d3.scaleLinear()
							.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
							.domain(vertical_extent);

					} else {
						yScale = d3.scaleLog()
							.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
							.domain(vertical_extent);
						yAxisScale = d3.scaleLog()
							.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
							.domain(vertical_extent);
					}


				} else if (chart_object.verticalscale.substring(0, 3) == 'pow') {

					//The exponent of the power scale is indicated by a number
					//following the 'pow', e.g. 'pow2'.
					var exp = parseInt(chart_object.scales[1].substring(3, chart_object.scales[1].length));

					//Provide a power scaling.
					yScale = d3.scalePow()
						.exponent(exp)
						.range([chart_object.padding + chart_object.label_size, chart_object.height - chart_object.padding])
						.domain(vertical_extent);
					yAxisScale = d3.scalePow()
						.exponent(exp)
						.range([chart_object.height - chart_object.padding, chart_object.padding + chart_object.label_size])
						.domain(vertical_extent);
				}
				;
			};

			/*Drawing the initial SVG containing the chart by selecting the specific div element of the DOM
            and appending a svg tag with the following attributes. The selection is saved as a variable
            for later reference.*/
			var svg = d3.select('#'.concat(chart_object.div_hook)).append("svg")
				.attr("width", chart_object.width)
				.attr("height", chart_object.height);

			var tooltip = d3.select('#'.concat(chart_object.div_hook)).append("div")
			var tooltip = d3.select('#'.concat(chart_object.div_hook)).append("div")
				.attr("class", "tooltip")
				.style("opacity", "0.0")
				.style("top", 0 + "px");

			var xaxis = d3.axisBottom();
			var yaxis = d3.axisLeft();

			//X Axis initialization.
			function initializeXAxis() {
				xaxis.tickValues(barScale.domain().filter(function (d, i) {
					return !(i % chart_object.filter);
				}))
					.scale(barScale);

			};

			function initializeYAxis() {
				yaxis.scale(yAxisScale);
			};

			initializeXAxis();
			initializeYAxis();

			function barUpdate() {
				var bars = svg.selectAll("rect").data(viewdata);

				bars.enter()
					.append("rect")
					.attr("opacity", 0.0)
					.attr("class", "bar")
					.on("mouseover", function (d, i) {
						var tx = d3.pointer(d)[0];
						var ty = d3.pointer(d)[1];
						d3.select(this).transition("barUpdateMouseover")
							.attr("opacity", 0.5);
						showTooltip([i.value, i.label], [tx, ty], i);
					})
					.on("mouseout", function () {
						hideTooltip();
						d3.select(this).transition("barUpdateMouseout")
							.attr("opacity", 1.0);
					})
					.transition("barUpdateMain")
					.duration(750)
					.ease(d3.easeElastic)
					.attr("opacity", 1.0)
					.attr("x", function (d) {
						return barScale(d.label);
					})
					.attr("y", function (d) {
						return (chart_object.height - chart_object.padding - chart_object.label_size) - yScale(d.value);
					})
					.attr("height", function (d) {
						return yScale(d.value);
					})
					.attr("width", function (d) {
						return barScale.bandwidth();
					})
					.attr("fill", function (d, i) {
						return getColorIndex(i);
					})

				bars.exit().remove();


			}

			barUpdate();

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
				.attr("class", "x label")
				.attr("x", (chart_object.width / 2) + (chart_object.padding / 2))
				.attr("y", chart_object.height)
				.style("text-anchor", "middle")
				.style("font-size", chart_object.label_size)
				.text(chart_object.xlabel);

			var left_label = svg.append("text")
				.attr("class", "y label")
				.attr("transform", "rotate(-90)")
				.attr("x", (-chart_object.height / 2) + (chart_object.padding / 2))
				.attr("y", 0)
				.attr("dy", "1em")
				.style("text-anchor", "middle")
				.style("font-size", chart_object.label_size)
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

			function forwardData() {
				current_offset += chart_object.jumplength;

				if ((current_offset + chart_object.viewport) > dataset.length) {
					viewdata = dataset.slice(current_offset, dataset.length);
					current_offset -= chart_object.jumplength;
				} else {
					viewdata = dataset.slice(current_offset, current_offset + chart_object.viewport);
				}
				;

				barScale.domain(viewdata.map(function (d) {
					return d.label;
				}));

				updateAxes();
				barUpdate();

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

				barScale.domain(viewdata.map(function (d) {
					return d.label;
				}));

				updateAxes();
				barUpdate();
			};


			function updateAxes() {

				xaxis.tickValues(barScale.domain().filter(function (d, i) {
					return !(i % chart_object.filter);
				}));

				svg.select(".x.axis")
					.transition("updateAxesX")
					.duration(250)
					.call(xaxis)

				svg.select(".y.axis")
					.transition("updateAxesY")
					.duration(250)
					.call(yaxis)

				svg.select(".x.axis")
					.selectAll("text")
					.style("text-anchor", "end")
					.attr("dx", "-.8em")
					.attr("dy", ".15em")
					.attr("transform", function (d) {
						return "rotate(" + chart_object.tickrotation + ")"
					});

			};


			function getColorIndex(y_accessor) {
				var colorindex = y_accessor;
				var color;

				while (colorindex > chart_object.colors.length - 1) {
					colorindex = colorindex - chart_object.colors.length;

				}

				color = chart_object.colors[colorindex];
				return color;
			}


			function hideTooltip() {
				tooltip.transition("hideTooltip")
					.duration(200)
					.style("opacity", 0.0)
					.style("top", 0 + "px");
			}

			function showTooltip(values, position, accessor) {
				var keyindex = parseInt(accessor) + 1;

				tooltip.text(values[1] + ": " + values[0])
					.style("left", (position[0] + "px"))
					.transition("showTooltip")
					.delay(600)
					.duration(400)
					.style("opacity", 1.0)
					.style("position", "absolute")
					.style("background-color", getColorIndex(accessor))
					.style("top", (position[1] + "px"));

			}

		}).catch(function (error) {
			console.error(error)
		});

	}
}

pive.addChartVersion("barchart", "0.3.4", Barchart);