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


class MapVisualization(object):
    IMPL_ERROR_MESSAGE = 'Method required and needs to be implemented.'

    def __init__(self):
        self._div_hook_map = default.div_hook_map
        self._div_hook_legend = default.div_hook_legend
        self._div_hook_tooltip = default.div_hook_tooltip

    def set_div_hook_map(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook_map = div_hook

    def set_div_hook_legend(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook_legend = div_hook

    def set_div_hook_tooltip(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook_tooltip = div_hook

    def set_title(self, title):
        assert isinstance(title, str)
        self._title = title

    def align_map_view(self, city):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def set_scales(self, scale, scale_extent):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def generate_visualization_dataset(self, dataset):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def write_dataset_file(self, dataset, destination_url, filename):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def create_html(self, template):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def create_js(self, template, dataset_url):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def write_file(self, output, destination_url, filename):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def get_js_code(self):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def get_json_dataset(self):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def create_visualization_files(self, destination_url):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def set_height(self, height):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def set_width(self, width):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def set_dimension(self, width, height):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)

    def load_template_file(self, template_url):
        raise NotImplementedError(self.IMPL_ERROR_MESSAGE)
