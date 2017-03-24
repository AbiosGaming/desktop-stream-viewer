# -*- coding: utf-8 -*-
import copy
import containers.stream_container import StreamContainer

class RewindedStreamContainer(StreamContainer):
    """This class represents a **rewinded** stream and contains all information
    regarding it's media.
    
    The RewindedStreamContainer takes another streams buffer, copies that and
    pulls all of it's video data directly from the copied buffer.
    """
    def __init__(self, vlc_instance, stream_info, stream_buffer):
        super().__init__(vlc_instance, stream_info)

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
