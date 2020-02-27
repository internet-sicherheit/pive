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
from glob import glob
from collections import OrderedDict

from pive.visualization import defaults as default

CONFIG_PATH = default.config_path
# The directory in which pive was installed.
REAL_PATH = os.path.dirname(os.path.realpath(__file__))
INTERNAL_CONFIG_PATH = '{}{}'.format(REAL_PATH, CONFIG_PATH)

NUMBER_OF_DATAPOINTS = 0
NUMBER_OF_VARIABLES = 1
DATESUPPORT = 2
LIST_VIZTYPES = 3
LEXICOGRAPHIC_ORDER = 4


def open_config_files(default_config_path):
    """Opens all json-config files in a directory and
    returns a list of each files content."""
    configs = []
    for filename in glob(INTERNAL_CONFIG_PATH + '*.json'):
        fp = open(filename, 'r')
        conf = json.load(fp, object_pairs_hook=OrderedDict)
        configs.append(conf)
    return configs


def has_date(viz_types):
    """Checks if the datapoint has dates."""
    times = False
    for item in viz_types:
        if item == 'time':
            times = True
    return times


def get_visualization_properties(dataset, viz_types):
    """Generates a list of the dataset properties.

    Returns all properties in the following order:
    Number of Datapoints, Number of Variables, Datesupport,
    List of Visualization-Types.
    """
    props = []
    length = len(dataset)
    props.append(length)
    props.append(len(viz_types))
    times = has_date(viz_types)
    props.append(times)
    props.append(viz_types)

    # Indicates, if the abcissa of the dataset is in lexicographic order.
    if (viz_types[0] in ('number', 'time')) and length > 1:
        lexicographic = is_data_in_lexicographic_order(dataset)
    else:
        lexicographic = False

    props.append(lexicographic)
    return props


def types_matching_data_requirements(given_types, required_types):
    """Verifies if all given types match the requirements.
    Requirements may vary and support multiple options."""
    matches = True
    i = 0

    for item in given_types:
        if item not in required_types[i]:
            matches = False
        i += 1
    return matches


def is_multiple_data_consistent(given_types, single_data_length):
    """Verifies if the multiple data elements following
    the last single data element are consistent."""
    consistent = True
    last_index = single_data_length - 1
    last_element = given_types[last_index]

    for item in given_types[last_index:]:
        if item != last_element:
            consistent = False
    return consistent


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
    if not (is_data_value_descending(dataset)
            or is_data_value_ascending(dataset)):
        lexicographic = False
    return lexicographic


def check_possibilities(property_list):
    """Checks if the input data maps to any of
    the visualization configs and returns a resultlist
    with the supported charts."""
    result = []
    props = property_list
    conf = open_config_files(CONFIG_PATH)

    for item in conf:
        item_type = item['title']
        is_possible = True
        supports_multi_data = False

        for elem in item.keys():
            # The dataset should contain at
            # least the minimum required datapoints.
            if elem == 'min_datapoints':
                if props[NUMBER_OF_DATAPOINTS] < item[elem]:
                    is_possible = False
            # The dataset should not contain more
            # than the maximum number off supported
            # datapoints.
            if elem == 'max_datapoints':
                if item[elem] != 'inf':
                    if (props[NUMBER_OF_DATAPOINTS] > item[elem]):
                        is_possible = False

            # If the data contains a date, the visualization
            # has to support date-types.
            if elem == 'datesupport':
                if props[DATESUPPORT]:
                    if item[elem] != props[DATESUPPORT]:
                        is_possible = False
            if elem == 'multiple_data':
                supports_multi_data = item[elem]

            if elem == 'lexical_required':
                if item[elem] is True:
                    if not props[LEXICOGRAPHIC_ORDER]:
                        is_possible = False

            # Checks if the input order of the desired viz-types matches
            # the requirements.
            if ((elem == 'vistypes') and is_possible):
                is_possible = check_input_order(
                    elem, item, props, supports_multi_data)
        if is_possible:
            result.append(item_type)
    return result


def check_input_order(elem, item, props, supports_multi_data):
    """Checks if the input vistypes match the requirements."""
    is_possible = True
    req_vtypes = []
    for i in item[elem]:
        for j in i:
            req_vtypes.append(i[j])

    # Length required to render a single dataset.
    single_data_length = len(req_vtypes)

    each_val_count = len(req_vtypes) - 1
    data_val_count = len(props[LIST_VIZTYPES]) - 1

    try:
        if ((data_val_count % each_val_count) != 0):
            is_possible = False
    except ZeroDivisionError:
        if each_val_count != data_val_count and not supports_multi_data:
            is_possible = False

    # Determines the given types.
    if (len(props[LIST_VIZTYPES]) >= single_data_length):
        given_types = props[LIST_VIZTYPES][:single_data_length]
    else:
        given_types = props[LIST_VIZTYPES]

    data_length = len(props[LIST_VIZTYPES])
    required_length = len(req_vtypes)

    # If the data is larger than the single length it must match the
    # requirements for multiple datasets.
    data_matches = types_matching_data_requirements(given_types, req_vtypes)

    if not data_matches:
        is_possible = False

    if (data_length > required_length):
        if supports_multi_data:
            # All points in multiple datasets must be consistent.
            multi_consistent = is_multiple_data_consistent(
                given_types, single_data_length)
            if not multi_consistent:
                is_possible = False
        else:
            is_possible = False
    elif (data_length < required_length):
        is_possible = False

    return is_possible
