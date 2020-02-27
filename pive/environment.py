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

# -*- coding: utf-8 -*-
""" The pive environment manages the visualizations and
 relies on a given input manager to read data before
 processing the visualizations. """
import pathlib
import importlib

from pive.visualization import defaults as default

# Accessor to choose the charts. Corresponding with
# the config files 'title' attribute in
# pive/visualization/config
CHART_LINE = 'linechart'
CHART_SCATTER = 'scatterchart'
CHART_BUBBLE = 'bubblechart'
CHART_BAR = 'barchart'
CHART_PIE = 'piechart'
CHART_CHORD = 'chordchart'
MAP_HEAT = 'heatmap'
MAP_POI = 'poi'
MAP_POLYGON = 'polygon'

# Bundles all essential access methods to render visualizations.

NO_SUITABLES_FOUND_ERR_MSG = 'No suitable visualization methods were found reading this file.'

class Environment_(object):
    """Contains all suitable visualizations.

    Only those visualizations are imported and it is not
    allowed to render unsuited visualizations.
    """

    __suitables = []
    __data = []

    # The actual visualization modules.
    __modules = []

    __has_datefields = False

    __datakeys = []

    __map_shape = []

    def __init__(self, filename, inputmanager = None, outputpath=default.output_path):
        """ The Environment needs an input manager instance to work.

        This is optional at creation, leaving the user to configure the
        input manager first.
        """
        self.__inputmanager = inputmanager
        self.__filename = filename
        self.__outputpath = outputpath
        self.__is_geodata = False

    def set_output_path(self, outputpath):
        """Set the output path of all visualization files."""
        self.__outputpath = outputpath

    def set_input_manager(self, inputmanager):
        """Change the internal input manager instance."""
        self.__inputmanager = inputmanager

    # Load the dataset utilizing the internal input manager.
    def load(self, source):
        """Loads data from a source."""
        try:
            input_data = self.__inputmanager.read(source)
            self.__suitables = self.__inputmanager.map(input_data)
            self.__data = input_data
        except ValueError as e:
            print('Failed to load the dataset: {}'.format(e))
            raise
        
        self.__modules = self.import_suitable_visualizations(self.__suitables)
        self.__has_datefields = self.__inputmanager.has_date_points()

        # Converting the datakeys into strings.
        if not self.__inputmanager.dataset_is_shape():
            self.__datakeys = [str(i) for i in list(self.__data[0].keys())]

        # Loads the corresponding map shape if suitable for visualization
        for x in self.__suitables:
            if x in ['heatmap', 'poi', 'polygon']:
                (self.__map_shape, self.__inner_shape, self.__city) = self.__inputmanager.get_map_shape(input_data)

        return self.__suitables

    @staticmethod
    def import_suitable_visualizations(suitable_visualization_list):
        """Dynamically import all suited visualization modules."""

        mods = []
        for item in suitable_visualization_list:
            mod = '.{}'.format(item)
            mods.append(mod)

        modules = []

        for item in mods:
            modules.append(importlib.import_module(
                item, package=default.module_path))

        return modules

    # Choose a chart to start modifying or render it.
    def choose(self, chart):
        """Choose a chart from the suitable visualizations."""
        if chart not in self.__suitables:
            raise ValueError('Visualization not possible.')

        # Depending on the users choice mark the visualization method as geodata
        if chart in ['heatmap', 'poi', 'polygon']:
            self.__is_geodata = True

        # Automatically create the chart instance and
        # return it to the user.
        index = self.__suitables.index(chart)
        modname = self.__suitables[index]
        module = self.__modules[index]

        if self.__is_geodata:
            class_ = getattr(module, 'Map')
        else:
            class_ = getattr(module, 'Chart')

        # When dates occur the constructor is called differently.
        if self.__is_geodata:
            chart_decision = class_(self.__data, modname, self.__filename, self.__map_shape, self.__inner_shape, self.__city)
        elif self.__has_datefields:
            chart_decision = class_(self.__data, modname, times=True)
        else:
            chart_decision = class_(self.__data, modname)

        chart_decision.set_data_keys(self.__datakeys)
        return chart_decision

    def render(self, chart):
        """Renders the chart and creates all files to display the visualization.

        Files are stored under the environments output path.
        """

        chart.create_visualization_files(self.__outputpath)

    def render_code(self, chart):
        """Renders the chart.

        It returns the javascript code and its json dataset to include the
        visualization in another document.
        """
        js = chart.get_js_code()
        data = chart.get_json_dataset()
        return (js, data)

    def __json_is_file(self, json):
        """Returns the file extension of the passed source."""
        try:
            extension = pathlib.Path(json).suffix
        except TypeError:
            return False
        else:
            if extension == '.json':
                return True
            else:
                return False