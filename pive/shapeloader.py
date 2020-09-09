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

import pive.consistenceprofiler as profiler

from re import split as resplit
from math import ceil

from pive import overpass

def get_all_coordinates_poi(dataset):
    """Returns every pair of coordinates from the dataset."""
    result = []
    for item in dataset:
        coord_pair = []
        # Points of Interest
        for key in list(item.keys()):
            if profiler.is_coordinate(item[key]):
                coord_pair.append(item[key])
            if len(coord_pair) == 2:
                result.append(coord_pair)
                break
    return result

def get_all_coordinates_polygon(dataset):
    """Returns every pair of coordinates from the dataset."""
    result = []
    for item in dataset:
        key = list(item.keys())[0]
        for point in item[key]:
            #FIXME: Officially released data is ordered backwards.
            lat = str(point[1])
            lon = str(point[0])
            if profiler.is_coordinate(lat) and profiler.is_coordinate(lon):
                coord_pair = [lat, lon]
                result.append(coord_pair)
    return result

def find_map_shape(coordinates):
    """Returns a map shape fitting every coordinate pair.
    
    Iterates through every pair of the coordinate list.
    Finds the smallest possible map shape they have in common."""
    result = []
    candidate = []
    level = '0'

    common_shapes = overpass.get_common_shapes(coordinates)
    #FIXME: Hardcoded admin_level
    #FIXME: Will break if a single point is outside of the city
    city_shape = [ element for element in common_shapes if element["tags"]["admin_level"] == '6'][0]
    smallest_shape = max(common_shapes, key=lambda element: int(element["tags"]["admin_level"]))

    shape_name = smallest_shape["tags"]["name"]
    city_name = city_shape["tags"]["name"]
    #FIXME: Get City tag for zoom levels
    shape_id = "XYZ"

    # If the shape is not a city but a district, display the city name in addition to the district
    if city_name != shape_name:
        (shape_name, shape_id) = __concat_city_district(shape_name, shape_id, city_name)

    shape_json = __edit_shape(overpass.geojsonify(smallest_shape), shape_name, shape_id)
    shape_json = __edit_json(shape_json)

    return (shape_json, city_name)

def build_heatmap(dataset):
    """Builds a heatmap for the given city."""
    full_shape = ''
    district_names = [element['Stadtteil'] for element in dataset]
    #city = __get_city(dataset)
    city, city_id = overpass.get_city_for_districts(district_names)
    result = {}

    # Get all districts covered by this city
    districts = overpass.get_districts_for_city_id(city_id)

    # Find the correct area level, which is the most occurring
    for district in districts:
        level = district["tags"]["admin_level"]
        result[level] = result.get(level, 0) + 1

    area_levels = max(result, key=result.get)

    # Find the right districts with their name and id
    shortened_names = __get_shortened_names({district["tags"]["name"] for district in districts})

    for district in districts:
        area_id = district["id"]
        name = district["tags"]['name']
        district_id = shortened_names[name]
        level = district["tags"]["admin_level"]
        if level == area_levels:
            shape = overpass.geojsonify(district)
            json = __edit_shape(shape, name, district_id)
            # Append the districts JSON data
            full_shape = full_shape + json

    # Final formatting to JSON data to fit visualization requirements
    shape_json = __edit_json(full_shape)

    return (shape_json, city)

def __get_shortened_names(names, tag_length=2):

    def find_duplicates(sn):
        occurrences = {}
        for key in sn:
            if sn[key] in occurrences:
                occurrences[sn[key]].append(key)
            else:
                occurrences[sn[key]] = [key]
        duplicates = set()
        for o in occurrences:
            if len(occurrences[o]) > 1:
                duplicates.update(occurrences[o])
        return duplicates

    shortened_names = {}
    for name in names:
        shortened = ""
        splitted = resplit("([\-, ])",name)
        segment_count = len(splitted)
        remaining_length_total = max(tag_length, segment_count)
        for segment in splitted:
            segment_length = min(ceil(tag_length / segment_count), remaining_length_total, len(segment))
            shortened += segment[0:segment_length]
            remaining_length_total -= segment_length
        shortened_names[name] = shortened.upper()
    # If the length of the set of shortened names is equal to the length of unique names, that means every unique name has a unique shortened version mapped
    duplicates = find_duplicates(shortened_names)
    while duplicates:
        shortened_names.update(__get_shortened_names(duplicates, tag_length=tag_length+1))
        duplicates = find_duplicates(shortened_names)
    return shortened_names

def __edit_shape(shape, name, name_id):
    """Edit Shape data to fit visualization requirements.

    Add its name and id to the properties."""
    shape_str = str(shape)
    shape_str = shape_str.replace("'", '"')
    # Append this to Shape string for it to be readable by d3.json() method
    new_str = '{"type":"Feature","properties":{"name":"' + name + '", "id":"' + name_id + '"},"geometry":' + shape_str + '},'
    return new_str

def __edit_json(json):
    """Edit JSON data to fit visualization requirements."""
    json_str = str(json)
    # Remove comma after last element of shape string
    json_str = json_str[:-1]
    # Append this to JSON string for it to be readable by d3.json() method
    new_str = '{"type":"FeatureCollection","features":[' + json_str + ']}'
    return new_str

def __concat_city_district(district, district_id, city):
    """Combines city and district names and ids."""
    city_id = 'XXX'

    name = city + ' ' + district
    id_ = city_id + ' ' + district_id
    
    return (name, id_)