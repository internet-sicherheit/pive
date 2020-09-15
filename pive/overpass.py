import requests
from time import sleep
import json
import csv

API_URL = 'http://overpass-api.de/api/interpreter'

def execute_query(query, api_url=API_URL, output_format="json"):
    response = requests.post(api_url, data=query)
    if response.status_code != 200:
        pass
    try:
        if output_format:
            if output_format == "json":
                data = response.json()
            elif output_format == "csv":
                data = csv.DictReader(response.content.decode('utf-8').splitlines(), delimiter='\t')
            else:
                raise ValueError("Unsupported format")
        else:
            data = response.content
    except:
        sleep(5)
        response = requests.post(api_url, data=query)
        if output_format:
            if output_format == "json":
                data = response.json()
            elif output_format == "csv":
                data = csv.reader(response.content.decode('utf-8').splitlines(), delimiter='\t')
            else:
                raise ValueError("Unsupported format")
        else:
            data = response.content
    return data

def get_shape_at_point(lat, lon, admin_level):

    overpass_query = """
[out:json];
is_in({}, {}) -> .a;
area.a["boundary"="administrative"]["admin_level"={}]->.b;
rel(pivot.b);
out geom;
    """.format(lat, lon, admin_level)
    return execute_query(overpass_query)["elements"]

def get_common_shapes(coord_pair_list):
    debug_query = """
[out:csv(::id, name, ::count)];
() -> .empty;
is_in({}, {}) -> .smallest_common_area;""".format(coord_pair_list[0][0],coord_pair_list[0][1])
    overpass_query = """
[out:json];
() -> .empty;
is_in({}, {}) -> .smallest_common_area;""".format(coord_pair_list[0][0],coord_pair_list[0][1])
    for coord_pair in coord_pair_list[1:]:
        overpass_query += """
is_in({}, {}) -> .new_areas;
area.smallest_common_area.new_areas -> .smallest_common_area;""".format(coord_pair[0],coord_pair[1])
        debug_query += """
 is_in({}, {}) -> .new_area;
 area.new_area.smallest_common_area -> .smallest_common_area;
.smallest_common_area -> ._;
out;
out count;""".format(coord_pair[0],coord_pair[1])
    overpass_query += """
rel(pivot.smallest_common_area)["boundary"="administrative"];
out geom;"""
    return execute_query(overpass_query)["elements"]

def get_city_candidates_for_district(district_name):
    # TODO: Create a single-call version that outputs cheaper CSV
    # TODO: Get admin_level for city depending on which country this is in
    query = f"""[out:json];
rel["name"="{district_name}"]["boundary"="administrative"] -> .a;
.a > -> .a;
node.a -> .a;
.a is_in -> .a;
rel(pivot.a)["boundary"="administrative"]["admin_level"=6];
out center;"""
    return execute_query(query)["elements"]

def get_city_candidates_for_districts(districts):
    # TODO: Create a single-call version that outputs cheaper CSV
    # TODO: Get admin_level for city depending on which country this is in
    query = f"""[out:csv(name, ::id, ::lat, ::lon)];
"""
    for district_name in districts:
        query += f"""rel["name"="{district_name}"]["boundary"="administrative"] -> .a;
.a > -> .a;
node.a -> .a;
.a is_in -> .a;
rel(pivot.a)["boundary"="administrative"]["admin_level"=6];
out center;"""
    return execute_query(query, output_format="csv")

def get_common_city(districts):
    # TODO: Create a single-call version that outputs cheaper CSV
    # TODO: Get admin_level for city depending on which country this is in
    query = f"""[out:csv(name, ::id, ::lat, ::lon)];
rel["name"="{districts[0]}"]["boundary"="administrative"] -> .a;
.a > -> .a;
node.a -> .a;
.a is_in -> .a;
rel(pivot.a)["boundary"="administrative"]["admin_level"=6] -> .collected;
out center;
"""
    for district_name in districts[1:]:
        query += f"""rel["name"="{district_name}"]["boundary"="administrative"] -> .a;
.a > -> .a;
node.a -> .a;
.a is_in -> .a;
rel.collected(pivot.a)["boundary"="administrative"]["admin_level"=6] -> .collected;
out center;"""
    return execute_query(query, output_format="csv")

def get_city_for_districts(district_names):
    #TODO: Expensive, there has to be a cheaper call
    candidate_count = {}
    result = get_city_candidates_for_districts(district_names)
    for line in result:
        city_id = (line["name"], int(line["@id"]))
        candidate_count[city_id] = candidate_count.get(city_id, 0) + 1
    city = max(candidate_count, key=candidate_count.get)
    return city

def get_districts_for_city_id(city_id):
    # TODO: Get admin_level for district depending on which country this is in
    query = f"""[out:json];
area(id:{city_id + 3600000000}) -> .a;
rel(area.a)["boundary"="administrative"]["admin_level"=10];
out geom;"""
    return execute_query(query)["elements"]

def get_city_shape_at_point(lat, lon):
    #TODO: Get admin_level for city depending on which country this is in
    return get_shape_at_point(lat, lon, 6)

def get_district_shape_at_point(lat, lon):
    #TODO: Get admin_level for district depending on which country this is in
    return get_shape_at_point(lat, lon, 10)

def geojsonify(shape):
    coordinates = []
    for member in shape['members']:
        coordinate_entry = []
        if member['type'] == 'way':
            for point in member['geometry']:
                coordinate_entry.append([point['lon'], point['lat']])
            coordinates.append(coordinate_entry)
    coordinates = reorder_segments(coordinates)
    if len(coordinates) == 1:
        geojson_object = {'type': 'Polygon'}
        geojson_object['coordinates'] = coordinates[0]
    else:
        geojson_object = {'type': 'MultiPolygon'}
        geojson_object['coordinates'] = coordinates
    return geojson_object

def reorder_segments(coordinates):
    reordered_segments = []
    current_polygon = [coordinates.pop(0)]
    first_point = current_polygon[0][0]
    while coordinates:
        last_point = current_polygon[-1][-1]
        if last_point == first_point:
            found_next_segment = True
            current_polygon = flatten_coordinates(current_polygon)
            if not is_clockwise(current_polygon):
                current_polygon.reverse()
            reordered_segments.append([current_polygon])
            # reset current polygon
            current_polygon = [coordinates.pop(0)]
            first_point = current_polygon[0][0]
            last_point = current_polygon[-1][-1]
        found_next_segment = False
        for (index, segment) in zip(range(len(coordinates)), coordinates):
            if segment[0] == last_point:
                #Next segment found, append to output, remove from input, break out of foreach an continue search
                found_next_segment = True
                current_polygon.append(segment)
                coordinates.pop(index)
                break
            elif segment[-1] == last_point:
                # Next segment found, but in reversed order, append to output, remove from input, break out of foreach an continue search
                found_next_segment = True
                segment.reverse()
                current_polygon.append(segment)
                coordinates.pop(index)
                break
        if not found_next_segment:
            raise ValueError('Missing Segments')
    current_polygon = flatten_coordinates(current_polygon)
    if is_clockwise(current_polygon):
        current_polygon.reverse()
    reordered_segments.append([current_polygon])
    return reordered_segments

def flatten_coordinates(coordinates):
    flattened = []
    for segment in coordinates:
        for point in segment:
            flattened.append(point)
    return flattened

def is_clockwise(polygon):
    summed_orientation = 0
    for index in range(len(polygon)):
        p1 = polygon[index]
        p2 = polygon[(index+1)%len(polygon)]
        summed_orientation += (p2[0]-p1[0])*(p2[1]-p1[1])
    return summed_orientation > 0.0