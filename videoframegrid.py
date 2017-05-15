# -*- coding: utf-8 -*-

import sip

from PyQt5 import QtWidgets
from models.coordinates import VideoFrameCoordinates
from videoframes import LiveVideoFrame


class VideoFrameGrid(QtWidgets.QGridLayout):
    """The VideoFrameGrid is the GridLayout container for all LiveVideoFrames.

    The VideoFrameGrid keeps track of the position of all LiveVideoFrames and
    is in charge of reparenting a VideoFrame back to it's original position
    after a toggled fullscreen mode.
    """

    def __init__(self, parent):
        """Creates a new VideoFrameGrid.

        The VidoeFrameGrid holds a list of the active videoframe objects as
        well as a coordinates object to keep track of the current grid
        coordinates (beginning at (0, 0)).
        """
        super(VideoFrameGrid, self).__init__()
        self.parent = parent
        self.videoframes = []
        self.coordinates = VideoFrameCoordinates(x=0, y=0)
        self.selected_frame = None
        self.fullscreen = False
        self.url_list = []

    def _add_videoframe(self, videoframe):
        """Adds the provided videoframeobject to the VideoFrameGrid."""
        self.videoframes.append(videoframe)
        self.addWidget(videoframe, self.coordinates.x, self.coordinates.y)
        self.coordinates = self.coordinates.update_coordinates()

    def _create_videoframe(self, stream_url, stream_options, quality):
        """Creates a new LiveVideoFrame object."""
        return LiveVideoFrame(self.parent, stream_url, stream_options, quality)

    def add_new_videoframe(self, stream_url, stream_options, quality):
        """Creates and adds a new LiveVideoFrame to the VideoFrameGrid."""
        videoframe = self._create_videoframe(stream_url, stream_options, quality)
        videoframe._swap = self.swap_frame
        videoframe._fullscreen = self.toggle_fullscreen
        videoframe._coordinates = self.coordinates
        videoframe._delete_stream = self.delete_stream
        self._add_videoframe(videoframe)

        if stream_url in self.url_list:
            self.url_list.remove(stream_url)
        self.url_list.insert(0, stream_url)

    def swap_frame(self, frame):
        """Swaps the provided VideoFrame with the currently selected one."""
        if self.selected_frame is None:
            self.selected_frame = frame
        else:
            if self.selected_frame.selected and self.selected_frame != frame:
                x, y, _, _ = self.getItemPosition(self.indexOf(frame))
                x2, y2, _, _ = self.getItemPosition(self.indexOf(self.selected_frame))
                self.removeWidget(frame)
                self.removeWidget(self.selected_frame)
                self.selected_frame._coordinates = VideoFrameCoordinates(x=x, y=y)
                self.addWidget(self.selected_frame, x, y)
                frame._coordinates = VideoFrameCoordinates(x=x2, y=y2)
                self.addWidget(frame, x2, y2)

                # Deselect
                frame.deselect()
                self.selected_frame.deselect()
                self.selected_frame = None
            else:
                self.selected_frame = frame

    def toggle_fullscreen(self, selected_frame):
        if not self.fullscreen:
            for videoframe in self.videoframes:
                if videoframe != selected_frame:
                    videoframe.hide()
                    videoframe.player.audio_set_mute(True)

            self.parent.menubar.hide()
            self.window_state = self.parent.windowState()
            self.parent.showFullScreen()
            self.fullscreen = True

        else:
            for videoframe in self.videoframes:
                if videoframe != selected_frame:
                    videoframe.show()
                    videoframe.player.audio_set_mute(False)

            self.parent.menubar.show()
            self.parent.setWindowState(self.window_state)
            self.fullscreen = False

    def delete_stream(self, videoframe):
        """Removes selected stream/videoframe from grid"""

        videoframe.hide()

        # If one or two frames
        if len(self.videoframes) < 3:
            # Reset coordinates and delete frame
            self.coordinates = VideoFrameCoordinates(x=0, y=0)
            self.delete_videoframe(videoframe)
            # If one frame left after deletion
            if len(self.videoframes) == 1:
                # Set last frame's coordinates to (0,0) and update coordinates
                last_frame = self.videoframes[0]
                last_frame._coordinates = self.coordinates
                self.update_new_stream_coordinates()
        # Otherwise there are more frames
        else:
            # Get coordinates of frame
            x = videoframe._coordinates.x
            y = videoframe._coordinates.y
            self.coordinates = VideoFrameCoordinates(x=x, y=y)

            # Determine which frames need to be moved
            index = self.videoframes.index(videoframe)
            frames_to_move = self.videoframes[index + 1:]

            # Delete frame and all its children
            self.delete_videoframe(videoframe)

            # Move remaining frames
            for frame in frames_to_move:
                self.relocate_frame(frame, self.coordinates)

    def relocate_frame(self, videoframe, coordinates):
        """Moves an existing videoframe to the new coordinates."""
        # Pause stream and remove widget from grid
        videoframe.player.pause()
        self.removeWidget(videoframe)

        # Set videoframes coordinates to provided coordinates
        videoframe._coordinates = coordinates

        # Readd widget to target location and play stream
        self.addWidget(videoframe, coordinates.x, coordinates.y)
        videoframe.player.play()

        # Update coordinates for adding next stream
        self.update_new_stream_coordinates()

    def delete_videoframe(self, videoframe):
        """Deletes a videoframe and all its children from grid"""
        self.videoframes.remove(videoframe)
        self.removeWidget(videoframe)
        sip.delete(videoframe)
        videoframe = None

    def update_new_stream_coordinates(self):
        """Prepares coordinates for next stream"""
        self.coordinates = self.coordinates.update_coordinates()
