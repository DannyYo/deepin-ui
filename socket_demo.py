#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
python socket_demo.py 46137376
��ID��python plug_demo.py������
'''

import string
import pygtk
import gtk,sys

window = gtk.Window()
window.show()

socket = gtk.Socket()
socket.show()
window.add(socket)

print "Socket ID=", socket.get_id()
window.connect("destroy", lambda w: gtk.main_quit())

def plugged_event(widget):
    print "I (", widget, ") have just had a plug inserted!"

socket.connect("plug-added", plugged_event)

if len(sys.argv) == 2:
    socket.add_id(long(sys.argv[1]))

gtk.main()
