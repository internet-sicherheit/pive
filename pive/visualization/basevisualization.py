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
from . import defaults as default
from abc import ABCMeta, abstractmethod
import json
import jinja2
import jinja2.ext
from jinja2.lexer import Token, TOKEN_VARIABLE_END, TOKEN_VARIABLE_BEGIN, TOKEN_PIPE, TOKEN_NAME, TOKEN_LBRACKET, TOKEN_RBRACKET
from functools import reduce

from pathlib import Path

class BaseVisualization:
    __metaclass__ = ABCMeta
    implErrorMessage = 'Function not yet implemented.'

    def __init__(self):
        self._div_hook = default.div_hook
        self._template_url = ''
        self._static_url = Path(__file__).resolve().parent.joinpath(default.static_path)

        self._html_template = Path(__file__).resolve().parent.joinpath(default.template_path, "html.jinja")
        self._template_name = ''
        self._dataset_url = ''
        self._dataset = []
        self._title = ''
        self._colors = []
        self._config_url = None
        # Protected members that should not end up in the config file
        self._config_blacklist = ['_config_blacklist', '_template_url', '_static_url', '_dataset']

        self._shape_rendering = default.shape_rendering
        self._line_stroke = default.line_stroke
        self._font_size = default.font_size
        self._label_size = default.label_size
        self._padding = default.padding

    def set_div_hook(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook = div_hook

    def get_js_code(self):
        js_template = self.load_js_template(Path(self._template_url).joinpath('%s.jinja' % self._template_name))
        js = self.create_js(js_template, self._dataset_url)
        return js

    def get_json_dataset(self):
        return self.generate_visualization_dataset(self._dataset)

    def set_title(self, title):
        assert isinstance(title, str)
        self._title = title

    def set_html_template(self, file_path):
        self._html_template = Path(file_path)

    def set_labels(self, labels):
        raise NotImplementedError(self.implErrorMessage)

    def set_dataset(self, dataset):
        raise NotImplementedError(self.implErrorMessage)

    def set_dataset_url(self, dataset_url):
        assert (isinstance(dataset_url, str) or isinstance(dataset_url, Path))
        self._dataset_url = Path(dataset_url)

    def set_chart_colors(self, colors):
        """Basic Method."""
        self._colors = colors

    def get_persisted_data(self):
        return {'dataset': self._dataset}

    def load_persisted_data(self, data):
        pass

    @abstractmethod
    def generate_visualization_dataset(self, dataset):
        #TODO: Should this raise NotImpmenetedError?
        return


    def write_dataset_file(self, dataset, dataset_url):
        with dataset_url.open(mode='w') as output:
            json.dump(dataset, output, indent=2)
        print ('Writing: %s' % (dataset_url))

    def get_modifiable_template_variables(self):
        """Returns a dictionary of all template variables, that are supposed to be modifiable by the client.
        Subclasses should override this method and add their own variables.
        """
        return {"t_width": self._width,
                "t_height": self._height,
                "t_title": self._title,
                "t_colors": self._colors,
                "t_line_stroke": self._line_stroke,
                "t_shape_rendering": self._shape_rendering,
                "t_font_size": self._font_size,
                "t_label_size": self._label_size,
                "t_padding": self._padding
                }

    def create_config(self):
        config = {key[1:]: self.__dict__[key] for key in self.__dict__.keys() if key.startswith("_") and not key in self._config_blacklist}
        config.update(self.get_modifiable_template_variables())
        return json.dumps(config, default=lambda o: str(o))


    def get_modifiable_template_variables_typehints(self):
        """Returns a dictionary of typehints for variables that are modifiable by the client.
        Subclasses should override this method and add their own variables.
        """
        return {
            "default" : {
                "t_width" : {
                    "type" : "int",
                    "min" : 1
                },
                "t_height": {
                    "type": "int",
                    "min": 1
                },
                "t_title": {
                    "type": "string"
                },
                "t_colors": {
                    "type" : "list",
                    "length" : len(self._colors),
                    "item_type" : {
                        "type" : "color",
                        "channels" : 3
                    }
                },
                "t_line_stroke" : { #TODO: Get choices for CSS
                    "type": "selection",
                    "multi_selection" : False,
                    "choices" : ["black"]
                },
                "t_shape_rendering": {  # TODO: Get choices for CSS
                    "type": "selection",
                    "multi_selection" : False,
                    "choices": ["optimizeSpeed"]
                },
                "t_font_size": {
                    "type": "int",
                    "min": 1
                },
                "t_label_size": {
                    "type": "int",
                    "min": 1
                },
                "t_padding": {
                    "type": "int",
                    "min": 1
                }
            }
        }

    def create_html(self, template):
        if not self._config_url:
            self._config_url = f"{self._title}_config.json"

        templateVars = { "t" + key:self.__dict__[key] for key in self.__dict__.keys() if key.startswith("_") }
        templateVars.update(self.get_modifiable_template_variables())
        # Add dictionaries of user modifiable variables
        templateVars.update({'i_variables': self.get_modifiable_template_variables(),
                             'i_typehints': self.get_modifiable_template_variables_typehints()
                             })
        outputText = template.render(templateVars)
        return outputText

    @abstractmethod
    def create_js(self, template, dataset_url):
        return

    def write_file(self, output, destination_folder, filename):

        dest_path = destination_folder.joinpath(filename)

        if not destination_folder.exists():
            print ("Folder does not exist. Creating folder '%s'. " % destination_folder)
            destination_folder.mkdir(parents=True)

        with dest_path.open(mode='w') as f:
            print ('Writing: %s' % dest_path)
            for line in output:
                f.write(line)

    def create_visualization_files(self):

        rendered_data = {}
        rendered_data[f'{self._title}_config.json'] = self.create_config()
        html_template = self.load_html_template(self._html_template)
        rendered_data[f'{self._title}.html'] = self.create_html(html_template)
        with open(self._static_url.joinpath('%s.js' % self._template_name), mode="r") as js_file:
            rendered_data[f'{self._title}.js'] = js_file.read()
        rendered_data[f'{self._title}.json'] = json.dumps(self.generate_visualization_dataset(self._dataset))
        rendered_data[f'{self._title}_persisted.json'] = json.dumps(self.get_persisted_data())
        return rendered_data


    def set_height(self, height):
        """Basic method for height driven data."""
        if not isinstance(height, int):
            raise ValueError("Integer expected, got %s instead." % (type(height)))
        if (height <= 0):
            print ("Warning: Negative or zero height parameter. Using default settings instead.")
            height = default.height
        self._height = height

    def set_width(self, width):
        """Basic method for width driven data."""
        if not isinstance(width, int):
            raise ValueError("Integer expected, got %s instead." % (type(width)))
        if (width <= 0):
            print ("Warning: Negative or zero width parameter. Using default settings instead.")
            width = default.width
        self._width = width

    def set_dimension(self, width, height):
        self.set_width(width)
        self.set_height(height)

    def load_html_template(self, template_url):
        path = template_url.resolve().parent
        template_loader = jinja2.FileSystemLoader(searchpath=[path, './'])
        template_env = jinja2.Environment(loader=template_loader, autoescape=True)
        return self.load_template(template_env, template_url)

    def load_js_template(self, template_url):
        _js_escapes = {
            '\\': '\\u005C',
            '\'': '\\u0027',
            '"': '\\u0022',
            '>': '\\u003E',
            '<': '\\u003C',
            '&': '\\u0026',
            '=': '\\u003D',
            '-': '\\u002D',
            ';': '\\u003B',
            u'\u2028': '\\u2028',
            u'\u2029': '\\u2029'
        }
        # Escape every ASCII character with a value less than 32.
        _js_escapes.update(('%c' % z, '\\u%04X' % z) for z in range(32))

        def jinja2_escapejs_filter(value):
            if type(value) == str:
                retval = []
                for letter in value:
                    if letter in _js_escapes:
                        retval.append(_js_escapes[letter])
                    else:
                        retval.append(letter)
            else:
                return jinja2.Markup(value)

            return jinja2.Markup("".join(retval))

        def jinja2_stringify_filter(value):
            if type(value) != str:
                value = str(value)
            if len(value) < 2 or not (value[0] == '\'' and value[-1] == '\'' or value[0] == '\"' and value[-1] == '\"'):
                value = "'{}'".format(value)
            return jinja2.Markup(value)

        path = template_url.resolve().parent
        template_loader = jinja2.FileSystemLoader(searchpath=[path, './'])
        template_env = jinja2.Environment(loader=template_loader, extensions=(JSAutoescape,), autoescape=True)
        template_env.filters['escapejs'] = jinja2_escapejs_filter
        template_env.filters['stringify'] = jinja2_stringify_filter
        return self.load_template(template_env, template_url)

    def load_template(self, environment, template_url):
        filename = template_url.name
        return environment.get_template(filename)

    def set_css(self, line_stroke, shape_rendering, font_size, axis_label_size):
        self._line_stroke = line_stroke
        self._shape_rendering = shape_rendering
        self._font_size = font_size
        self._label_size = axis_label_size

    def load_from_dict(self, dictionary):
        """Load configuration values from a dictionaries.
        No value is mandatory. In case of missing values current values or default values are valid options.
        Implementations must only read values they declared in get_modifiable_template_variables.
        Implementations should check for all values they declared in get_modifiable_template_variables."""

        self.set_dimension(int(dictionary.get('t_width', self._width)), int(dictionary.get('t_height', self._height)))
        self.set_title(dictionary.get('t_title', self._title))
        if 't_colors' in dictionary:
            self.set_chart_colors(json.loads(dictionary['t_colors'].replace('\'', '\"')))
        self.set_css(dictionary.get('t_line_stroke',self._line_stroke),
                     dictionary.get('t_shape_rendering',self._shape_rendering),
                     dictionary.get('t_font_size', self._font_size),
                     dictionary.get('t_label_size', self._label_size)
                     )
        if "t_padding" in dictionary:
            self._padding = int(dictionary['t_padding'])


class JSAutoescape(jinja2.ext.Extension):
    def filter_stream(self, stream):
        tokens = []
        autoescape = self.environment.autoescape
        for token in stream:
            if len(tokens) != 0 or token.type == TOKEN_VARIABLE_BEGIN:
                tokens.append(token)
                if token.type == TOKEN_VARIABLE_END:
                    block_is_safe = reduce(
                        lambda reduced, element: reduced or element.type == TOKEN_NAME and element.value == 'safe',
                        tokens, False)
                    encountered_named = False
                    for t, index in zip(tokens, range(len(tokens))):
                        if t.type == TOKEN_NAME and t.value == 'e':
                            # Yield escape code
                            # TODO: Parametrize, maybe with decorator?
                            yield Token(token.lineno, TOKEN_NAME, 'escapejs')
                        elif autoescape and not block_is_safe and not encountered_named and (t.type == TOKEN_NAME or t.type == TOKEN_RBRACKET) and (tokens[index+1].type != TOKEN_LBRACKET):
                            encountered_named = True
                            # Yield original token
                            yield t
                            # Yield escape code
                            # TODO: Parametrize, maybe with decorator?
                            yield Token(token.lineno, TOKEN_PIPE, '|')
                            yield Token(token.lineno, TOKEN_NAME, 'escapejs')
                            # Mark as safe to avoid double escaping
                            yield Token(token.lineno, TOKEN_PIPE, '|')
                            yield Token(token.lineno, TOKEN_NAME, 'safe')
                        else:
                            yield t
                    # clear tokens at the end of variable
                    tokens = []
            else:
                # Directly yield all tokens outside of a variable
                yield token
