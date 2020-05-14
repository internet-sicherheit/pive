# Copyright (c) 2014 - 2015, David Bothe
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import jinja2
import os
import json
from pive.visualization import defaults as default
from pive.visualization import basevisualization as bv
from pive.visualization import viewportvisualization as vv


class Chart(bv.BaseVisualization, vv.ViewportVisualization):
    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height,
                 padding=default.padding,
                 viewport=default.viewport,
                 jumplength=default.jumplength):

        # Initializing the inherited pseudo-interfaces.
        bv.BaseVisualization.__init__(self)
        vv.ViewportVisualization.__init__(self)

        # Metadata
        self._title = 'barchart'
        self._template_name = 'barchart'
        self._dataset = dataset
        self._dataset_url = ''

        realpath = os.path.dirname(os.path.realpath(__file__))
        self._template_url = '%s%s' % (realpath, default.template_path)
        self._datakeys = []
        self._version = default.p_version


        # Visualization properties.
        self._width = width
        self._height = height
        self._padding = padding
        self._viewport = viewport
        self._jumplength = jumplength
        self._xlabel = default.xlabel
        self._ylabel = default.ylabel
        self._label_size = default.label_size
        self._threshold = default.threshold

        self._iconwidth = default.iconwidth
        self._iconheight = default.iconheight
        self._iconcolor = default.iconcolor
        self._iconhighlight = default.iconhighlight
        self._colors = default.chartcolors

        # Axis properties.
        self._shape_rendering = default.shape_rendering
        self._line_stroke = default.line_stroke
        self._font_size = default.font_size

        self._barwidth = default.barwidth
        self._verticalscale = 'linear'

    def set_title(self, title):
        self._title = title

    def set_threshold(self, threshold):
        self._threshold = threshold

    def getViewport(self):
        return self._viewport

    def set_labels(self, labels):
        self._xlabel = labels[0]
        self._ylabel = labels[1]

    def setDataKeys(self, datakeys):
        self._datakeys = datakeys;

    def setTimeProperties(self, timelabel, timeformat):
        """Basic Method for time supporting visualizations."""
        self._timeformat = timeformat
        self._timelabel = timelabel

    def setIconProperties(self, iconwidth, iconheight, iconcolor, iconhighlight):
        """Basic Method for viewport driven data.
        Defines the icon properties. All arguments required."""
        self._iconwidth = iconwidth
        self._iconheight = iconheight
        self._iconcolor = iconcolor
        self._iconhighlight = iconhighlight

    def set_chart_colors(self, colors):
        """Basic Method."""
        self._colors = colors

    def generate_visualization_dataset(self, dataset):
        """Basic Method."""
        visdataset = []

        for datapoint in dataset:
            visdatapoint = {}
            points = list(datapoint.keys())
            visdatapoint['value'] = datapoint[points[0]]
            visdatapoint['label'] = datapoint[points[1]]
            visdataset.append(visdatapoint)
        return visdataset

    def write_dataset_file(self, dataset, dataset_url):
        outp = open(dataset_url, 'w')
        json.dump(dataset, outp, indent=2)
        outp.close()
        print ('Writing: %s' % (dataset_url))

    def setVerticalScale(self, scale):
        self._verticalscale = scale

    def create_html(self, template):
        templateVars = {'t_title': self._title,
                        't_chart_type': self._template_name,
                        't_width': self._width,
                        't_height': self._height,
                        't_padding': self._padding,
                        't_viewport': self._viewport,
                        't_jumplength': self._jumplength,
                        't_xlabel': self._xlabel,
                        't_ylabel': self._ylabel,
                        't_iconwidth': self._iconwidth,
                        't_iconheight': self._iconheight,
                        't_iconcolor': self._iconcolor,
                        't_iconhighlight': self._iconhighlight,
                        't_datakeys': self._datakeys,
                        't_url': self._dataset_url,
                        't_colors': self._colors,
                        't_barwidth': self._barwidth,
                        't_verticalscale': self._verticalscale,
                        't_threshold' : self._threshold,
                        't_div_hook': self._div_hook,
                        't_font_size': self._font_size,
                        't_shape_rendering': self._shape_rendering,
                        't_line_stroke': self._line_stroke,
                        't_pive_version' : self._version,
                        't_axis_label_size' : self._label_size}

        outputText = template.render(templateVars)
        return outputText

    def create_js(self, template, dataset_url):
        templateVars = {'t_width': self._width,
                        't_height': self._height,
                        't_padding': self._padding,
                        't_viewport': self._viewport,
                        't_jumplength': self._jumplength,
                        't_xlabel': self._xlabel,
                        't_ylabel': self._ylabel,
                        't_iconwidth': self._iconwidth,
                        't_iconheight': self._iconheight,
                        't_iconcolor': self._iconcolor,
                        't_iconhighlight': self._iconhighlight,
                        't_datakeys': self._datakeys,
                        't_url': dataset_url,
                        't_colors': self._colors,
                        't_barwidth': self._barwidth,
                        't_verticalscale': self._verticalscale,
                        't_threshold' : self._threshold,
                        't_div_hook': self._div_hook,
                        't_font_size': self._font_size,
                        't_shape_rendering': self._shape_rendering,
                        't_line_stroke': self._line_stroke,
                        't_pive_version' : self._version,
                        't_axis_label_size' : self._label_size}

        outputText = template.render(templateVars)
        return outputText

    def write_file(self, output, destination_url, filename):

        dest_file = '%s%s' % (destination_url, filename)

        if not os.path.exists(destination_url):
            print ("Folder does not exist. Creating folder '%s'. " % (destination_url))
            os.makedirs(destination_url)

        f = open(dest_file, 'w')

        print ('Writing: %s' % (dest_file))

        for line in output:
            #f.write(line.encode('utf-8'))
            f.write(line)

        f.close()


    def get_js_code(self):
        js_template = self.load_template_file('%s%s.jinja' % (self._template_url, self._template_name))
        js = self.create_js(js_template, self._dataset_url)
        return js


    def get_json_dataset(self):
        return self.generate_visualization_dataset(self._dataset)


    # def create_visualization_files(self, destination_url):
    #     html_template = self.load_template_file('%shtml.jinja' % (self._template_url))
    #     js_template = self.load_template_file('%s%s.jinja' % (self._template_url, self._template_name))

    #     # Default dataset url is used when nothing was explicitly passed.
    #     if not self._dataset_url:
    #         dataset_url = destination_url + '%s%s.json' % (os.sep, self._title)
    #         self.set_dataset_url(dataset_url)

    #     js = self.create_js(js_template, self._dataset_url)
    #     html = self.create_html(html_template)

    #     self.write_file(html, destination_url, '%s%s.html' % (os.sep, self._title))
    #     self.write_file(js, destination_url, '%s%s.js' % (os.sep, self._title))

    #     visdata = self.generate_visualization_dataset(self._dataset)
    #     self.write_dataset_file(visdata, self._dataset_url)

    def setJumplength(self, jumplength):
        """Basic Method for viewport driven data."""
        if not isinstance(jumplength, int):
            raise ValueError("Integer expected, got %s instead." % (type(jumplength)))
        if (jumplength <= 0):
            print ("Warning: Negative or zero jumplength parameter. Using default settings instead.")
            jumplength = default.jumplength

        self._jumplength = jumplength

    def setViewport(self, viewport):
        """Basic method for viewport driven data."""
        if not isinstance(viewport, int):
            raise ValueError("Integer expected, got %s instead." % (type(viewport)))
        if (viewport <= 0):
            print ("Warning: Negative or zero viewport parameter. Using default settings instead.")
            viewport = default.viewport
        self._viewport = viewport

    def set_height(self, height):
        """Basic method for height driven data."""
        if not isinstance(height, int):
            raise ValueError("Integer expected, got %s instead." % (type(height)))
        if (height <= 0):
            print ("Warning: Negative or zero height parameter. Using default settings instead.")
            height = default.height
        self._height = height

    def set_width(self, width):
        """Basic method for width driven data."""
        if not isinstance(width, int):
            raise ValueError("Integer expected, got %s instead." % (type(width)))
        if (width <= 0):
            print ("Warning: Negative or zero width parameter. Using default settings instead.")
            width = default.width
        self._width = width

    def set_dimension(self, width, height):
        self.set_width(width)
        self.set_height(height)

