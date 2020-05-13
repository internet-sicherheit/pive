class Piechart {
    constructor(width,height,padding, datakeys, url,colors,highlightopacity, div_hook,line_stroke,shape_rendering,font_size,axis_label_size) {
        this.width = width;
        this.height = height;
        this.padding = padding;
        this.labelsize = 16;
        this.datakeys = datakeys;
        this.url = url;
        this.colors = colors;
        this.highlightopacity = highlightopacity;
        this.div_hook = div_hook;
        this.line_stroke = line_stroke;
        this.shape_rendering = shape_rendering;
        this.font_size = font_size;
        this.axis_label_size = axis_label_size;


        this.hashtag = '#';
        this.hash_div_hook = this.hashtag.concat(div_hook);
    }

    create() {
        const css_line = `#${this.div_hook} .line { stroke: ${this.line_stroke}; fill: none; stroke-width: 2.5px}\n`,
            css_tooltip = `#${this.div_hook} .tooltip {color: white; line-height: 1; padding: 12px; font-weight: italic; font-family: arial; border-radius: 5px;}\n`,
            css_axis_path = `#${this.div_hook} .axis path { fill: none; stroke: ${this.line_stroke}; shape-rendering: crispEdges;}\n`,
            css_axis_line = `#${this.div_hook} .axis line { stroke: ${this.line_stroke}; shape-rendering: ${this.shape_rendering};}\n`,
            css_path_area = `#${this.div_hook} .path area { fill: blue; }\n`,
            css_axis_text = `#${this.div_hook} .axis text {font-family: sans-serif; font-size: ${this.font_size}px }\n`,
            css_xlabel_text = `#${this.div_hook} .xlabel {font-family: helvetica; font-size: ${this.axis_label_size}px }\n`,
            css_ylabel_text = `#${this.div_hook} .ylabel {font-family: helvetica; font-size: ${this.axis_label_size}px }\n`,
            css_x_axis_line = `#${this.div_hook} .x.axis line { stroke: grey; stroke-opacity: 0.25; stroke-width: 2.5px}\n`,
            css_y_axis_line = `#${this.div_hook} .y.axis line { stroke: grey; stroke-opacity: 0.25; stroke-width: 2.5px}`;
        const css = css_line.concat(css_tooltip).concat(css_axis_path).concat(css_axis_line).concat(css_path_area).concat(css_axis_text)
          .concat(css_xlabel_text).concat(css_ylabel_text).concat(css_x_axis_line).concat(css_y_axis_line);

        this.root_div = document.getElementById(this.div_hook);

        this.style = document.createElement('style');
        this.style.type = 'text/css';
        this.style.appendChild(document.createTextNode(css));
        this.root_div.appendChild(this.style);

        const _this = this;

        d3.json(_this.url, function(data){
            //The complete dataset.
            const dataset = data;

            const radius = _this.width < _this.height ? (_this.width - _this.padding) / 2 : (_this.height - _this.padding) / 2;

            const total = d3.sum(dataset, function(d){
                return d.value;
            });

            const percentformat = d3.format("0.1%");

            _this.tooltip = d3.select(_this.hashtag.concat(_this.div_hook)).append("div")
                    .attr("class", "tooltip")
                    .style("opacity", "0.0")
                    .style("position", "absolute")
                    .style("top", 0 + "px");

            _this.svg = d3.select(_this.hashtag.concat(_this.div_hook)).append("svg")
                        .datum(dataset)
                        .attr("width", _this.width)
                        .attr("height", _this.height);

            const arc = d3.svg.arc().outerRadius(radius);
            const pie = d3.layout.pie().value(function(d) {
                return d.value;
            });

            const arcs = _this.svg.selectAll("g.arc")
                          .data(pie)
                          .enter()
                          .append("g")
                          .attr("class", "arc")
                          .attr("transform", "translate(" + (radius + _this.padding) + ", " + (radius + _this.padding) + ")");

            arcs.append("path")
                .attr("fill", function(d, i){
                    return getColorIndex(i);
                })
                .attr("d", arc)
                .on("mouseover", function(d, i){
                    const tx = d3.mouse(this)[0];
                    const ty = d3.mouse(this)[1];
                    d3.select(this).transition()
                                   .attr("opacity", _this.highlightopacity);
                    showTooltip([d.value, dataset[i].label], [tx, ty], i);
                })
                .on("mouseout", function(){
                        hideTooltip();
                        d3.select(this).transition()
                                   .attr("opacity", 1.0);
                    });

            function getColorIndex(y_accessor){
                let colorindex = y_accessor;

                while (colorindex > _this.colors.length - 1) {
                    colorindex = colorindex - _this.colors.length;

                }
                return _this.colors[colorindex];
            }


           function hideTooltip(){
                _this.tooltip.transition()
                .duration(200)
                .style("opacity", 0.0)
                .style("top", 0 + "px");
            }

            function showTooltip(values, position, accessor){
                    _this.tooltip.html((values[1] + ": " + values[0] + "<br><br><center>" + percentformat(values[0] / total)))
                           .style("left", ((position[0] + radius) +  "px"))
                           .transition()
                           .delay(600)
                           .duration(400)
                           .style("opacity", 1.0)
                           .style("position", "absolute")
                           .style("background-color", getColorIndex(accessor))
                           .style("top", ((position[1] + radius) + "px"));

                }

        });

    }

    destroy() {
        if(this.style) {
            this.style.remove();
            this.style = null;
        }
        if(this.svg) {
            this.svg.remove();
            this.svg = null;
        }
        if(this.tooltip) {
            this.tooltip.remove();
            this.tooltip = null;
        }
    }
}