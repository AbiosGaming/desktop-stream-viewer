#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Example application for the Abios Gaming - Desktop Stream Viewer.
# Sven Anderzén - 2017

import sys

import streamlink
# Qt imports
from PyQt5 import QtWidgets, uic, QtCore

import vlc
from constants import MUTE_CHECKBOX, MUTE_ALL_STREAMS, EXPORT_STREAMS_TO_CLIPBOARD, ADD_NEW_STREAM
from containers import LiveStreamContainer
from coordinates import StreamCoordinates
from videoframes import LiveVideoFrame


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
        self.coordinates = StreamCoordinates(x=0, y=0)

        # List of video frames.
        self.videoframes = []

        # Used when moving two frames
        self.selected_frame = None

    def setup_ui(self):
        """Loads the main.ui file and sets up the window and grid."""
        self.ui = uic.loadUi("ui/main.ui")
        self.grid = self.ui.findChild(QtCore.QObject, "grid")

        # Connect up all actions.
        self.actions = {}
        self.actions[MUTE_CHECKBOX] = self.ui.findChild(QtCore.QObject, MUTE_ALL_STREAMS)
        self.actions[MUTE_CHECKBOX].toggled.connect(self.mute_all_streams)

        self.ui.findChild(QtCore.QObject, EXPORT_STREAMS_TO_CLIPBOARD) \
            .triggered.connect(self.export_streams_to_clipboard)
        self.ui.findChild(QtCore.QObject, ADD_NEW_STREAM) \
            .triggered.connect(self.add_new_stream)

        self.ui.show()

    def mute_all_streams(self):
        """Toggles the audio of all the players."""
        for videoframe in self.videoframes:
            if self.actions[MUTE_CHECKBOX].isChecked():
                videoframe.player.audio_set_mute(True)
            else:
                if not videoframe.is_muted:
                    videoframe.player.audio_set_mute(False)

    def export_streams_to_clipboard(self):
        """Exports all streams to the users clipboard."""
        stream_urls = []

        for videoframe in self.videoframes:
            stream_urls.append(videoframe.stream.url)

        text = "\n".join(stream_urls)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        clipboard.setText(text, mode=clipboard.Clipboard)

    def add_new_stream(self, *args, stream_url=None, stream_quality="best"):
        """Adds a new player for the specified stream in the grid."""
        if not stream_url:
            stream_url, ok = QtWidgets.QInputDialog.getText(self, "Stream input", "Enter the stream URL:")

            if not ok:
                return

        new_stream = {"url": stream_url, "quality": stream_quality}

        try:
            self.setup_videoframe(new_stream, self.coordinates)
            self.new_coordinates()
        except KeyError:
            filtered_qualities = LiveStreamContainer.filtered_quality_options(
                streamlink.streams(stream_url)
            )

            stream_quality, ok = QtWidgets.QInputDialog.getItem(self,
                                                                "Stream Quality option",
                                                                """The default stream quality option could not be used.
                                                                Please select another one:""",
                                                                reversed(filtered_qualities)
                                                                )

            if not ok:
                return

            self.add_new_stream(stream_url=stream_url, stream_quality=stream_quality)
        except streamlink.exceptions.NoPluginError:
            error_window = QtWidgets.QMessageBox().warning(self,
                                                           "Error",
                                                           "Could not open stream: The provided URL is not supported"
                                                           )

            self.add_new_stream()

    def setup_videoframe(self, stream_info, coordinates):
        """Sets ups a videoframe and with the provided stream information."""
        videoframe = LiveVideoFrame(self.vlc_instance, stream_info)
        self.grid.addWidget(videoframe, coordinates.x, coordinates.y)
        videoframe._move = self.move_frame

        return videoframe

    def move_frame(self, frame):
        if self.selected_frame is None:
            self.selected_frame = frame
        else:
            if self.selected_frame.selected and self.selected_frame != frame:
                x, y, _, _ = self.grid.getItemPosition(self.grid.indexOf(frame))
                x2, y2, _, _ = self.grid.getItemPosition(self.grid.indexOf(self.selected_frame))
                self.grid.removeWidget(frame)
                self.grid.removeWidget(self.selected_frame)
                self.grid.addWidget(self.selected_frame, x, y)
                self.grid.addWidget(frame, x2, y2)

                # Deselect
                frame.deselect()
                self.selected_frame.deselect()
                self.selected_frame = None
            else:
                self.selected_frame = frame

    # TODO:
    # Perhaps update_new_stream_coordinates() is a
    # better suited name for the function?
    def new_coordinates(self):
        # TODO:
        # Docstring missing and some explanation on what the code
        # does is missing.
        self.coordinates = self.coordinates.new_coordinates()


def main():
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
