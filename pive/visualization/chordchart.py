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

from pathlib import Path


class Chart(bv.BaseVisualization):
    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height,
                 padding=default.padding):

        # Initializing the inherited pseudo-interfaces.
        bv.BaseVisualization.__init__(self)

        # Metadata
        self._title = 'chordchart'
        self._template_name = 'chordchart'
        self._dataset = dataset
        self._dataset_url = ''

        self._template_url = Path(__file__).resolve().parent.joinpath(default.template_path)
        self._datakeys = []
        self._version = default.p_version
        self._js_name = "Chordchart"

        # Visualization properties.
        self._width = width
        self._height = height
        self._padding = padding
        self._colors = default.chartcolors
        self._label_size = default.label_size

        #Axis properties.
        self._shape_rendering = default.shape_rendering
        self._line_stroke = default.line_stroke
        self._font_size = default.font_size

        #Chord specific.
        self._textpadding = default.textpadding
        self._elementfontsizse = default.fontsize
        self._tickfontsize = default.ticksize
        self._ticksteps = default.ticksteps
        self._tickprefix = default.prefix

    def set_title(self, title):
        self._title = title

    def setDataKeys(self, datakeys):
        self._datakeys = datakeys;

    def setTicksteps(self, ticksteps):
        self._ticksteps = ticksteps;

    def setTickprefix(self, tickprefix):
        self._tickprefix = tickprefix;

    def set_chart_colors(self, colors):
        """Basic Method."""
        self._colors = colors

    def get_modifiable_template_variables(self):
        """Returns a dictionary of all template variables, that are supposed to be modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        variables = super().get_modifiable_template_variables()
        variables["t_datakeys"] = self._datakeys
        variables["t_textpadding"] = self._textpadding
        variables["t_elementfontsizse"] = self._elementfontsizse
        variables["t_tickfontsize"] = self._tickfontsize
        variables["t_ticksteps"] = self._ticksteps
        variables["t_tickprefix"] = self._tickprefix
        return variables

    def get_modifiable_template_variables_typehints(self):
        """Returns a dictionary of typehints for variables that are modifiable by the client.
        Subclasses should override this method and add their own variables.
        """
        typehints = super().get_modifiable_template_variables_typehints();
        new_typehints = {
            "default" : {
                "t_datakeys": {
                    "type": "list",
                    "length": len(self._datakeys),
                    "item_type": {
                        "type": "string"
                    }
                },
                "t_textpadding": {
                    "type": "int",
                    "min": 1
                },
                "t_elementfontsizse": {
                    "type": "int",
                    "min": 1
                },
                "t_tickfontsize": {
                    "type": "int",
                    "min": 1
                },
                "t_tickprefix": {
                    "type": "string",
                    "min": 1,
                    "max": 1
                }
            }
        }
        for key in new_typehints.keys():
            if key not in typehints.keys():
                typehints[key] = {}
            typehints[key].update(new_typehints[key])
        return typehints

    def initMatrixRow(self, elements):
        """Initializes a matrix row with zero values."""
        mrow = []
        for i in range(0, elements):
            mrow.append(0)
        return mrow

    def generateAdjacencyMatrix(self, elements, dataset):
        """Generates the adacency matrix of the graph."""
        matrix = []
        for source in elements:
            i = 0

            mrow = self.initMatrixRow(len(elements))

            for line in dataset:

                keys = list(line.keys())

                current_element = line[keys[0]]
                if source == current_element:

                    for dest in elements:
                        if line[keys[1]] == dest:
                            index = elements.index(dest)
                            mrow.pop(index)
                            mrow.insert(index, line[keys[2]])
                            i += 1
            matrix.append(mrow)
        return matrix

    def generate_visualization_dataset(self, dataset):
        """Basic Method."""
        visdataset = {}

        elements = []

        for item in dataset:
            keys = list(item.keys())
            # The elements consist of the distinct sources
            # and destinations.
            source = item[keys[0]]
            dest = item[keys[1]]
            if source not in elements:
                elements.append(source)
            if dest not in elements:
                elements.append(dest)
        matrix = self.generateAdjacencyMatrix(elements, dataset)

        visdataset['elements'] = elements
        visdataset['matrix'] = matrix

        return visdataset


    def create_js(self, template, dataset_url):
        templateVars = {'t_width': self._width,
                        't_height': self._height,
                        't_padding': self._padding,
                        't_url': dataset_url,
                        't_colors': self._colors,
                        't_textpadding': self._textpadding,
                        't_elementFontSize': self._elementfontsizse,
                        't_tickFontSize': self._tickfontsize,
                        't_ticksteps': self._ticksteps,
                        't_tickprefix': self._tickprefix,
                        't_div_hook': self._div_hook,
                        't_font_size': self._font_size,
                        't_shape_rendering': self._shape_rendering,
                        't_line_stroke': self._line_stroke,
                        't_pive_version' : self._version,
                        't_axis_label_size' : self._label_size}

        outputText = template.render(templateVars)
        return outputText

    def load_from_dict(self, dictionary):
        super().load_from_dict(dictionary)
        if "t_datakeys" in dictionary:
            self.setDataKeys(json.loads(dictionary['t_datakeys'].replace('\'', '\"')))
        if "t_textpadding" in dictionary:
            self._textpadding = int(dictionary['t_textpadding'])
        if "t_elementfontsizse" in dictionary:
            self._elementfontsizse = dictionary['t_elementfontsizse']
        if "t_tickfontsize" in dictionary:
            self._tickfontsize = dictionary['t_tickfontsize']
        if "t_ticksteps" in dictionary:
            self.setTicksteps( int(dictionary['t_ticksteps']) )
        if "t_tickprefix" in dictionary:
            self.setTickprefix((dictionary['t_tickprefix']))
