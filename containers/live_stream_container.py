# -*- coding: utf-8 -*-
import streamlink
from collections import deque
from containers.stream_container import StreamContainer

class LiveStreamContainer(StreamContainer):
    """This class representas a **live** stream and contains all information 
    regarding it's media.

    The LiveStreamContainer pulls all of it's video data directly from the 
    livestream itself, while at the same time caching away previous data in a 
    buffer.
    """
    def __init__(self, vlc_instance, stream_info, buffer_length=200):
        super().__init__(vlc_instance, stream_info)

        streams = streamlink.streams(stream_info["url"])
        self._stream = streams[stream_info["quality"]].open()
        self.buffer = deque(maxlen=buffer_length)

    def open(self):
        """Called by libVLC upon opening the media. Not currently used."""
        return 0

    def read(self, buf, length):
        """Called by libVLC upon requesting more data. 
        
        Reads 'length' video data directly from the stream, as well as caches
        it away in the buffer accordingly. 
        """
        data = self._stream.read(length)
        self.buffer.append(data)

        for i, val in enumerate(data):
            buf[i] = val

        return len(data)

    def seek(self, offset):
        """Called by libVLC upon seeking in the media."""
        return 0

    def close(self):
        """Called by libVLC upon closing the media."""
        self._stream.close()
        return 0
