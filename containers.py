# -*- coding: utf-8 -*-
import ctypes
from abc import ABC, abstractmethod
from collections import deque

import callbacks as cb
from constants import CONFIG_BUFFER_SIZE, CONFIG_BUFFER_STREAM
from config import cfg


class StreamContainer(ABC):
    """An abstract class representing stream data. This class exposes the
    neccesary functions for libVLC playback.

    Args:
        vlc_instance (libvlc_instance_t*): The vlc instance.
        stream_info (dict): Holds information about stream url and stream quality.

    Attributes:
        media (libvlc_media_t*): The media object that vlc uses, includes callbacks.
    """
    def __init__(self, vlc_instance):
        # Cast this container to a c pointer to use in the callbacks
        self._opaque = ctypes.cast(ctypes.pointer(
            ctypes.py_object(self)), ctypes.c_void_p)

        # Create the vlc callbacks, these will in turn call the methods defined
        # in this container
        self.media = vlc_instance.media_new_callbacks(
            cb.CALLBACKS["read"],
            cb.CALLBACKS["open"],
            cb.CALLBACKS["seek"],
            cb.CALLBACKS["close"],
            self._opaque
        )

    @abstractmethod
    def open(self):
        """The open event is triggered after media_open_cb in libVLC."""
        pass

    @abstractmethod
    def read(self, buf, length):
        """Read reads from the stream and writes this to the buf according to
        the length parameter.

        Args:
            buf (LP_c_char):    char pointer to the video buffer.
            length:             amount that should be read from the buffer.
        """
        pass

    @abstractmethod
    def seek(self, offset):
        """Seeks in the stream according to the offset.

        Args:
            offset: absolute byte offset to seek to in the media.
        """
        pass

    @abstractmethod
    def close(self):
        """Close calls all neccesary functions to close down the container."""
        pass


class LiveStreamContainer(StreamContainer):
    """This class representas a **live** stream and contains all information
    regarding it's media.

    The LiveStreamContainer pulls all of it's video data directly from the
    livestream itself, while at the same time caching away previous data in a
    buffer.

    Add attribute on_stream_end() to bind a callback for when the stream has ended.
    Note: Do not try to remove this Container in that callback, as it will not work.
    """

    def __init__(self, vlc_instance, url, streams, quality, buffer_length=cfg[CONFIG_BUFFER_SIZE]):

        super().__init__(vlc_instance)
        # Use default value for buffer_length if none specified
        if not buffer_length:
            buffer_length = cfg[CONFIG_BUFFER_SIZE]
        self.streams = streams
        self.stream = self.streams[quality].open()
        self.buffer = deque(maxlen=buffer_length)

        self.update_info(url, quality)

    def open(self):
        """Called by libVLC upon opening the media. Not currently used."""
        return 0

    def read(self, buf, length):
        """Called by libVLC upon requesting more data.

        Reads 'length' video data directly from the stream, as well as caches
        it away in the buffer accordingly.
        """
        data = self.stream.read(length)
        if cfg[CONFIG_BUFFER_STREAM]:
            self.buffer.append(data)
        data_len = len(data)

        # if the stream has ended invoke on_stream_end
        if data_len == 0:
            try:
                self.on_stream_end()
            except AttributeError:
                pass

        for i, val in enumerate(data):
            buf[i] = val

        return len(data)

    def seek(self, offset):
        """Called by libVLC upon seeking in the media."""
        return 0

    def close(self):
        """Called by libVLC upon closing the media."""
        self.stream.close()
        return 0

    @staticmethod
    def quality_options(streams):
        return sorted(streams.keys())

    def update_info(self, url, quality):
        """Updates the current quality as well as available qualities of
        the stream.
        """
        self.url = url
        self.quality = quality

        self.all_qualities = LiveStreamContainer.quality_options(self.streams)

    def change_stream_quality(self, quality):
        """Changes the streams quality."""
        self.stream.close()
        self.stream = self.streams[quality].open()
        self.buffer.clear()

        self.quality = quality

    def refresh(self):
        self.change_stream_quality(self.quality)


class RewindedStreamContainer(StreamContainer):
    """This class represents a **rewinded** stream and contains all information
    regarding it's media.

    The RewindedStreamContainer takes another streams buffer, copies that and
    pulls all of it's video data directly from the copied buffer.
    """

    def __init__(self, vlc_instance, stream_buffer):
        super().__init__(vlc_instance)

        self.buffer = list(stream_buffer)
        self.curr = 0
        self.on_seek = None

    def open(self):
        """Called by libVLC upon opening the media. Not currently used."""
        return 0

    def read(self, buf, length):
        """Called by libVLC upon requesting more data.

        Reads 'length' video data directly from the copied buffer.
        """
        # If we have no data to read HACK:
        if self.curr >= len(self.buffer):
            # Force vlc to continue reading some arbitrary data
            # as we may want to seek
            buf[0] = 1
            return 2

        data = self.buffer[self.curr]
        for i, val in enumerate(data):
            buf[i] = val

        self.curr = (self.curr + 1)

        return len(data)

    def seek(self, offset):
        """Called by libVLC upon seeking in the media."""
        # Set the current pointer to the correct location
        self.curr = int((offset / 2 ** 62) * self.curr)
        if self.on_seek is not None:
            self.on_seek(offset)
        return 0

    def close(self):
        """Called by libVLC upon closing the media."""
        return 0
