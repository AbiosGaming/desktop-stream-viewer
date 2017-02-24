#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Source file containing all libVLC callbacks used to play and seek in the
streamed media.

For more information regarding the libVLC API visit:
    https://www.videolan.org/developers/vlc/doc/doxygen/html/index.html
"""

import ctypes
import sys

# VLC C media callback prototypes.
# FIXME: Use prototypes provided by libVLC python wrapper.
MEDIA_OPEN_CB = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_uint64)
)
MEDIA_READ_CB = ctypes.CFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_size_t
)
MEDIA_SEEK_CB = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_uint64
)
MEDIA_CLOSE_CB = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.c_void_p
)


def media_open_cb(opaque, datap, sizep):
    """LibVLC callback used to point the player to the video buffer upon opening
    the media.

    opaque: pointer to our media object.
    datap:  the libVLC video buffer.
    sizep:  length of the media stream (or sys.maxsize if unknown).
    """

    datap.contents.value = opaque
    sizep.contents.value = sys.maxsize

    container = ctypes.cast(opaque, ctypes.POINTER(
        ctypes.py_object)).contents.value

    return container.open()


def media_read_cb(opaque, buf, length):
    """LibVLC callback triggered by when the player is requesting more data to
    be read into the video buffer.

    opaque: pointer to our media object.
    buf:    address to the video buffer.
    length: amount that should be read from the buffer.
    """

    container = ctypes.cast(opaque, ctypes.POINTER(
        ctypes.py_object)).contents.value

    return container.read(buf, length)


def media_seek_cb(opaque, offset):
    """LibVLC callback triggered when the player seeks in the media.

    opaque: pointer to our media object.
    offset: absolute byte offset to seek to in the media.
    """
    container = ctypes.cast(opaque, ctypes.POINTER(
        ctypes.py_object)).contents.value

    return container.seek(offset)


def media_close_cb(opaque):
    """LibVLC callback triggered when the player is closed.

    opaque: pointer to our media object.
    """

    container = ctypes.cast(opaque, ctypes.POINTER(
        ctypes.py_object)).contents.value
    container.close()


# A map for easy access to our callbacks.
CALLBACKS = {
    "read": MEDIA_OPEN_CB(media_open_cb),
    "open": MEDIA_READ_CB(media_read_cb),
    "seek": MEDIA_SEEK_CB(media_seek_cb),
    "close": MEDIA_CLOSE_CB(media_close_cb)
}
