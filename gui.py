#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GTK application window containing all information regarding the Desktop Stream
Viewers graphical user interface.

TODO: Add Windows support by using window handles instead of xid.
TODO: etc.....
"""

# GTK imports
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkX11", "3.0")
from gi.repository import Gtk
from gi.repository import GdkX11

import vlc

class ApplicationWindow(Gtk.Window):

    def __init__(self, instance, media_one, media_two):
        
        # Build the main GTK window.
        Gtk.Window.__init__(self, title = "Desktop Stream Viewer")
        self.connect("destroy", Gtk.main_quit)

        # Store the VLC instance.
        self.vlc_instance = instance
        
        self.media_one = media_one
        self.media_two = media_two

        # Setup the application window.
        self.setup()

    def setup(self):
        
        # Draw area one. 
        self.draw_area_one = Gtk.DrawingArea()
        self.draw_area_one.set_size_request(720, 480)
        self.draw_area_one.connect("realize", self.realized_one)
        
        # Draw area two.
        self.draw_area_two = Gtk.DrawingArea()
        self.draw_area_two.set_size_request(720, 480)
        self.draw_area_two.connect("realize", self.realized_two)

        # Horizontal wrapper.
        self.hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.hbox.pack_start(self.draw_area_one, True, True, 0)
        self.hbox.pack_start(self.draw_area_two, True, True, 0)
        self.add(self.hbox)

    def realized_one(self, widget, data = None):
        
        self.player_one = self.vlc_instance.media_player_new()
        xid = widget.get_window().get_xid()
        self.player_one.set_xwindow(xid)
        self.player_one.set_media(self.media_one)
        self.player_one.play()

    def realized_two(self, widget, data = None):
        
        self.player_two = self.vlc_instance.media_player_new()
        xid = widget.get_window().get_xid()
        self.player_two.set_xwindow(xid)
        self.player_two.set_media(self.media_two)
        self.player_two.play()

