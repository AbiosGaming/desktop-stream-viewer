#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import textwrap
import threading

import streamlink
# Qt imports
from PyQt5 import QtWidgets, uic, QtCore, QtGui

from config import cfg
from constants import (
    MUTE_CHECKBOX, MUTE_ALL_STREAMS, EXPORT_STREAMS_TO_CLIPBOARD,
    IMPORT_STREAMS_FROM_CLIPBOARD, ADD_NEW_STREAM, CONFIG_QUALITY,
)
from containers import LiveStreamContainer
from enums import AddStreamError
from models import StreamModel, VideoFrameCoordinates
from videoframegrid import VideoFrameGrid


class ApplicationWindow(QtWidgets.QMainWindow):
    """The main GUI window."""

    # Define a new signal, used to add_frames from the separate thread
    add_frame = QtCore.pyqtSignal(str, dict, str, VideoFrameCoordinates)
    # Used when the add stream thread fails
    fail_add_stream = QtCore.pyqtSignal(AddStreamError, tuple)

    def __init__(self):
        super(ApplicationWindow, self).__init__(None)
        self.setup_ui()

        # Connect threading signals
        self.add_frame.connect(self.setup_videoframe)
        self.fail_add_stream.connect(self.on_fail_add_stream)

        self.model = StreamModel(self.grid)

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

        self.__bind_view_to_action(MUTE_ALL_STREAMS, self.mute_all_streams, toggled=True)
        self.__bind_view_to_action(EXPORT_STREAMS_TO_CLIPBOARD, self.export_streams_to_clipboard)
        self.__bind_view_to_action(ADD_NEW_STREAM, self.add_new_stream)
        self.__bind_view_to_action(IMPORT_STREAMS_FROM_CLIPBOARD, self.import_streams_from_clipboard)

        # Create the loading gear but dont add it to anywhere, just save it
        self.setup_loading_gif()

        self.ui.show()

    def setup_videoframe(self, stream_url, stream_options, quality):
        """Sets up a videoframe and with the provided stream information."""
        self.model.add_new_videoframe(stream_url, stream_options, quality)
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
        self.model.add_widget(self.loading, self.model.grid.coordinates.x, self.model.grid.coordinates.y)
        self.loading.show()

    def hide_loading_gif(self):
        """Removes the loading gif from the next frame location"""
        self.model.remove_widget(self.loading)
        self.loading.hide()

    def mute_all_streams(self):
        """Toggles the audio of all the players."""
        is_mute_checked = self.actions[MUTE_CHECKBOX].isChecked()
        self.model.mute_all_streams(is_mute_checked)

    def export_streams_to_clipboard(self):
        """Exports all streams to the users clipboard."""
        text = self.model.export_streams_to_clipboard()
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        clipboard.setText(text, mode=clipboard.Clipboard)

    def import_streams_from_clipboard(self):
        """Imports all streams from the users clipboard."""
        streams = QtWidgets.QApplication.clipboard().text().rsplit("\n")

        for stream in streams:
            self.add_new_stream(stream_url=stream)

    def add_new_stream(self, *args, stream_url=None, stream_quality=cfg[CONFIG_QUALITY]):
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

        # Run the rest on a separate thread to be able to show the loading feedback
        # Also helps a lot with lag
        threading.Thread(target=self._add_new_stream, args=(stream_url, stream_quality)).start()

    def _add_new_stream(self, stream_url=None, stream_quality=cfg[CONFIG_QUALITY]):
        """Fetches qualities and if possible adds a frame to the main window."""
        try:
            stream_options = self.model.get_stream_options(stream_url)

            # If the stream is not currently broadcasting, 'stream_options'
            # will be an empty list.
            if not stream_options:
                raise streamlink.exceptions.NoStreamsError(stream_url)

            if stream_quality not in stream_options:
                self.fail_add_stream.emit(
                    AddStreamError.DEFAULT_QUALITY_MISSING,
                    (
                        stream_options,
                        stream_url,
                        stream_quality
                    )
                )
                return

            self.add_frame.emit(stream_url, stream_options, stream_quality, self.model.grid.coordinates)

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
                    textwrap.dedent(
                        """
                        Could not open stream!
                        The provided URL is supported, but could not be opened.
                        Check for spelling mistakes!
                        """
                    )
                )
            )

        except streamlink.exceptions.NoStreamsError:
            self.fail_add_stream.emit(
                AddStreamError.OTHER,
                (
                    "Error",
                    textwrap.dedent(
                        """
                        Could not open stream: No streams was found.
                        Is the stream running?
                        """
                    )
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

    def __bind_view_to_action(self, view, action, toggled=False):
        return self.ui.findChild(QtCore.QObject, view).toggled.connect(action) if toggled else self.ui.findChild(
            QtCore.QObject, view).triggered.connect(action)

    def _get_user_quality_preference(self, stream_options):
        """Prompts the user to select what quality they want on the stream."""
        filtered_qualities = LiveStreamContainer.filtered_quality_options(
            stream_options
        )

        return QtWidgets.QInputDialog.getItem(
            self,
            "Stream Quality option",
            textwrap.dedent(
                """
                The default stream quality option could not be used.
                Please select another one:
                """
            ),
            reversed(filtered_qualities)
        )


def main():
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if str(e) == "no function 'libvlc_new'":
            sys.exit(textwrap.dedent(
                """
                Crap! Could not call some of the VLC functions...
                Be a darling and check that you've installed libVLC 3.0 correctly <3
                """
            ))

        sys.exit(textwrap.dedent(
            """
            Crap! You've encountered the following error: {error}
            Post an issue about it in the GitHub repo and someone will help you asap! <3
            """.format(error=str(e))
        ))
