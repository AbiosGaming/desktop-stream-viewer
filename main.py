#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import textwrap
import threading

from datetime import datetime

import streamlink
# Qt imports
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QDialog

from config import cfg
from constants import (
    MUTE_CHECKBOX, MUTE_ALL_STREAMS, EXPORT_STREAMS_TO_CLIPBOARD,
    IMPORT_STREAMS_FROM_CLIPBOARD, ADD_NEW_STREAM, CONFIG_MUTE,
    CONFIG_QUALITY, CONFIG_BUFFER_STREAM, CONFIG_BUFFER_SIZE,
    SETTINGS_MENU, BUTTONBOX, QUALITY_SETTINGS, MUTE_SETTINGS,
    RECORD_SETTINGS, BUFFER_SIZE, ADD_NEW_SCHEDULED_STREAM,
    LOAD_STREAM_HISTORY
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
        with open("ui/styles.qss", "r") as f:
            self.setStyleSheet(f.read())
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
        self.__bind_view_to_action(ADD_NEW_SCHEDULED_STREAM, self.add_new_scheduled_stream)
        self.__bind_view_to_action(IMPORT_STREAMS_FROM_CLIPBOARD, self.import_streams_from_clipboard)
        self.__bind_view_to_action(SETTINGS_MENU, self.show_settings)
        self.__bind_view_to_action(LOAD_STREAM_HISTORY, self.stream_history)

        self.recent_menu = self.ui.findChild(QtCore.QObject, "menuRecent")

        # Create the loading gear but dont add it to anywhere, just save it
        self.setup_loading_gif()

        self.ui.show()

    def setup_videoframe(self, stream_url, stream_options, quality):
        """Sets up a videoframe and with the provided stream information."""
        self.model.add_new_videoframe(stream_url, stream_options, quality)
        # Remove the loading feedback
        self.hide_loading_gif()
        # Update recent meny option
        self.update_recent()

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

    def show_settings(self):
        """Shows a dialog containing settings for DSW"""
        self.dialog = QDialog(self)
        self.dialog.ui = uic.loadUi("ui/dialog.ui", self.dialog)
        self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dialog.findChild(QtCore.QObject, BUTTONBOX) \
            .accepted.connect(self.generate_conf)
        if cfg[CONFIG_BUFFER_STREAM]:
            self.dialog.findChild(QtCore.QObject, RECORD_SETTINGS).setChecked(True)
        if cfg[CONFIG_MUTE]:
            self.dialog.findChild(QtCore.QObject, MUTE_SETTINGS).setChecked(True)
        index = self.dialog.findChild(QtCore.QObject, QUALITY_SETTINGS).findText(cfg[CONFIG_QUALITY])
        self.dialog.findChild(QtCore.QObject, QUALITY_SETTINGS).setCurrentIndex(index)
        self.dialog.findChild(QtCore.QObject, BUFFER_SIZE).setValue(cfg[CONFIG_BUFFER_SIZE])
        self.dialog.show()

    def generate_conf(self):
        """Reads values from settings and generates new config"""
        is_buffer = False
        is_mute = False
        quality = str(self.dialog.findChild(QtCore.QObject, QUALITY_SETTINGS).currentText())
        buffer_size = self.dialog.findChild(QtCore.QObject, BUFFER_SIZE) \
            .value()
        if self.dialog.findChild(QtCore.QObject, RECORD_SETTINGS).isChecked():
            is_buffer = True
        if self.dialog.findChild(QtCore.QObject, MUTE_SETTINGS).isChecked():
            is_mute = True

        # Set new cfg values
        cfg[CONFIG_BUFFER_STREAM] = is_buffer
        cfg[CONFIG_MUTE] = is_mute
        cfg[CONFIG_QUALITY] = quality
        cfg[CONFIG_BUFFER_SIZE] = buffer_size

        try:
            cfg.dump()
        except IOError:
            print("Could not dump config file.")

    def update_recent(self):
        """Updates the recent menu option."""
        self.recent_menu.clear()
        # Only the 30 recently added streams are shown
        for url in self.grid.url_list[:30]:
            action = QtWidgets.QAction(url, parent=self)
            action.triggered.connect(self.add_stream_from_history(action.text()))
            self.recent_menu.addAction(action)

    def add_stream_from_history(self, stream_url):
        def func():
            self.add_new_stream(stream_url)
        return func

    def import_streams_from_clipboard(self):
        """Imports all streams from the users clipboard."""
        streams = QtWidgets.QApplication.clipboard().text().rsplit("\n")

        for stream in streams:
            self.add_new_stream(stream_url=stream)

    def add_new_stream(self, stream_url=None, stream_quality=None):
        """Adds a new player for the specified stream in the grid."""
        if not stream_url:
            stream_url, ok = QtWidgets.QInputDialog.getText(
                self,
                "Stream input",
                "Enter the stream URL:"
            )

            if not ok:
                return

        # Use default quality if not specified
        if not stream_quality:
            stream_quality = cfg[CONFIG_QUALITY]

        # Lower case the stream url for easier handling in future cases
        stream_url = self.model.parse_url(stream_url)

        # Give some feedback to the user
        self.show_loading_gif()

        # Run the rest on a separate thread to be able to show the loading feedback

        # Also helps a lot with lag
        threading.Thread(target=self._add_new_stream, args=(stream_url, stream_quality)).start()

    def add_new_scheduled_stream(self, *args, stream_url=None, stream_quality=cfg[CONFIG_QUALITY]):
        """Schedules a new stream at given time"""
        if not stream_url:
            stream_url, ok1 = QtWidgets.QInputDialog.getText(
                self,
                "Schedule stream",
                "Enter the stream URL:"
            )
        if not ok1:
            return

        inputTime, ok2 = QtWidgets.QInputDialog.getText(
            self,
            "Schedule stream",
            "Time (HH.MM)"
        )

        if not ok2:
            return

        # Add stream after certain delay (factory function)
        def schedule_stream():
            self.model.save_stream_to_history(stream_url)
            self._add_new_stream(stream_url, stream_quality)

        try:
            h, m = inputTime.split(".")
            now = datetime.now()
            runtime = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
            if not runtime > now:
                raise ValueError
            delay = (runtime - now).total_seconds() * 1000
            QtCore.QTimer(self).singleShot(delay, schedule_stream)
            QtWidgets.QMessageBox.information(
                self,
                "Schedule stream",
                "Succesfully scheduled stream at " + h + "." + m
            )

        except ValueError:
            QtWidgets.QMessageBox().warning(
                self,
                "Error!",
                "Not a valid time"
            )

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

            # Save url to stream history
            self.model.save_stream_to_history(stream_url)

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
        qualities = LiveStreamContainer.quality_options(
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
            reversed(qualities)
        )

    def stream_history(self):
        """Starts streaming all streams that were playing when last session was closed."""
        if self.model.stream_history:
            for stream in self.model.stream_history:
                self.add_new_stream(stream)


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
