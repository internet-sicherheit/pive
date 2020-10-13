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
from pathlib import Path

import jinja2

from pive.visualization import mapdefaults as default
from pive.visualization import mapvisualization as mv
from pive import shapeloader


class Map(mv.MapVisualization):
    """Map class for heatmap data."""

    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height,
                 padding=default.padding):
        """Initializing the chart with default settings."""

        # Initializing the inherited pseudo-interface.
        mv.MapVisualization.__init__(self)

        # Metadata
        self._title = 'poi'
        self._template_name = 'poi'
        self._dataset = dataset
        self._template_url = Path(__file__).resolve().parent.joinpath(default.template_path)
        self._datakeys = []
        self._version = default.p_version

        # Visualization properties.
        self._width = width
        self._height = height
        self._padding = padding
        self._max_poi = default.max_poi

        # Starting, min and max values for zoom levels on the map
        self._scale_extent = default.scale_extent

        # Map rendering
        self._zoom_threshold = default.zoom_threshold
        self._tooltip_div_border = default.tooltip_div_border
        self._map_fill = default.map_fill
        self._map_stroke = default.map_stroke
        self._fill_opacity = default.fill_opacity
        self._stroke_opacity = default.stroke_opacity
        self._mouseover_opacity = default.mouseover_opacity
        self._mouseout_opacity = default.mouseout_opacity
        self._circle_fill = default.circle_fill
        self._circle_stroke = default.circle_stroke
        self._circle_radius = default.circle_radius
        self._circle_stroke_width = default.circle_stroke_width
        self._headers = ['Longitude','Latitude'] + list(dataset[0].keys())[2:]

    def get_modifiable_template_variables(self):
        """Returns a dictionary of all template variables, that are supposed to be modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        variables = super().get_modifiable_template_variables()
        variables["t_datakeys"] = self._datakeys
        variables["t_zoom_threshold"] = self._zoom_threshold
        variables["t_tooltip_div_border"] = self._tooltip_div_border
        variables["t_map_fill"] = self._map_fill
        variables["t_map_stroke"] = self._map_stroke
        variables["t_mouseover_opacity"] = self._mouseover_opacity
        variables["t_fill_opacity"] = self._fill_opacity
        variables["t_mouseout_opacity"] = self._mouseout_opacity
        variables["t_max_poi"] = self._max_poi
        variables["t_circle_fill"] = self._circle_fill
        variables["t_circle_stroke"] = self._circle_stroke
        variables["t_circle_radius"] = self._circle_radius
        variables["t_circle_stroke_width"] = self._circle_stroke_width
        return variables

    def get_modifiable_template_variables_typehints(self):
        """Returns a dictionary of typehints for variables that are modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        typehints = super().get_modifiable_template_variables_typehints()
        new_typehints = {
            "default": {
                "t_zoom_threshold": {
                    "type": "int",
                    "min": 1
                },
                "t_tooltip_div_border": {
                    "type": "string"
                },
                "t_datakeys": {
                    "type": "list",
                    "length": len(self._datakeys),
                    "item_type": {
                        "type": "string"
                    }
                },
                "t_map_fill": {
                    "type": "color",
                    "channels": 3
                },
                "t_map_stroke": {
                    "type": "color",
                    "channels": 3
                },
                "t_mouseover_opacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_fill_opacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_mouseout_opacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_max_poi": {
                    "type": "int",
                    "min": 1
                },
                "t_circle_fill": {
                    "type": "color",
                    "channels": 3
                },
                "t_circle_stroke": {
                    "type": "color",
                    "channels": 3
                },
                "t_circle_radius": {
                    "type": "float",
                    "min": 0.0
                },
                "t_circle_stroke_width": {
                    "type": "float",
                    "min": 0.0
                }
            }
        }
        for key in new_typehints.keys():
            if key not in typehints.keys():
                typehints[key] = {}
            typehints[key].update(new_typehints[key])
        return typehints

    def load_from_dict(self, dictionary):
        super().load_from_dict(dictionary)
        if "t_datakeys" in dictionary:
            self.set_data_keys(json.loads(dictionary['t_datakeys'].replace('\'', '\"')))
        if 't_zoom_threshold' in dictionary:
            self._zoom_threshold = int(dictionary['t_zoom_threshold'])
        if 't_tooltip_div_border' in dictionary:
            self._tooltip_div_border = dictionary['t_tooltip_div_border']
        if 't_map_fill' in dictionary:
            self._map_fill = dictionary['t_map_fill']
        if 't_map_stroke' in dictionary:
            self._map_stroke = dictionary['t_map_stroke']
        if 't_fill_opacity' in dictionary:
            self._fill_opacity = dictionary['t_fill_opacity']
        if "t_mouseover_opacity" in dictionary:
            self._mouseover_opacity = float(dictionary['t_mouseover_opacity'])
        if "t_mouseout_opacity" in dictionary:
            self._mouseout_opacity = float(dictionary['t_mouseout_opacity'])
        if "t_max_poi" in dictionary:
            self.set_max_poi(int(dictionary['t_max_poi']))
        if "t_circle_fill" in dictionary:
            self.set_circle_color(dictionary['t_circle_fill'])
        if "t_circle_stroke" in dictionary:
            self._circle_stroke = dictionary['t_circle_stroke']
        if "t_circle_stroke_width" in dictionary:
            self._circle_stroke_width = dictionary['t_circle_stroke_width']


    def get_map_shape(self):
        coordinates = shapeloader.get_all_coordinates_poi(self._dataset)
        (self._shape, self._city, self._shortend_names) = shapeloader.find_map_shape(coordinates)

    def set_data_keys(self, datakeys):
        """Setting the data keys for the visualization."""
        self._datakeys = datakeys


    def set_max_poi(self, max_poi):
        """Setting the maximum number of points of interest to visualize."""
        self._max_poi = max_poi

    def set_map_color(self, color):
        """Setting the color for the map."""
        self._map_fill = color

    def set_fill_opacity(self, opacity):
        """Setting the opacity for the map and points of interest."""
        self._fill_opacity = opacity
        self._mouseout_opacity = opacity

    def set_circle_radius(self, radius):
        """Setting the radius for the points of interest."""
        self._circle_radius = radius

    def set_circle_color(self, color):
        """Setting the color for the points of interest."""
        self._circle_fill = color

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

    def create_js(self, template, dataset_url):
        """Basic Method. Creates the JavaScript code based on the template."""
        template_vars = {'t_width': self._width,
                         't_height': self._height,
                         't_filename': "poi.json",
                         't_shape': self.get_shapefile_path(Path(dataset_url).resolve().parent),
                         't_city': self._city,
                         't_scale_extent': self._scale_extent,
                         't_max_poi': self._max_poi,
                         't_file_extension': ".json",
                         't_zoom_threshold': self._zoom_threshold,
                         't_div_hook_map': self._div_hook_map,
                         't_div_hook_tooltip': self._div_hook_tooltip,
                         't_tooltip_div_border': self._tooltip_div_border,
                         't_map_fill': self._map_fill,
                         't_map_stroke': self._map_stroke,
                         't_fill_opacity': self._fill_opacity,
                         't_stroke_opacity': self._stroke_opacity,
                         't_mouseover_opacity': self._mouseover_opacity,
                         't_mouseout_opacity': self._mouseout_opacity,
                         't_circle_fill': self._circle_fill,
                         't_circle_stroke': self._circle_fill,
                         't_circle_radius': self._circle_radius,
                         't_circle_stroke_width': self._circle_stroke_width,
                         't_pive_version': self._version,
                         't_headers': self._headers}

        output_text = template.render(template_vars)
        return output_text