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

class Piechart {

	constructor(config, init) {
		this.config = config
		this.serialisable_elements = [
			'width', 'height', 'padding', 'label_size', 'datakeys', 'colors', 'highlightopacity', 'div_hook'
		];
		this.width = config.width;
		this.height = config.height;
		this.padding	= config.padding;
		this.label_size = config.label_size;
		this.datakeys = config.datakeys;
		this.dataset_url = config.dataset_url;
		this.colors = config.colors;
		this.highlightopacity = config.highlightopacity;
		this.div_hook = config.div_hook;

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
			css_axis_line = `#${this.div_hook} .axis line { stroke: ${this.config.line_stroke}; shape-rendering: ${this.config.shape_rendering};}\n`,
			css_path_area = `#${this.div_hook} .path area { fill: blue; }\n`,
			css_axis_text = `#${this.div_hook} .axis text {font-family: sans-serif; font-size: ${this.config.font_size}px }\n`,
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
		d3.json(chart_object.dataset_url, chart_object.init).then(function (data) {
			//The complete dataset.
			var dataset = data;

			var radius;
			if (chart_object.width < chart_object.height) {
				radius = (chart_object.width - chart_object.padding) / 2;
			} else {
				radius = (chart_object.height - chart_object.padding) / 2;
			}

			var total = d3.sum(dataset, function (d) {
				return d.value;
			});

			var percentformat = d3.format("0.1%");

			var tooltip = d3.select('#'.concat(chart_object.div_hook)).append("div")
				.attr("class", "tooltip")
				.style("opacity", "0.0")
				.style("position", "absolute")
				.style("top", 0 + "px");


			var svg = d3.select('#'.concat(chart_object.div_hook)).append("svg")
				.datum(dataset)
				.attr("width", chart_object.width)
				.attr("height", chart_object.height);

			var arc = d3.arc().innerRadius(0).outerRadius(radius);
			var pie = d3.pie().value(function (d) {
				return d.value;
			});

			var arcs = svg.selectAll("g.arc")
				.data(pie(data))
				.enter()
				.append("g")
				.attr("class", "arc")
				.attr("transform", "translate(" + (radius + chart_object.padding) + ", " + (radius + chart_object.padding) + ")");

			arcs.append("path")
				.attr("fill", function (d, i) {
					return getColorIndex(i);
				})
				.attr("d", arc)
				.on("mouseover", function (d, i) {
					var tx = d3.pointer(d)[0];
					var ty = d3.pointer(d)[1];
					d3.select(this).transition("arcMouseover")
						.attr("opacity", chart_object.highlightopacity);
					showTooltip([i.data.value, i.data.label], [tx, ty], i);
				})
				.on("mouseout", function () {
					hideTooltip();
					d3.select(this).transition("arcMouseout")
						.attr("opacity", 1.0);
				});


			function getColorIndex(index) {
				var colorindex = index;
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

				tooltip.html((values[1] + ": " + values[0] + "<br><br><center>" + percentformat(values[0] / total)))
					.style("left", ((position[0] + radius) + "px"))
					.transition("showTooltip")
					.delay(600)
					.duration(400)
					.style("opacity", 1.0)
					.style("position", "absolute")
					.style("background-color", getColorIndex(accessor))
					.style("top", ((position[1] + radius) + "px"));

			}

		});
	}
}