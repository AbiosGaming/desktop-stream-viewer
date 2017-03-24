# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from containers.callbacks import callbacks as cb
import ctypes

class StreamContainer(ABC):
    """An abstract class representing stream data. This class exposes the
    neccesary functions for libVLC playback.
    
    Args:
        vlc_instance (libvlc_instance_t*): The vlc instance.
        stream_info (dict): Holds information about stream url and stream quality.
    
    Attributes:
        media (libvlc_media_t*): The media object that vlc uses, includes callbacks.
    """
    def __init__(self, vlc_instance, stream_info):
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

        self.stream_info = stream_info

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
