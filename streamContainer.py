# -*- coding: utf-8 -*-
import callbacks as cb
import streamlink
import ctypes

class StreamContainer(object):
    """Contains all neccesary values for libVLC playback.

    Args:
        vlc_instance (libvlc_instance_t*): The vlc instance.
        stream_info (dict): Holds information about stream url and stream quality.

    Attributes:
        media (libvlc_media_t*): The media object that vlc uses, includes callbacks.
    """
    def __init__(self, vlc_instance, stream_info):
        # Get the stream from streamlink
        streams = streamlink.streams(stream_info["url"])
        self._stream = streams[stream_info["quality"]].open()
        # Cast the stream to a c pointer to use in the callbacks
        self._opaque = ctypes.cast(ctypes.pointer(ctypes.py_object(self._stream)), ctypes.c_void_p)
        # Create the vlc callbacks
        self.media = vlc_instance.media_new_callbacks(
            cb.callbacks["read"],
            cb.callbacks["open"],
            cb.callbacks["seek"],
            cb.callbacks["close"],
            self._opaque
        )
