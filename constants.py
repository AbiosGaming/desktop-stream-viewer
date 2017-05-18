#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Signals and constants used in the application."""

MUTE_CHECKBOX = 'mute_checkbox'
EXPORT_STREAMS_TO_CLIPBOARD = 'ExportStreamsToClipboard'
IMPORT_STREAMS_FROM_CLIPBOARD = 'ImportStreamsFromClipboard'
MUTE_ALL_STREAMS = 'MuteAllStreams'
ADD_NEW_STREAM = 'AddNewStream'
SETTINGS_MENU = 'Settings'
BUTTONBOX = 'buttonBox'
BUFFER_SIZE = 'bufferSize'
RECORD_SETTINGS = 'buffer'
QUALITY_SETTINGS = 'qualityBox'
MUTE_SETTINGS = 'mute'
ADD_NEW_SCHEDULED_STREAM = "AddNewScheduledStream"
EXPORT_STREAMS_TO_CLIPBOARD = 'ExportStreamsToClipboard'
LOAD_STREAM_HISTORY = 'LoadStreamsFromHistory'
BUTTON_PLAY = 'QPushButton#pause_button {background-color: transparent; border-image: url(ui/res/pause2.png); background: none; border: none; background-repeat: none;}'
BUTTON_PAUSE = 'QPushButton#pause_button {background-color: transparent; border-image: url(ui/res/play1.png); background: none; border: none; background-repeat: none;}'
CONFIG_FILE = 'config.json'
CONFIG_MUTE = 'mute'
CONFIG_QUALITY = 'quality'
CONFIG_BUFFER_STREAM = 'buffer_stream'
CONFIG_BUFFER_SIZE = 'buffer_size'
CONFIG_DEFAULT_VALUES = {
    CONFIG_MUTE: False,
    CONFIG_QUALITY: "best",
    CONFIG_BUFFER_STREAM: True,
    CONFIG_BUFFER_SIZE: 100
}
FRAME_SELECT_STYLE = """QFrame
                        {
                            border-style: outset;
                            border-width: 2px;
                            border-color: blue;
                        }
                        """
HISTORY_FILE = 'history.txt'
