# -*- coding: utf-8 -*-

import platform
import sys

from PyQt5 import QtWidgets, QtCore, uic

import vlc
from constants import FRAME_SELECT_STYLE, SLIDER_MAX_VALUE
from containers import LiveStreamContainer, RewindedStreamContainer
from utils import OS


class _VideoFrame(QtWidgets.QFrame):
    """An class representing a QFrame object containing a libVLC media player.

    Args:
        vlc_instance: VLC instance object.
    """

    def __init__(self, parent):
        super(_VideoFrame, self).__init__(parent)
        # Opengl performs better on windows, which is odd
        self.vlc_instance = vlc.Instance(
            "--no-xlib " +         # Turn off XInitThreads()
            "--vout=opengl " +     # Force OpenGL as vout module for better performance on windows
            "--avcodec-threads=0"  # Number of threads used for decoding, 0 meaning auto
        )
        self.player = self.vlc_instance.media_player_new()
        # Remove input handling from vlc, and give it back
        self.player.video_set_mouse_input(False)
        # key also have to be taken back for mouse input
        self.player.video_set_key_input(False)

        # Build the ui for this videoFrame
        self.setup_ui()

        self.is_muted = False
        self.selected = False

    def setup_ui(self):
        uic.loadUi("ui/frame.ui", self)
        # Find the draw area
        self.draw_area = self.findChild(QtCore.QObject, "drawArea")
        # Connect the playback toggle to the toolbox
        # TODO: Some other solution
        self.findChild(QtCore.QObject, "toolButton").clicked.connect(self.toggle_playback)
        # Bind the player
        # Get the current operating system
        os = platform.system().lower()
        if os == OS.LINUX:
            self.player.set_xwindow(self.draw_area.winId())
        elif os == OS.WINDOWS:
            self.player.set_hwnd(self.draw_area.winId())
        elif os == OS.MAC_OS:
            self.player.set_nsobject(int(self.draw_area.winId()))
        else:
            sys.exit("Platform unsupported")

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

    def mouseReleaseEvent(self, event):
        """Toggles playback of a stream when the mouse is released."""
        if event.button() == QtCore.Qt.LeftButton:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                self.toggle_select()
            else:
                self.toggle_playback()

    def mouseDoubleClickEvent(self, event):
        """Toggles fullscreen mode on the current stream."""
        if event.modifiers() != QtCore.Qt.ControlModifier:
            self._fullscreen(self)

    def context_menu(self, event):
        """Opens a menu upon right clicking the frame."""
        self.context_menu = QtWidgets.QMenu(parent=self)

    def toggle_playback(self):
        """Toggles playback of a stream."""
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def delete_stream(self):
        """Deletes videoframe/stream"""
        self.player.stop()
        self.player.release()
        self._delete_stream(self)

    def select(self):
        self.selected = True
        self.setStyleSheet(FRAME_SELECT_STYLE)
        self._swap(self)

    def deselect(self):
        self.selected = False
        self.setStyleSheet("")

    def toggle_select(self):
        if self.selected:
            self.deselect()
        else:
            self.select()


class LiveVideoFrame(_VideoFrame):
    """A class representing a VideoFrame containing a **live** stream.

    Args:
        vlc_instance: VLC instance object.
    """

    stream_end = QtCore.pyqtSignal()

    def __init__(self, parent, stream_url, stream_options, quality):
        super(LiveVideoFrame, self).__init__(parent)
        self.stream = LiveStreamContainer(self.vlc_instance, stream_url, stream_options, quality)
        self.stream.on_stream_end = self.stream_end.emit
        self.stream_end.connect(self.on_stream_end)
        self.player.set_media(self.stream.media)
        self.player.play()

        # Setup attribute used for the rewinded stream
        self.rewinded = None

    def setup_ui(self):
        super(LiveVideoFrame, self).setup_ui()

        # Hide the slider
        # TODO: Perhaps it should not even be created?
        # is there a huge overhead for QtWidgets?
        self.findChild(QtCore.QObject, "seek_slider").hide()
        # Connect the rewind button
        self.findChild(QtCore.QObject, "rewind_button").clicked.connect(self.rewind)

        # Store stream_end_label
        self.stream_end_label = self.findChild(QtWidgets.QLabel, "end_label")

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

    def resizeEvent(self, event):
        rect = self.geometry()
        label_rect = self.stream_end_label.geometry()
        self.stream_end_label.move(
            rect.width() / 2 - label_rect.width() / 2,
            rect.height() / 2 - label_rect.height() / 2
        )

    def on_stream_end(self):
        self.stream_end_label.show()

    def contextMenuEvent(self, event):
        super(LiveVideoFrame, self).context_menu(event)
        self.setup_actions()

        user_action = self.check_actions(event)

    def change_stream_quality(self, quality):
        self.player.stop()
        self.stream.change_stream_quality(quality)
        self.player.play()

    def rewind(self):
        if self.rewinded is None:
            self.rewinded = QtWidgets.QMainWindow(parent=self)
            self.rewinded.setWindowTitle("Rewinded Stream")
            self.rewinded.frame = RewindedVideoFrame(self.rewinded, self.stream.buffer)
            # Set events:
            self.rewinded.closeEvent = self.close_rewinded
            self.rewinded.frame._fullscreen = self.fullscreen_rewinded

            self.rewinded.setCentralWidget(self.rewinded.frame)
            self.rewinded.show()
            # Init values
            self.rewinded.is_fullscreen = False

    # Following functions belong to the rewinded window

    def close_rewinded(self, _):
        """Called whenever the rewinded window is closed"""
        # First stop and release the media player
        self.rewinded.frame.player.stop()
        self.rewinded.frame.player.release()
        # Stop the timer
        self.rewinded.frame.timer.stop()
        # To remove the rewinded video window;
        # Let the garbage collector do its magic
        self.rewinded = None

    def fullscreen_rewinded(self, _):
        """Called whenever the rewinded window is to be fullscreened"""
        if self.rewinded.is_fullscreen:
            self.rewinded.setWindowState(self.rewinded.window_state)
            self.rewinded.is_fullscreen = False
        else:
            self.rewinded.window_state = self.windowState()
            self.rewinded.showFullScreen()
            self.rewinded.is_fullscreen = True


class RewindedVideoFrame(_VideoFrame):
    """A class representing a VideoFrame containing a **rewinded** stream.

    Args:
        vlc_instance: VLC instance object.
        stream_buffer: A reference to the buffer that should be copied and
            played from.
    """

    def __init__(self, parent, stream_buffer):
        super(RewindedVideoFrame, self).__init__(parent)
        self.stream = RewindedStreamContainer(self.vlc_instance, stream_buffer)
        self.stream.on_seek = self.on_seek
        self.player.set_media(self.stream.media)
        self.player.play()

    def setup_ui(self):
        super(RewindedVideoFrame, self).setup_ui()
        # Find the slider
        self.slider = self.findChild(QtCore.QObject, "seek_slider")
        # Seek when the slider is released
        self.slider.pressed = False
        self.slider.sliderReleased.connect(self.scrub)
        self.slider.sliderPressed.connect(self.slider_pressed)
        # Hide the rewind button:
        self.findChild(QtCore.QObject, "rewind_button").hide()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_slider_value)
        self.timer.start(1)

    def on_seek(self, offset):
        """Called when the underlying media_player is trying to seek
        """
        self.slider.pressed = False

    def contextMenuEvent(self, event):
        super(RewindedVideoFrame, self).context_menu(event)
        self.setup_actions()
        user_action = self.check_actions(event)

    def slider_pressed(self):
        """Called whenever the slider is pressed
        Consequently stops the slider value from getting updated
        """
        self.slider.pressed = True

    def scrub(self):
        """Called whenever the slider is released, which is followed by a scrub
        """
        self.player.set_position(self.slider.value() / SLIDER_MAX_VALUE)

    def update_slider_value(self):
        """Updates the slider with a guesstimate of video position
        """
        # Some guessing magic to get the timing right, kind of works for 480p30
        percentage_played = self.player.get_time() / (145 * len(self.stream.buffer))
        if not self.slider.pressed:
            self.slider.setValue(percentage_played * SLIDER_MAX_VALUE)
