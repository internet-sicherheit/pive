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
import json
from pive.visualization import defaults as default
from pive.visualization import basevisualization as bv
from pive.visualization import viewportvisualization as vv
from pive.visualization import customscalesvisualization as csv

from pathlib import Path

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

        self._template_url = Path(__file__).resolve().parent.joinpath(default.template_path)
        self._datakeys = []
        self._version = default.p_version
        self._js_name = "Bubblechart"

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

    @classmethod
    def get_chart_type(cls):
        return 'barchart'

    def getViewport(self):
        return self._viewport

    def get_modifiable_template_variables(self):
        """Returns a dictionary of all template variables, that are supposed to be modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        variables = super().get_modifiable_template_variables()
        variables["t_viewport"] = self._viewport
        variables["t_jumplength"] = self._jumplength
        variables["t_scales"] = self._scales
        variables["t_datakeys"] = self._datakeys
        variables["t_circleopacity"] = self._circleopacity
        variables["t_highlightfactor"] = self._highlightfactor
        variables["t_minradius"] = self._minradius
        variables["t_maxradius"] = self._maxradius
        variables["t_xlabel"] = self._xlabel
        variables["t_ylabel"] = self._ylabel
        variables["t_timeformat"] = self._timeformat
        variables["t_iconwidth"] = self._iconwidth
        variables["t_iconheight"] = self._iconheight
        variables["t_iconcolor"] = self._iconcolor
        variables["t_iconhighlight"] = self._iconhighlight
        return variables

    def get_modifiable_template_variables_typehints(self):
        """Returns a dictionary of typehints for variables that are modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        typehints = super().get_modifiable_template_variables_typehints();
        new_typehints = {
            "default" : {
                "t_viewport": {
                    "type": "int",
                    "min": 1
                },
                "t_jumplength": {
                    "type": "int",
                    "min": 1
                },
                "t_scales": {
                    "type": "list",
                    "length": 2,
                    "item_type": {
                        "type": "selection",
                        "multi_selection" : False,
                        "choices" : ["linear","log","pow","date"]
                    }
                },
                "t_datakeys": {
                    "type": "list",
                    "length": len(self._datakeys),
                    "item_type": {
                        "type": "string"
                    }
                },
                "t_circleopacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_highlightfactor": {
                    "type": "float",
                    "min": 0.0,
                },
                "t_minradius": {
                    "type": "int",
                    "min": 1
                },
                "t_maxradius": {
                    "type": "int",
                    "min": 1
                },
                "t_xlabel": {
                    "type": "string"
                },
                "t_ylabel": {
                    "type": "string"
                },
                "t_timeformat": {
                    "type": "string"
                },
                "t_iconwidth": {
                    "type": "int",
                    "min": 1
                },
                "t_iconheight": {
                    "type": "int",
                    "min": 1
                },
                "t_iconcolor": {
                    "type": "color",
                    "channels": 3
                },
                "t_iconhighlight": {
                    "type": "color",
                    "channels": 3
                }


            }
        }
        for key in new_typehints.keys():
            if key not in typehints.keys():
                typehints[key] = {}
            typehints[key].update(new_typehints[key])
        return typehints

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

    def setScales(self, scales):
        self._scales = scales

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
        if "t_scales" in dictionary:
            self.setScales(json.loads(dictionary['t_scales'].replace('\'', '\"')))
        self.set_labels([dictionary.get('t_xlabel', self._xlabel), dictionary.get('t_ylabel',self._ylabel)])
        if "t_datakeys" in dictionary:
            self.setDataKeys(json.loads(dictionary['t_datakeys'].replace('\'', '\"')))
        if "t_circleopacity" in dictionary:
            self.setCircleOpacity(float(dictionary['t_circleopacity']))
        if "t_highlightfactor" in dictionary:
            self.setHighlightFactor(float(dictionary['t_highlightfactor']))
        if "t_minradius" in dictionary:
            self.setMinRadius(int(dictionary['t_minradius']))
        if "t_maxradius" in dictionary:
            self.setMaxRadius(int(dictionary['t_maxradius']))
        self.setTimeProperties(self._timelabel,dictionary.get('t_timeformat', self._timeformat))
        self.setIconProperties(int(dictionary.get('t_iconwidth',self._iconwidth)),
                               int(dictionary.get('t_iconheight',self._iconheight)),
                               dictionary.get('t_iconcolor',self._iconcolor),
                               dictionary.get('t_iconhighlight', self._iconhighlight)
                               )


