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
""" The input manager reads files and strings containing
datasets in json and csv format. The data is automatically
validated and corrected if necessary."""
from collections import OrderedDict

from . import inputreader as reader
from . import datavalidater as validater
from . import consistenceprofiler as profiler
from . import visualizationmapper as vizmapper
from . import shapeloader as shapeloader

NOT_CONSISTENT_ERR_MSG = "Data is not consistent."
NO_DATA_LOADED_ERR_MSG = "Unexpected data source."


class InputManager(object):
    """Contains and manages the data."""
    isHive = False

    # Input Managers can try to merge false datapoints or not.
    def __init__(self, mergedata=False):
        self.__mergedata = mergedata
        #TODO: Should __contains_datefields be a property of InputManager
        #   and if yes, should it be set the way it is
        self.__contains_datefields = False

    def read(self, source):
        """Reads the input source."""
        inputdata = reader.load_input_source(source)

        # Raise an error if the data source is empty or nor readable.
        if not inputdata:
            raise ValueError(NO_DATA_LOADED_ERR_MSG)

        dataset = self.__validate_input(inputdata)
        # Raise an error if the dataset is not consistent.
        for i in dataset:
            for key,value in i.items():
                if key == 'LINKS':
                    isHive = True
                    break
        if self.__file_is_map_shape(inputdata):
            self.__shape_data = inputdata
            self.__shape_source = source
            dataset = inputdata

        if not self.__is_dataset_consistent(dataset):
            raise ValueError(NOT_CONSISTENT_ERR_MSG)

        return dataset

    def map(self, dataset):
        """Maps the dataset to supported visualizations."""
        viz_types = self.__get_datapoint_types(dataset)
        properties = vizmapper.get_visualization_properties(dataset, viz_types)
        self.__suitables = vizmapper.check_possibilities(properties)
        self.__contains_datefields = vizmapper.has_date(viz_types)

        return self.__suitables

    def has_date_points(self):
        """Returns true if the data contains dates."""
        #FIXME: Value only set after call to map(self, dataset)
        return self.__contains_datefields

    def get_map_shape(self, dataset):
        """Returns the map shape representing the dataset."""
        inner_shape = ''
        # If the dataset contains coordinates
        if 'poi' in self.__suitables:
            # If the chosen dataset is the map shape
            coordinates = shapeloader.get_all_coordinates_poi(dataset)
            (shape, city) = shapeloader.find_map_shape(coordinates)
        elif 'polygon' in self.__suitables:
            coordinates = shapeloader.get_all_coordinates_polygon(dataset)
            (shape, city) = shapeloader.find_map_shape(coordinates)
        # If the dataset is suitable for a heatmap
        elif 'heatmap' in self.__suitables:
            (shape, city) = shapeloader.build_heatmap(dataset)

        return (shape, None, city)

    def __is_dataset_consistent(self, dataset):
        """Checks if the dataset is consistent."""
        consistent = profiler.is_dataset_consistent(dataset)
        return consistent

    def __get_datapoint_types(self, dataset):
        """Returns all containing visualization types."""
        viztypes = profiler.get_consistent_types(dataset)
        return viztypes

    def __validate_input(self, inputdata):
        """Validates the input data:"""
        validdata = []
        if self.__mergedata:
            validdata = self.__merged_dataset_validation(inputdata)
        else:
            validdata = self.__dataset_validation(inputdata)
        return validdata

    def __merged_dataset_validation(self, inputdata):
        """Validate the data by merging all shared keys."""
        allkeys = validater.get_all_keys_in_dataset(inputdata)
        sharedkeys = validater.determine_shared_keys_in_dataset(allkeys,
                                                                inputdata)
        dataset = validater.generate_valid_dataset_from_shared_keys(sharedkeys,
                                                                    inputdata)
        return dataset

    def __dataset_validation(self, inputdata):
        """Validate the unmerged data by counting the keys and
        filtering out data points with minority keysets"""
        keycount = validater.count_keys_in_raw_data(inputdata)
        validkeys = validater.validate_data_keys(keycount)
        dataset = validater.generate_valid_dataset(validkeys, inputdata)
        return dataset

    def __get_json_features(self, json):
        """Handle every single entry (feature) of the JSON dataset and get their properties."""
        result = []
        if isinstance(json, OrderedDict):
            for key in json.keys():
                if key == 'features':
                    features = json[key]
                    for feature in features:
                        props = OrderedDict()
                        props = self.__get_feature_properties(feature, props)
                        result.append(props)
        return result

    def __get_feature_properties(self, feature, props):
        """Returns a dict with properties and coordinates of the feature."""
        if isinstance(feature, OrderedDict):
            for prop in feature.keys():
                if prop == 'properties':
                    for elem in feature[prop].keys():
                        props[elem] = feature[prop][elem]
                if prop == 'geometry':
                    next_prop = feature[prop]
                    props = self.__get_feature_properties(next_prop, props)
                if prop == 'type':
                    props[prop] = feature[prop]
                if prop == 'coordinates':
                    if props['type'] == 'Point':
                        lat = feature[prop][1]
                        lon = feature[prop][0]
                        props['Latitude'] = lat
                        props['Longitude'] = lon
                    elif props['type'] == 'Polygon':
                        for polygon in feature[prop]:
                            props['Polygon'] = polygon

        return props

    def __file_is_map_shape(self, dataset):
        """Checks if the file itself represents a map shape."""
        self.__is_shape = False
        try:
            if dataset[0]['type'] == 'Polygon':
                self.__is_shape = True
        except KeyError:
            self.__is_shape = False

        return self.__is_shape

    def dataset_is_shape(self):
        return self.__is_shape

    def __edit_json_geodata(self, source, input_data):
        """If geodata is in JSON format, edit its data structure to match with geodata in CSV format."""
        geodata = []
        if self.__get_file_extension(source) == '.json':
            # Get CSV and JSON to same data structure
            geodata = self.__get_json_features(input_data)
        if not geodata:
            geodata = input_data

        return geodata

    def __get_file_extension(self, source):
        """Returns the file extension of the passed source."""
        extension = pathlib.Path(source).suffix

        return extension