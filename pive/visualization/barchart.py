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

    def set_threshold(self, threshold):
        self._threshold = threshold

    def getViewport(self):
        return self._viewport

    def get_modifiable_template_variables(self):
        """Returns a dictionary of all template variables, that are supposed to be modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        variables = super().get_modifiable_template_variables()
        variables["t_viewport"] = self._viewport
        variables["t_jumplength"] = self._jumplength
        variables["t_datakeys"] = self._datakeys
        variables["t_verticalscale"] = self._verticalscale
        variables["t_iconwidth"] = self._iconwidth
        variables["t_iconheight"] = self._iconheight
        variables["t_iconcolor"] = self._iconcolor
        variables["t_iconhighlight"] = self._iconhighlight
        variables["t_xlabel"] = self._xlabel
        variables["t_ylabel"] = self._ylabel
        variables["t_barwidth"] = self._barwidth
        variables["t_threshold"] = self._threshold
        return variables

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

    def setVerticalScale(self, scale):
        self._verticalscale = scale

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

    def load_from_dict(self, dictionary):
        super().load_from_dict(dictionary)
        if "t_viewport" in dictionary:
            self.setViewport(int(dictionary['t_viewport']))
        if "t_jumplength" in dictionary:
            self.setJumplength(int(dictionary['t_jumplength']))
        if "t_verticalscale" in dictionary:
            self.setVerticalScale(dictionary['t_verticalscale'])
        self.set_labels([dictionary.get('t_xlabel', self._xlabel), dictionary.get('t_ylabel',self._ylabel)])
        if "t_datakeys" in dictionary:
            self.setDataKeys(json.loads(dictionary['t_datakeys'].replace('\'', '\"')))
        self.setIconProperties(int(dictionary.get('t_iconwidth', self._iconwidth)),
                               int(dictionary.get('t_iconheight', self._iconheight)),
                               dictionary.get('t_iconcolor', self._iconcolor),
                               dictionary.get('t_iconhighlight', self._iconhighlight)
                               )
        if "t_barwidth" in dictionary:
            self._barwidth = int(dictionary['t_barwidth'])
        if "t_threshold" in dictionary:
            self._threshold = int(dictionary['t_threshold'])
