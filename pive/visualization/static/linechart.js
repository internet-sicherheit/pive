class Linechart {
    constructor(width,height,padding,labelsize,viewport,jumplength,xlabel,ylabel,datakeys,timeformat,iconwidth,iconheight,iconcolor,iconhighlight,interpolation,url,iso,scales,colors,div_hook,line_stroke,shape_rendering,font_size,axis_label_size) {
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
        this.interpolation = interpolation;
        this.url = url;
        this.iso = d3.time.format.utc(iso);
        this.scales = scales;
        this.colors = colors;
        this.div_hook = div_hook;
        this.line_stroke = line_stroke;
        this.shape_rendering = shape_rendering;
        this.font_size = font_size;
        this.axis_label_size = axis_label_size;

        this.tickrotation = -45;
        this.highlightradius = 8;
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

            const dataset = data;
            let current_offset = 0;
            let viewdata = dataset.slice(current_offset, current_offset + _this.viewport);
            
            const max_y = d3.max(data, function(d){
                return d3.max(d.y, function(d1) {
                    return d1;
                });
            });

            const min_y = d3.min(data, function(d){
                return d3.min(d.y, function(d1) {
                    return d1;
                });
            });

            let x_extent = d3.extent(viewdata, function(d){ return d.x});
            let y_extent = [min_y, max_y];
            let xScale;
            let yScale;
            let yAxisScale;
            scaleXAxis();
            scaleYAxis();
           
            function getDateFromTime(time){
                try {
                    return new Date(time);  
                } catch (err) {
                    console.log("An Error occured while parsing the date object.");
                    console.log(err.message);
                    return null;
                };
            };

            function scaleXAxis(){                  
                //###################################
                //######## scale the x-axis. ########
                //###################################
                const xrange = [_this.padding + _this.labelsize + _this.iconwidth, _this.width - _this.padding];

                if (_this.scales[0] == 'linear') {
                    //Provide a linear scaling.
                    xScale = d3.scale.linear()
                               .range(xrange)                      
                               .domain(x_extent);

                } else if (_this.scales[0] == 'log') {
                    if (x_extent[0] <= 0){
                        xScale = d3.scale.linear()
                               .range(xrange)                      
                               .domain(x_extent);               
                    } else {
                        xScale = d3.scale.log()
                               .range(xrange)                      
                               .domain(x_extent);
                    }

                    
                } else if (_this.scales[0].substring(0,3) == 'pow') { 
                    
                    //The exponent of the power scale is indicated by a number
                    //following the 'pow', e.g. 'pow2'.
                    exp = parseInt(_this.scales[0].substring(3, _this.scales[0].length));
                    
                    //Provide a power scaling.
                    xScale = d3.scale.pow()
                               .exponent(exp)
                               .range(xrange)          
                               .domain(x_extent);

                } else if (_this.scales[0] == 'date') {
                    //Date-code to be implemented.
                    const minDate = getDateFromTime(x_extent[0]);
                    const maxDate = getDateFromTime(x_extent[1]);
                    console.log(minDate.toString());
                    console.log(maxDate.toString());
                    
                    xScale = d3.time.scale()
                               .range(xrange)
                               .domain([minDate, maxDate]);                     
                };
            };

            function scaleYAxis(){                  
                //###################################
                //######## scale the x-axis. ########
                //###################################
                if (_this.scales[1] == 'linear') {
                    //Provide a linear scaling.
                    yScale = d3.scale.linear()
                           .range([_this.padding + _this.labelsize, _this.height - _this.padding])
                           .domain(y_extent);
                    yAxisScale = d3.scale.linear()
                           .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                           .domain(y_extent);

                } else if (_this.scales[1] == 'log') {
                    if (y_extent[0] <= 0){
                        yScale = d3.scale.linear()
                           .range([_this.padding + _this.labelsize, _this.height - _this.padding])
                           .domain(y_extent);
                        yAxisScale = d3.scale.linear()
                           .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                           .domain(y_extent);
                    } else {
                        yScale = d3.scale.log()
                               .range([_this.padding + _this.labelsize, _this.height - _this.padding])                     
                               .domain(y_extent);
                        yAxisScale = d3.scale.log()
                               .range([_this.height - _this.padding, _this.padding + _this.labelsize])                     
                               .domain(y_extent);
                    }

                    
                } else if (_this.scales[1].substring(0,3) == 'pow') { 
                    
                    //The exponent of the power scale is indicated by a number
                    //following the 'pow', e.g. 'pow2'.
                    exp = parseInt(_this.scales[1].substring(3, _this.scales[1].length));
                    
                    //Provide a power scaling.
                    yScale = d3.scale.pow()
                               .exponent(exp)
                               .range([_this.padding + _this.labelsize, _this.height - _this.padding])         
                               .domain(y_extent);
                    yAxisScale = d3.scale.pow()
                               .exponent(exp)
                               .range([_this.height - _this.padding, _this.padding + _this.labelsize])         
                               .domain(y_extent);

                } else if (_this.scales[1] == 'date') {
                    //Date-code to be implemented.
                    const minDate = getDateFromTime(y_extent[0]);
                    const maxDate = getDateFromTime(y_extent[1]);
                    console.log(minDate.toString());
                    console.log(maxDate.toString());
                    yScale = d3.time.scale()
                               .range([_this.padding + _this.labelsize, _this.height - _this.padding])
                               .domain([minDate, maxDate]);     
                    yAxisScale = d3.time.scale()
                               .range([_this.height - _this.padding, _this.padding + _this.labelsize])
                               .domain([minDate, maxDate]);                 
                };
            };

            _this.svg = d3.select(_this.hashtag.concat(_this.div_hook)).append("svg")
                        .attr("width", _this.width)                           
                        .attr("height", _this.height);

            _this.tooltip = d3.select(_this.hashtag.concat(_this.div_hook)).append("div")
                        .attr("class", "tooltip")
                        .style("opacity", "0.0")
                        .style("top", 0 + "px");

            const xaxis = d3.svg.axis();
            const yaxis = d3.svg.axis();

            function initializeXAxis() {

                if (_this.scales[0] == 'date') {
                    xaxis.ticks(d3.time.milliseconds, 10)
                         .tickFormat(d3.time.format(_this.timeformat))                            
                         .tickSize(-(_this.height - _this.padding * 2 - _this.labelsize), 0, 0)
                         .scale(xScale);
                } else {

                    xaxis.tickSize(-(_this.height - _this.padding * 2 - _this.labelsize), 0, 0)                           
                         .scale(xScale);
                };                  
            };

            function initializeYAxis() {
                yaxis.orient('left')                    
                     .scale(yAxisScale); 
            };

            initializeXAxis();      
            initializeYAxis();                      

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
                                  .attr("class", "xlabel")
                                  .attr("x", (_this.width / 2) + (_this.padding / 2))
                                  .attr("y", _this.height)
                                  .style("text-anchor", "middle")
                                  .text(_this.xlabel);

            const left_label = _this.svg.append("text")
                                  .attr("class", "ylabel")
                                  .attr("transform", "rotate(-90)")
                                  .attr("x", (- _this.height / 2) + (_this.padding / 2))
                                  .attr("y", 0)
                                  .attr("dy", "1em")
                                  .style("text-anchor", "middle")
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
            
            
            function updateXAxis(new_extent) {

                if (_this.scales[0] == 'date') {
                    const minDate = _this.iso(getDateFromTime(new_extent[0]));
                    const maxDate = _this.iso(getDateFromTime(new_extent[1]));
                    xScale.domain([minDate, maxDate]);
                } else {
                    xScale.domain(new_extent);
                }
                
            }

            function forwardData() {
                current_offset += _this.jumplength;
                
                if ((current_offset + _this.viewport) > dataset.length) {
                    viewdata = dataset.slice(current_offset, dataset.length);
                    current_offset -= _this.jumplength;
                } else {
                    viewdata = dataset.slice(current_offset, current_offset + _this.viewport);
                };
                
                //Binds the new viedata to the line generation.
                lines.datum(viewdata);

                x_extent = d3.extent(viewdata, function(d){ return d.x});

                
                if (_this.scales[0] == 'date') {
                    const minDate = getDateFromTime(x_extent[0]);
                    const maxDate = getDateFromTime(x_extent[1]);
                    xScale.domain([minDate, maxDate]);  
                } else {
                    xScale.domain(x_extent);
                };
                
                updateView();
                            
            };

            
            function backwardData() {
                current_offset -= _this.jumplength;
                
                if (current_offset < 0) {
                    viewdata = dataset.slice(0, 0 + _this.viewport);
                    current_offset = 0;
                } else {
                    viewdata = dataset.slice(current_offset, current_offset + _this.viewport);
                };
                
                //Binds the new viedata to the line generation.
                lines.datum(viewdata);

                x_extent = d3.extent(viewdata, function(d){ return d.x});

                
                if (_this.scales[0] == 'date') {
                    const minDate = getDateFromTime(x_extent[0]);
                    const maxDate = getDateFromTime(x_extent[1]);
                    xScale.domain([minDate, maxDate]);  
                } else {
                    xScale.domain(x_extent);
                };
                
                updateView();
                            
            };
            
            
            function updateView(){

                _this.svg.select(".x.axis")
                    .transition()
                    .duration(250)
                    .call(xaxis)
                    
                _this.svg.select(".x.axis")
                    .selectAll("text")  
                    .style("text-anchor", "end")
                    .attr("dx", "-.8em")
                    .attr("dy", ".15em")
                    .attr("transform", function(d) {
                        return "rotate(" + _this.tickrotation + ")" 
                    });

                _this.svg.selectAll(".line").remove();
                _this.svg.selectAll(".circle").remove();

                for (let i = 0; i < viewdata[0].y.length; i++)
                    drawData(i);

            };


            let valueline = d3.svg.line();
            let lines;
            let circles = _this.svg.selectAll("circle");


            for (let i = 0; i < viewdata[0].y.length; i++)
                drawData(i);

            function getColorIndex(y_accessor){
                let colorindex = y_accessor;

                while (colorindex > _this.colors.length - 1) {
                    colorindex = colorindex - _this.colors.length;

                }
                return _this.colors[colorindex];
            }           

            function drawData(y_accessor){
                //If no y_accessor was defined, the data is assumed to contain only one dataset.
                //the y_accessor then becomes obsolete.
                y_accessor = (typeof y_accessor == "undefined") ? "singleData" : y_accessor;
                //Describes a line for each dataset.
                valueline = d3.svg.line()
                              .interpolate(_this.interpolation)
                              .x(function (d) {
                                    
                                    if (_this.scales[0] == 'date') {
                                        d.x = getDateFromTime(d.x);
                                    };
                                    return xScale(d.x);
                              })
                              .y(function (d) {

                                    let y_value;

                                    if (d.y instanceof Array){
                                        y_value = d.y[y_accessor];
                                    } else {
                                        y_value = d.y;
                                    };
                                    
                                    return _this.height - yScale(y_value);
                              });

                
                
                
                //sellectAll("path") causes a path element to be added for each data array
                //member. So call the line method on each data entry in the data for this
                //one "path"-element. The d-attribute of SVG usualy contains a string with a series of path
                //descriptions.
                lines = _this.svg.append("path")
                           .datum(viewdata)
                           .attr("class", "line")
                           .style("stroke", getColorIndex(y_accessor))
                           .attr("d", valueline);

                function drawCircleHighlights(index){

                    circles = _this.svg.append("circle")
                             .datum(viewdata)
                             .attr("class", "circle")
                             .transition()
                             .duration(200)
                             .attr("cx", function(d) {
                                return xScale(d[index].x);
                             })
                             .attr("cy", function(d) {
                                return _this.height - yScale(d[index].y[y_accessor]);
                             })
                             .attr("r", _this.highlightradius)
                             //.attr("index", index)
                             .attr("xvalue", function(d){
                                return d[index].x;
                             })
                             .attr("yvalue", function(d){
                                return d[index].y[y_accessor];
                             })
                             .attr("y_accessor", y_accessor)
                             .attr("opacity", 0)
                             .attr("fill", getColorIndex(y_accessor));              
                }
                
                for (let i = 0; i < viewdata.length; i++)
                    drawCircleHighlights(i);
                
                

             

                _this.svg.selectAll("circle")
                    .on("mouseover", function(){
                        const xvalue = d3.select(this).attr("xvalue");
                        const yvalue = d3.select(this).attr("yvalue");
                        const circlex = d3.select(this).attr("cx");
                        const circley = d3.select(this).attr("cy");
                        const accessor = d3.select(this).attr("y_accessor");


                        const values = [xvalue, yvalue];
                        const position = [circlex, circley];
                        const coords = d3.mouse(this);

                        d3.select(this).transition()
                        .duration(500)
                        .attr('opacity', 1)
                        .each('end', showTooltip(coords, values, position, accessor));
                    })
                    .on("mouseout", function(){
                        d3.select(this).transition().
                        attr('opacity', 0);
                        hideTooltip();
                    });
            };

           function hideTooltip(){
                _this.tooltip.transition()
                .duration(200)
                .style("opacity", 0.0)
                .style("top", 0 + "px");
            }

            function showTooltip(coords, values, position, accessor){
                    const keyindex = parseInt(accessor) + 1;
                    
                    _this.tooltip.text(_this.datakeys[0] + ": " + values[0] + " " + _this.datakeys[keyindex] + ": " + values[1])
                           .style("left", (position[0] + "px"))
                           .transition()
                           .delay(600)
                           .duration(400)
                           .style("opacity", 1.0)
                           .style("position", "absolute")                  
                           .style("background-color", getColorIndex(accessor))
                           .style("top", ((position[1] - (2 * _this.highlightradius)) + "px"));

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

