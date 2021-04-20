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

class Hiveplot {
	constructor(config, init) {
		this.config = config;
		this.serialisable_elements = [
			'width', 'height', 'label_size', 'div_hook', 'colors', 'tickrotation', 'line_stroke', 'shape_rendering',
			'font_size', 'axis_label_size'
		];
		this.width = config.width;
		this.height= config.height;
		this.label_size = config.label_size;
		this.div_hook= config.div_hook;
		this.dataset_url= config.dataset_url;
		this.colors= config.colors;
		this.tickrotation= config.tickrotation;
		this.line_stroke= config.line_stroke;
		this.shape_rendering= config.shape_rendering;
		this.font_size= config.font_size;
		this.axis_label_size= config.axis_label_size;

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
			css_y_axis_line = `#${this.div_hook} .y.axis line { stroke: grey; stroke-opacity: 0.25; stroke-width: 2.5px}`,
			css_axis = '.axis { stroke: #000; stroke-width:1.5px; }\n',
			css_node = '.node { stroke:#000; }\n',
			css_link = '.link { fill: none; stroke-width: 1.5px; , stroke-opacity: 0.8; }\n',
			css_link_turnedOn = '.link.turnedOn { stroke-width: 3px; }\n',
			css_link_turnedOff = '.link.turnedOff { stroke-opacity: 0.3, stroke-width: 1px; }\n',
			css_node_turnedOn = '.node.turnedOn { stroke: red; stroke-width: 3px; }\n';

		const css = css_line.concat(css_tooltip).concat(css_axis_path).concat(css_axis_line).concat(css_path_area).concat(css_axis_text)
          .concat(css_xlabel_text).concat(css_ylabel_text).concat(css_x_axis_line).concat(css_y_axis_line).concat(css_axis)
          .concat(css_node).concat(css_link).concat(css_link_turnedOn)
          .concat(css_link_turnedOff).concat(css_node_turnedOn);

		var style = document.createElement('style');
		style.type = 'text/css';
		style.appendChild(document.createTextNode(css));
		root_div.appendChild(style);
		const chart_object = this;
		d3.json(chart_object.dataset_url, chart_object.init).then(function (data) {

			var innerRadius = 40,
				outerRadius = 240,
				nodes = data,
				links = createLinks(data),
				types = getTypes(data), // TYPE of data for axis.
				range = types.length; // count of TYPE for count of axis.

			var angle = d3.scalePoint()
					.domain(d3.range(range + 1))
					.range([0, 2 * Math.PI]), // angle from axis to axis
				radius = d3.scaleLinear()
					.range([innerRadius, outerRadius]), // scale of lines
				color = d3.scaleOrdinal(d3.schemeCategory10)
					.domain(d3.range(20))

			/* SVG - Body  */
			var svg = d3.select('#'.concat(chart_object.div_hook)).append("svg")
				.attr("width", chart_object.width)
				.attr("height", chart_object.height)
				.append("g")
				.attr("transform", "translate(" + chart_object.width / 2 + "," + chart_object.height / 2 + ")");

			/* TOOLTIP - DABOTH */
			var tooltip = d3.select('#'.concat(chart_object.div_hook)).append("div")
				.attr("class", "tooltip")
				.style("opacity", "0.0")
				.style("top", 0 + "px");

			/* SVG - all axis, draws in right position */
			svg.selectAll(".axis")
				.data(d3.range(range))
				.enter().append("line")
				.attr("class", "axis")
				.attr("transform", function (d) {
					return "rotate(" + degrees(angle(d)) + ")"
				})
				.attr("x1", radius.range()[0])
				.attr("x2", radius.range()[1]);

			/* Draws all links, with their curves, styles and hovers. */
			svg.selectAll(".link")
				.data(links)
				.enter().append("path")
				.attr("class", "link")
				.attr("d", d3.hive.link()
					.angle(function (d) {
						return angle(d.TYPE);
					})
					.radius(function (d) {
						return radius(d.WEIGHT);
					}))
				.style("stroke", function (d) {
					return color(d.source.TYPE);
				})
				.on("mouseover", linkMouseover)
				.on("mouseout", mouseout);

			/* Draws nodes wit their right position, styles and hovers. */
			svg.selectAll(".node")
				.data(nodes)
				.enter().append("circle")
				.attr("class", "node")
				.attr("transform", function (d) {
					return "rotate(" + degrees(angle(getNumberForType(d.TYPE))) + ")";
				})
				.attr("cx", function (d) {
					return radius(d.WEIGHT);
				})
				.attr("r", 5)
				.style("fill", function (d) {
					return color(d.TYPE);
				})
				.on("mouseover", nodeMouseover)
				.on("mouseout", mouseout);

			/* link-hover-stati and changes from on and off. */
			function linkMouseover(d) {
				svg.selectAll(".link")
					.classed("turnedOn", function (dl) {
						return dl === d;
					})
					.classed("turnedOff", function (dl) {
						return !(dl === d);
					})
				svg.selectAll(".node")
					.classed("turnedOn", function (dl) {
						return dl === d.source || dl === d.target;
					})
			}

			/* node-hover stati and changes from on and off. */
			function nodeMouseover(d) {
				svg.selectAll(".link")
					.classed("turnedOn", function (dl) {
						return (dl.source.WEIGHT === d.srcElement.__data__.WEIGHT && dl.source.TYPE === d.srcElement.__data__.TYPE) || (dl.target.WEIGHT === d.target.__data__.WEIGHT && dl.target.TYPE === d.target.__data__.TYPE);
					})
					.classed("turnedOff", function (dl) {
						return (dl.source.WEIGHT === d.srcElement.__data__.WEIGHT && dl.source.TYPE === d.srcElement.__data__.TYPE) || (dl.target.WEIGHT === d.target.__data__.WEIGHT && dl.target.TYPE === d.target.__data__.TYPE);
					});
				var tx = d3.pointer(d)[0];
				var ty = d3.pointer(d)[1];
				var ind;

				for (var i = 0; i < nodes.length; i++) {
					if (nodes[i].ID == d.srcElement.__data__.ID) {
						ind = i;
					}
				}

				showTooltip(["ID: " + d.srcElement.__data__.ID, "WEIGHT: " + d.srcElement.__data__.WEIGHT], [tx, ty], ind);

				d3.select(this)
					.classed("turnedOn", true);
			}

			/* Clears highlighted nodes or links and sets info and tooltip to default.  */
			function mouseout() {
				svg.selectAll(".turnedOn").classed("turnedOn", false);
				svg.selectAll(".turnedOff").classed("turnedOff", false);
				hideTooltip();
			}

			/* Calculates degrees of radians for drawing axes with appropriate distances. */
			function degrees(radians) {
				return radians / Math.PI * 180 - 90;
			}

			/* Searches the original node per ID and prepares a hive-conform node and target in a link object. Returns the filled link object. */
			function findNode(linkID) {
				var n = {};
				for (var i = 0; i < data.length; i++) {
					if (data[i].ID == linkID) {
						/* change id to type, because we have current 3 types for 3 axes. */
						n = {TYPE: getNumberForType(data[i].TYPE), WEIGHT: data[i].WEIGHT};
					}
				}
				return n;
			}

			/* Creates links in a hive-conform way. link = {source[type, weight], target[type, weight]}, returns all possible links in an array. */
			function createLinks() {
				var l = [];
				for (var i = 0; i < data.length; i++) {
					var lA = data[i].LINKS; // linkarray, nodes can have more than 1 links
					for (var j = 0; j < lA.length; j++) {
						var lID = lA[j],
							trg = findNode(lID),
							src = findNode(data[i].ID);
						l.push({source: src, target: trg});
					}
				}
				return l;
			}

			/* Checks in JSON-data how many types are defined for creating the count of axes and returns array with the types. */
			function getTypes() {
				const s = new Set();
				for (var i = 0; i < data.length; i++) {
					s.add(data[i].TYPE);
				}
				var a = Array.from(s);
				return a;
			}

			/* Converts the types to numbers to achieve the hive-confimity.
            Currently are 5 axes the maximum for all datasets we get. Returns the number according to the type.  */
			function getNumberForType(type) {
				var t = ['A', 'B', 'C', 'D', 'E'],
					n = t.find(elem => elem == type);
				n = t.indexOf(n) + 1;
				return n
			}


			function getColorIndex(y_accessor) {
				var colorindex = y_accessor;
				var color;

				while (colorindex > chart_object.colors.length - 1) {
					colorindex = colorindex - colors.length;

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
				//console.log("tooltip")
				//var keyindex = parseInt(accessor) + 1;

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

		});

	}
}

pive.addChartVersion("hiveplot", "0.3.4", Hiveplot);