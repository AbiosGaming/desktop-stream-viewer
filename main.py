#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import streamlink
# Qt imports
from PyQt5 import QtWidgets, uic, QtCore

import vlc
from constants import (
    MUTE_CHECKBOX, MUTE_ALL_STREAMS, EXPORT_STREAMS_TO_CLIPBOARD, ADD_NEW_STREAM,
    CONFIG_QUALITY
)
from containers import LiveStreamContainer
from videoframegrid import VideoFrameGrid
from config import cfg


class ApplicationWindow(QtWidgets.QMainWindow):
    """The main GUI window."""

    def __init__(self):
        super(ApplicationWindow, self).__init__(None)
        self.setup_ui()

        self.vlc_instance = vlc.Instance("--no-xlib")
        self.streamlink_session = streamlink.Streamlink()

        # Used when moving two frames
        self.selected_frame = None

    def setup_ui(self):
        """Loads the main.ui file and sets up the window and grid."""
        self.ui = uic.loadUi("ui/main.ui")
        self.grid = VideoFrameGrid()

        self.container = self.ui.findChild(QtCore.QObject, "container")
        self.container.addLayout(self.grid)

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

    def add_new_stream(self, *args, stream_url=None, stream_quality=cfg[CONFIG_QUALITY]):
        """Adds a new player for the specified stream in the grid."""
        if not stream_url:
            stream_url, ok = QtWidgets.QInputDialog.getText(self, "Stream input", "Enter the stream URL:")

            if not ok:
                return

        try:
            stream_options = self.streamlink_session.streams(stream_url)

            if stream_quality not in stream_options:
                stream_quality, ok = self._get_user_quality_preference(stream_options)

                if not ok:
                    return

            self.setup_videoframe(stream_options, stream_quality)

        except streamlink.exceptions.NoPluginError:
            error_window = QtWidgets.QMessageBox().warning(
                self,
                "Error",
                "Could not open stream: The provided URL is not supported"
            )

            self.add_new_stream()

    def _get_user_quality_preference(self, stream_options):
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

    def setup_videoframe(self, stream_options, quality):
        """Sets up a videoframe and with the provided stream information."""
        self.grid.add_new_videoframe(self.vlc_instance, stream_options, quality)


def main():
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
