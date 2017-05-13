#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Signals and constants used in the application."""

MUTE_CHECKBOX = 'mute_checkbox'
MUTE_ALL_STREAMS = 'mute_all_streams'
ADD_NEW_STREAM = 'add_new_stream'
EXPORT_STREAMS_TO_CLIPBOARD = 'ExportStreamsToClipboard'
IMPORT_STREAMS_FROM_CLIPBOARD = 'ImportStreamsFromClipboard'
MUTE_ALL_STREAMS = 'MuteAllStreams'
ADD_NEW_STREAM = 'AddNewStream'
EXPORT_STREAMS_TO_CLIPBOARD = 'ExportStreamsToClipboard'
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
SLIDER_MAX_VALUE = 10000  # The maxvalue in the ui for the rewind slider
FRAME_SELECT_STYLE = """QFrame
                        {
                            border-style: outset;
                            border-width: 2px;
                            border-color: blue;
                        }"""
