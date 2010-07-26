#!/usr/bin/env python

class Dir(object):
    NONE      = -1
    LEFT      = 0
    RIGHT     = 1
    UP        = 2
    DOWN      = 3
    UPLEFT    = 4
    UPRIGHT   = 5
    DOWNLEFT  = 6
    DOWNRIGHT = 7

    ANGLE     = [180, 0, 90, 270, 135, 45, 225, 315]

    VECTOR    = [(-1, 0), (1, 0), ( 0,  1), ( 0, -1),
                 (-1, 1), (1, 1), (-1, -1), ( 1, -1)]
