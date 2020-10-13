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

from pive.visualization import mapdefaults as default
from pive.visualization import mapvisualization as mv
from pive import shapeloader

from pathlib import Path
import json


class Map(mv.MapVisualization):
    """Map class for heatmap data."""

    def __init__(self,
                 dataset,
                 template_name,
                 shapeloader,
                 width=default.width,
                 height=default.height,
                 padding=default.padding):
        """Initializing the chart with default settings."""

        # Initializing the inherited pseudo-interface.
        mv.MapVisualization.__init__(self)

        # Metadata
        self._title = 'polygon'
        self._template_name = 'polygon'
        self._dataset = dataset
        self._template_url = Path(__file__).resolve().parent.joinpath(default.template_path)
        self._datakeys = []
        self._version = default.p_version

        self.__shapeloader = shapeloader

        # Visualization properties.
        self._width = width
        self._height = height
        self._padding = padding

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
        self._outer_map_fill = default.outer_map_fill

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
        variables["t_fill_opacity"] = self._fill_opacity
        variables["t_mouseover_opacity"] = self._mouseover_opacity
        variables["t_mouseout_opacity"] = self._mouseout_opacity
        variables["t_outer_map_fill"] = self._outer_map_fill
        return variables

    def get_modifiable_template_variables_typehints(self):
        """Returns a dictionary of typehints for variables that are modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        typehints = super().get_modifiable_template_variables_typehints();
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
                "t_fill_opacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_mouseover_opacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_mouseout_opacity": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0
                },
                "t_outer_map_fill": {
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
        if "t_outer_map_fill" in dictionary:
            self.set_outer_map_color(dictionary['t_outer_map_fill'])


    def get_map_shape(self):
        coordinates = shapeloader.get_all_coordinates_polygon(self._dataset)
        (self._shape, self._city, self._shortend_names) = self.__shapeloader.find_map_shape(coordinates, [datapoint['name'] for datapoint in self._dataset])


    def set_data_keys(self, datakeys):
        """Setting the data keys for the visualization."""
        self._datakeys = datakeys

    def set_inner_map_color(self, color):
        """Setting the color for the inner map."""
        self._map_fill = color

    def set_outer_map_color(self, color):
        """Setting the color for the outer map."""
        self._outer_map_fill = color

    def set_fill_opacity(self, opacity):
        """Setting the opacity for the map."""
        self._fill_opacity = opacity
        self._mouseout_opacity = opacity

    def generate_visualization_dataset(self, dataset):
        """Basic Method."""
        vis_dataset = []

        for datapoint in dataset:
            vis_datapoint = {}
            vis_datapoint['geometry'] = {"type": "Polygon", "coordinates": [datapoint['polygon']]}
            vis_datapoint['properties'] = {"name": datapoint['name'], "id": self._shortend_names[datapoint['name']]}
            vis_datapoint["type"] = "Feature"
            vis_dataset.append(vis_datapoint)
        return vis_dataset

    def create_js(self, template, dataset_url):
        """Basic Method. Creates the JavaScript code based on the template."""
        template_vars = {'t_width': self._width,
                         't_height': self._height,
                         't_shape': self.get_shapefile_path(Path(dataset_url).resolve().parent),
                         't_inner': "polygon.json",
                         't_city': self._city,
                         't_scale_extent': self._scale_extent,
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
                         't_outer_map_fill': self._outer_map_fill,
                         't_pive_version': self._version}

        output_text = template.render(template_vars)
        return output_text