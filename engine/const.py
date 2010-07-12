#!/usr/bin/env python

class Dir(object):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    UPLEFT = 4
    UPRIGHT = 5
    DOWNLEFT = 6
    DOWNRIGHT = 7
    VECTOR = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1),
              (1, -1)]
