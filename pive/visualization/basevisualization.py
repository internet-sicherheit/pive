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
import os
import json
import jinja2
import jinja2.ext
from jinja2.lexer import Token, TOKEN_VARIABLE_END, TOKEN_VARIABLE_BEGIN, TOKEN_PIPE, TOKEN_NAME, TOKEN_LBRACKET, TOKEN_RBRACKET
from functools import reduce

class BaseVisualization:
    __metaclass__ = ABCMeta
    implErrorMessage = 'Function not yet implemented.'

    def __init__(self):
        self._div_hook = default.div_hook
        self._template_url = ''
        self._template_name = ''
        self._dataset_url = ''
        self.dataset = []
        self._title = ''

    def set_div_hook(self, div_hook):
        assert isinstance(div_hook, str)
        self._div_hook = div_hook

    def get_js_code(self):
        js_template = self.load_js_template('%s%s.jinja' % (self._template_url, self._template_name))
        js = self.create_js(js_template, self._dataset_url)
        return js

    def get_json_dataset(self):
        return self.generate_visualization_dataset(self._dataset)

    def set_title(self, title):
        assert isinstance(title, str)
        self._title = title

    def set_labels(self, labels):
        raise NotImplementedError(self.implErrorMessage)

    def set_dataset(self, dataset):
        raise NotImplementedError(self.implErrorMessage)

    def set_dataset_url(self, dataset_url):
        assert isinstance(dataset_url, str)
        self._dataset_url = dataset_url

    def set_chart_colors(self, colors):
        """Basic Method."""
        self._colors = colors

    @abstractmethod
    def generate_visualization_dataset(self, dataset):
        #TODO: Should this raise NotImpmenetedError?
        return


    def write_dataset_file(self, dataset, dataset_url):
        outp = open(dataset_url, 'w')
        json.dump(dataset, outp, indent=2)
        outp.close()
        print ('Writing: %s' % (dataset_url))


    def create_html(self, template):
        templateVars = {'t_title': self._title,
                        't_div_hook': self._div_hook}

        outputText = template.render(templateVars)
        return outputText

    @abstractmethod
    def create_js(self, template, dataset_url):
        return

    def write_file(self, output, destination_url, filename):

        dest_file = '%s%s' % (destination_url, filename)

        if not os.path.exists(destination_url):
            print ("Folder does not exist. Creating folder '%s'. " % (destination_url))
            os.makedirs(destination_url)

        f = open(dest_file, 'w')

        print ('Writing: %s' % (dest_file))

        for line in output:
            f.write(line)

        f.close()

    def create_visualization_files(self, destination_url):

        html_template = self.load_html_template('%shtml.jinja' % (self._template_url))
        js_template = self.load_js_template('%s%s.jinja' % (self._template_url, self._template_name))

        # Default dataset url is used when nothing was explicitly passed.
        data_output_path = destination_url + '%s%s.json' % (os.sep, self._title)


        js = self.create_js(js_template, data_output_path)
        html = self.create_html(html_template)

        self.write_file(html, destination_url, '%s%s.html' % (os.sep, self._title))
        self.write_file(js, destination_url, '%s%s.js' % (os.sep, self._title))

        visdata = self.generate_visualization_dataset(self._dataset)
        self.write_dataset_file(visdata, data_output_path)

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
        path, filename = os.path.split(template_url)
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

        path, filename = os.path.split(template_url)
        template_loader = jinja2.FileSystemLoader(searchpath=[path, './'])
        template_env = jinja2.Environment(loader=template_loader, extensions=(JSAutoescape,), autoescape=True)
        template_env.filters['escapejs'] = jinja2_escapejs_filter
        template_env.filters['stringify'] = jinja2_stringify_filter
        return self.load_template(template_env, template_url)

    def load_template(self, environment, template_url):
        path, filename = os.path.split(template_url)
        return environment.get_template(filename)


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