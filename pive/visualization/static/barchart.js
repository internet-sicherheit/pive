class Barchart {
    constructor(width,height,padding,labelsize,viewport,jumplength,xlabel,ylabel,datakeys,timeformat,iconwidth,iconheight,iconcolor,iconhighlight,verticalscale,div_hook,url,threshold,colors,line_stroke,shape_rendering,font_size,axis_label_size) {
        this.width = width;
        this.height = height;
        this.padding = padding;
        this.labelsize = labelsize;
        this.viewport = viewport;
        this.jumplength = jumplength;
        this.xlabel = xlabel;
        this.ylabel = ylabel;
        this.datakeys = datakeys;
        this.timeformat = timeformat;
        this.iconwidth = iconwidth;
        this.iconheight = iconheight;
        this.iconcolor = iconcolor;
        this.iconhighlight = iconhighlight;
        this.verticalscale = verticalscale;
        this.div_hook = div_hook;
        this.url = url;
        this.threshold = threshold;
        this.colors = colors;
        this.line_stroke = line_stroke;
        this.shape_rendering = shape_rendering;
        this.font_size = font_size;
        this.axis_label_size = axis_label_size;

        this.barbreak = 0.2;
        this.tickrotation = -45;
        this.hashtag = '#';
        this.hash_div_hook = this.hashtag.concat(div_hook);
        if ((width / viewport) < threshold){
            this.filter = parseInt(threshold * (viewport / width));
        };
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

        d3.json(this.url, function(data){
            //The complete dataset.
            const dataset = data;
            //The current offset starting at zero.
            let current_offset = 0;
            //Define the viewport of the data. Only a slice of the full dataset is currently shown.
            let viewdata = dataset.slice(current_offset, current_offset + _this.viewport);

            const vertical_extent = d3.extent(dataset, function(d){ return d.value});

            let yScale;
            let yAxisScale;

            const barScale = d3.scale.ordinal()
                .domain(d3.range(viewdata.length))
                .rangeRoundBands([_this.padding + _this.iconwidth + _this.labelsize, _this.width - _this.padding - _this.iconwidth], _this.barbreak);

            barScale.domain(viewdata.map(function(d){
                return d.label;
            }));

            scaleYAxis();

            function scaleYAxis(){
                //###################################
                //######## scale the x-axis. ########
                //###################################
                if (_this.verticalscale == 'linear') {
                    //Provide a linear scaling.
                    yScale = d3.scale.linear()
                           .range([_this.padding + _this.labelsize, _this.height - ((2 * _this.padding) + _this.labelsize)])
                           .domain(vertical_extent);
                    yAxisScale = d3.scale.linear()
                           .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                           .domain(vertical_extent);

                } else if (_this.verticalscale == 'log') {
                    if (vertical_extent[0] <= 0){
                        yScale = d3.scale.linear()
                           .range([_this.padding + _this.labelsize, _this.height - ((2 * _this.padding) + _this.labelsize)])
                           .domain(vertical_extent);
                        yAxisScale = d3.scale.linear()
                           .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                           .domain(vertical_extent);

                    } else {
                        yScale = d3.scale.log()
                               .range([_this.padding + _this.labelsize, _this.height - _this.padding])
                               .domain(vertical_extent);
                        yAxisScale = d3.scale.log()
                               .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                               .domain(vertical_extent);
                    }

                } else if (_this.verticalscale.substring(0,3) == 'pow') {
                    //The exponent of the power scale is indicated by a number
                    //following the 'pow', e.g. 'pow2'.

                    //FIXME: scales is undefined in barchart
                    exp = parseInt(scales[1].substring(3, scales[1].length));

                    //Provide a power scaling.
                    yScale = d3.scale.pow()
                               .exponent(exp)
                               .range([_this.padding + _this.labelsize, _this.height - _this.padding])
                               .domain(vertical_extent);
                    yAxisScale = d3.scale.pow()
                               .exponent(exp)
                               .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                               .domain(vertical_extent);
                };
            };

            _this.svg = d3.select(_this.hashtag.concat(_this.div_hook)).append("svg")
                        .attr("width", _this.width)
                        .attr("height", _this.height);

            _this.tooltip = d3.select(_this.hashtag.concat(_this.div_hook)).append("div")
                        .attr("class", "tooltip")
                        .style("opacity", "0.0")
                        .style("top", 0 + "px");

            const xaxis = d3.svg.axis().orient('bottom');
            const yaxis = d3.svg.axis().orient('left');

            //X Axis initialization.
            function initializeXAxis() {
                xaxis.tickValues(barScale.domain().filter(function(d, i) { return !(i % _this.filter); }))
                     .scale(barScale);

            };

            function initializeYAxis() {
                yaxis.scale(yAxisScale);
            };

            initializeXAxis();
            initializeYAxis();

            function barUpdate() {
                const bars = _this.svg.selectAll("rect").data(viewdata);
                bars.enter()
                    .append("rect")
                    .attr("opacity", 0.0);

                bars.exit().remove();

                bars.attr("class", "bar")
                    .transition()
                    .duration(750)
                    .ease("elastic")
                    .attr("opacity", 1.0)
                    .attr("x", function (d) {
                        return barScale(d.label);
                    })
                        .attr("y", function (d) {
                        return (_this.height - _this.padding - _this.labelsize) - yScale(d.value);
                    })
                        .attr("height", function (d) {
                        return yScale(d.value);
                    })
                        .attr("width", function (d) {
                        return barScale.rangeBand();
                    })
                        .attr("fill", function (d, i) {
                        return getColorIndex(i);
                    });

                bars.on("mouseover", function(d, i){
                        let tx = d3.mouse(this)[0];
                        let ty = d3.mouse(this)[1];
                        d3.select(this).transition()
                                       .attr("opacity", 0.5);
                        showTooltip([d.value, viewdata[i].label], [tx, ty], i);
                    })
                    .on("mouseout", function(){
                        hideTooltip();
                        d3.select(this).transition()
                                   .attr("opacity", 1.0);
                    });
            }

            barUpdate();

            const xa = _this.svg.append('g')
                       .attr('class', 'x axis')
                       .attr('transform', 'translate(0, ' + (_this.height - _this.padding - _this.labelsize) + ')')
                       .data(viewdata)
                       .call(xaxis)
                       .selectAll("text")
                        .style("text-anchor", "end")
                        .attr("dx", "-.8em")
                        .attr("dy", ".15em")
                        .attr("transform", function(d) {
                            return "rotate(" + _this.tickrotation + ")"
                            });

            const ya = _this.svg.append('g')
                       .attr('class', 'y axis')
                       .attr('transform', 'translate('+ (_this.padding + _this.labelsize + _this.iconwidth) + ', ' + (-_this.labelsize) + ')')
                       .data(viewdata)
                       .call(yaxis);

            const bottom_label = _this.svg.append("text")
                                  .attr("class", "x label")
                                  .attr("x", (_this.width / 2) + (_this.padding / 2))
                                  .attr("y", _this.height)
                                  .style("text-anchor", "middle")
                                  .style("font-size", _this.labelsize)
                                  .text(_this.xlabel);

            const left_label = _this.svg.append("text")
                                  .attr("class", "y label")
                                  .attr("transform", "rotate(-90)")
                                  .attr("x", (- _this.height / 2) + (_this.padding / 2))
                                  .attr("y", 0)
                                  .attr("dy", "1em")
                                  .style("text-anchor", "middle")
                                  .style("font-size", _this.labelsize)
                                  .text(_this.ylabel);

            function drawButtons(){
                //Append the buttons.
                const buttons = _this.svg.append("g")
                                 .attr("class", "button")

                const vertical_center = (_this.height / 2) - (_this.padding / 2) - (_this.iconheight / 2);

                //Prepare the transformation.
                const right_translation = 'translate(' + (_this.width - _this.iconwidth) + ',' + (vertical_center) + ')';
                const left_translation = 'translate(' + (_this.iconwidth + 10 + _this.labelsize) + ',' + (vertical_center) + ')';

                //Append the right arrow button and apply its transformation.
                buttons.append("path")
                    .attr('d', 'm 0 0 0 ' + _this.iconheight + ' ' + _this.iconwidth + ' -' + _this.iconheight / 2 + 'z')
                    .attr('transform', right_translation)
                    .attr('fill', _this.iconcolor)
                    .on("click", function() {
                            forwardData();
                    })
                    .on('mouseover', function() {
                        d3.select(this).attr('fill', _this.iconhighlight);
                    })
                    .on('mouseout', function() {
                        d3.select(this).attr('fill', _this.iconcolor);
                    });

                //Append the left arrow button and apply its transformation.
                buttons.append("path")
                    .attr('d', 'm 0 0 0 ' + _this.iconheight + ' -' + _this.iconwidth + ' -' + _this.iconheight / 2 + 'z')
                    .attr('transform',  left_translation)
                    .attr('fill', _this.iconcolor)
                    .on("click", function() {
                            backwardData();
                    })
                    .on('mouseover', function() {
                        d3.select(this).attr('fill', _this.iconhighlight);
                    })
                    .on('mouseout', function() {
                        d3.select(this).attr('fill', _this.iconcolor);
                    });

            }

            if (_this.viewport > viewdata.length){
                _this.viewport = viewdata.length;
            } else {
                drawButtons();
            }

            function forwardData() {
                current_offset += _this.jumplength;

                if ((current_offset + _this.viewport) > dataset.length) {
                    viewdata = dataset.slice(current_offset, dataset.length);
                    current_offset -= _this.jumplength;
                } else {
                    viewdata = dataset.slice(current_offset, current_offset + _this.viewport);
                };

                barScale.domain(viewdata.map(function(d){
                    return d.label;
                }));

                updateAxes();
                barUpdate();

            };


            function backwardData() {
                current_offset -= _this.jumplength;

                if (current_offset < 0) {
                    viewdata = dataset.slice(0, 0 + _this.viewport);
                    current_offset = 0;
                } else {
                    viewdata = dataset.slice(current_offset, current_offset + _this.viewport);
                };

                barScale.domain(viewdata.map(function(d){
                    return d.label;
                }));

                updateAxes();
                barUpdate();
            };

            function updateAxes(){
                xaxis.tickValues(barScale.domain().filter(function(d, i) { return !(i % _this.filter); }));

                _this.svg.select(".x.axis")
                    .transition()
                    .duration(250)
                    .call(xaxis)

                _this.svg.select(".y.axis")
                    .transition()
                    .duration(250)
                    .call(yaxis)

                _this.svg.select(".x.axis")
                    .selectAll("text")
                    .style("text-anchor", "end")
                    .attr("dx", "-.8em")
                    .attr("dy", ".15em")
                    .attr("transform", function(d) {
                        return "rotate(" + _this.tickrotation + ")"
                    });

            };


            function getColorIndex(y_accessor){
                    let colorindex = y_accessor;
                    let color;

                    while (colorindex > _this.colors.length - 1) {
                        colorindex = colorindex - _this.colors.length;
                    }

                    color = _this.colors[colorindex];
                    return color;
                }


           function hideTooltip(){
                _this.tooltip.transition()
                .duration(200)
                .style("opacity", 0.0)
                .style("top", 0 + "px");
            }

            function showTooltip(values, position, accessor){
                let keyindex = parseInt(accessor) + 1;

                _this.tooltip.text(values[1] + ": " + values[0])
                       .style("left", (position[0] + "px"))
                       .transition()
                       .delay(600)
                       .duration(400)
                       .style("opacity", 1.0)
                       .style("position", "absolute")
                       .style("background-color", getColorIndex(accessor))
                       .style("top", (position[1] + "px"));

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


