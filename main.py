#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Example application for the Abios Gaming - Desktop Stream Viewer.
# Sven Anderzén - 2017

import sys
import platform

# Qt imports
from PyQt5 import QtWidgets, QtGui, uic, QtCore

import streamlink
import vlc
from containers.live_stream_container import LiveStreamContainer

class ApplicationWindow(QtWidgets.QMainWindow):
    """The main GUI window."""

    def __init__(self):
        super(ApplicationWindow, self).__init__(None)
        self.setup_ui()

        # Kick up a VLC instance.
        self.vlc_instance = vlc.Instance("--no-xlib")

        # TODO:
        # Maybe we should explain what kind of coordinates these are?
        # It is probably also a good idea to only have one attribute,
        # called new_stream_coordinates (or something similar) and let
        # it be a tuple of x, y.
        # Set coordinates
        self.x = 0
        self.y = 0

        # Streamlink streams.
        self.streams = []

        # Setup the players.
        self.players = []

    def setup_ui(self):
        """Loads the main.ui file and sets up the window and grid."""
        self.ui = uic.loadUi("ui/main.ui")
        self.grid = self.ui.findChild(QtCore.QObject, "grid")

        # Connect up all actions.
        self.ui.findChild(QtCore.QObject, "mute_all_streams") \
            .toggled.connect(self.mute_all_streams)
        self.ui.findChild(QtCore.QObject, "export_streams_to_clipboard") \
            .triggered.connect(self.export_streams_to_clipboard)
        self.ui.findChild(QtCore.QObject, "add_new_stream") \
            .triggered.connect(self.add_new_stream)

        self.ui.show()

    def mute_all_streams(self):
        """Toggles the audio of all the players."""
        for player in self.players:
            player.audio_toggle_mute()

    def export_streams_to_clipboard(self):
        """Exports all streams to the users clipboard."""
        stream_urls = []

        for stream in self.streams:
            stream_urls.append(stream.stream_info["url"])

        text = "\n".join(stream_urls)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear(mode = clipboard.Clipboard)
        clipboard.setText(text, mode = clipboard.Clipboard)

    def add_new_stream(self):
        """Adds a new player for the specified stream in the grid."""
        stream_url, status = QtWidgets.QInputDialog.getText(self, "Stream input", "Enter the stream URL:")
        if not status:
            return
        new_stream = {"url": "twitch.tv/esl_csgo", "quality": "480p30"}
        new_container = LiveStreamContainer(self.vlc_instance, new_stream)
        self.setup_stream(new_container, self.x, self.y)
        self.new_coordinates()

        # Add streams here.

    def setup_stream(self, stream, grid_xpos, grid_ypos):
        """Sets up and starts to play a stream in the defined video frame
        above.
        """
        # Get our video frame in the grid
        video_frame = self.get_video_frame(grid_xpos, grid_ypos)

        # Create our player
        player = self.vlc_instance.media_player_new()
        player.set_media(stream.media)

        if platform.system() == "Linux":
            player.set_xwindow(video_frame.winId())
        elif platform.system() == "Windows":
            player.set_hwnd(video_frame.winId())
        elif platform.system() == "Darwin":
            player.set_nsobject(video_frame.winId())

        player.play()

        return player

    def get_video_frame(self, grid_xpos, grid_ypos):
        if platform.system() == "Darwin":
            video_frame = QtWidgets.QMacCocoaViewContainer(0)
        else:
            video_frame = QtWidgets.QFrame()

        # Add the frame to the global grid.
        self.grid.addWidget(video_frame, grid_xpos, grid_ypos)

        return video_frame

    # TODO:
    # Perhaps update_new_stream_coordinates() is a
    # better suited name for the function?
    def new_coordinates(self):
        # TODO:
        # Docstring missing and some explanation on what the code
        # does is missing.
        if self.y == self.x:
            self.y += 1
            self.x = 0
        elif self.y == self.x + 1:
            self.x = self.y
            self.y = 0
        else:
            if self.x < self.y:
                self.x += 1
            else:
                self.y += 1

def main():

    app = QtWidgets.QApplication([])

    window = ApplicationWindow()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
