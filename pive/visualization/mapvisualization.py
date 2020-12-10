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
from . import mapdefaults as default
from .basevisualization import BaseVisualization
from abc import abstractmethod
from json import dumps

from pathlib import Path


class MapVisualization(BaseVisualization):
    IMPL_ERROR_MESSAGE = 'Method required and needs to be implemented.'

    def __init__(self):
        BaseVisualization.__init__(self)

        self._html_template = Path(__file__).resolve().parent.joinpath(default.template_path, "map_html.jinja")
        self._div_hook_map = default.div_hook_map
        self._div_hook_legend = default.div_hook_legend
        self._div_hook_tooltip = default.div_hook_tooltip

    #FIXME: Compatibility funtion, codebase needs to adhere to uniform naming standard
    def setDataKeys(self, datakeys):
        self.set_data_keys(datakeys)

    def set_div_hook(self, div_hook):
        self.set_div_hook_map(div_hook)

    def set_div_hook_map(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook_map = div_hook

    def set_div_hook_legend(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook_legend = div_hook

    def set_div_hook_tooltip(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook_tooltip = div_hook

    def get_shapefile_path(self, output_folder):
        return output_folder.joinpath('%s_shape.json' % self._title)

    def create_visualization_files(self):
        rendered_data = super().create_visualization_files()
        rendered_data[f'{self._title}_shape.json'] = dumps(self._shape)
        return rendered_data

    @abstractmethod
    def get_map_shape(self):
        pass

    @abstractmethod
    def set_map_data(self, data):
        pass