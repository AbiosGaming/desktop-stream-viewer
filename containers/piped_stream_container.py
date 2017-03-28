# -*- coding: utf-8 -*-
import streamlink
import threading
from streamlink.utils.named_pipe import NamedPipe
from collections import deque
from containers.stream_container import StreamContainer

class PipedStreamContainer(StreamContainer):
    """This class representas a **live** stream and contains all information
    regarding it's media.

    The BufferedStreamContainer pulls all of it's video data directly from the
    livestream itself, while at the same time caching away previous data in a
    buffer.
    """
    def __init__(self, vlc_instance, stream_info, pipename, buffer_length=200):
        super().__init__(vlc_instance, stream_info)

        self.pipe = NamedPipe(pipename)
        self.media = vlc_instance.media_new("stream://\\\\\\.\\pipe\\" + pipename)
        streams = streamlink.streams(stream_info["url"])
        self._stream = streams[stream_info["quality"]].open()
        # self.buffer = deque(maxlen=buffer_length)
        self.readWorker = ReadWorker(self)
        # Only used by UNIX systems (this is handled within the named pipe)
        self.pipe.open("wb")
        self.readWorker.start()

    def open(self):
        """"""
        # Not used yet
        pass

    def read(self):
        """Called by the worker thread to read more data into vlc.
        """
        data = self._stream.read(8192) # Same buffer size as the named pipe size
        # self.buffer.append(data)
        self.pipe.write(data)

        return len(data)

    def seek(self, offset):
        """Called by libVLC upon seeking in the media."""
        # Not used yet
        pass

    def close(self):
        """Called by libVLC upon closing the media."""
        # Not used yet
        self._stream.close()
        self.pipe.close()

class ReadWorker(threading.Thread):
    def __init__(self, container):
        threading.Thread.__init__(self)
        self.container = container

    def run(self):
        while True:
            self.container.read()
