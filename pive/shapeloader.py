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

import requests
import geojson_rewind
import json


import pive.consistenceprofiler as profiler
import pive.reversegeocoder as geocoder

from pive.reversegeocoder import API_SHAPE

def get_all_coordinates(dataset):
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
        # Polygon
        try:
            if item['type'] == 'Polygon':
                lat = str(item['Polygon'][0][1])
                lon = str(item['Polygon'][0][0])
                if profiler.is_coordinate(lat) and profiler.is_coordinate(lon):
                    coord_pair = [lat, lon]
                    result.append(coord_pair)
        except KeyError:
            pass
            
    return result

def find_map_shape(coordinates):
    """Returns a map shape fitting every coordinate pair.
    
    Iterates through every pair of the coordinate list.
    Finds the smallest possible map shape they have in common."""
    result = []
    candidate = []
    level = '0'
    city = ''

    for pair in coordinates:
        possible = []
        lat = str(pair[0])
        lon = str(pair[1])
        # Get name of city covered by this dataset
        city = geocoder.request_location(lat, lon)
        # Only 2580 Requests at once
        shapes = geocoder.get_possible_shapes(lat, lon)
        if shapes:
            for shape in shapes:
                map_shape = tuple(shape)
                possible.append(map_shape)
            if not result:
                result = possible
            elif result != possible:
                # Only keep common shapes in the result list
                result = set(result) & set(possible)
    # The higher the area level the smaller the map shape
    for elem in result:
        area_level = elem[1]
        if area_level > level:
            level = area_level
            candidate = elem
    result = candidate

    # Get the map shape by its area id
    area_id = result[0]
    map_shape = geocoder.request_map_shape(area_id)
    # Get name and id of the shape location
    shape_name = geocoder.get_shape_name(area_id)
    shape_id = __get_id(shape_name)
    # If the shape is not a city but a district, display the city name in addition to the district
    if city != shape_name:
        (shape_name, shape_id) = __concat_city_district(shape_name, shape_id, city)

    shape_json = __edit_shape(map_shape, shape_name, shape_id)
    shape_json = __edit_json(shape_json)

    if shape_name == 'Aachen' or shape_name == 'Gelsenkirchen':
        shape_json = geojson_rewind.rewind(shape_json, False)

    return (shape_json, city)

def build_heatmap(dataset):
    """Builds a heatmap for the given city."""
    full_shape = ''
    city = __get_city(dataset)

    result = {}
    num = 0
    area_levels = ''

    # Get all districts covered by this city
    area_id = __get_area_id(city)
    districts = geocoder.get_covered_districts(area_id)

    # Find the correct area level, which is the most occurring
    for key in districts:
        level = districts[key]['type'][1:]
        result[level] = result.get(level, 0) + 1

    for key in result:
        if result[key] > num:
            num = result[key]
            area_levels = key

    # Find the right districts with their name and id
    for key in districts:
        area_id = key
        name = districts[key]['name']
        # Cut from string for Wuppertal districts
        name = name.replace('Gemarkung ', '')
        district_id = __get_id(name)
        level = districts[key]['type'][1:]
        if level == area_levels:
            shape = geocoder.request_map_shape(area_id)
            json = __edit_shape(shape, name, district_id)
            # Append the districts JSON data
            full_shape = full_shape + json

    # Final formatting to JSON data to fit visualization requirements
    shape_json = __edit_json(full_shape)

    return (shape_json, city)

def __get_city(dataset):
    """Returns the city according to the most occuring districts in a heatmap dataset."""
    # city = ''
    # num = 0
    # result = {}
    #
    # gelsenkirchen = ['Altstadt', 'Schalke', 'Schalke-Nord', 'Bismarck', 'Bulmke-Hüllen', 'Feldmark', 'Heßler',
    #                  'Buer', 'Scholven', 'Hassel', 'Horst', 'Beckhausen', 'Beckhausen-Schaffrath', 'Erle', 'Resse', 'Resser Mark',
    #                  'Neustadt', 'Ückendorf', 'Rotthausen']
    #
    # wuppertal = ['Nächstebreck', 'Barmen', 'Schöller', 'Vohwinkel', 'Elberfeld', 'Beyenburg', 'Langerfeld',
    #              'Ronsdorf', 'Cronenberg', 'Dönberg']
    #
    # aachen = ['Richterich', 'Laurensberg', 'Haaren', 'Eilendorf', 'Aachen-Mitte', 'Brand', 'Kornelimünster/Walheim']
    #
    # for elem in dataset:
    #     for key in elem:
    #         if key == 'Stadtteil':
    #             district = elem[key]
    #             if district in gelsenkirchen:
    #                 result['Gelsenkirchen'] = result.get('Gelsenkirchen', 0) + 1
    #             elif district in wuppertal:
    #                 result['Wuppertal'] = result.get('Wuppertal', 0) + 1
    #             elif district in aachen:
    #                 result['Aachen'] = result.get('Aachen', 0) + 1
    #
    # # Get the city with the highest count of districts
    # for key in result:
    #     if result[key] > num:
    #         num = result[key]
    #         city = key
    #
    # return city

    city_candidates = {}
    for elem in dataset:
        for key in elem:
            if key == 'Stadtteil':
                district = elem[key]
                # FIXME: OSM Administrative boundary level for districts is country dependant.
                # Check https://wiki.openstreetmap.org/wiki/Tag:boundary=administrative for details.
                # Defaulting to O10 for Germany
                r = requests.get("{API_SHAPE}areas/{district}?type=O10".format(API_SHAPE=API_SHAPE, district=district))
                if r.status_code == 200:
                    district_response = json.loads(r.content)
                    for district_id in district_response.keys():
                        # FIXME: OSM Administrative boundary level for cities is country dependant.
                        # Check https://wiki.openstreetmap.org/wiki/Tag:boundary=administrative for details.
                        # Defaulting to O6 for Germany
                        r = requests.get("{API_SHAPE}area/{district_id}/covered?type=O06".format(API_SHAPE=API_SHAPE, district_id=district_id))
                        if r.status_code == 200:
                            city_response = json.loads(r.content)
                            for city_id in city_response.keys():
                                name = city_response[city_id]["name"]
                                city_candidates[name] = city_candidates.get(name, 0) + 1

    city = max(city_candidates, key=city_candidates.get)
    return city


def __get_area_id(city):
    """Returns city specific area ids."""
    # FIXME: OSM Administrative boundary level for cities is country dependant.
    # Check https://wiki.openstreetmap.org/wiki/Tag:boundary=administrative for details.
    # Defaulting to O6 for Germa
    r = requests.get("{API_SHAPE}areas/{city}?type=O06".format(API_SHAPE=API_SHAPE, city=city))
    if r.status_code == 200:
        city_response = json.loads(r.content)
        for city_id in city_response.keys():
            # return first id in dict, there should be only one anyway
            return city_id

def __get_id(city):
    #FIXME: Differenciate between city and district
    """Returns an id for given cities and districts."""
    return {
        'Gelsenkirchen': 'GE',
        'Altstadt': 'AL',
        'Schalke': 'SC',
        'Schalke-Nord': 'SN',
        'Bismarck': 'BI',
        'Bulmke-Hüllen': 'BH',
        'Feldmark': 'FE',
        'Heßler': 'HE',
        'Buer': 'BU',
        'Scholven': 'SV',
        'Hassel': 'HA',
        'Horst': 'HO',
        'Beckhausen': 'BE',
        'Beckhausen-Schaffrath': 'BS',
        'Erle': 'ER',
        'Resse': 'RE',
        'Resser Mark': 'RM',
        'Neustadt': 'NE',
        'Ückendorf': 'UE',
        'Rotthausen': 'RO',

        'Aachen': 'AC',
        'Richterich': 'RI',
        'Laurensberg': 'LA',
        'Haaren': 'HA',
        'Eilendorf': 'EI',
        'Aachen-Mitte': 'AM',
        'Brand': 'BR',
        'Kornelimünster/Walheim': 'KW',

        'Wuppertal': 'WU',
        'Nächstebreck': 'NB',
        'Barmen': 'BA',
        'Schöller': 'SC',
        'Vohwinkel': 'VO',
        'Elberfeld': 'EL',
        'Beyenburg': 'BE',
        'Langerfeld': 'LA',
        'Ronsdorf': 'RO',
        'Cronenberg': 'CR',
        'Dönberg': 'DB'
    }.get(city, '')

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
    city_id = __get_id(city)

    name = city + ' ' + district
    id_ = city_id + ' ' + district_id
    
    return (name, id_)