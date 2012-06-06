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
import gobject
from draw import draw_blank_mask
from window import Window
from scrolled_window import ScrolledWindow
from iconview import IconView
from titlebar import Titlebar
from button import Button
from utils import gdkcolor_to_string, color_hex_to_cairo, propagate_expose, color_hex_to_rgb, color_rgb_to_hex, is_hex_color
from label import Label
from spin import SpinBox
from entry import TextEntry

class HSV(gtk.ColorSelection):
    '''HSV.'''
	
    def __init__(self):
        '''Init color selection.'''
        gtk.ColorSelection.__init__(self)
        
        # Remove right buttons.
        self.get_children()[0].remove(self.get_children()[0].get_children()[1])
        
        # Remove bottom color pick button.
        self.get_children()[0].get_children()[0].remove(self.get_children()[0].get_children()[0].get_children()[1])
        
    def get_hsv_widget(self):
        '''Get HSV widget.'''
        return self.get_children()[0].get_children()[0].get_children()[0]
    
    def get_color_string(self):
        '''Get color string.'''
        return gdkcolor_to_string(self.get_current_color())
    
    def get_rgb_color(self):
        '''Get rgb color.'''
        gdk_color = self.get_current_color()
        return (gdk_color.red / 256, gdk_color.green / 256, gdk_color.blue / 256)
    
gobject.type_register(HSV)

class ColorSelectDialog(Window):
    '''Color select dialog.'''
    
    DEFAULT_COLOR_LIST = ["#000000", "#808080", "#E20417", "#F29300", "#FFEC00", "#95BE0D", "#008F35", "#00968F", "#FFFFFF", "#C0C0C0", "#E2004E", "#E2007A", "#920A7E", "#162883", "#0069B2", "#009DE0"]
	
    def __init__(self, confirm_callback=None, cancel_callback=None):
        '''Init color select dialog.'''
        Window.__init__(self)
        self.set_modal(True)                                # grab focus to avoid build too many skin window
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG) # keeep above
        self.set_skip_taskbar_hint(True)                    # skip taskbar
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
        
        self.titlebar = Titlebar(["close"], None, None, "颜色选择")
        self.add_move_event(self.titlebar)
        
        self.color_box = gtk.HBox()
        self.color_align = gtk.Alignment()
        self.color_align.set(0.5, 0.5, 0.0, 0.0)
        self.color_align.set_padding(0, 0, 10, 0)
        self.color_align.add(self.color_box)
        self.color_hsv = HSV()
        self.color_string = self.color_hsv.get_color_string()
        (self.color_r, self.color_g, self.color_b) = self.color_hsv.get_rgb_color()
        self.color_hsv.get_hsv_widget().connect(
            "button-release-event", 
            lambda w, e: self.update_color_info(self.color_hsv.get_color_string()))
        self.color_box.pack_start(self.color_hsv, False, False)
        
        self.color_right_box = gtk.VBox()
        self.color_right_align = gtk.Alignment()
        self.color_right_align.set(0.5, 0.5, 0.0, 0.0)
        self.color_right_align.set_padding(8, 0, 0, 0)
        self.color_right_align.add(self.color_right_box)
        self.color_box.pack_start(self.color_right_align)
        
        self.color_info_box = gtk.HBox()
        self.color_right_box.pack_start(self.color_info_box, False, False)
        
        self.color_display_box = gtk.VBox()
        self.color_display_button = gtk.Button()
        self.color_display_button.connect("expose-event", self.expose_display_button)
        self.color_display_button.set_size_request(70, 49)
        self.color_display_align = gtk.Alignment()
        self.color_display_align.set(0.5, 0.5, 1.0, 1.0)
        self.color_display_align.set_padding(5, 5, 5, 5)
        self.color_display_align.add(self.color_display_button)
        self.color_display_box.pack_start(self.color_display_align, False, False, 5)
        
        self.color_hex_box = gtk.HBox()
        self.color_hex_label = Label("颜色值")
        self.color_hex_box.pack_start(self.color_hex_label, False, False, 5)
        self.color_hex_entry = TextEntry(self.color_string)
        self.color_hex_entry.entry.check_text = is_hex_color
        self.color_hex_entry.entry.connect("press-return", self.press_return_color_entry)
        self.color_hex_entry.set_size(70, 24)
        self.color_hex_box.pack_start(self.color_hex_entry, False, False, 5)
        self.color_display_box.pack_start(self.color_hex_box, False, False, 5)
        
        self.color_info_box.pack_start(self.color_display_box, False, False, 5)
        
        self.color_rgb_box = gtk.VBox()
        self.color_r_box = gtk.HBox()
        self.color_r_label = Label("红色: ")
        self.color_r_spin = SpinBox(self.color_r, 0, 255, 1)
        self.color_r_spin.connect("value-changed", lambda s, v: self.click_rgb_spin())
        self.color_r_box.pack_start(self.color_r_label, False, False)
        self.color_r_box.pack_start(self.color_r_spin, False, False)
        self.color_g_box = gtk.HBox()
        self.color_g_label = Label("绿色: ")
        self.color_g_spin = SpinBox(self.color_g, 0, 255, 1)
        self.color_g_spin.connect("value-changed", lambda s, v: self.click_rgb_spin())
        self.color_g_box.pack_start(self.color_g_label, False, False)
        self.color_g_box.pack_start(self.color_g_spin, False, False)
        self.color_b_box = gtk.HBox()
        self.color_b_label = Label("蓝色: ")
        self.color_b_spin = SpinBox(self.color_b, 0, 255, 1)
        self.color_b_spin.connect("value-changed", lambda s, v: self.click_rgb_spin())
        self.color_b_box.pack_start(self.color_b_label, False, False)
        self.color_b_box.pack_start(self.color_b_spin, False, False)
        
        self.color_rgb_box.pack_start(self.color_r_box, False, False, 8)
        self.color_rgb_box.pack_start(self.color_g_box, False, False, 8)
        self.color_rgb_box.pack_start(self.color_b_box, False, False, 8)
        self.color_info_box.pack_start(self.color_rgb_box, False, False, 5)
        
        self.color_select_view = IconView()
        self.color_select_view.connect("button-press-item", lambda view, item, x, y: self.update_color_info(item.color, False))
        self.color_select_view.draw_mask = draw_blank_mask
        self.color_select_scrolled_window = ScrolledWindow()
        self.color_select_scrolled_window.set_scroll_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        for color in self.DEFAULT_COLOR_LIST:
            self.color_select_view.add_items([ColorItem(color)])
            
        self.color_select_align = gtk.Alignment()
        self.color_select_align.set(0.5, 0.5, 1.0, 1.0)
        self.color_select_align.set_padding(10, 5, 8, 5)
        
        self.color_select_scrolled_window.add_child(self.color_select_view)
        self.color_select_align.add(self.color_select_scrolled_window)
        self.color_right_box.pack_start(self.color_select_align)    
        
        self.confirm_button = Button("确定")
        self.cancel_button = Button("取消")
        
        self.button_align = gtk.Alignment()
        self.button_align.set(1.0, 0.5, 0, 0)
        self.button_align.set_padding(10, 10, 5, 10)
        self.button_box = gtk.HBox()
        
        self.button_align.add(self.button_box)        
        self.button_box.pack_start(self.confirm_button, False, False, 5)
        self.button_box.pack_start(self.cancel_button, False, False, 5)
        
        self.window_frame.pack_start(self.titlebar, False, False)
        self.window_frame.pack_start(self.color_align, False, False)
        self.window_frame.pack_start(self.button_align, False, False)
        
        self.titlebar.close_button.connect("clicked", lambda w: self.destroy())
        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())
        self.connect("destroy", lambda w: self.destroy())
        
        self.update_color_info(self.color_string)
        
    def click_confirm_button(self):
        '''Click confirm button.'''
        if self.confirm_callback != None:
            self.confirm_callback(self.color_hex_entry.get_text())
        
        self.destroy()
        
    def click_cancel_button(self):
        '''Click cancel button.'''
        if self.cancel_callback != None:
            self.cancel_callback()
        
        self.destroy()
        
    def click_rgb_spin(self):
        '''Click rgb spin.'''
        self.update_color_info(color_rgb_to_hex((self.color_r_spin.get_value(),
                                                 self.color_g_spin.get_value(),
                                                 self.color_b_spin.get_value())))        
        
    def press_return_color_entry(self, entry):
        '''Press return on color entry.'''
        self.update_color_info(entry.get_text())
        entry.select_all()
        
    def expose_display_button(self, widget, event):
        '''Expose display button.'''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        cr.set_source_rgb(*color_hex_to_cairo(self.color_string))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()

        # Propagate expose.
        propagate_expose(widget, event)
        
        return True
        
    def update_color_info(self, color_string, clear_highlight=True):
        '''Update color info.'''
        self.color_string = color_string
        (self.color_r, self.color_g, self.color_b) = color_hex_to_rgb(self.color_string)
        self.color_r_spin.update(self.color_r)
        self.color_g_spin.update(self.color_g)
        self.color_b_spin.update(self.color_b)
        self.color_hex_entry.set_text(self.color_string)
        self.color_hsv.set_current_color(gtk.gdk.color_parse(color_string))
        
        if clear_highlight:
            self.color_select_view.clear_highlight()
        
        self.color_display_button.queue_draw()
        
gobject.type_register(ColorSelectDialog)

class ColorItem(gobject.GObject):
    '''Icon item.'''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, color):
        '''Init item icon.'''
        gobject.GObject.__init__(self)
        self.color = color
        self.width = 20
        self.height = 16
        self.padding_x = 4
        self.padding_y = 4
        self.hover_flag = False
        self.highlight_flag = False
        
    def emit_redraw_request(self):
        '''Emit redraw-request signal.'''
        self.emit("redraw-request")
        
    def get_width(self):
        '''Get width.'''
        return self.width + self.padding_x * 2
        
    def get_height(self):
        '''Get height.'''
        return self.height + self.padding_y * 2
    
    def render(self, cr, rect):
        '''Render item.'''
        # Init.
        draw_x = rect.x + self.padding_x
        draw_y = rect.y + self.padding_y
        
        # Draw color.
        cr.set_source_rgb(*color_hex_to_cairo(self.color))
        cr.rectangle(draw_x, draw_y, self.width, self.height)
        cr.fill()
        
        if self.hover_flag:
            cr.set_source_rgb(*color_hex_to_cairo("#333333"))
            cr.rectangle(draw_x, draw_y, self.width, self.height)
            cr.stroke()
        elif self.highlight_flag:
            cr.set_source_rgb(*color_hex_to_cairo("#FF0000"))
            cr.rectangle(draw_x, draw_y, self.width, self.height)
            cr.stroke()
            
    def icon_item_motion_notify(self, x, y):
        '''Handle `motion-notify-event` signal.'''
        self.hover_flag = True
        
        self.emit_redraw_request()
        
    def icon_item_lost_focus(self):
        '''Lost focus.'''
        self.hover_flag = False
        
        self.emit_redraw_request()
        
    def icon_item_highlight(self):
        '''Highlight item.'''
        self.highlight_flag = True

        self.emit_redraw_request()
        
    def icon_item_normal(self):
        '''Set item with normal status.'''
        self.highlight_flag = False
        
        self.emit_redraw_request()
    
    def icon_item_button_press(self, x, y):
        '''Handle button-press event.'''
        pass
    
    def icon_item_button_release(self, x, y):
        '''Handle button-release event.'''
        pass
    
    def icon_item_single_click(self, x, y):
        '''Handle single click event.'''
        pass

    def icon_item_double_click(self, x, y):
        '''Handle double click event.'''
        pass
    
gobject.type_register(ColorItem)