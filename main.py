#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example program of using libVLC to play online livestreams with full access
to video buffer using Streamlink.

For more information about the Streamlink API visit:
    https://streamlink.github.io/api_guide.html
For more information about the libVLC API visit:
    https://www.videolan.org/developers/vlc/doc/doxygen/html/index.html
"""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkX11", "3.0")
from gi.repository import Gtk
from gi.repository import GdkX11

import ctypes
import shutil
import sys

import vlc
import streamlink
import gui
import callbacks as cb

def main(stream_one_info, stream_two_info):
    """Creates the application containing 2 separate VLC media players."""

    # Open the StreamLink streams.
    streams = streamlink.streams(stream_one_info["url"])
    stream_one = streams[stream_one_info["quality"]].open()
    streams = streamlink.streams(stream_two_info["url"])
    stream_two = streams[stream_two_info["quality"]].open()

    # Create our VLC media for the two streams.
    instance = vlc.Instance("--no-xlib")
    opaque_one = ctypes.cast(ctypes.pointer(ctypes.py_object(stream_one)), ctypes.c_void_p)
    opaque_two = ctypes.cast(ctypes.pointer(ctypes.py_object(stream_two)), ctypes.c_void_p)
    media_one = instance.media_new_callbacks(
        cb.callbacks["read"],
        cb.callbacks["open"],
        cb.callbacks["seek"],
        cb.callbacks["close"],
        opaque_one
    )
    media_two = instance.media_new_callbacks(
        cb.callbacks["read"],
        cb.callbacks["open"],
        cb.callbacks["seek"],
        cb.callbacks["close"],
        opaque_two
    )

    # Create the GTK window.
    window = gui.ApplicationWindow(instance, media_one, media_two)
    window.show_all()

    # GTK main event loop.
    Gtk.main()

    # Destory the players and relese the VLC instance.
    # window.player_one.stop()
    # window.player_two.stop()
    # window.vlc_instance.release()

if __name__ == "__main__":

    # Ghetto-check that VLC is installed.
    if not shutil.which("vlc"):
        sys.exit("Could not find VLC executable.")

    try:
        stream_one_info, stream_two_info = {}, {}
        stream_one_info["url"], stream_one_info["quality"] = sys.argv[1], sys.argv[2]
        stream_two_info["url"], stream_two_info["quality"] = sys.argv[3], sys.argv[4]
    except IndexError:
        sys.exit("Usage: {0} <url> <quality> <url> <quality> ".format(__file__))

    main(stream_one_info, stream_two_info)
