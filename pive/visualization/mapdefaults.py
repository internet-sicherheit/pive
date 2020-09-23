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

import sys

from pive.visualization import colorthemes
from pive.visualization.defaults import *

####################
#  Meta Data #######
####################
# # Div container in which the map, legend and tooltip will be placed.
div_hook_map = 'map'
div_hook_legend = 'legend'
div_hook_tooltip = 'tooltip'

####################
#  Map Rendering ##
####################
zoom_threshold = 10
fill_opacity = 0.5
stroke_opacity = 0.6
mouseover_opacity = 1
mouseout_opacity = 0.5
tooltip_div_border = '2px solid lightblue'

##########################
# Scales for zoom level ##
##########################
scale = 1
scale_extent = [1, 20]

########################
#  POI Map specific ####
########################
max_poi = 100
circle_fill = '#0B6673'
circle_stroke = 'gray'
circle_radius = 5
circle_stroke_width = 0.25

#####################
# Heatmap specific ##
#####################
legendwidth = 80
legendheight = 200
legendmargin = {'top': 10, 'right': 60, 'bottom': 30, 'left': 2}
legendticksize = 6
legendborder = '1px solid #000'
heatmapcolors = colorthemes.heatmap

#########################
# Polygon Map specific ##
#########################
outer_map_fill = 'white'

####################
# Pan Buttons ######
####################
pan_north_rect_x = 0
pan_north_rect_y = 0
pan_north_rect_height = 30
pan_north_text_y = 20

pan_south_rect_x = 0
pan_south_rect_height = 30

pan_east_rect_y = 30
pan_east_rect_width = 30

pan_west_rect_x = 0
pan_west_rect_y = 30
pan_west_rect_width = 30
pan_west_text_x = 15

pan_moveamount = 1

####################
# Zoom Buttons #####
####################
zoom_rect_x = 0
zoom_rect_y = 0
zoom_rect_width = 30
zoom_rect_height = 30
zoom_rect_radius = 5

zoom_text_x = 15
zoom_text_y = 20

zoom_in_width_translate = 110
zoom_in_height_translate = 70
zoom_out_width_translate = 70
zoom_out_height_translate = 70

scale_factor_in = 1.5
scale_factor_out = 0.75

####################
#  Colors ##########
####################
map_fill = 'lightblue'
map_stroke = '#13CDE7'