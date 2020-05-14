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
from pive.visualization import customscalesvisualization as csv


class Chart(bv.BaseVisualization, csv.CustomScalesVisualization, vv.ViewportVisualization):
    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height,
                 padding=default.padding,
                 viewport=default.viewport,
                 jumplength=default.jumplength,
                 times=False):

        # Initializing the inherited pseudo-interfaces.
        bv.BaseVisualization.__init__(self)
        csv.CustomScalesVisualization.__init__(self)
        vv.ViewportVisualization.__init__(self)

        # Metadata
        self._title = 'bubblechart'
        self._template_name = 'bubblechart'
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

        if times:
            self._scales = default.timescales
        else:
            self._scales = default.scales

        self._timelabel = default.timelabel
        self._timeformat = default.isotimeformat
        self._iconwidth = default.iconwidth
        self._iconheight = default.iconheight
        self._iconcolor = default.iconcolor
        self._iconhighlight = default.iconhighlight
        self._colors = default.chartcolors

        self._circleopacity = default.circleopacity
        self._highlightfactor = default.highlightfactor
        self._minradius = default.minradius
        self._maxradius = default.maxradius

        #Axis properties.
        self._shape_rendering = default.shape_rendering
        self._line_stroke = default.line_stroke
        self._font_size = default.font_size

    # def set_title(self, title):
    #     self._title = title

    def getViewport(self):
        return self._viewport

    def set_labels(self, labels):
        self._xlabel = labels[0]
        self._ylabel = labels[1]

    def setDataKeys(self, datakeys):
        self._datakeys = datakeys

    def setCircleOpacity(self, opacity):
        self._circleopacity = opacity

    def setHighlightFactor(self, factor):
        self._highlightfactor = factor

    def setMinRadius(self, radius):
        self._minradius = radius

    def setMaxRadius(self, radius):
        self._maxradius = radius

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
            visdatapoint['x'] = datapoint[points[0]]
            ordinates = []
            radii = []
            for item in points[1::2]:
                ordinates.append(datapoint[item])

            for radius in points[2::2]:
                radii.append(datapoint[radius])

            bubbles = zip(ordinates, radii)
            bubble = []
            for item in bubbles:
                bubble.append(list(item))
                visdatapoint['y'] = bubble

            visdataset.append(visdatapoint)
        return visdataset

    def write_dataset_file(self, dataset, dataset_url):
        outp = open(dataset_url, 'w')
        json.dump(dataset, outp, indent=2)
        outp.close()
        print ('Writing: %s' % (dataset_url))

    def setScales(self, scales):
        self._scales = scales


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
                        't_timeformat': self._timeformat,
                        't_iconwidth': self._iconwidth,
                        't_iconheight': self._iconheight,
                        't_iconcolor': self._iconcolor,
                        't_iconhighlight': self._iconhighlight,
                        't_datakeys': self._datakeys,
                        't_url': self._dataset_url,
                        't_format': self._timeformat,
                        't_iso': self._timeformat,
                        't_scales': self._scales,
                        't_colors': self._colors,
                        't_highlightfactor': self._highlightfactor,
                        't_minradius': self._minradius,
                        't_maxradius': self._maxradius,
                        't_circleopacity': self._circleopacity,
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
                        't_timeformat': self._timeformat,
                        't_iconwidth': self._iconwidth,
                        't_iconheight': self._iconheight,
                        't_iconcolor': self._iconcolor,
                        't_iconhighlight': self._iconhighlight,
                        't_datakeys': self._datakeys,
                        't_url': dataset_url,
                        't_format': self._timeformat,
                        't_iso': self._timeformat,
                        't_scales': self._scales,
                        't_colors': self._colors,
                        't_highlightfactor': self._highlightfactor,
                        't_minradius': self._minradius,
                        't_maxradius': self._maxradius,
                        't_circleopacity': self._circleopacity,
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
            f.write(line)

        f.close()


    def get_js_code(self):
        js_template = self.load_template_file('%s%s.jinja' % (self._template_url, self._template_name))
        js = self.create_js(js_template, self._dataset_url)
        return js


    def get_json_dataset(self):
        return self.generate_visualization_dataset(self._dataset)


    # def create_visualization_files(self, destination_url):
    #
    #     html_template = self.load_template_file('%shtml.jinja' % (self._template_url))
    #     js_template = self.load_template_file('%s%s.jinja' % (self._template_url, self._template_name))
    #
    #     # Default dataset url is used when nothing was explicitly passed.
    #     if not self._dataset_url:
    #         dataset_url = destination_url + '%s%s.json' % (os.sep, self._title)
    #         self.set_dataset_url(dataset_url)
    #         # By default, the dataset is stored directly in the visualizations javascript path,
    #         # the templating engine then only references the relative path.
    #         js = self.create_js(js_template, '%s.json' % (self._title))
    #     else:
    #         # When a dataset url was passed, the visualization references
    #         # this as the absolute path to the dataset.
    #         js = self.create_js(js_template, self._dataset_url)
    #
    #     html = self.create_html(html_template)
    #
    #     self.write_file(html, destination_url, '%s%s.html' % (os.sep, self._title))
    #     self.write_file(js, destination_url, '%s%s.js' % (os.sep, self._title))
    #
    #     visdata = self.generate_visualization_dataset(self._dataset)
    #     self.write_dataset_file(visdata, self._dataset_url)

    def setJumplength(self, jumplength):
        """Basic Method for viewport driven data."""
        if not isinstance(jumplength, int):
            raise ValueError("Integer expected, got %s instead." % (type(jumplength)))
        if (jumplength <= 0):
            print ("Warning: Negative or zero jumplength parameter. Using default settings instead.")
            jumplength = default.jumplength

        self.__jumplength = jumplength

    def setViewport(self, viewport):
        """Basic method for viewport driven data."""
        if not isinstance(viewport, int):
            raise ValueError("Integer expected, got %s instead." % (type(viewport)))
        if (viewport <= 0):
            print ("Warning: Negative or zero viewport parameter. Using default settings instead.")
            viewport = default.viewport
        self.__viewport = viewport

    def set_height(self, height):
        """Basic method for height driven data."""
        if not isinstance(height, int):
            raise ValueError("Integer expected, got %s instead." % (type(height)))
        if (height <= 0):
            print ("Warning: Negative or zero height parameter. Using default settings instead.")
            height = default.height
        self.__height = height

    def set_width(self, width):
        """Basic method for width driven data."""
        if not isinstance(width, int):
            raise ValueError("Integer expected, got %s instead." % (type(width)))
        if (width <= 0):
            print ("Warning: Negative or zero width parameter. Using default settings instead.")
            width = default.width
        self.__width = width

    def set_dimension(self, width, height):
        self.set_width(width)
        self.set_height(height)

