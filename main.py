#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import threading
import textwrap

import streamlink
# Qt imports
from PyQt5 import QtWidgets, uic, QtCore, QtGui

from constants import (
    MUTE_CHECKBOX, MUTE_ALL_STREAMS, EXPORT_STREAMS_TO_CLIPBOARD, ADD_NEW_STREAM,
    CONFIG_QUALITY
)
from videoframegrid import VideoFrameGrid
from containers import LiveStreamContainer
from config import cfg
from enums import AddStreamError
from coordinates import VideoFrameCoordinates


class ApplicationWindow(QtWidgets.QMainWindow):
    """The main GUI window."""

    # Define a new signal, used to add_frames from the seperate thread
    add_frame = QtCore.pyqtSignal(str, dict, str, VideoFrameCoordinates)
    # Used when the add stream thread fails
    fail_add_stream = QtCore.pyqtSignal(AddStreamError, tuple)

    def __init__(self):
        super(ApplicationWindow, self).__init__(None)
        self.setup_ui()

        # Connect threading signals
        self.add_frame.connect(self.setup_videoframe)
        self.fail_add_stream.connect(self.on_fail_add_stream)

        self.streamlink_session = streamlink.Streamlink()

    def setup_ui(self):
        """Loads the main.ui file and sets up the window and grid."""
        self.ui = uic.loadUi("ui/main.ui", self)
        self.grid = VideoFrameGrid(self)

        self.container = self.ui.findChild(QtCore.QObject, "container")
        self.container.addLayout(self.grid)
        self.menubar = self.ui.findChild(QtCore.QObject, "MenuBar")

        # Connect up all actions.
        self.actions = {}
        self.actions[MUTE_CHECKBOX] = self.ui.findChild(QtCore.QObject, MUTE_ALL_STREAMS)
        self.actions[MUTE_CHECKBOX].toggled.connect(self.mute_all_streams)

        self.ui.findChild(QtCore.QObject, EXPORT_STREAMS_TO_CLIPBOARD) \
            .triggered.connect(self.export_streams_to_clipboard)
        self.ui.findChild(QtCore.QObject, ADD_NEW_STREAM) \
            .triggered.connect(self.add_new_stream)

        # Create the loading gear but dont add it to anywhere, just save it
        self.setup_loading_gif()

        self.ui.show()

    def setup_videoframe(self, stream_url, stream_options, quality):
        """Sets up a videoframe and with the provided stream information."""
        self.grid.add_new_videoframe(stream_url, stream_options, quality)
        # Remove the loading feedback
        self.hide_loading_gif()

    def setup_loading_gif(self):
        """Creates the loading gear as QMovie and its label."""
        self.movie = QtGui.QMovie(self)
        self.movie.setFileName("ui/res/loading.gif")
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.start()
        self.loading = QtWidgets.QLabel(self)
        self.loading.setAlignment(QtCore.Qt.AlignCenter)
        self.loading.setMovie(self.movie)
        self.loading.hide()

    def show_loading_gif(self):
        """Shows the loading gif on the next frame location"""
        self.grid.addWidget(self.loading, self.grid.coordinates.x, self.grid.coordinates.y)
        self.loading.show()

    def hide_loading_gif(self):
        """Removes the loading gif from the next frame location"""
        self.grid.removeWidget(self.loading)
        self.loading.hide()

    def mute_all_streams(self):
        """Toggles the audio of all the players."""
        for videoframe in self.grid.videoframes:
            if self.actions[MUTE_CHECKBOX].isChecked():
                videoframe.player.audio_set_mute(True)
            else:
                if not videoframe.is_muted:
                    videoframe.player.audio_set_mute(False)

    def export_streams_to_clipboard(self):
        """Exports all streams to the users clipboard."""
        stream_urls = []

        for videoframe in self.grid.videoframes:
            stream_urls.append(videoframe.stream.url)

        text = "\n".join(stream_urls)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        clipboard.setText(text, mode=clipboard.Clipboard)

    def add_new_stream(self, stream_url=None, stream_quality=cfg[CONFIG_QUALITY]):
        """Adds a new player for the specified stream in the grid."""
        if not stream_url:
            stream_url, ok = QtWidgets.QInputDialog.getText(
                self,
                "Stream input",
                "Enter the stream URL:"
            )

            if not ok:
                return

        # Give some feedback to the user
        self.show_loading_gif()

        # Run the rest on a seperate thread to be able to show the loading feedback
        # Also helps a lot with lag
        threading.Thread(target=self._add_new_stream, args=(stream_url, stream_quality)).start()

    def _add_new_stream(self, stream_url=None, stream_quality=cfg[CONFIG_QUALITY]):
        """Fetches qualities and if possible adds a frame to the main window."""
        try:
            stream_options = self.streamlink_session.streams(stream_url)

            if stream_quality not in stream_options:
                self.fail_add_stream.emit(AddStreamError.DEFAULT_QUALITY_MISSING, (stream_options, stream_url, stream_quality))
                return

            self.add_frame.emit(stream_url, stream_options, stream_quality, self.grid.coordinates)

        except streamlink.exceptions.NoPluginError:
            self.fail_add_stream.emit(
                AddStreamError.URL_NOT_SUPPORTED,
                (
                    "Error",
                    "Could not open stream: The provided URL is not supported"
                )
            )

        except streamlink.exceptions.PluginError:
            self.fail_add_stream.emit(
                AddStreamError.OTHER,
                (
                    "Error",
                    # Wierd formatting because whitespaces are also included
                    """Could not open stream!
The provided URL is supported, but could not be opened.
Check for spelling mistakes!"""
                )
            )

        except streamlink.exceptions.NoStreamsError:
            self.fail_add_stream.emit(
                AddStreamError.OTHER,
                (
                    "Error",
                    """Could not open stream: No streams was found.
Is the stream running?"""
                )
            )

        except streamlink.exceptions.StreamError:
            self.fail_add_stream.emit(
                AddStreamError.OTHER,
                (
                    "Error",
                    "Could not open stream."
                )
            )

        except streamlink.exceptions.StreamlinkError:
            self.fail_add_stream.emit(
                AddStreamError.OTHER,
                (
                    "Error",
                    "Could not open stream."
                )
            )

    def on_fail_add_stream(self, err, args):
        # Remove the loading feedback
        self.hide_loading_gif()

        if err == AddStreamError.URL_NOT_SUPPORTED:
            (title, text) = args
            QtWidgets.QMessageBox().warning(self, title, text)
        elif err == AddStreamError.DEFAULT_QUALITY_MISSING:
            (stream_options, url, quality) = args
            quality, ok = self._get_user_quality_preference(stream_options)
            if ok:
                self.add_new_stream(url, quality)
                return
        else:
            (title, text) = args
            QtWidgets.QMessageBox().warning(self, title, text)

        self.add_new_stream()

    def _get_user_quality_preference(self, stream_options):
        """Prompts the user to select what quality they want on the stream."""
        filtered_qualities = LiveStreamContainer.filtered_quality_options(
            stream_options
        )

        return QtWidgets.QInputDialog.getItem(
            self,
            "Stream Quality option",
            """The default stream quality option could not be used.
            Please select another one:""",
            reversed(filtered_qualities)
        )


def main():
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(textwrap.dedent(
            """
            Could not start app, are you sure you fullfill the requirements?
              - Qt5
              - VLC 3.0
            """
        ))
