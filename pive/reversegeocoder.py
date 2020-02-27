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

API_LOCATE = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json"
# Request available map shapes
API_SHAPE = "https://global.mapit.mysociety.org/"
SRID = "/point/4326/"

def request_location(lat, lon):
    """Returns a location for passed latitude and longitude coordinates."""
    latLon = lat + "," + lon

    # Request location with lat and lon
    PARAMS = {'prox': latLon,
            'mode': "retrieveAddresses",
            'maxresults': "1",
            'gen': "9",
            'app_id': "51t4toTQqJlNOJhLl9os",
            'app_code': "DlLlFmiu6FNI0sJbQXQICw"}

    r = requests.get(url = API_LOCATE, params = PARAMS)
    try:
        # Location in JSON format
        data = r.json()
    except ValueError:
        print("Error " + str(r.status_code) + ": No location available for this coordinate pair.")

    result = data['Response']['View'][0]['Result']
    # Get city and district of result list
    city = result[0]['Location']['Address']['City']
    # district = result[0]['Location']['Address']['District']

    return city


def request_map_shape(area_id):
    """Returns a map shape in JSON format by searching for the area id."""
    map_data = []

    # Request map shape for this area id
    url_area_request = "{0}area/{1}.geojson".format(API_SHAPE, area_id)
    r = requests.get(url_area_request)

    try:
        # Map shape in JSON format
        map_data = r.json()
    except ValueError:
        print("Error " + str(r.status_code) + ": No Map Shapes available for this dataset.")

    return map_data


def __searchdict(d):
    """Searches data structure for area id and area level."""
    result = []
    level = '0'
    id = '0'
    for k, v in d.items():
        shape = []
        if isinstance(v, dict):
            level = v['type'][1:]
            if level.isdigit():
                id = v['id']
                shape.append(id)
                shape.append(level)
        if shape:
            result.append(shape)


    return result

def get_possible_shapes(lat, lon):
    """Returns data of all map shapes covering passed latitude and longitude coordinates."""
    result = []
    data = []

    request_url = API_SHAPE + SRID + lon + "," + lat
    r = requests.get(request_url)

    try:
        data = r.json()
    except ValueError:
        print("Error " + str(r.status_code) + ": No Map Shapes available for this coordinate pair.")

    # Store all area ids and area levels for result list
    if data:
        result = __searchdict(data)

    return result

def get_covered_districts(area_id):
    """Returns covered districts in JSON format by searching for the area id."""
    map_data = []

    # Request discricts covered by this area id
    url_area_request = "{0}area/{1}/covers".format(API_SHAPE, area_id)
    r = requests.get(url_area_request)

    try:
        # All districts in JSON format
        map_data = r.json()
    except ValueError:
        print("Error " + str(r.status_code) + ": No Map Shapes available for this dataset.")

    return map_data

def get_shape_name(area_id):
    """Returns name of the city or district where the shape is located in."""
    name = ""

    # Request area of the shape
    url_area_request = "{0}area/{1}".format(API_SHAPE, area_id)
    r = requests.get(url_area_request)

    try:
        # Area in JSON format
        map_data = r.json()
    except ValueError:
        print("Error " + str(r.status_code))

    # Read shape name out of the JSON
    name = map_data['all_names']['default'][1]

    return name