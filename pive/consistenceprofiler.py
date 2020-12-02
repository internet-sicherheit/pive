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
from functools import reduce
import sys
import re

VISTYPE_STRING = 0;
VISTYPE_NUMERICAL = 1;
VISTYPE_DATETIME = 2;

ISO8601_REGEX = re.compile(r"^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$")
COORD_REGEX = re.compile(r'^-?[0-9]{1,3}(?:\.[0-9]{1,20})+$') #FIXME: Only works for GPS-Coordinates

def get_datapoint_types(datapoint):
    """Determines the datas visualization-types of a given datapoint.
    Valid visualization-types are 'number', 'string' and 'time'"""
    types = []
    for key in list(datapoint.keys()):
        typeset = set()

        item = datapoint[key]

        if isinstance(item, list):
            typeset.add("list")
            if is_polygon(item):
                typeset.add("polygon")

        # If the datapoint contains a float or int it will
        # be considered as a numerical datapoint.
        if is_int(item) or is_float(item):
            typeset.add("number")

        if is_gps_latitude(item):
            typeset.add("latitude")
        if is_gps_longitude(item):
            typeset.add("longitude")

        # If the item is a string, it may also be formatted as
        # a datetime item.
        if is_string(item):
            typeset.add("string")
            if is_date(item):
                typeset.add("time")
        types.append(typeset)
    return types

def is_gps_latitude(value):
    """Checks if the passed value is a coordinate."""
    try:
        if isinstance(value, str):
            value = float(value)
        return -90 <= value <= 90
    except Exception as e:
        return False

def is_gps_longitude(value):
    """Checks if the passed value is a coordinate."""
    try:
        if isinstance(value, str):
            value = float(value)
        return -180 <= value <= 180
    except Exception as e:
        return False

def is_polygon(gps_list):
    try:
        matches_mapshape = True
        if len(gps_list) >= 3:
           for point in gps_list:
               matches_mapshape = matches_mapshape & is_gps_latitude(point[0]) & is_gps_longitude(point[1])
        else:
            matches_mapshape = False
    except Exception as e:
        matches_mapshape = False
        print(e)
    return matches_mapshape

def is_coordinate(item):
    return is_gps_longitude(item) or is_gps_latitude(item)

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
        if ISO8601_REGEX.match(item) is not None and parse(item) is not None:
            return True
    except (ValueError, TypeError, AttributeError):
        pass
    return False


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
        if ISO8601_REGEX.match(item) is not None and parse(item) is not None:
            return True
    except (ValueError, TypeError, AttributeError):
        pass
    return False


def is_float(value):
    try:
        number = float(value)
    except (ValueError,TypeError):
        return False
    else:
        return True


def is_int(value):
    try:
        num_a = float(value)
        num_b = int(num_a)
    except (ValueError, TypeError, OverflowError):
        return False
    else:
        return num_a == num_b

def get_consistent_types(dataset):
    # List of possible viztype candidates
    current_types = get_datapoint_types(dataset[0])
    for data_point in dataset[1:]:
        test_types = get_datapoint_types(data_point)
        current_types = [ x & y for (x,y) in zip(current_types,test_types) ]
    return current_types


def is_dataset_consistent(input_data):
    """Checks the consistency of the dataset.
    All data points must have at least one type in common.
    As everything can be at least a string, this most likely will return true."""
    if input_data:
        types = get_consistent_types(input_data)
        consistency = reduce(lambda x, y: x and (y != set()), types, True)
        return consistency
    #TODO: is the absence of input data consistent?
    return True
