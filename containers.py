# -*- coding: utf-8 -*-
import copy
import ctypes
import callbacks as cb
from abc import ABC, abstractmethod
from collections import deque
from streamlink import Streamlink

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
    """
    def __init__(self, vlc_instance, stream_info, buffer_length=200):
        super().__init__(vlc_instance)

        self.session = Streamlink()
        self.streams = self.session.streams(stream_info["url"])
        self.stream = self.streams[stream_info["quality"]].open()
        self.buffer = deque(maxlen=buffer_length)

        self.update_info(stream_info["url"], stream_info["quality"])

    def open(self):
        """Called by libVLC upon opening the media. Not currently used."""
        return 0

    def read(self, buf, length):
        """Called by libVLC upon requesting more data.

        Reads 'length' video data directly from the stream, as well as caches
        it away in the buffer accordingly.
        """
        data = self.stream.read(length)
        self.buffer.append(data)

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

    def update_info(self, url, quality):
        """Updates the URL, current quality as well as available qualities of
        the stream.
        """
        self.url = url
        self.quality = quality

        self.all_qualities = sorted(self.streams.keys())
        self.qualities = [opt for opt in self.all_qualities if not opt[0].isalpha()]

    def change_stream_quality(self, quality):
        """Changes the streams quality."""
        self.stream = self.streams[quality].open()
        self.buffer.clear()

        self.quality = quality

class RewindedStreamContainer(StreamContainer):
    """This class represents a **rewinded** stream and contains all information
    regarding it's media.

    The RewindedStreamContainer takes another streams buffer, copies that and
    pulls all of it's video data directly from the copied buffer.
    """
    def __init__(self, vlc_instance, stream_buffer):
        super().__init__(vlc_instance)

        self.buffer = copy.deepcopy(stream_buffer)

    def open(self):
        """Called by libVLC upon opening the media. Not currently used."""
        return 0

    def read(self, buf, length):
        """Called by libVLC upon requesting more data.

        Reads 'length' video data directly from the copied buffer.
        """
        # If we've played the whole buffer, send EOS (End of Stream).
        if len(self.buffer) == 0:
            return 0

        data = self.buffer.popleft()
        for i, val in enumerate(data):
            buf[i] = val

        return len(data)

    def seek(self):
        """Called by libVLC upon seeking in the media."""
        return 0

    def close(self):
        """Called by libVLC upon closing the media."""
        return 0
