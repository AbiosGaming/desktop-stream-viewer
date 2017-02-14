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
MediaOpenCb = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_uint64)
)
MediaReadCb = ctypes.CFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_size_t
)
MediaSeekCb = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_uint64
)
MediaCloseCb = ctypes.CFUNCTYPE(
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

    return 0

def media_read_cb(opaque, buf, length):
    """LibVLC callback triggered by when the player is requesting more data to
    be read into the video buffer.

    opaque: pointer to our media object.
    buf:    address to the video buffer.
    length: amount that should be read from the buffer.
    """

    stream = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
    data = stream.read(length)

    for i in range(len(data)):
        buf[i] = data[i]

    return len(data)

def media_seek_cb(opaque, offset):
    """LibVLC callback triggered when the player seeks in the media.

    opaque: pointer to our media object.
    offset: absolute byte offset to seek to in the media.
    """
    
    return 0

def media_close_cb(opaque):
    """LibVLC callback triggered when the player is closed.
    
    opaque: pointer to our media object.
    """

    stream = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
    stream.close()

# A map for easy access to our callbacks.
callbacks = {
    "read": MediaOpenCb(media_open_cb),
    "open": MediaReadCb(media_read_cb),
    "seek": MediaSeekCb(media_seek_cb),
    "close": MediaCloseCb(media_close_cb)
}
