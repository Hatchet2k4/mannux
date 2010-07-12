#!/usr/bin/env python

import ika
import video


class Fade(object):

    def __init__(self, length=255):
        super(Fade, self).__init__()
        self.length = length
        self.alpha = 255
        self.time = 0

    def update(self):
        self.time += 1

    def draw(self):
        if self.alpha > 0:
            video.clear(ika.RGB(0, 0, 0, self.alpha))


class FadeIn(Fade):

    def update(self):
        super(FadeIn, self).update()
        if self.time < self.length:
            self.alpha = int(255 - (self.time * 255 / self.length))
        else:
            self.alpha = 0


class FadeOut(Fade):

    def update(self):
        super(FadeOut, self).update()
        if self.time < self.length:
            self.alpha = int(self.time * 255 / self.length)
        else:
            self.alpha = 255
