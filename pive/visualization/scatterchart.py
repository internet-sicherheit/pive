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

from pive.visualization import defaults as default
from pive.visualization import basevisualization as bv
from pive.visualization import viewportvisualization as vv
from pive.visualization import customscalesvisualization as csv


class Chart(bv.BaseVisualization, csv.CustomScalesVisualization,
            vv.ViewportVisualization):
    """Chart class for viewport driven data with custom scaling."""

    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height,
                 padding=default.padding,
                 viewport=default.viewport,
                 jumplength=default.jumplength,
                 times=False):
        """Initializing the chart with default settings."""

        # Initializing the inherited pseudo-interfaces.
        bv.BaseVisualization.__init__(self)
        csv.CustomScalesVisualization.__init__(self)
        vv.ViewportVisualization.__init__(self)
        real_path = os.path.dirname(os.path.realpath(__file__))

        # Metadata
        self._title = 'scatterchart'
        self.__template_name = 'scatterchart'
        self.__dataset = dataset
        self.__template_url = '{}{}'.format(real_path, default.template_path)
        self.__datakeys = []
        self.__version = default.p_version

        # Visualization properties.
        self.__width = width
        self.__height = height
        self.__padding = padding
        self.__viewport = viewport
        self.__jumplength = jumplength
        self.__xlabel = default.xlabel
        self.__ylabel = default.ylabel
        self.__label_size = default.label_size

        if times:
            self.__scales = default.timescales
        else:
            self.__scales = default.scales

        self.__timelabel = default.timelabel
        self.__timeformat = default.isotimeformat
        self.__iconwidth = default.iconwidth
        self.__iconheight = default.iconheight
        self.__iconcolor = default.iconcolor
        self.__iconhighlight = default.iconhighlight
        self.__colors = default.chartcolors

        self.__circleradius = default.circleradius
        self.__circlehighlightradius = default.circlehighlightradius
        self.__circleopacity = default.circleopacity

        # Axis properties.
        self.__shape_rendering = default.shape_rendering
        self.__line_stroke = default.line_stroke
        self.__font_size = default.font_size

    def set_title(self, title):
        """Basic Method."""
        self._title = title

    def get_viewport(self):
        """Basic method for viewport driven data."""
        return self.__viewport

    def set_labels(self, labels):
        """Basic Method."""
        self.__xlabel = labels[0]
        self.__ylabel = labels[1]

    def set_data_keys(self, datakeys):
        """Setting the data keys for the visualization."""
        self.__datakeys = datakeys

    def set_circle_opacity(self, opacity):
        """Setting the opacity of individual circles."""
        self.__circleopacity = opacity

    def set_circle_radius(self, radius):
        """Setting the radius of individual circles."""
        self.__circleradius = radius

    def set_circle_highlight_radius(self, radius):
        """Setting the highlighting radius of individual circles."""
        self.__circlehighlightradius = radius

    def set_time_properties(self, timelabel, timeformat):
        """Basic Method for time supporting visualizations."""
        self.__timeformat = timeformat
        self.__timelabel = timelabel

    def set_icon_properties(self, iconwidth, iconheight,
                            iconcolor, iconhighlight):
        """Basic Method for viewport driven data.
                Defines the icon properties. All arguments required."""
        self.__iconwidth = iconwidth
        self.__iconheight = iconheight
        self.__iconcolor = iconcolor
        self.__iconhighlight = iconhighlight

    def set_chart_colors(self, colors):
        """Basic Method."""
        self.__colors = colors

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

    def generate_visualization_dataset(self, dataset):
        """Basic Method."""
        vis_dataset = []

        for datapoint in dataset:
            vis_datapoint = {}
            points = list(datapoint.keys())
            vis_datapoint['x'] = datapoint[points[0]]
            ordinates = []
            for item in points[1:]:
                ordinates.append(datapoint[item])
            vis_datapoint['y'] = ordinates

            vis_dataset.append(vis_datapoint)

        return vis_dataset

    def write_dataset_file(self, dataset, destination_url, filename):
        """Basic Method."""
        dest_file = '{}{}'.format(destination_url, filename)
        outp = open(dest_file, 'w')
        json.dump(dataset, outp, indent=2)
        outp.close()
        print('Writing: {}'.format(dest_file))

    def set_scales(self, scales):
        """Basic Method for data with custom scaling."""
        self.__scales = scales

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
                         't_viewport': self.__viewport,
                         't_jumplength': self.__jumplength,
                         't_xlabel': self.__xlabel,
                         't_ylabel': self.__ylabel,
                         't_timeformat': self.__timeformat,
                         't_iconwidth': self.__iconwidth,
                         't_iconheight': self.__iconheight,
                         't_iconcolor': self.__iconcolor,
                         't_iconhighlight': self.__iconhighlight,
                         't_datakeys': self.__datakeys,
                         't_url': dataset_url,
                         't_format': self.__timeformat,
                         't_iso': self.__timeformat,
                         't_scales': self.__scales,
                         't_colors': self.__colors,
                         't_circleradius': self.__circleradius,
                         't_highlightfactor': self.__circlehighlightradius,
                         't_circleopacity': self.__circleopacity,
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
            f.write(line)

        f.close()

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

    def set_jumplength(self, jumplength):
        """Basic Method for viewport driven data."""
        if not isinstance(jumplength, int):
            raise ValueError(
                'Integer expected, got {} instead.'.format(type(jumplength)))
        if (jumplength <= 0):
            print(
                'Warning: Negative or zero jumplength parameter. '
                + 'Using default settings instead.')
            jumplength = default.jumplength

        self.__jumplength = jumplength

    def set_viewport(self, viewport):
        """Basic method for viewport driven data."""
        if not isinstance(viewport, int):
            raise ValueError(
                'Integer expected, got {} instead.'.format(type(viewport)))
        if (viewport <= 0):
            print(
                'Warning: Negative or zero viewport parameter. '
                + 'Using default settings instead.')
            viewport = default.viewport
        self.__viewport = viewport

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
