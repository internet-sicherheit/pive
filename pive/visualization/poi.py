# Copyright (c) 2019 - 2020, Tobias Stratmann
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
import pathlib

import jinja2

from pive.visualization import mapdefaults as default
from pive.visualization import mapvisualization as mv


class Map(mv.MapVisualization):
    """Map class for heatmap data."""

    def __init__(self,
                 dataset,
                 template_name,
                 shape,
                 inner,
                 city,
                 width=default.width,
                 height=default.height,
                 padding=default.padding):
        """Initializing the chart with default settings."""

        # Initializing the inherited pseudo-interface.
        mv.MapVisualization.__init__(self)

        # Metadata
        self._title = 'poi'
        self.__template_name = 'poi'
        self.__dataset = dataset
        real_path = os.path.dirname(os.path.realpath(__file__))
        self.__template_url = '{}{}'.format(real_path, default.template_path)
        self.__datakeys = []
        self.__version = default.p_version

        # Visualization properties.
        self.__width = width
        self.__height = height
        self.__padding = padding
        self.__shape = shape
        self.__city = city
        self.__max_poi = default.max_poi

        # Starting, min and max values for zoom levels on the map
        self.__scale = default.scale
        self.__scale_extent = default.scale_extent

        # Map rendering
        self.__zoom_threshold = default.zoom_threshold
        self.__tooltip_div_border = default.tooltip_div_border
        self.__map_fill = default.map_fill
        self.__map_stroke = default.map_stroke
        self.__fill_opacity = default.fill_opacity
        self.__stroke_opacity = default.stroke_opacity
        self.__mouseover_opacity = default.mouseover_opacity
        self.__mouseout_opacity = default.mouseout_opacity
        self.__circle_fill = default.circle_fill
        self.__circle_stroke = default.circle_stroke
        self.__circle_radius = default.circle_radius
        self.__circle_stroke_width = default.circle_stroke_width
        self.__headers = ['Longitude','Latitude'] + list(dataset[0].keys())[2:]



    def set_title(self, title):
        """Basic Method."""
        self._title = title

    def set_data_keys(self, datakeys):
        """Setting the data keys for the visualization."""
        self.__datakeys = datakeys

    def set_scales(self, scale, scale_extent):
        """Setting scale and scale extent for the map."""
        self.__scale = scale
        self.__scale_extent = scale_extent

    def set_max_poi(self, max_poi):
        """Setting the maximum number of points of interest to visualize."""
        self.__max_poi = max_poi

    def set_map_color(self, color):
        """Setting the color for the map."""
        self.__map_fill = color

    def set_fill_opacity(self, opacity):
        """Setting the opacity for the map and points of interest."""
        self.__fill_opacity = opacity
        self.__mouseout_opacity = opacity

    def set_circle_radius(self, radius):
        """Setting the radius for the points of interest."""
        self.__circle_radius = radius

    def set_circle_color(self, color):
        """Setting the color for the points of interest."""
        self.__circle_fill = color

    def generate_visualization_dataset(self, dataset):
        """Basic Method."""
        vis_dataset = []

        keys = list(dataset[0].keys())
        for datapoint in dataset:
            vis_datapoint = {}

            vis_datapoint['Latitude'] = datapoint[keys[0]]
            vis_datapoint['Longitude'] = datapoint[keys[1]]
            for other_keys in keys[2:]:
                vis_datapoint[other_keys] = datapoint[other_keys]
            vis_dataset.append(vis_datapoint)
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
                         't_div_hook_map': self._div_hook_map,
                         't_div_hook_legend': self._div_hook_legend,
                         't_div_hook_tooltip': self._div_hook_tooltip}

        output_text = template.render(template_vars)
        return output_text

    def create_js(self, template, dataset_url, shape_file):
        """Basic Method. Creates the JavaScript code based on the template."""
        template_vars = {'t_width': self.__width,
                         't_height': self.__height,
                         't_filename': "poi.json",
                         't_shape': shape_file,
                         't_city': self.__city,
                         't_scale': self.__scale,
                         't_scale_extent': self.__scale_extent,
                         't_max_poi': self.__max_poi,
                         't_file_extension': ".json",
                         't_zoom_threshold': self.__zoom_threshold,
                         't_div_hook_map': self._div_hook_map,
                         't_div_hook_tooltip': self._div_hook_tooltip,
                         't_tooltip_div_border': self.__tooltip_div_border,
                         't_map_fill': self.__map_fill,
                         't_map_stroke': self.__map_stroke,
                         't_fill_opacity': self.__fill_opacity,
                         't_stroke_opacity': self.__stroke_opacity,
                         't_mouseover_opacity': self.__mouseover_opacity,
                         't_mouseout_opacity': self.__mouseout_opacity,
                         't_circle_fill': self.__circle_fill,
                         't_circle_stroke': self.__circle_fill,
                         't_circle_radius': self.__circle_radius,
                         't_circle_stroke_width': self.__circle_stroke_width,
                         't_pive_version': self.__version,
                         't_headers': self.__headers}

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

    def get_js_code(self):
        """Basic Method."""
        dataset_url = '{}.json'.format(self._title)
        js_template = self.load_template_file(
            '{}{}.jinja'.format(self.__template_url, self.__template_name))
        shape_filename = '{}_shape.json'.format(self._title)
        js = self.create_js(js_template, dataset_url, shape_filename)
        return js

    def get_json_dataset(self):
        """Basic Method."""
        return self.generate_visualization_dataset(self.__dataset)

    def create_visualization_files(self, destination_url):
        """Basic Method."""
        html_template = self.load_template_file(
            '{}map_html.jinja'.format(self.__template_url))

        js_template = self.load_template_file(
            '{}{}.jinja'.format(self.__template_url, self.__template_name))

        shape_filename = '{}_shape.json'.format(self._title)
        self.write_file(self.__shape, destination_url, '/' + shape_filename)

        dataset_url = '{}.json'.format(self._title)
        js = self.create_js(js_template, dataset_url, shape_filename)
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

    def __get_file_extension(self, filename):
        """Returns the file extension of the passed source."""
        try:
            extension = pathlib.Path(filename).suffix
        except TypeError:
            print('Filename expected, got {} instead.'.format(filename))
        else:
            return extension
