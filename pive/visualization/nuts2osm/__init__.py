from pathlib import Path
from json import load
import re

MAPPING_PATH = Path(__file__).resolve().parent.joinpath("mappings.json")
MAPPING_DATA = load(MAPPING_PATH.open(mode="r"))

NUTS_REGEX = re.compile(r"^(NUTS-?)[1,2,3,4,5]$")
LAU_REGEX = re.compile(r"^(LAU-?)[1,2]$")

ERR_MSG_WRONG_COUNTRY = "Wrong country code or country not supported."

def parse_nuts_level(nuts_level_string):
    nuts_level_string = nuts_level_string.upper()
    if NUTS_REGEX.match(nuts_level_string):
        return int(nuts_level_string[-1])
    elif LAU_REGEX.match(nuts_level_string):
        return int(nuts_level_string[-1]) + 3
    else:
        raise ValueError("String contains neither NUTS nor LAU level")


def get_osm_levels(nuts_level, country):
    if country not in MAPPING_DATA:
        raise ValueError(ERR_MSG_WRONG_COUNTRY)
    if not 1 <= nuts_level <= 5:
        raise ValueError("Invalid NUTS level. Supported values are from 1-5.")
    return MAPPING_DATA[country][str(nuts_level)]


def get_next_best_osm_levels(nuts_level, country, ascending_level=False):
    if ascending_level:
        for level in range(nuts_level, 6):
            osm_levels = get_osm_levels(level, country)
            if osm_levels != []:
                return osm_levels
        return []
    else:
        for level in range(nuts_level, 0, -1):
            osm_levels = get_osm_levels(level, country)
            if osm_levels != []:
                return osm_levels
        # Level 2 is full country
        return [2]


def get_nuts_level(osm_level, country):
    if country not in MAPPING_DATA:
        raise ValueError(ERR_MSG_WRONG_COUNTRY)
    country_data = MAPPING_DATA[country]
    for index in range(1, 6):
        if osm_level in country_data[str(index)]:
            return index
    return None
