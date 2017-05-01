# -*- coding: utf-8 -*-

import platform
import sys

from PyQt5 import QtWidgets, QtCore
from containers import LiveStreamContainer, RewindedStreamContainer

class _VideoFrame(QtWidgets.QFrame):
    """An class representing a QFrame object containing a libVLC media player.

    Args:
        vlc_instance: VLC instance object.
    """
    def __init__(self, vlc_instance):
        super(_VideoFrame, self).__init__()
        self.player = vlc_instance.media_player_new()

        self.is_muted = False

        if platform.system() == "Linux":
            self.player.set_xwindow(self.winId())
        elif platform.system() == "Windows":
            self.player.set_hwnd(self.winId())
        else:
            sys.exit("Platform unsupported.")

    def setup_actions(self):
        """Sets up the actions in the context menu provided."""
        self.mute_action = self.context_menu.addAction("Mute stream")
        self.mute_action.setCheckable(True)

        if self.player.audio_get_mute():
            self.mute_action.setChecked(True)
        else:
            self.mute_action.setChecked(False)

        self.context_menu.addSeparator()

    def check_actions(self, event):
        """Checks if the user action matches any of the actions."""
        user_action = self.context_menu.exec_(self.mapToGlobal(event.pos()))

        if user_action == self.mute_action:
            if self.player.audio_get_mute():
                self.player.audio_set_mute(False)
                self.is_muted = False
            else:
                self.player.audio_set_mute(True)
                self.is_muted = True

        return user_action

    def context_menu(self, event):
        """Opens a menu upon right clicking the frame."""
        self.context_menu = QtWidgets.QMenu(parent=self)

    def mouse_release(self, event):
        """Toggles playback of a stream. How the playback itself is done is
        handeled by the deriving class.
        """
        if event.button() == QtCore.Qt.LeftButton:
            if self.player.is_playing():
                self.player.pause()
            else:
                self.player.play()

class LiveVideoFrame(_VideoFrame):
    """A class representing a VideoFrame containing a **live** stream.

    Args:
        vlc_instance: VLC instance object.
        stream_info: Dictionary containing the URL ('url') as well as the
            quality ('quality') of the requested stream.
    """
    def __init__(self, vlc_instance, stream_info):
        super(LiveVideoFrame, self).__init__(vlc_instance)
        self.stream = LiveStreamContainer(vlc_instance, stream_info)
        self.player.set_media(self.stream.media)
        self.player.play()

    def setup_actions(self):
        super(LiveVideoFrame, self).setup_actions()
        quality_submenu = QtWidgets.QMenu("Change quality", parent=self)

        # Add the quality options to the submenu.
        self.quality_actions = []
        for opt in self.stream.filtered_qualities:
            action = quality_submenu.addAction(opt)
            action.setCheckable(True)

            if opt == self.stream.quality:
                action.setChecked(True)
            else:
                action.setChecked(False)

            self.quality_actions.append(action)

        self.context_menu.addMenu(quality_submenu)

    def check_actions(self, event):
        user_action = super(LiveVideoFrame, self).check_actions(event)

        for quality_action in self.quality_actions:
            quality = quality_action.text()
            if user_action == quality_action and quality != self.stream.quality:
                self.change_stream_quality(quality)

    def contextMenuEvent(self, event):
        super(LiveVideoFrame, self).context_menu(event)
        self.setup_actions()

        user_action = self.check_actions(event)

    def mouseReleaseEvent(self, event):
        """Toggles playback of the live stream."""
        super(LiveVideoFrame, self).mouse_release(event)

    def change_stream_quality(self, quality):
        self.player.stop()
        self.stream.change_stream_quality(quality)
        self.player.play()

class RewindedVideoFrame(_VideoFrame):
    """A class representing a VideoFrame containing a **rewinded** stream.

    Args:
        vlc_instance: VLC instance object.
        stream_buffer: A reference to the buffer that should be copied and
            played from.
    """
    def __init__(self, vlc_instance, stream_buffer):
        super(RewindedVideoFrame, self).__init__(vlc_instance)
        self.stream = RewindedStreamContainer(vlc_instance, stream_buffer)
        self.player.set_media(self.stream.media)
        self.player.play()

    def contextMenuEvent(self, event):
        super(RewindedVideoFrame, self).context_menu(event)
        self.setup_actions()

        user_action = self.check_actions(event)

    def mouseReleaseEvent(self, event):
        """Toggles playback of the rewinded stream."""
        super(RewindedVideoFrame, self).mouse_release(event)
