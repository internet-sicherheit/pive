# Copyright (c) 2014 - 2016, David Bothe
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

# The visualization types determine which charts can be generated out of
# the given dataset.

from dateutil.parser import parse
import sys

VISTYPE_STRING = 0;
VISTYPE_NUMERICAL = 1;
VISTYPE_DATETIME = 2;


def get_datapoint_types(datapoint):
    """Determines the datas visualization-types of a given datapoint.
    Valid visualization-types are 'number', 'string' and 'time'"""
    types = []
    for key in list(datapoint.keys()):

        item = datapoint[key]

        # If the datapoint contains a float or int it will
        # be considered as a numerical datapoint.
        if is_float(item) or is_int(item):
            types.append("number")

        # If the item is a string, it may also be formatted as
        # a datetime item.
        if is_string(item):
            types.append("string")
            #Strings might also be dates
            if is_date(item):
                types.append("time")

    return types


def is_string(item):
    """Determines if the item is a string type for Python 3 and
    Python 2.7."""
    is_string = False

    if sys.version_info[0] >= 3:
    # Python 3 string determination.
        if isinstance(item, str):
            is_string = True

    # Python 2.7 workaround to determine strings.
    # Basestring was deprecated with Python 3.
    if sys.version_info[0] < 3:
        try:
            if isinstance(item, basestring):
                is_string = True
        except TypeError:
            pass

    return is_string


def is_date(item):
    """Checks if the item is a date."""
    try:
        parse(item)
        return True
    except (ValueError,TypeError):
        return False


def is_float(value):
    try:
        number = float(value)
    except ValueError:
        return False
    else:
        return True


def is_int(value):
    try:
        num_a = float(value)
        num_b = int(num_a)
    except ValueError:
        return False
    else:
        return num_a == num_b

def get_consistent_types(dataset):
    # List of possible viztype candidates
    current_types = get_datapoint_types(dataset[0])
    for data_point in dataset[1:]:
        checked_datapoint_types = get_datapoint_types(data_point)
        new_viztypes = []
        for viztype in current_types:
            if viztype in checked_datapoint_types:
                new_viztypes.append(viztype)
        if new_viztypes == []:
            # All possible viztypes have been eliminated, dataset is inconsistent
            return []
        current_types = new_viztypes
    return current_types


def is_dataset_consistent(input_data):
    """Checks the consistency of the dataset.
    All data points must have at least one type in common.
    As everything can be at least a string, this most likely will return true."""
    if input_data:
        return get_consistent_types(input_data) != []
    return True
