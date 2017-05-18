from unittest import TestCase
from models.coordinates import VideoFrameCoordinates


class TestVideoFrameCoordinates(TestCase):

    def test_default_initialization(self):
        self.coordinates = VideoFrameCoordinates()

        self.assertEqual(self.coordinates.x, 0)
        self.assertEqual(self.coordinates.y, 0)

    def test_initialization_with_values(self):
        self.coordinates = VideoFrameCoordinates(x=1, y=1)

        self.assertEqual(self.coordinates.x, 1)
        self.assertEqual(self.coordinates.y, 1)

    def test_update_coordinates_equal_x_y(self):
        self.coordinates = VideoFrameCoordinates()
        new_coordinates = self.coordinates.update_coordinates()

        self.assertEqual(new_coordinates.x, 0)
        self.assertEqual(new_coordinates.y, 1)

    def test_update_coordinates_x_one_larger_than_y(self):
        self.coordinates = VideoFrameCoordinates(x=0, y=1)
        new_coordinates = self.coordinates.update_coordinates()

        self.assertEqual(new_coordinates.x, self.coordinates.y)
        self.assertEqual(new_coordinates.y, 0)

    def test_update_coordinates_y_larger_than_x(self):
        self.coordinates = VideoFrameCoordinates(x=0, y=2)
        new_coordinates = self.coordinates.update_coordinates()

        self.assertEqual(new_coordinates.x, self.coordinates.x + 1)
        self.assertEqual(new_coordinates.y, self.coordinates.y)

    def test_update_coordinates_x_larger_equal_y(self):
        self.coordinates = VideoFrameCoordinates(x=2, y=0)
        new_coordinates = self.coordinates.update_coordinates()

        self.assertEqual(new_coordinates.x, self.coordinates.x)
        self.assertEqual(new_coordinates.y, self.coordinates.y + 1)
