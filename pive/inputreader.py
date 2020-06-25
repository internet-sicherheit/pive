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

import json
import csv
from collections import OrderedDict


def load_input_source(input_source):
    """Load data from an arbitrary input source. Currently supported:
	JSON, JSON-String, CSV, CSV-String. Returns an empty list if no data
	is available."""
    input_data = None
    try:
        input_data = load_json_from_file(input_source)
    except ValueError as e:
        pass
    except IOError as e:
        pass
    except Exception as e:
        pass
    else:
        return input_data
    if not input_data:
        try:
            input_data = load_json_string(input_source)
        except AttributeError as e:
            pass
        except ValueError as e:
            pass
        except Exception as e:
            pass
    if not input_data:
        try:
            input_data = load_csv_from_file(input_source)
        except csv.Error as e:
            pass
        except IOError as e:
            pass
        except Exception as e:
            pass
    if not input_data:
        try:
            input_data = load_csv_string(input_source)
        except Exception as e:
            pass
    return input_data

def load_json_from_file(json_input):
    """Load a JSON File."""
    with open(json_input, 'r') as fp:
        inpt = json.load(fp)
        return parse_json_to_internal(inpt)


def load_json_string(json_input):
    """Load a JSON-String."""
    inpt = json.loads(json_input)
    return parse_json_to_internal(inpt)


def load_csv_string(csv_input):
    """Load a CSV-String."""
    inputstring = csv_input.split('\n')
    data = []
    dialect = csv.Sniffer().sniff(csv_input[:4096])
    delimiterchar = dialect.delimiter
    inputdata = csv.DictReader(inputstring)
    header = inputdata.fieldnames

    for row in inputdata:
        od = OrderedDict()

        for item in header:
            value = parse_value_type(row[item])
            od[item] = value
        data.append(od)

    return data


def load_csv_from_file(csv_input):
    """Loads the input from a csv file and returns
	a list of ordered dictionaries for further processing."""
    data = []
    with open(csv_input) as csvfile:
        csvfile.seek(0)
        dialect = csv.Sniffer().sniff(csvfile.read(4096))
        csvfile.seek(0)
        isHeader = csv.Sniffer().has_header(csvfile.read(4096))
        csvfile.seek(0)
        # The delimiter used in the dialect.
        delimiterchar = dialect.delimiter
        # Opens the input file with the determined delimiter.
        dictreader = csv.DictReader(csvfile, dialect=dialect)

        header = dictreader.fieldnames

        #Translate the data into a list of dictionaries.
        for row in dictreader:

            ordered_data = OrderedDict()
            for item in header:
                value = parse_value_type(row[item])

                ordered_data[item] = value

            data.append(ordered_data)
        return data


def parse_value_type(value):
    if is_int(value):
        value = int(value)
    elif is_float(value):
        value = float(value)
    return value


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

def parse_json_to_internal(json_element):

    def name_gen(length):
        index = 0
        while index < length:
            if index == 0:
                yield 'x'
            elif index == 1:
                yield 'y'
            elif index == 2:
                yield 'z'
            else:
                yield 'a' + str(index-3)
            index += 1


    data = []

    #check if there is an order tag
    if type(json_element) == dict:
        if json_element.get("order"):
            for datapoint in json_element["data"]:
                if len(datapoint) != len(json_element["order"]):
                    raise ValueError("Length mismatch between datapoint and order")
                internal_datapoint = OrderedDict()
                for k,v in zip(json_element["order"],datapoint):
                    internal_datapoint[k] = v
                data.append(internal_datapoint)
        else:
            raise ValueError("Root JSON Element is an object, but has no order metadata")
    #Otherwise the element should be a list
    elif type(json_element) == list:
        #If no input data exists we dont need to do anything further
        if len(json_element) != 0:
            first = json_element[0]
            if type(first) == list:
                if len(first) != 0:
                    if type(first[0]) == dict and len(first[0].keys()) == 1:
                        #if length other than 1 assume complex object
                        #KV-Pairs available
                        for datapoint in json_element:
                            internal_datapoint = OrderedDict()
                            for datum in datapoint:
                                internal_datapoint[list(datum.keys())[0]] = list(datum.values())[0]
                            data.append(internal_datapoint)
                    else:
                        for datapoint in json_element:
                            internal_datapoint = OrderedDict()
                            for k,v in zip(name_gen(len(datapoint)),datapoint):
                                internal_datapoint[k] = v
                            data.append(internal_datapoint)

            else:
                raise ValueError("Expected a list of coordinates")

    else:
        raise ValueError("Unsupported format")
    return data

