# -*- coding: utf-8 -*-

import platform
import sys
import webbrowser
import os as os2

from PyQt5 import QtWidgets, QtCore, uic
from urllib.parse import urlparse, urlunparse

import vlc
from constants import (
    FRAME_SELECT_STYLE, CONFIG_MUTE, CONFIG_BUFFER_STREAM
)
from containers import LiveStreamContainer, RewindedStreamContainer
from utils import OS
from config import cfg


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

        # Set default value for mute
        self.is_muted = cfg[CONFIG_MUTE]
        self.player.audio_set_mute(self.is_muted)

        self.selected = False

    def setup_ui(self, ui_file):
        uic.loadUi(ui_file, self)
        # Find the draw area
        self.draw_area = self.findChild(QtCore.QObject, "drawArea")
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
        self.mute_action = self.context_menu.addAction("Mute")
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

    def set_volume(self):
        """Sets the volume according to the range of the UI volume slider."""
        self.player.audio_set_volume(self.volume_slider.value())

    def delete_stream(self):
        """Deletes videoframe/stream"""
        self._fullscreen(self, force_minimize=True)
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

    def resizeEvent(self, event):
        rect = self.geometry()
        pauseButton_rect = self.pause_button.geometry()
        volumeSlider_rect = self.volume_slider.geometry()
        self.pause_button.move(
            0,
            rect.height() - pauseButton_rect.size().height()
        )
        self.volume_slider.move(
            rect.width() - volumeSlider_rect.size().width(),
            rect.height() - volumeSlider_rect.size().height()
        )

    def enterEvent(self, event):
        self.pause_button.show()
        self.volume_slider.show()

    def leaveEvent(self, event):
        self.pause_button.hide()
        self.volume_slider.hide()


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
        super(LiveVideoFrame, self).setup_ui("ui/frame.ui")

        self.findChild(QtCore.QObject, "delete_button").clicked.connect(self.delete_stream)
        self.findChild(QtCore.QObject, "pause_button").clicked.connect(self.toggle_playback)
        self.findChild(QtCore.QObject, "volume_slider").valueChanged.connect(self.set_volume)

        # Store stream_end_label
        self.stream_end_label = self.findChild(QtWidgets.QLabel, "end_label")

    def setup_actions(self):
        super(LiveVideoFrame, self).setup_actions()
        self.rewind_action = self.context_menu.addAction("Rewind")
        self.rewind_action.triggered.connect(self.rewind)
        self.context_menu.addSeparator()

        self.reload_action = self.context_menu.addAction("Reload")
        self.reload_action.triggered.connect(self.reload_stream)
        self.context_menu.addSeparator()

        self.chat_action = self.context_menu.addAction("Open Chat")
        self.chat_action.triggered.connect(self.open_stream_in_browser)
        self.context_menu.addSeparator()

        quality_submenu = QtWidgets.QMenu("Change Quality", parent=self)

        # Add the quality options to the submenu.
        self.quality_actions = []
        for opt in self.stream.all_qualities:
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

    def open_stream_in_browser(self, event):
        # The URL is split to its different elements.
        # E.g. https://www.twitch.tv/example
        url_comp = urlparse(self.stream.url)
        url_sch = url_comp.scheme  # https
        url_net = url_comp.netloc  # www.twitch.tv
        url_path = url_comp.path  # /example

        # If the url does not contain www. URL netloc is "" and path is the whole URL.
        # Solved by adding "http://www." to path and then reparsing.
        if url_net is "":
            url_comp2 = urlparse("http://www." + url_path)
            url_net = url_comp2.netloc
            url_path = url_comp2.path

        if "http" != url_sch:
            url_sch = "http"
        # If the URL is from twitch, then go to its chat
        if "twitch" in url_net:
            url_path = url_path + "/chat"

        # Creates a URL with given elements
        url = urlunparse((url_sch, url_net, url_path, "", "", ""))
        os = platform.system()
        if os == OS.WINDOWS:
            os2.startfile(url)
        else:
            webbrowser.open(url)

    def reload_stream(self, event):
        self.player.stop()
        self.stream.refresh()
        self.player.play()

    def resizeEvent(self, event):
        super(LiveVideoFrame, self).resizeEvent(event)
        rect = self.geometry()
        deleteButton_rect = self.delete_button.geometry()
        label_rect = self.stream_end_label.geometry()
        self.delete_button.move(
            rect.width() - deleteButton_rect.size().width(),
            0
        )
        self.stream_end_label.move(
            rect.width() / 2 - label_rect.width() / 2,
            rect.height() / 2 - label_rect.height() / 2
        )

    def enterEvent(self, event):
        super(LiveVideoFrame, self).enterEvent(event)
        self.delete_button.show()

    def leaveEvent(self, event):
        super(LiveVideoFrame, self).leaveEvent(event)
        self.delete_button.hide()

    def rewind(self):
        if not cfg[CONFIG_BUFFER_STREAM]:
            QtWidgets.QMessageBox().warning(
                self,
                "Warning",
                "Cannot Rewind. You currently have buffering turned off."
            )
            return
        if self.rewinded is None:
            self.rewinded = QtWidgets.QMainWindow(parent=self)
            self.rewinded.setWindowTitle("Rewinded Stream")
            self.rewinded.resize(QtWidgets.QDesktopWidget().availableGeometry(-1).size() * 0.5)
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
        self.player.set_media(self.stream.media)
        self.player.play()

    def setup_ui(self):
        super(RewindedVideoFrame, self).setup_ui("ui/rewoundframe.ui")

        self.findChild(QtCore.QObject, "pause_button").clicked.connect(self.toggle_playback)
        self.findChild(QtCore.QObject, "forward_button").clicked.connect(self.scrub_forward)
        self.findChild(QtCore.QObject, "backward_button").clicked.connect(self.scrub_backward)
        self.findChild(QtCore.QObject, "volume_slider").valueChanged.connect(self.set_volume)

    def contextMenuEvent(self, event):
        super(RewindedVideoFrame, self).context_menu(event)
        self.setup_actions()
        user_action = self.check_actions(event)

    def scrub_forward(self):
        self.player.set_position(self.player.get_position() * 1.1)

    def scrub_backward(self):
        self.player.set_position(self.player.get_position() * 0.9)

    def resizeEvent(self, event):
        super(RewindedVideoFrame, self).resizeEvent(event)
        rect = self.geometry()
        forwardButton_rect = self.forward_button.geometry()
        backwardButton_rect = self.backward_button.geometry()
        self.forward_button.move(
            rect.width() / 2 - forwardButton_rect.width() / 2 + 0.5 * forwardButton_rect.size().width(),
            rect.height() - forwardButton_rect.size().height()
        )
        self.backward_button.move(
            rect.width() / 2 - backwardButton_rect.width() / 2 - 0.5 * backwardButton_rect.size().width(),
            rect.height() - backwardButton_rect.size().height()
        )

    def enterEvent(self, event):
        super(RewindedVideoFrame, self).enterEvent(event)
        self.forward_button.show()
        self.backward_button.show()

    def leaveEvent(self, event):
        super(RewindedVideoFrame, self).leaveEvent(event)
        self.forward_button.hide()
        self.backward_button.hide()
