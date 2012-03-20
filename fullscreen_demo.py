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

from dtk.ui.theme import *
from dtk.ui.panel import *
from dtk.ui.utils import *
from dtk.ui.draw import *

class TestPanel(Panel):
    '''Panel to test fullscreen.'''
	
    def __init__(self):
        '''Init test panel.'''
        Panel.__init__(self)
        
        self.connect_after("expose-event", self.expose_test_panel)
        self.connect("size-allocate", self.shape_test_panel)
        
    def expose_test_panel(self, widget, event):
        '''Expose test panel.'''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation

        # Clear color to transparent window.
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        # Draw background.
        cr.set_source_rgba(1.0, 0.0, 0.0, 0.5)
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
        
        # Propagate expose.
        propagate_expose(widget, event)
        
        return True

    def shape_test_panel(self, widget, rect):
        '''Shap window frame.'''
        if widget.window != None and widget.get_has_window() and rect.width > 0 and rect.height > 0:
            # Init.
            x, y, w, h = rect.x, rect.y, rect.width, rect.height
            bitmap = gtk.gdk.Pixmap(None, w, h, 1)
            cr = bitmap.cairo_create()
            
            # Clear the bitmap
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cr.set_operator(cairo.OPERATOR_CLEAR)
            cr.paint()
            
            # Draw our shape into the bitmap using cairo.
            cr.set_source_rgb(1.0, 1.0, 1.0)
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.rectangle(0, 0, w, 25)
            cr.fill()
            
            # Shape with given mask.
            widget.shape_combine_mask(bitmap, 0, 0)
            
def test_window_event(widget, event):
    '''docs'''
    print "press window event"
            
def test_panel_event(widget, event):
    '''docs'''
    print "press panel event"
            
if __name__ == "__main__":
    # Init window.
    window = gtk.Window()
    window.add_events(gtk.gdk.ALL_EVENTS_MASK)        
    window.connect("destroy", lambda w: gtk.main_quit())
    window.add(gtk.image_new_from_pixbuf(ui_theme.get_pixbuf("background5.jpg").get_pixbuf()))
    
    # Init panel window.
    panel = TestPanel()
    
    # Full mplayer window first.
    window.fullscreen()
    
    # Full panel window.
    panel.move(0, 0)
    panel.fullscreen()
    
    # Destroy window if destroy panel window. 
    window.set_transient_for(panel)
    window.set_destroy_with_parent(True)
    
    # Show mplayer window first, then show panel window.
    window.show_all()
    panel.show_panel()

    # Test event area.
    window.connect("button-press-event", test_window_event)
    panel.connect("button-press-event", test_panel_event)
    
    gtk.main()
