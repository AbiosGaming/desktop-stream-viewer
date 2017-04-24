#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class StreamCoordinates:
    def __init__(self, x=0, y=0):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @x.setter
    def x(self, x):
        self.__x = x

    @y.setter
    def y(self, y):
        self.__y = y

    def new_coordinates(self):
        if self.y == self.x:
            return StreamCoordinates(x=0, y=self.y + 1)
        elif self.y == self.x + 1:
            return StreamCoordinates(x=self.y, y=0)
        else:
            if self.x < self.y:
                return StreamCoordinates(x=self.x + 1, y=self.y)
            else:
                return StreamCoordinates(x=self.x, y=self.y + 1)
