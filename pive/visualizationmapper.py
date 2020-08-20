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

import json
from collections import OrderedDict
from functools import reduce
from .visualization import defaults as default
from pathlib import Path

config_path = default.config_path
# The directory in which pive was installed.
realpath = Path(__file__).resolve().parent
internal_config_path = realpath.joinpath(config_path)


def open_config_files(default_config_path):
    """Opens all json-config files in a directory and
    returns a list of each files content."""
    configs = []

    for json_path in internal_config_path.glob('*.json'):
        with json_path.open(mode='r') as fp:
            conf = json.load(fp, object_pairs_hook=OrderedDict)
        configs.append(conf)
        # configs is type of list
    return configs


def has_date(viz_types):
    """Checks if the datapoint has dates."""
    times = False
    for item in viz_types:
        if "time" in item:
            times = True
    return times


def get_visualization_properties(dataset, viz_types):
    """Generates a list of the dataset properties. Returns
    all properties in the following order: Number of Datapoints,
    Number of Variables, Datesupport,
    List of Visualization-Types."""
    props = {}
    length = len(dataset)
    props["dataset_length"] = length
    props["viz_types_length"] = len(viz_types)
    times = has_date(viz_types)
    props["has_date"] = times
    props["viz_types"] = viz_types
    props["lexicographic"] = (viz_types[0] & {'number', 'time'}) and length > 1 and is_data_in_lexicographic_order(
        dataset)
    isHive = False
    # for checking hive initials
    for i in dataset:
        try:
            for key,value in i.items():
                if key == 'LINKS':
                    isHive = True
                    break
        except KeyError:
            pass
    props["hive"] = isHive

    return props


def types_matching_data_requirements(given_types, required_types):
    """Verifies if all given types match the requirements.
    Requirements may vary and support multiple options."""
    if len(given_types) != len(required_types):
        return False
    return reduce(lambda x, zipped: x and (set(zipped[1]) & set(zipped[0])), list(zip(given_types, required_types)),
                  True)


def is_multiple_data_consistent(given_types, singleDataLength):
    """Verifies if the multiple data elements following
    the last single data element are consistent."""

    last_index = singleDataLength - 1
    consistent_types = given_types[last_index]

    for item in given_types[last_index:]:
        consistent_types = consistent_types & item
    return (consistent_types != set())


def is_data_value_ascending(dataset):
    """Checks if the data is ascending."""
    ascending = True
    starting_abscissa = list((dataset[0]).items())[0][1]
    last_abscissa = starting_abscissa
    for item in dataset[1:]:
        current_abscisssa = list(item.items())[0]
        if (current_abscisssa[1] <= last_abscissa):
            ascending = False
        last_abscissa = current_abscisssa[1]
    return ascending


def is_data_value_descending(dataset):
    """Checks if the data ist descending."""
    descending = True
    starting_abscissa = list((dataset[0]).items())[0][1]
    last_abscissa = starting_abscissa
    for item in dataset[1:]:
        current_abscisssa = list(item.items())[0]
        if (current_abscisssa[1] >= last_abscissa):
            descending = False
        last_abscissa = current_abscisssa[1]
    return descending


def is_data_in_lexicographic_order(dataset):
    """Checks if the data is ascending or descending."""
    lexicographic = True
    if not (is_data_value_descending(dataset) or is_data_value_ascending(dataset)):
        lexicographic = False
    return lexicographic


def check_possibilities(property_list):
    """Checks if the input data maps to any of
    the visualization configs and returns a resultlist
    with the supported charts."""
    result = []
    props = property_list
    configurations = open_config_files(config_path)
    for config in configurations:
        item_type = config['title']
        is_possible = True
        supports_multi_data = False
        # item is ordereddict

        for elem in config.keys():
            # The dataset should contain at
            # least the minimum required datapoints.
            # elem is a string
            if elem == 'min_datapoints':
                if props["dataset_length"] < config[elem]:
                    is_possible = False
            # The dataset should not contain more
            # than the maximum number off supported
            # datapoints.
            if elem == 'max_datapoints':
                if config[elem] != 'inf':
                    if (props["dataset_length"] > config[elem]):
                        is_possible = False

            # If the data contains a date, the visualization
            # has to support date-types.
            if elem == 'datesupport':
                if props["has_date"]:
                    if config[elem] != props["has_date"]:
                        is_possible = False
            if elem == 'multiple_data':
                supports_multi_data = config[elem]

            if elem == 'lexical_required':
                if config[elem] == True:
                    if not props["lexicographic"]:
                        is_possible = False

            # Checks if the input order of the desired viz-types matches
            # the requirements.
            if ((elem == 'vistypes') and is_possible):
                is_possible = checkInputOrder(elem, config, props, supports_multi_data)
        if is_possible:
            result.append(item_type)
    return result


def checkInputOrder(elem, config, props, supportsMultiData):
    """Checks if the input vistypes match the requirements."""
    isPossible = True
    req_vtypes = []
    # if props["hive"]:
    #     for k in config[elem]:
    #         source_list = v
    #         for i in source_list:
    #             for j in i:
    #                 req_vtypes.append(i[j])
    for i in config[elem]:
        for j in i:
            if type(i[j]) == str:
                req_vtypes.append(set([i[j]]))
            else:
                req_vtypes.append(set(i[j]))

    # Length required to render a single dataset.
    singleDataLength = len(req_vtypes)

    # TODO: Check if the following formula fits all possible chart types
    #       Might not work for multidimensional graphs or network graphs

    # Subract 1 for X-value from both sets
    # Number of required datapoint-values per element must fit N times
    #       into the available data without rest

    eachValCount = len(req_vtypes) - 1
    dataValCount = len(props["viz_types"]) - 1
    #FIXME: eachValCount == 0 avoids divisionByZero errors, but why is it necessary in the first place?
    if (eachValCount == 0 or (dataValCount % eachValCount) != 0):
        isPossible = False

    # Determines the given types.
    if (len(props["viz_types"]) >= singleDataLength):
        given_types = props["viz_types"][:singleDataLength]
    else:
        given_types = props["viz_types"]

    datalength = len(props["viz_types"])
    requiredlength = len(req_vtypes)

    # If the data is larger than the single length it must match the
    # requirements for multiple datasets.
    data_matches = types_matching_data_requirements(given_types, req_vtypes)
    if not data_matches:
        isPossible = False

    if (datalength > requiredlength):
        if supportsMultiData:
            # All points in multiple datasets must be consistent.
            multi_consistent = is_multiple_data_consistent(given_types, singleDataLength)
            if not multi_consistent:
                isPossible = False
        else:
            isPossible = False
    elif (datalength < requiredlength):
        isPossible = False

    return isPossible
