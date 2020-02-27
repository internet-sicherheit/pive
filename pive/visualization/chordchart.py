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

import os
import json

import jinja2

from . import defaults as default
from . import basevisualization as bv


class Chart(bv.BaseVisualization):
    """Basic chart class."""

    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height,
                 padding=default.padding):
        """Initializing the chart with default settings."""

        # Initializing the inherited pseudo-interfaces.
        bv.BaseVisualization.__init__(self)

        # Metadata
        self._title = 'chordchart'
        self.__template_name = 'chordchart'
        self.__dataset = dataset
        real_path = os.path.dirname(os.path.realpath(__file__))
        self.__template_url = '{}{}'.format(real_path, default.template_path)
        self.__datakeys = []
        self.__version = default.p_version

        # Visualization properties.
        self.__width = width
        self.__height = height
        self.__padding = padding
        self.__colors = default.chartcolors
        self.__label_size = default.label_size

        # Axis properties.
        self.__shape_rendering = default.shape_rendering
        self.__line_stroke = default.line_stroke
        self.__font_size = default.font_size

        # Chord specific.
        self.__textpadding = default.textpadding
        self.__elementfontsizse = default.fontsize
        self.__tickfontsize = default.ticksize
        self.__ticksteps = default.ticksteps
        self.__tickprefix = default.prefix

    def set_title(self, title):
        """Basic Method."""
        self._title = title

    def set_data_keys(self, datakeys):
        """Setting the data keys for the visualization."""
        self.__datakeys = datakeys

    def set_ticksteps(self, ticksteps):
        """Setting the ticksteps for the visualization."""
        self.__ticksteps = ticksteps

    def set_tickprefix(self, tickprefix):
        """Setting the tickprefix for the visualization."""
        self.__tickprefix = tickprefix

    def set_chart_colors(self, colors):
        """Basic Method."""
        self.__colors = colors

    def init_matrix_row(self, elements):
        """Initializes a matrix row with zero values."""
        m_row = []
        for i in range(0, elements):
            m_row.append(0)
        return m_row

    def generate_adjacency_matrix(self, elements, dataset):
        """Generates the adacency matrix of the graph."""
        matrix = []
        for source in elements:
            i = 0

            m_row = self.init_matrix_row(len(elements))

            for line in dataset:

                keys = list(line.keys())

                current_element = line[keys[0]]
                if source == current_element:

                    for dest in elements:
                        if line[keys[1]] == dest:
                            index = elements.index(dest)
                            m_row.pop(index)
                            m_row.insert(index, line[keys[2]])
                            i += 1
            matrix.append(m_row)
        return matrix

    def generate_visualization_dataset(self, dataset):
        """Basic Method."""
        vis_dataset = {}

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
        matrix = self.generate_adjacency_matrix(elements, dataset)

        vis_dataset['elements'] = elements
        vis_dataset['matrix'] = matrix

        return vis_dataset

    def write_dataset_file(self, dataset, destination_url, filename):
        """Basic Method."""
        dest_file = '{}{}'.format(destination_url, filename)
        outp = open(dest_file, 'w')
        json.dump(dataset, outp, indent=2)
        outp.close()
        print('Writing: {}'.format(dest_file))

    def create_html(self, template):
        """Basic Method."""
        template_vars = {'t_title': self._title,
                         't_div_hook': self._div_hook}

        output_text = template.render(template_vars)
        return output_text

    def create_js(self, template, dataset_url):
        """Basic Method. Creates the JavaScript code based on the template."""
        template_vars = {'t_width': self.__width,
                         't_height': self.__height,
                         't_padding': self.__padding,
                         't_url': dataset_url,
                         't_colors': self.__colors,
                         't_textpadding': self.__textpadding,
                         't_elementFontSize': self.__elementfontsizse,
                         't_tickFontSize': self.__tickfontsize,
                         't_ticksteps': self.__ticksteps,
                         't_tickprefix': self.__tickprefix,
                         't_div_hook': self._div_hook,
                         't_font_size': self.__font_size,
                         't_shape_rendering': self.__shape_rendering,
                         't_line_stroke': self.__line_stroke,
                         't_pive_version': self.__version,
                         't_axis_label_size': self.__label_size}

        output_text = template.render(template_vars)
        return output_text

    def write_file(self, output, destination_url, filename):
        """Basic Method."""
        dest_file = '{}{}'.format(destination_url, filename)

        if not os.path.exists(destination_url):
            print('Folder does not exist. '
                  + 'Creating folder "{}". '.format(destination_url))
            os.makedirs(destination_url)

        f = open(dest_file, 'w')

        print('Writing: {}'.format(dest_file))

        for line in output:
            # f.write(line.encode('utf-8'))
            f.write(line)

        f.close()

    def get_js_code(self):
        """Basic Method."""
        dataset_url = '{}.json'.format(self._title)
        js_template = self.load_template_file(
            '{}{}.jinja'.format(self.__template_url, self.__template_name))
        js = self.create_js(js_template, dataset_url)
        return js

    def get_json_dataset(self):
        """Basic Method."""
        return self.generate_visualization_dataset(self.__dataset)

    def create_visualization_files(self, destination_url):
        """Basic Method."""
        html_template = self.load_template_file(
            '{}html.jinja'.format(self.__template_url))
        js_template = self.load_template_file(
            '{}{}.jinja'.format(self.__template_url, self.__template_name))

        dataset_url = '{}.json'.format(self._title)

        js = self.create_js(js_template, dataset_url)
        html = self.create_html(html_template)

        self.write_file(html, destination_url, '/{}.html'.format(self._title))
        self.write_file(js, destination_url, '/{}.js'.format(self._title))

        vis_data = self.generate_visualization_dataset(self.__dataset)
        self.write_dataset_file(
            vis_data,
            destination_url,
            '/{}.json'.format(self._title))

    def set_height(self, height):
        """Basic method for height driven data."""
        if not isinstance(height, int):
            raise ValueError(
                'Integer expected, got {} instead.'.format(type(height)))
        if (height <= 0):
            print(
                'Warning: Negative or zero height parameter. '
                + 'Using default settings instead.')
            height = default.height
        self.__height = height

    def set_width(self, width):
        """Basic method for width driven data."""
        if not isinstance(width, int):
            raise ValueError(
                'Integer expected, got {} instead.'.format(type(width)))
        if (width <= 0):
            print(
                'Warning: Negative or zero width parameter. '
                + 'Using default settings instead.')
            width = default.width
        self.__width = width

    def set_dimension(self, width, height):
        """Basic Method."""
        self.set_width(width)
        self.set_height(height)

    def load_template_file(self, template_url):
        """Basic Method."""
        template_loader = jinja2.FileSystemLoader(
            searchpath=[default.template_path, '/'])
        print('Opening template: {}'.format(template_url))

        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template_url)
        return template
