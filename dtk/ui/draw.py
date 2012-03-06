#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import cairo
from theme import *
from math import pi
from utils import *
from constant import *
import math

def draw_radial_ring(cr, x, y, outer_radius, inner_radius, color_infos):
    '''Draw radial ring.'''
    with cairo_state(cr):
        # Clip.
        cr.arc(x, y, outer_radius, 0, pi * 2)
        cr.arc(x, y, inner_radius, 0, pi * 2)
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.clip()
        
        # Draw radial round.
        draw_radial_round(cr, x, y, outer_radius, color_infos)
        
def draw_round_rectangle(cr, x, y, width, height, r):
    '''Draw round rectangle.'''
    # Top side.
    cr.move_to(x + r, y)
    cr.line_to(x + width - r, y)
    
    # Top-right corner.
    cr.arc(x + width - r, y + r, r, pi * 3 / 2, pi * 2)
    
    # Right side.
    cr.line_to(x + width, y + height - r)
    
    # Bottom-right corner.
    cr.arc(x + width - r, y + height - r, r, 0, pi / 2)
    
    # Bottom side.
    cr.line_to(x + r, y + height)
    
    # Bottom-left corner.
    cr.arc(x + r, y + height - r, r, pi / 2, pi)
    
    # Left side.
    cr.line_to(x, y + r)
    
    # Top-left corner.
    cr.arc(x + r, y + r, r, pi, pi * 3 / 2)

    # Close path.
    cr.close_path()

def draw_pixbuf(cr, pixbuf, x=0, y=0, alpha=1.0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint_with_alpha(alpha)
        
def draw_window_rectangle(cr, sx, sy, ex, ey, r):
    '''Draw window rectangle.'''
    # Save antialias.
    antialias = cr.get_antialias()
    
    # Set line width.
    cr.set_line_width(1)
    
    # Set OPERATOR_OVER operator.
    cr.set_operator(cairo.OPERATOR_OVER)
    
    # Turn off antialias.
    cr.set_antialias(cairo.ANTIALIAS_NONE)
    
    cr.move_to(sx + r, sy)        # top line
    cr.line_to(ex - r, sy)
    cr.stroke()
    
    cr.move_to(ex, sy + r)    # right side
    cr.line_to(ex, ey - r)
    cr.stroke()
    
    cr.move_to(ex - r, ey) # bottom side
    cr.line_to(sx + r, ey)     
    cr.stroke()
    
    cr.move_to(sx, ey - r)    # left side
    cr.line_to(sx, sy + r)        
    cr.stroke()

    cr.arc(sx + r, sy + r, r, pi, pi * 3 / 2) # top-left
    cr.stroke()

    cr.arc(ex - r, sy + r, r, pi * 3 / 2, pi * 2) # top-right
    cr.stroke()
    
    cr.arc(ex - r, ey - r, r, 0, pi / 2) # bottom-right
    cr.stroke()
    
    cr.arc(sx + r, ey - r, r, pi / 2, pi) # bottom-left
    cr.stroke()
    
    # Restore antialias.
    cr.set_antialias(antialias)
        
def draw_font(cr, content, font_size, font_color, x, y, width, height, x_align=ALIGN_MIDDLE, y_align=ALIGN_MIDDLE):
    '''Draw font.'''
    # Set font face.
    try:
        cr.select_font_face(DEFAULT_FONT,
                            cairo.FONT_SLANT_NORMAL, 
                            cairo.FONT_WEIGHT_NORMAL)
    except Exception, e:
        print e
        
    # Set font size.
    cr.set_font_size(font_size)
    
    # Get font size.
    font_height = font_size
    font_width = cr.text_extents(content)[2]
    
    # Set font color.
    cr.set_source_rgb(*color_hex_to_cairo(font_color))
    
    # Set font coordinate.
    if x_align == ALIGN_START:
        font_x = x
    elif x_align == ALIGN_END:
        font_x = x + width - font_width
    else:
        font_x = x + (width - font_width) / 2
        
    if y_align == ALIGN_START:
        fontY = y
    elif y_align == ALIGN_END:
        fontY = y + height
    else:
        fontY = y + (height + font_height) / 2
    cr.move_to(font_x, fontY - int(font_size) / 8)

    # Show font.
    cr.show_text(content)

def draw_line(cr, sx, sy, ex, ey, line_width=1, antialias_status=cairo.ANTIALIAS_NONE):
    '''Draw line.'''
    # Save antialias.
    antialias = cr.get_antialias()
    
    # Draw line.
    cr.set_line_width(line_width)
    cr.set_antialias(antialias_status)
    cr.move_to(sx, sy)
    cr.line_to(ex, ey)
    cr.stroke()
    
    # Restore antialias.
    cr.set_antialias(antialias)

def draw_vlinear(cr, x, y, w, h, color_infos, radius=0, top_to_bottom=True):
    '''Draw linear rectangle.'''
    if top_to_bottom:
        pat = cairo.LinearGradient(0, y, 0, y + h)
    else:
        pat = cairo.LinearGradient(0, y + h, 0, y)
    for (pos, color_info) in color_infos:
        add_color_stop_rgba(pat, pos, color_info)
    cr.set_source(pat)
    draw_round_rectangle(cr, x, y, w, h, radius)
    cr.fill()

def draw_hlinear(cr, x, y, w, h, color_infos, radius=0, left_to_right=True):
    '''Draw linear rectangle.'''
    if left_to_right:
        pat = cairo.LinearGradient(x, 0, x + w, 0)
    else:
        pat = cairo.LinearGradient(x + w, 0, x, 0)
    for (pos, color_info) in color_infos:
        add_color_stop_rgba(pat, pos, color_info)
    cr.set_source(pat)
    draw_round_rectangle(cr, x, y, w, h, radius)
    cr.fill()
    
def expose_linear_background(widget, event, color_infos):
    '''Expose linear background.'''
    # Init.
    cr = widget.window.cairo_create()
    rect = widget.allocation
    
    # Draw linear background.
    draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height, color_infos)
    
    # Propagate expose.
    propagate_expose(widget, event)
    
    return True

def draw_radial_round(cr, x, y, r, color_infos):
    '''Draw radial round.'''
    radial = cairo.RadialGradient(x, y, r, x, y, 0)
    for (pos, color_info) in color_infos:
        add_color_stop_rgba(radial, pos, color_info)
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.set_source(radial)
    cr.fill()
    