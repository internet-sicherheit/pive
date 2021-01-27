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
import importlib
import pkgutil

from .visualization import defaults as default
from .overpass import API_URL
from .outputmanager import FolderOutputManager
import pive.shapeloader as shapeloader

# Accessor to choose the charts. Corresponding with
# the config files 'title' attribute in
# pive/visualization/config
CHART_LINE = 'linechart'
CHART_SCATTER = 'scatterchart'
CHART_BUBBLE = 'bubblechart'
CHART_BAR = 'barchart'
CHART_PIE = 'piechart'
CHART_CHORD = 'chordchart'
CHART_HIVE = 'hiveplot'
MAP_HEAT = 'heatmap'
MAP_POI = 'poi'
MAP_POLYGON = 'polygon'

# Bundles all essential access methods to render visualizations.
class Environment(object):
    """Contains all suitable visualizations. Only those
    visualizations are imported and it is not
    allowed to render unsuited visualizations."""
    __suitables = []
    __data = []

    # The actual visualization modules.
    __modules = []

    __has_datefields = False

    __datakeys = []


    def __init__(self, inputmanager=None, outputmanager=FolderOutputManager(default.output_path), country="DE", overpass_endpoint=API_URL):
        """ The Environment needs an input manager instance to work, but is
        optional at creation. Leaving the user to configure the
        input manager first. """
        self.__inputmanager = inputmanager
        self.__outputmanager = outputmanager
        self.__country = country
        self.__endpoint = overpass_endpoint
        self.__shapeloader = None
        self.reset_map_config()

    def set_map_country(self, country):
        self.__country = country
        self.reset_map_config()

    def set_map_api_endpoint(self, endpoint):
        self.__endpoint = endpoint
        self.reset_map_config()

    def reset_map_config(self):
        self.__shapeloader = shapeloader.Shapeloader(self.__country, self.__endpoint)

    def set_output_path(self, outputpath):
        """Set the output path of all visualization files."""
        self.__outputmanager = FolderOutputManager(outputpath)

    def set_input_manager(self, inputmanager):
        """Change the internal input manager instance."""
        self.__inputmanager = inputmanager

    # Load the dataset utilizing the internal input manager.
    def load(self, source):
        """Loads data from a source."""
        try:
            inputdata = self.__inputmanager.read(source)
            self.__suitables = self.__inputmanager.map(inputdata)
            self.__data = inputdata
            #print("after try (inpurtdata): ", inputdata)
        except ValueError as e:
            print ("Failed to load the dataset: %s" % e)
            raise

        self.__modules = self.import_suitable_visualizations(self.__suitables)


        self.__has_datefields = self.__inputmanager.has_date_points()


        # Converting the datakeys into strings.
        self.set_datakeys()


        return self.__suitables

    def set_datakeys(self):
        self.__datakeys = [str(i) for i in list(self.__data[0].keys())]

    @staticmethod
    def import_suitable_visualizations(suitable_visualization_list):
        """Dynamically import all suited visualization modules."""
        mods = []
        for item in suitable_visualization_list:
            mod = '.%s' % item
            mods.append(mod)

        modules = []

        for item in mods:
            modules.append(importlib.import_module(item,
                                                   package=default.module_path))
        return modules

    @staticmethod
    def import_visualisations(package, recursive=True):
        """ Import all submodules of a module, recursively, including subpackages
        https://gist.github.com/breeze1990/0253cb96ce04c00cb7a67feb2221e95e

        :param recursive: bool
        :param package: package (name or actual module)
        :type package: str | module
        :rtype: dict[str, types.ModuleType]
        """
        if isinstance(package, str):
            package = importlib.import_module(package)
        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + '.' + name
            try:
                module = importlib.import_module(full_name)
                if hasattr(module, 'Chart'):
                    results[full_name.split('.')[-1]] = module.Chart
                if hasattr(module, 'Map'):
                    results[full_name.split('.')[-1]] = module.Map
            except:
                pass
            if recursive and is_pkg:
                results.update(Environment.import_visualisations(full_name))
        return results

    @staticmethod
    def import_all_visualisations():
        return Environment.import_visualisations(default.module_path)

    # Choose a chart to start modifying or render it.
    def choose(self, chart):
        """Choose a chart from the suitable visualizations."""
        if chart not in self.__suitables:
            raise ValueError('Visualization not possible.')

        # Depending on the users choice mark the visualization method as geodata
        #TODO: Check class if it is geodata class instead of hardcoding
        if chart in ['heatmap', 'poi', 'polygon']:
            self.__is_geodata = True
        else:
            self.__is_geodata = False

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
            chart_decision = class_(self.__data, modname, self.__shapeloader)
            chart_decision.get_map_shape()
        elif self.__has_datefields:
            chart_decision = class_(self.__data, modname, times=True)
        else:
            chart_decision = class_(self.__data, modname)

        chart_decision.setDataKeys(self.__datakeys)
        return chart_decision

    def load_raw(self, persisted_data):
        """Load preprocessed data and skip validation."""

        self.__data = persisted_data['dataset']
        chart_name = persisted_data['chart_name']
        self.set_datakeys()
        self.__is_geodata = persisted_data.get('is_geodata', False)
        self.__suitables = [chart_name]
        self.__modules = self.import_suitable_visualizations(self.__suitables)
        module = self.__modules[0]
        if self.__is_geodata:
            class_ = getattr(module, 'Map')
        else:
            class_ = getattr(module, 'Chart')
        if self.__is_geodata:
            chart_decision = class_(self.__data, chart_name, self.__shapeloader)
        elif self.__has_datefields:
            chart_decision = class_(self.__data, chart_name, times=True)
        else:
            chart_decision = class_(self.__data, chart_name)
        chart_decision.setDataKeys(self.__datakeys)
        chart_decision.load_persisted_data(persisted_data)
        return chart_decision


    def render(self, chart, template_variables={}, **options):
        """Creates all the output data and hands it to the output manager."""
        self.__outputmanager.output(data=chart.create_visualization_files(template_variables), **options)

    @staticmethod
    def render_code(chart):
        """Renders the chart and returns the javascript
        code and its json dataset to include the
        visualization in another document."""
        js = chart.get_js_code()
        data = chart.get_json_dataset()
        return (js, data)
