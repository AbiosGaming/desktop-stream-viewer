#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Example application for the Abios Gaming - Desktop Stream Viewer.
# Sven Anderzén - 2017

# GTK imports.
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkX11", "3.0")
from gi.repository import GObject, Gio, Gtk, GdkX11

import sys
import ctypes

import vlc
import streamlink
import callbacks as cb
from streamContainer import StreamContainer

class Application(Gtk.Application):

    def __init__(self, application_id, flags, stream_info):
        Gtk.Application.__init__(self, application_id = application_id, flags = flags)
        self.connect("activate", self.activate)

        # Kick up a VLC instance.
        self.vlc_instance = vlc.Instance("--no-xlib")
        self.streams = []

        # Streamlink streams.
        self.streams.append(StreamContainer(self.vlc_instance, stream_info[0]))
        self.streams.append(StreamContainer(self.vlc_instance, stream_info[1]))

    def activate(self, *args):
        ApplicationWindow(self)

class ApplicationWindow(object):

    def __init__(self, application):
        self.application = application

        # Load Glade UI file.
        try:
            builder = Gtk.Builder.new_from_file("gui.glade")
            builder.connect_signals(self)
        except GObject.GError:
            print("Could not read gui.glade.")
            raise

        self.window = builder.get_object("window")
        self.window.set_application(application)

        self.window.set_size_request(1280, 720)
        self.window.show()

    def onDrawReadyOne(self, widget,  *args):
        player = self.application.vlc_instance.media_player_new()
        xid = widget.get_window().get_xid()
        player.set_xwindow(xid)
        player.set_media(self.application.streams[0].media)
        player.play()

    # Temporary workaround since we read stream_info from CLI and not GUI atm.
    def onDrawReadyTwo(self, widget,  *args):
        player = self.application.vlc_instance.media_player_new()
        xid = widget.get_window().get_xid()
        player.set_xwindow(xid)
        player.set_media(self.application.streams[1].media)
        player.play()

    def onDelete(self, *args):
        self.application.vlc_instance.release()
        self.window.destroy()

def main():

    try:
        stream_info = [{}, {}]
        stream_info[0]["url"], stream_info[0]["quality"] = sys.argv[1], sys.argv[2]
        stream_info[1]["url"], stream_info[1]["quality"] = sys.argv[3], sys.argv[4]
    except Exception as e:
        sys.exit("Usage: {} <url> <quality> <url> <quality>".format(__file__))

    app = Application("com.abiosgaming", Gio.ApplicationFlags.FLAGS_NONE, stream_info)
    app.run()

if __name__ == "__main__":
    main()
