#!/usr/bin/env python

import ika


class Camera(object):

    def __init__(self, target=None):
        self.target = target
        self.xlock = False
        self.ylock = False
        self.xoffset = 0
        self.yoffset = 0
        self.drift = False
        self.reset_borders()
        self.camspeed = 1

    def update(self):
        if self.target is not None:
            y = self.target.y - ika.Video.yres / 2 + self.yoffset
            x = self.target.x - ika.Video.xres / 2 + self.xoffset
            #self.drift = (ika.Map.ywin != y or ika.Map.xwin != x)
            if self.drift:
                d = 0
                if not self.ylock:
                    if y > ika.Map.ywin and ika.Map.ywin < self.bottom:
                        ika.Map.ywin += self.camspeed
                    elif y < ika.Map.ywin and ika.Map.ywin > self.top:
                        ika.Map.ywin -= self.camspeed
                    else:
                        d += 1
                if not self.xlock:
                    if x > ika.Map.xwin and ika.Map.xwin < self.right:
                        ika.Map.xwin += self.camspeed
                    elif x < ika.Map.xwin and ika.Map.xwin > self.left:
                        ika.Map.xwin -= self.camspeed
                    else:
                        d += 1
                # Locked on.
                if d == 2:
                    self.drift = False
            else:
                if not self.ylock:
                    if y > self.top and y < self.bottom:
                        ika.Map.ywin = y
                if not self.xlock:
                    if x > self.left and x < self.right:
                        ika.Map.xwin = x

    def reset_borders(self):
        self.set_borders(0, 0, ika.Map.width, ika.Map.height)

    def set_borders(self, x, y, width, height):
        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height
