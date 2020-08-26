# hier wieder template Variablen anlegen
# ich brauche miene prepare() Methode
# nur für css vorbereiten
# muss nicht weggeschrieben werden in einer Datei

from pive.visualization import defaults as default
import jinja2
from jinja2 import *


class CssTemplate():
    def __init__(self,
                 div_hook,
                 line_div_hook=default.line_div_hook,
                 line_fill=default.line_fill,
                 line_stroke=default.line_stroke,
                 line_stroke_width=default.line_stroke_width,
                 tooltip_div_hook=default.tooltip_div_hook,
                 tooltip_color=default.tooltip_color,
                 tooltip_line_height=default.tooltip_line_height,
                 tooltip_padding=default.tooltip_padding,
                 tooltip_font_weight=default.tooltip_font_weight,
                 tooltip_font_family=default.tooltip_font_family,
                 tooltip_border_radius=default.tooltip_border_radius,
                 axis_path_div_hook=default.axis_path_div_hook,
                 axis_path_fill=default.axis_path_fill,
                 axis_path_shape_rendering=default.axis_path_shape_rendering,
                 axis_line_div_hook=default.axis_line_div_hook,
                 axis_line_shape_rendering=default.axis_line_shape_rendering,
                 path_area_div_hook=default.path_area_div_hook,
                 path_area_fill=default.path_area_fill,
                 axis_text_div_hook=default.axis_text_div_hook,
                 axis_text_font_family=default.axis_text_font_family,
                 axis_text_font_size=default.axis_text_font_size,
                 xlabel_text_div_hook=default.xlabel_text_div_hook,
                 xlabel_text_font_family=default.xlabel_text_font_family,
                 xlabel_text_font_size=default.xlabel_text_font_size,
                 ylabel_text_div_hook=default.ylabel_text_div_hook,
                 ylabel_text_font_family=default.ylabel_text_font_family,
                 ylabel_text_font_size=default.ylabel_text_font_size,
                 x_axis_line_div_hook=default.x_axis_line_div_hook,
                 x_axis_line_stroke=default.x_axis_line_stroke,
                 x_axis_line_stroke_opacity=default.x_axis_line_stroke_opacity,
                 x_axis_line_stroke_width=default.x_axis_line_stroke_width,
                 y_axis_line_div_hook=default.y_axis_line_div_hook,
                 y_axis_line_stroke=default.y_axis_line_stroke,
                 y_axis_line_stroke_opacity=default.y_axis_line_stroke_opacity,
                 y_axis_line_stroke_width=default.y_axis_line_stroke_width,
                 ):

        self.div_hook = div_hook
        self.line_stroke = line_stroke
        self.line_div_hook = line_div_hook
        self.line_fill = line_fill
        self.line_stroke_width = line_stroke_width
        self.tooltip_div_hook = tooltip_div_hook
        self.tooltip_color = tooltip_color
        self.tooltip_line_height = tooltip_line_height
        self.tooltip_padding = tooltip_padding
        self.tooltip_font_weight = tooltip_font_weight
        self.tooltip_font_family = tooltip_font_family
        self.tooltip_border_radius = tooltip_border_radius
        self.axis_path_div_hook = axis_path_div_hook
        self.axis_path_fill = axis_path_fill
        self.axis_path_shape_rendering = axis_path_shape_rendering
        self.axis_line_div_hook = axis_line_div_hook
        self.axis_line_shape_rendering = axis_line_shape_rendering
        self.path_area_div_hook = path_area_div_hook
        self.path_area_fill = path_area_fill
        self.axis_text_div_hook = axis_text_div_hook
        self.axis_text_font_family = axis_text_font_family
        self.axis_text_font_size = axis_text_font_size
        self.xlabel_text_div_hook = xlabel_text_div_hook
        self.xlabel_text_font_family = xlabel_text_font_family
        self.xlabel_text_font_size = xlabel_text_font_size
        self.ylabel_text_div_hook = ylabel_text_div_hook
        self.ylabel_text_font_family = ylabel_text_font_family
        self.ylabel_text_font_size = ylabel_text_font_size
        self.x_axis_line_div_hook = x_axis_line_div_hook
        self.x_axis_line_stroke = x_axis_line_stroke
        self.x_axis_line_stroke_opacity = x_axis_line_stroke_opacity
        self.x_axis_line_stroke_width = x_axis_line_stroke_width
        self.y_axis_line_div_hook = y_axis_line_div_hook
        self.y_axis_line_stroke = y_axis_line_stroke
        self.y_axis_line_stroke_opacity = y_axis_line_stroke_opacity
        self.y_axis_line_stroke_width = y_axis_line_stroke_width



        env = Environment(
            # not Packageloader, only file, searchpath is default
            loader=jinja2.FileSystemLoader(searchpath=[''])
        )
        # URL to jinja file in order to connect each other
        template_url = 'css.jinja'
        # load file into jinja2 Env
        templateFile = env.get_template(template_url)

        self.css_output = self.prepare_css(templateFile)

    def prepare_css(self, templateFile):
        # Dictionary
        templateVar = {

            't_line_div_hook': self.line_div_hook,
            't_line_stroke': self.line_stroke,
            't_line_fill': self.line_fill,
            't_line_stroke_width': self.line_stroke_width,

            't_tooltip_div_hook': self.tooltip_div_hook,
            't_tooltip_color': self.tooltip_color,
            't_tooltip_line_height': self.tooltip_line_height,
            't_tooltip_padding': self.tooltip_padding,
            't_tooltip_font_weight': self.tooltip_font_weight,
            't_tooltip_font_family': self.tooltip_font_family,
            't_tooltip_border_radius': self.tooltip_border_radius,

            't_axis_path_div_hook': self.axis_path_div_hook,
            't_axis_path_fill': self.axis_path_fill,
            't_axis_path_shape_rendering': self.axis_path_shape_rendering,

            't_axis_line_div_hook': self.axis_line_div_hook,
            't_axis_line_shape_rendering': self.axis_line_shape_rendering,

            't_path_area_div_hook': self.path_area_div_hook,
            't_path_area_fill': self.path_area_fill,

            't_axis_text_div_hook': self.axis_text_div_hook,
            't_axis_text_font_family': self.axis_text_font_family,
            't_axis_text_font_size': self.axis_text_font_size,

            't_xlabel_text_div_hook': self.xlabel_text_div_hook,
            't_xlabel_text_font_family': self.xlabel_text_font_family,
            't_xlabel_text_font_size': self.xlabel_text_font_size,

            't_ylabel_text_div_hook': self.ylabel_text_div_hook,
            't_ylabel_text_font_family': self.ylabel_text_font_family,
            't_ylabel_text_font_size': self.ylabel_text_font_size,

            't_x_axis_line_div_hook': self.x_axis_line_div_hook,
            't_x_axis_line_stroke': self.x_axis_line_stroke,
            't_x_axis_line_stroke_opacity': self.x_axis_line_stroke_opacity,
            't_x_axis_line_stroke_width': self.x_axis_line_stroke_width,

            't_y_axis_line_div_hook': self.x_axis_line_div_hook,
            't_y_axis_line_stroke': self.x_axis_line_stroke,
            't_y_axis_line_stroke_opacity': self.x_axis_line_stroke_opacity,
            't_y_axis_line_stroke_width': self.x_axis_line_stroke_width,
        }

        # render and print to see result
        output = templateFile.render(templateVar)

        return output


hemlo = CssTemplate("Blubb")
print(hemlo.prepare_css(templateFile))
# print(prepare_css(templateFile))
