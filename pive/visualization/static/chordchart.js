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

class Chordchart {
	constructor(config, init) {
		this.config = config;
		this.serialisable_elements = [
			'width', 'height', 'padding', 'textpadding', 'elementfontsize', 'tickfontsize', 'ticksteps', 'tickprefix', 'div_hook',
			'timeformat', 'iconwidth', 'iconheight', 'iconcolor', 'iconhighlight', 'iso', 'scales', 'colors',
			'label_size'
		];
		this.width = config.width;
		this.height = config.height;
		this.padding	= config.padding;
		this.textpadding = config.textpadding;
		this.elementfontsize = config.elementfontsize;
		this.tickfontsize = config.tickfontsize;
		this.ticksteps = config.ticksteps;
		this.tickprefix = config.tickprefix;
		this.url = config.dataset_url;
		this.div_hook = config.div_hook;
		this.colors = config.colors;
		this.label_size = config.label_size;

		this.innerRadius = Math.min(this.width, this.height) * .32;
		this.outerRadius = this.innerRadius * 1.2;
		this.labelFont = "Helvetica";
		this.transistionSpeed = 500;

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
		d3.json(chart_object.url, chart_object.init).then(function (data) {
			var svg = d3.select('#'.concat(chart_object.div_hook)).append("svg")
			.attr("width", chart_object.width)
			.attr("height", chart_object.height)
			.append("g")
			.attr("transform", "translate(" + chart_object.width/2 + "," + chart_object.height/2 + ")");

			var chordElements = data.elements;
			var matrix = data.matrix;

			function getColorIndex(index) {
				var colorindex = index;
				var color;

				while (colorindex > chart_object.colors.length - 1) {
					colorindex = colorindex - chart_object.colors.length;

				}

				color = chart_object.colors[colorindex];
				return color;
			}

			function generateChord() {

				svg.selectAll("rect").remove();
				svg.selectAll("g").remove();

				svg.attr("transform", "translate(" + chart_object.width / 2 + "," + chart_object.height / 2 + ")");

				var chord = d3.chord()
					//.matrix(matrix)
					//.padding(0.05)
					.sortSubgroups(d3.descending);

				//Select all groups from class "chordGroup"
				var chordGroup = svg.selectAll("g.chordGroup")
					.data(chord(matrix).groups)
					.enter().append("svg:g")
					.attr("class", "chordGroup");

				var arc = d3.arc()
					.innerRadius(chart_object.innerRadius)
					.outerRadius(chart_object.outerRadius);

				var ribbon = d3.ribbon()
					.radius(chart_object.innerRadius)

				chordGroup.append("path")
					.attr("d", arc)
					.style("fill", function (d) {
						return getColorIndex(d.index);
					})
					.style("stroke", function (d) {
						return getColorIndex(d.index);
					})
					.attr("id", function (d, i) {
						return "group-" + d.index;
					});

				chordGroup.append("text")
					.each(function (d) {
						d.angle = (d.startAngle + d.endAngle) / 2;
					})
					.attr("dy", ".35em")
					.attr("font-size", chart_object.elementfontsize)
					.attr("font-family", chart_object.labelFont)
					.attr("transform", function (d) {
						return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
							+ "translate(" + (chart_object.outerRadius + chart_object.textpadding) + ")"
							+ (d.angle > Math.PI ? "rotate(180)" : "");
					})
					.style("text-anchor", function (d) {
						return d.angle > Math.PI ? "end" : null;
					})
					.text(function (d) {
						return chordElements[d.index];
					});


				//Eventlistener for each chordGroup group.
				chordGroup.on("mouseover", fade(0.05))
					.on("mouseout", fade(0.75))
					.on("click", function (d, i) {
						showDetail(i.index);
					});


				svg.append("g")
					.attr("class", "chord")
					.selectAll("path")
					.data(chord(matrix))
					.enter().append("path")
					.attr("d", ribbon)
					.style("fill", function (d) {
						return chordColor(d);
					})
					.style("stroke", function (d) {
						return chordColor(d);
					})
					.style("opacity", 0.75);

				var ticks = svg.append("g").selectAll("g")
					.data(chord(matrix).groups)
					.enter().append("g").selectAll("g")
					.data(chordTicks)
					.enter().append("g")
					.attr("class", "ticks")
					.attr("transform", function (d) {
						return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
							+ "translate(" + chart_object.outerRadius + ",0)";
					});


				ticks.append("line")
					.attr("x1", 1)
					.attr("y1", 0)
					.attr("x2", 5)
					.attr("y2", 0)
					.style("stroke", "#111");

				ticks.append("text")
					.attr("x", 8)
					.attr("dy", ".35em")
					.attr("font-size", chart_object.tickfontsize)
					.attr("font-family", chart_object.labelFont)
					.attr("transform", function (d) {
						return d.angle > Math.PI ? "rotate(180)translate(-16)" : null;
					})
					.style("text-anchor", function (d) {
						return d.angle > Math.PI ? "end" : null;
					})
					.text(function (d) {
						return d.label;
					});

			}

			function chordColor(d) {

				var colorindex = (d.source.value > d.target.value ?
					d.source.index : d.target.index);
				return getColorIndex(colorindex);
			}


			function fade(opacity) {
				return function (d, i) {
					svg.selectAll(".chord path")
						.filter(function (d) {
							return d.source.index != i.index &&
								d.target.index != i.index;
						})
						.transition("fade")
						.duration(chart_object.transistionSpeed)
						.style("opacity", opacity);
				};
			};

			//Draws a detailed BarChart containing the absolute weight of the graphnode.
			function showDetail(index) {

				svg.attr("transform", "translate(0,0)");

				svg.selectAll("g").remove()

				const detailwidth = chart_object.width / 1.5;
				const detailheight = chart_object.height / 2;

				var color = getColorIndex(index);

				var dataset = matrix[index];

				var xScale = d3.scaleBand()
					.domain(d3.range(dataset.length))
					.rangeRound([0, detailwidth - chart_object.padding])
					.padding(0.1);

				var yScale = d3.scaleLinear()
					.domain([0, d3.max(dataset)])
					.range([0, detailheight - chart_object.padding]);

				var xAxisScale = d3.scaleBand()
					.domain(chordElements)
					.rangeRound([0, detailwidth - chart_object.padding])
					.padding(0.1);

				var yAxisScale = d3.scaleLinear()
					.domain([0, d3.max(dataset)])
					.range([detailheight - chart_object.padding, 0]);


				//Define X axis
				var xAxis = d3.axisBottom()
					.scale(xAxisScale)
					.ticks(5);

				//Define Y axis
				var yAxis = d3.axisLeft()
					.scale(yAxisScale)
					.ticks(10);

				//Create X axis
				svg.append("g")
					.attr("opacity", 0.0)
					.attr("class", "x axis")
					// .attr("transform", "translate(0," + (detailheight - padding) + ")")
					.attr("transform", "translate(" + chart_object.padding + "," + (detailheight - chart_object.padding) + ")")
					.call(xAxis)
					.transition("createXAxis")
					.duration(chart_object.transistionSpeed)
					.attr("opacity", 1.0);

				//Create Y axis
				svg.append("g")
					.attr("opacity", 0.0)
					.attr("class", "y axis")
					.attr("transform", "translate(" + chart_object.padding + ",0)")
					.call(yAxis)
					.transition("createYAxis")
					.duration(chart_object.transistionSpeed)
					.attr("opacity", 1.0);

				var bars = svg.selectAll("rect")
					.data(dataset)
					.enter()
					.append("rect")
					.attr("opacity", 0.0)
					.attr("fill", color)
					.on("click", generateChord)
					.transition("drawBars")
					.duration(chart_object.transistionSpeed)
					.attr("class", "bar")
					.attr("opacity", 1.0)
					.attr("x", function (d, i) {
						return xScale(i) + chart_object.padding;
					})
					.attr("y", function (d) {
						return detailheight - yScale(d) - chart_object.padding;
					})
					.attr("width", xScale.bandwidth())
					.attr("height", function (d) {
						return yScale(d);
					});
			};


			// Returns tick angles.
			function chordTicks(d) {
				var k = (d.endAngle - d.startAngle) / d.value;

				return d3.range(0, d.value, chart_object.ticksteps).map(function (v, i) {
					return {
						angle: v * k + d.startAngle,
						label: i % 5 ? null : v / chart_object.ticksteps + chart_object.tickprefix
					};
				});
			};
			generateChord();
		});

	}
}

pive.addChartVersion("chordchart", "0.3.4", Chordchart);