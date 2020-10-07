import requests
from time import sleep
import csv
import pive.visualization.nuts2osm as nuts2osm

API_URL = 'http://overpass-api.de/api/interpreter'

class Client(object):

    def __init__(self, country, endpoint=API_URL):
        self.country = country
        self.endpoint = endpoint

    def execute_query(self, query, output_format="json"):
        """Executes a query against the an Overpass and parses the result."""

        response = requests.post(self.endpoint, data=query)
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
            # Workaround, if any error happens, retry.
            # Rate-Limit returns 200 too, so it cannot easily be discerned from regular payload
            sleep(5)
            response = requests.post(self.endpoint, data=query)
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


    def get_shape_at_point(self, lat, lon, admin_level):
        """Returns a shape of and administrative boundary at a specified point in OSMs format."""

        """Set up output as JSON
        Get all areas at point (Lat,Lon)
        Filter for the area that matches the administrative boundary of level admin_level
        Get the relation of the filtered area and return its shape"""

        overpass_query = """
    [out:json];
    is_in({}, {}) -> .a;
    area.a["boundary"="administrative"]["admin_level"={}]->.b;
    rel(pivot.b);
    out geom;
        """.format(lat, lon, admin_level)
        return self.execute_query(overpass_query)["elements"]


    def get_common_shapes(self, coord_pair_list):
        """Get all shapes of administrative boundaries that have all passed coordinates in common."""

        """Set up output as JSON
        Get the areas of the first point in the list and save it to smallest_common_area
        For every other point in the list:
            Get the areas of the point and save it to new_areas
            Save the intersection of new_areas and smallest_common_area to smallest_common_area
        Get the relations of areas covered in smallest_common_area, filter for administrative boundaries and return their shapes
        """
        overpass_query = """
    [out:json];
    is_in({}, {}) -> .smallest_common_area;""".format(coord_pair_list[0][0], coord_pair_list[0][1])
        for coord_pair in coord_pair_list[1:]:
            overpass_query += """
    is_in({}, {}) -> .new_areas;
    area.smallest_common_area.new_areas -> .smallest_common_area;""".format(coord_pair[0], coord_pair[1])

        overpass_query += """
    rel(pivot.smallest_common_area)["boundary"="administrative"];
    out geom;"""
        return self.execute_query(overpass_query)["elements"]


    def get_city_candidates_for_district(self, district_name):
        """Get a list of cities that have a district with the given name."""

        # TODO: Create a single-call version that outputs cheaper CSV
        # TODO: Get admin_level for city depending on which country this is in

        """Set output to JSON
        Get the relation of the administrative boundary with the name (district_name) and save it to a
        Recurse down those relations and save the result in a
        Filter for nodes in a and save those in a (Remove everything from a thats not a node object)
        Get all areas that the nodes in a are in and save them to a
        Get all relations covered by the areas in a, filter for administrative boundaries of type city/county and return the center of those shapes"""

        admin_levels = nuts2osm.get_next_best_osm_levels(3, self.country, False)
        query = f"""[out:json];
rel["name"="{district_name}"]["boundary"="administrative"] -> .a;
.a > -> .a;
node.a -> .a;
.a is_in -> .a;
("""
        for admin_level in admin_levels:
             query += f"""rel(pivot.a)["boundary"="administrative"]["admin_level"={admin_level}];
"""
        query += """);
out center;"""
        return self.execute_query(query)["elements"]


    def get_city_candidates_for_districts(self, districts):
        """Get city candidates for a list of districts.
        The more often a city occurs in the returned list, the more likely it is to be the sought after city."""

        # TODO: Create a single-call version that outputs cheaper CSV
        # TODO: Get admin_level for city depending on which country this is in

        """Set output to CSV
        For each district
            Get the relation of the administrative boundary of the district and save it to a
            Recurse down those relations and save the result in a
            Filter for nodes in a and save those in a (Remove everything from a thats not a node object)
            Get all areas that the nodes in a are in and save them to a
            Get all relations covered by the areas in a, filter for administrative boundaries of type city/county and return the center of those shapes
    """

        admin_levels = nuts2osm.get_next_best_osm_levels(3, self.country, False)
        query = f"""[out:csv(name, ::id, ::lat, ::lon)];
"""
        for district_name in districts:
            query += f"""rel["name"="{district_name}"]["boundary"="administrative"] -> .a;
.a > -> .a;
node.a -> .a;
.a is_in -> .a;
("""
            for admin_level in admin_levels:
                 query += f"""rel(pivot.a)["boundary"="administrative"]["admin_level"={admin_level}];
"""
            query += """);
out center;"""
        return self.execute_query(query, output_format="csv")


    def get_city_for_districts(self, district_names):
        """Get the city that best matches a list of district names."""

        candidate_count = {}
        result = self.get_city_candidates_for_districts(district_names)
        for line in result:
            # For every occurence of a city increment its count in candidate_count
            city_id = (line["name"], int(line["@id"]))
            candidate_count[city_id] = candidate_count.get(city_id, 0) + 1
        # Return the most incremented city
        city = max(candidate_count, key=candidate_count.get)
        return city


    def get_districts_for_city_id(self, city_id):
        """Get all district shapes of a city by its Overpass ID"""

        # TODO: Get admin_level for district depending on which country this is in
        """Set Set output to JSON
        Get the area of the city (Area IDs are offset by their relations by 3600000000)
        Get all relations covered by the area, filter them for districts and return their shapes
        """

        admin_levels = nuts2osm.get_next_best_osm_levels(5, self.country, False)
        query = f"""[out:json];
    area(id:{city_id + 3600000000}) -> .a;
    ("""
        for admin_level in admin_levels:
            query += f"""rel(area.a)["boundary"="administrative"]["admin_level"={admin_level}];"""
        query += """);
    out geom;"""
        return self.execute_query(query)["elements"]


    def get_city_shape_at_point(self, lat, lon):
        admin_levels = nuts2osm.get_next_best_osm_levels(3, self.country, False)
        for level in admin_levels:
            shape = self.get_shape_at_point(lat, lon, admin_levels[0])
            if shape != []:
                return shape
        raise ValueError(f"No city at this location: ({lat}/{lon})")


    def get_district_shape_at_point(self, lat, lon):
        admin_levels = nuts2osm.get_next_best_osm_levels(5, self.country, False)
        for level in admin_levels:
            shape = self.get_shape_at_point(lat, lon, admin_levels[0])
            if shape != []:
                return shape
        raise ValueError(f"No district at this location: ({lat}/{lon})")


def geojsonify(shape, ccw=True):
    """Creates a geojson object from the passed shape.
    The default for outer rings is counter-clockwise, complying with RFC7946.
    For systems that dont comply with RFC7946 ccw needs to be set to False."""

    segments = []
    for member in shape['members']:
        segment_points = []
        # TODO: Stop ignoring holes (role: inner)
        if member['type'] == 'way' and member['role'] == 'outer':
            for point in member['geometry']:
                segment_points.append([point['lon'], point['lat']])
            segments.append(segment_points)
    polygons = build_polygons(segments,ccw)
    if len(polygons) == 1:
        geojson_object = {'type': 'Polygon'}
        geojson_object['coordinates'] = polygons[0]
    else:
        geojson_object = {'type': 'MultiPolygon'}
        geojson_object['coordinates'] = polygons
    return geojson_object


def build_polygons(segments, ccw=True):
    """The results of the Overpass API return shapes as edge segments.
    This method takes all segments and connects them to polygons.
    Afterwards it checks if the polygon has the correct point order.
    The default for outer rings is counter-clockwise, complying with RFC7946.
    For systems that dont comply with RFC7946 ccw needs to be set to False.
    """

    polygons = []
    # Search until all segments are used up
    while segments:
        current_polygon_segments = [segments.pop(0)]
        first_point = current_polygon_segments[0][0]
        last_point = current_polygon_segments[-1][-1]

        # Search until current segments create a closed loop
        while first_point != last_point:
            found_another_segment = False
            for (index, segment) in zip(range(len(segments)), segments):
                if segment[0] == last_point:
                    # Next segment found, in the same order as the previous ones
                    _ = segments.pop(index)
                    current_polygon_segments.append(segment)
                    found_another_segment = True
                    break
                elif segment[-1] == last_point:
                    # Next segment found, in the reversed order as the previous ones
                    _ = segments.pop(index)
                    segment.reverse()
                    current_polygon_segments.append(segment)
                    found_another_segment = True
                    break

            # If no new segments could be found that match the current segment no closed loop can be formed
            if not found_another_segment:
                raise ValueError("Segments dont form a closed loop, cant construct polygon")

            # Update last point
            last_point = current_polygon_segments[-1][-1]

        # Closed loop found, flatten and make sure that winding is counter-clockwise, as clockwise winding indicates holes
        polygon = flatten_coordinates(current_polygon_segments)
        """Spherical polygons also require a winding order convention to determine which side
        of the polygon is the inside: the exterior ring for polygons smaller than a hemisphere must be clockwise,
        while the exterior ring for polygons larger than a hemisphere must be anticlockwise.
        Interior rings representing holes must use the opposite winding order of their exterior ring.
        This winding order convention is also used by TopoJSON and ESRI shapefiles;
        however, it is the opposite convention of GeoJSON’s RFC 7946.
        (Also note that standard GeoJSON WGS84 uses planar equirectangular coordinates, not spherical coordinates,
        and thus may require stitching to remove antimeridian cuts.)
        
        https://github.com/d3/d3-geo"""
        if is_clockwise(polygon):
            polygon.reverse()
        if not ccw:
            polygon.reverse()
        polygons.append([polygon])
    return polygons


def flatten_coordinates(coordinates):
    """Connect a list of line snippets to a single polygon."""

    flattened = []
    for segment in coordinates:
        for point in segment:
            flattened.append(point)
    return flattened


def is_clockwise(polygon):
    """Check if a polygons winding is clockwise. The expected input order for points is [Longitude, Latitude].
    If the input order is reversed, the result will be reversed too."""

    summed_orientation = 0
    for index in range(len(polygon)):
        p1 = polygon[index]
        p2 = polygon[(index + 1) % len(polygon)]
        summed_orientation += (p2[0] - p1[0]) * (p2[1] + p1[1])
    return summed_orientation > 0.0
