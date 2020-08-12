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

import jinja2
import os
import json
from pive.visualization import defaults as default
from pive.visualization import basevisualization as bv
from pyveplot import Hiveplot, Axis, Node
import networkx as nx
import random
import json
import math

class Chart(bv.BaseVisualization):
    def __init__(self,
                 dataset,
                 template_name,
                 width=default.width,
                 height=default.height):

        # Initializing the inherited pseudo-interfaces.
        bv.BaseVisualization.__init__(self)

        # Metadata
        self._title = 'hiveplot'
        self.__template_name = 'hiveplot'
        self.__dataset = dataset
        realpath = os.path.dirname(os.path.realpath(__file__))
        self.__template_url = '%s%s' % (realpath, default.template_path)
        self.__datakeys = []
        self.__version = default.p_version

        # Visualization properties.
        self.__width = width
        self.__height = height
        self.__colors = default.chartcolors
        self.__label_size = default.label_size

        #Axis properties.
        self.__shape_rendering = default.shape_rendering
        self.__line_stroke = default.line_stroke
        self.__font_size = default.font_size

        #Hive specific.
        self.__innerRadius = 40
        self.__outerRadius = 240

    def setDataKeys(self, datakeys):
        self.__datakeys = datakeys;



    def getTypes(self, data):
        """ checks how many different types in the dataset are available.
        Returns a list with unique types (no duplicates). """ 
        s = set()
        for i in data:
          s.add(i['TYPE'])

        l = list(s)

        #l = []
        #for i in data:
        #    src = i["source"]
        #    trg = i["target"]
        #    l.append(src["TYPE"]) # set or dict for unique counts of types.
        #    l.append(trg["TYPE"])
        return l

    def get_modifiable_template_variables(self):
        """Returns a dictionary of all template variables, that are supposed to be modifiable by the client.
        Subclasses should override this method and add their own variables.
        """

        variables = super().get_modifiable_template_variables()
        variables["t_innerRadius"] = self.__innerRadius
        variables["t_outerRadius"] = self.__outerRadius
        return variables

    def get_modifiable_template_variables_typehints(self):
        """Returns a dictionary of typehints for variables that are modifiable by the client.
        Subclasses should override this method and add their own variables.
        """
        typehints = super().get_modifiable_template_variables_typehints();
        new_typehints = {
            "default" : {
                "t_innerRadius": {
                    "type": "int",
                    "min": 1
                },
                "t_outerRadius": {
                    "type": "int",
                    "min": 1
                }
            }
        }
        for key in new_typehints.keys():
            if key not in typehints.keys():
                typehints[key] = {}
            typehints[key].update(new_typehints[key])
        return typehints


    def findNode(self, linkID, data):
        """ Finds a node by ID to get access to its WEIGHT.
        Returns a hive conform format. """
        n = {}
        for i in data:
            if i['ID'] == linkID:
                n = {'TYPE':self.getNumberForType(i['TYPE']), 'WEIGHT':i['WEIGHT']}
        return n


    def createLinks(self, data):
        """ One Datapoints has often diverse LINKS. 
        Returns a hive confom format for source and target links by ID. """
        l = []
        for i in data:
            lIDsrc = i["source"]
            lIDtrg = i["target"]
            trg = self.findNode(lIDtrg["ID"], data)
            src = self.findNode(lIDsrc["ID"], data)
            l.append({'source':src, 'target':trg}) # maybe errorsource
        return l


    def generate_visualization_dataset(self, dataset):
        """ Maybe then error will be appeared,
         could be a problem at reading json.  """
        #nodes = data
        #links = self.createLinks(dataset)
        types = self.getTypes(dataset)
        typeRange = len(types)

        return dataset#, types, typeRange # look at that

    @staticmethod
    def degrees(radians):
        """ Returns degrees of radians. """
        return radians / math.PI * 180 - 90

    @staticmethod
    def getNumberForType(type):
        """ Return the index of the type because hive can only handle numbers as type. """
        t = ['A', 'B', 'C', 'D', 'E']
        return t.index(type) + 1


    def create_html(self, template):
        templateVars = {'t_title': self._title,
                        't_div_hook': self._div_hook}

        outputText = template.render(templateVars)
        return outputText


    def create_js(self, template, dataset_url):
        templateVars = {'t_width': self.__width,
                        't_height': self.__height,
                        't_url': dataset_url,
                        't_colors': self.__colors,
                        't_div_hook': self._div_hook,
                        't_font_size': self.__font_size,
                        't_shape_rendering': self.__shape_rendering,
                        't_line_stroke': self.__line_stroke,
                        't_pive_version' : self.__version,
                        't_axis_label_size' : self.__label_size}

        outputText = template.render(templateVars)
        return outputText

    def load_from_dict(self, dictionary):
        super().load_from_dict(dictionary)
        self.__innerRadius = dictionary["t_innerRadius"]
        self.__outerRadius = dictionary["t_outerRadius"]
