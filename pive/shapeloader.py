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

class Shapeloader(object):

    def __init__(self, country, endpoint):
        self.client = overpass.Client(country, endpoint)

    def find_map_shape(self, coordinates, other_names = []):
        """Returns a map shape fitting every coordinate pair.

        Iterates through every pair of the coordinate list.
        Finds the smallest possible map shape they have in common."""
        result = []
        candidate = []
        level = '0'

        common_shapes = self.client.get_common_shapes(coordinates)
        #FIXME: Hardcoded admin_level
        #FIXME: Will break if a single point is outside of the city
        city_shape = [ element for element in common_shapes if element["tags"]["admin_level"] == '6'][0]
        smallest_shape = max(common_shapes, key=lambda element: int(element["tags"]["admin_level"]))

        shape_name = smallest_shape["tags"]["name"]
        city_name = city_shape["tags"]["name"]
        shortend_names = get_shortened_names(other_names + [shape_name, city_name])

        features = []
        if city_name != shape_name:
            features.append(create_geojson_feature(overpass.geojsonify(smallest_shape, ccw=False), shape_name, shortend_names[shape_name]))
        features.append(create_geojson_feature(overpass.geojsonify(city_shape, ccw=False), city_name, shortend_names[city_name]))
        shape_json = add_geojson_header(features)

        return (shape_json, city_name, shortend_names)

    def build_heatmap(self, dataset):
        """Builds a heatmap for the given city."""

        district_names = [element['Stadtteil'] for element in dataset]
        city, city_id = self.client.get_city_for_districts(district_names)
        districts = self.client.get_districts_for_city_id(city_id)
        shortened_names = get_shortened_names({district["tags"]["name"] for district in districts})

        features = []
        for district in districts:
            name = district["tags"]['name']
            if name in district_names:
                shape = overpass.geojsonify(district, ccw=False)
                features.append(create_geojson_feature(shape, name, shortened_names[name]))

        shape = add_geojson_header(features)

        return (shape, city)

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

def get_shortened_names(names, tag_length=2):
    """Search for shortest possible abbreviation of a list of names
    by iterative deepening of allowed abbreviation length"""

    def find_duplicates(sn):
        """Get all names, that are still not resolved to a unique abbreviation by testing for bijective mapping"""
        occurrences = {}
        #For all abbreviation, create a mapping from abbreviation to unabbreviated names
        for key in sn:
            if sn[key] in occurrences:
                occurrences[sn[key]].append(key)
            else:
                occurrences[sn[key]] = [key]
        duplicates = set()
        # For all abbreviations, search for abbreviations that map to more than 1 unabbreviated name
        for o in occurrences:
            if len(occurrences[o]) > 1:
                duplicates.update(occurrences[o])
        return duplicates

    shortened_names = {}
    # Make sure that there are no duplicate names. Duplicate names should map to the same abbreviation anyway
    names = set(names)
    for name in names:
        # split names along dashes and spaces
        splitted = resplit("([\-, ])",name)
        segment_count = len(splitted)
        # shortened name needs to be at least 1 character per token
        remaining_length_total = max(tag_length, segment_count)
        segment_offset = 0
        segment_part = [""] * segment_count
        prev_remaining_length_total = None
        while remaining_length_total and prev_remaining_length_total != remaining_length_total:
            prev_remaining_length_total = remaining_length_total
            # Try to equally distribute all remaining characters over all segments by round-robin
            for index in range(len(splitted)):
                segment = splitted[index]
                # Check if there are characters left in this segment
                if len(segment) > segment_offset:
                    segment_part[index] += segment[segment_offset]
                    remaining_length_total -= 1
                    if remaining_length_total == 0:
                        # No more characters available, stop searching
                        break
            segment_offset += 1
        shortened_names[name] = "".join(segment_part)
    # Search all names without unique abbreviation
    duplicates = find_duplicates(shortened_names)
    while duplicates:
        # As long as there are conflicts keep searching recursively
        # Include previously clean names, as different segment names might cause new conflicts
        shortened_names.update(get_shortened_names(duplicates, tag_length=tag_length+1))
        duplicates = find_duplicates(shortened_names)
    return shortened_names

def create_geojson_feature(shape, name, name_id):
    """Edit Shape data to fit visualization requirements.

    Add its name and id to the properties."""

    # Append this to Shape string for it to be readable by d3.json() method

    return {"type":"Feature", "properties": {"name": name, "id": name_id}, "geometry": shape}

def add_geojson_header(feature_list):
    """Edit JSON data to fit visualization requirements."""
    return {"type": "FeatureCollection", "features": feature_list}