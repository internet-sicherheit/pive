class Chordchart {
    constructor(width, height, padding, textpadding, elementFontSize, tickFontSize, tickSteps, prefix, colors, url, div_hook, line_stroke, shape_rendering, font_size, axis_label_size) {
        this.width = width;
        this.height = height;
        this.padding = padding;
        this.textpadding = textpadding;
        this.elementFontSize = elementFontSize;
        this.tickFontSize = tickFontSize;
        this.tickSteps = tickSteps;
        this.prefix = prefix;
        this.colors = colors;
        this.url = url;
        this.div_hook = div_hook;
        this.line_stroke = line_stroke;
        this.shape_rendering = shape_rendering;
        this.font_size = font_size;
        this.axis_label_size = axis_label_size;

        this.hashtag = '#';
        this.hash_div_hook = this.hashtag.concat(div_hook);
        this.innerRadius = Math.min(width, height) * .34;
        this.outerRadius = this.innerRadius * 1.2;
        this.labelFont = "Helvetica";
        this.transistionSpeed = 500;

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


        d3.json(url, function(data){

            const chordElements = data.elements;
            const matrix = data.matrix;

            function getColorIndex(index){
                let colorindex = index;

                while (colorindex > _this.colors.length - 1) {
                    colorindex = colorindex - _this.colors.length;

                }
                
                return _this.colors[colorindex];
            }

            _this.svg = d3.select(_this.hashtag.concat(_this.div_hook)).append("svg")
              .attr("width", _this.width)
              .attr("height", _this.height)
            let g = _this.svg.append("g")
              .attr("transform", "translate(" + _this.width/2 + "," + _this.height/2 + ")");
            console.log(_this.svg);

            function generateChord() {

                g.selectAll("rect").remove();
                g.selectAll("g").remove();

                g.attr("transform", "translate(" + _this.width/2 + "," + _this.height/2 + ")");


                const chord = d3.layout.chord()
                        .matrix(matrix)
                        .padding(0.05)
                        .sortSubgroups(d3.descending);        

                //Select all groups from class "chordGroup"
                const chordGroup = g.selectAll("g.chordGroup")
                            .data(chord.groups)
                            .enter().append("svg:g")
                            .attr("class", "chordGroup");

                const arc = d3.svg.arc()
                            .innerRadius(_this.innerRadius)
                            .outerRadius(_this.outerRadius);

                chordGroup.append("path")
                    .attr("d", arc)
                    .style("fill", function(d) {                        
                        return getColorIndex(d.index);
                    })
                    .style("stroke", function(d) {
                        return getColorIndex(d.index);
                    })
                    .attr("id", function(d, i) {
                        return "group-" + d.index;
                    });

                chordGroup.append("text")
                      .each(function(d) { d.angle = (d.startAngle + d.endAngle) / 2; })
                      .attr("dy", ".35em")
                      .attr("font-size", _this.elementFontSize)
                      .attr("font-family", _this.labelFont)
                      .attr("transform", function(d) {
                        return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
                            + "translate(" + (_this.outerRadius + _this.textpadding) + ")"
                            + (d.angle > Math.PI ? "rotate(180)" : "");
                      })
                      .style("text-anchor", function(d) { return d.angle > Math.PI ? "end" : null; })
                      .text(function(d) { return chordElements[d.index]; });



                //Eventlistener for each chordGroup group.
                chordGroup.on("mouseover", fade(0.05))
                          .on("mouseout", fade(0.75))
                          .on("click", function(d,i) {
                              showDetail(i);
                          });


                 g.append("g")
                    .attr("class", "chord")
                    .selectAll("path")
                    .data(chord.chords)
                    .enter().append("path")
                    .attr("d", d3.svg.chord().radius(_this.innerRadius))
                    .style("fill", function(d) {
                        return chordColor(d);
                    })    
                    .style("stroke", function(d) {
                        return chordColor(d);
                    })                    
                    .style("opacity", 0.75); 

                const ticks = g.append("g").selectAll("g")
                           .data(chord.groups)
                           .enter().append("g").selectAll("g")
                           .data(chordTicks)
                           .enter().append("g")
                           .attr("class", "ticks")
                           .attr("transform", function(d) {
                              return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
                                  + "translate(" + _this.outerRadius + ",0)";
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
                    .attr("font-size", _this.tickFontSize)
                    .attr("font-family", _this.labelFont)
                    .attr("transform", function(d) { return d.angle > Math.PI ? "rotate(180)translate(-16)" : null; })
                    .style("text-anchor", function(d) { return d.angle > Math.PI ? "end" : null; })
                    .text(function(d) { return d.label; });

            }

            function chordColor(d) {

                        var colorindex = (d.source.value > d.target.value ?
                        d.source.index : d.target.index);
                    return getColorIndex(colorindex);
                }
                 

            function fade(opacity) {
                return function(d, i) {
                    g.selectAll(".chord path")
                        .filter(function(d) {                            
                            return d.source.index != i &&
                                   d.target.index != i;
                        })
                        .transition()
                        .duration(_this.transistionSpeed)
                        .style("opacity", opacity);
                };
            };

            //Draws a detailed BarChart containing the absolute weight of the graphnode.
            function showDetail(index) {

                g.attr("transform", "translate(0,0)");

                g.selectAll("g").remove()

                const detailwidth = _this.width / 1.5;
                const detailheight = _this.height / 2;

                const color = getColorIndex(index);
            
                const dataset = matrix[index];

                const xScale = d3.scale.ordinal()
                        .domain(d3.range(dataset.length))
                        .rangeRoundBands([0, detailwidth - _this.padding], 0.1);

                const yScale = d3.scale.linear()
                            .domain([1, d3.max(dataset)])
                            .range([0, detailheight - _this.padding]);

                const xAxisScale = d3.scale.ordinal()
                            .domain(chordElements)
                            .rangeRoundBands([0, detailwidth - _this.padding], 0.1);

                const yAxisScale = d3.scale.linear()
                        .domain([1, d3.max(dataset)])
                        .range([detailheight - _this.padding, 0]);


                //Define X axis
                const xAxis = d3.svg.axis()
                              .scale(xAxisScale)
                              .orient("bottom")
                              .ticks(5);

                //Define Y axis
                const yAxis = d3.svg.axis()
                              .scale(yAxisScale)
                              .orient("left")
                              .ticks(10);

                //Create X axis
                g.append("g")
                    .attr("opacity", 0.0)
                    .attr("class", "x axis")
                    // .attr("transform", "translate(0," + (detailheight - padding) + ")")
                    .attr("transform", "translate("+ _this.padding + "," + (detailheight - _this.padding) + ")")
                    .call(xAxis)
                    .transition()
                    .duration(transistionSpeed)
                    .attr("opacity", 1.0);

                //Create Y axis
                g.append("g")                    
                    .attr("opacity", 0.0)
                    .attr("class", "y axis")
                    .attr("transform", "translate(" + _this.padding + ",0)")
                    .call(yAxis)
                    .transition()
                    .duration(_this.transistionSpeed)
                    .attr("opacity", 1.0);

                //#FIXME: bars is never used
                const bars = g.selectAll("rect")
                   .data(dataset)
                   .enter()
                   .append("rect")
                   .attr("opacity", 0.0)
                   .attr("fill", color)                  
                   .on("click", generateChord)
                   .transition()
                   .duration(_this.transistionSpeed)
                   .attr("class", "bar")
                   .attr("opacity", 1.0)
                   .attr("x", function (d, i) {
                           return xScale(i) + _this.padding;
                   })
                   .attr("y", function (d) {
                           return detailheight - yScale(d) - _this.padding; 
                   })
                   .attr("width", xScale.rangeBand())
                   .attr("height", function (d){
                           return yScale(d);
                   });                
            };
             
             
            // Returns tick angles.
            function chordTicks(d) {
              var k = (d.endAngle - d.startAngle) / d.value;

              return d3.range(0, d.value, _this.tickSteps).map(function(v, i) {
                return {
                  angle: v * k + d.startAngle,
                  label: i % 5 ? null : v / _this.tickSteps + _this.prefix
                };
              });
            };
            generateChord();
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
