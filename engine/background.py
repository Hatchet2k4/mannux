#!/usr/bin/env python

import ika
import color


class Background(object):

    def __init__(self, background, xoffset=0, yoffset=0, parallax=True,
                 xparallax=1, yparallax=1, wrap=False):
        super(Background, self).__init__()
        self.bg = background
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.parallax = parallax
        self.xparallax = xparallax
        self.yparallax = yparallax
        self.wrap = wrap

    def draw(self):
        # Background scrolls according to parallax.
        if self.parallax:
            if self.wrap:
                ika.Video.TileBlit(self.bg, int(self.xoffset - (ika.Map.xwin *
                                                                self.xparallax)),
                                   int(self.yoffset -
                                       (ika.Map.ywin * self.yparallax)),
                                   ika.Video.xres, ika.Video.yres)
            else:
                ika.Video.Blit(self.bg, int(self.xoffset -
                                            (ika.Map.xwin * self.xparallax)),
                               int(self.yoffset -
                                   (ika.Map.ywin * self.yparallax)))
        # Stationary background.
        else:
            ika.Video.Blit(self.bg, self.xoffset, self.yoffset)

    def update(self):
        pass

class GlowBG(Background):

    def __init__(self, background, xoffset=0, yoffset=0, scroll=True,
                 xparallax=1, yparallax=1):
        super(GlowBG, self).__init__(background, xoffset, yoffset, xparallax,
                                     yparallax)
        self.scroll = scroll
        self.color = color.transparent
        self.duration = 100
        self.time = 0

    def update(self):
        self.time += 1
        if self.time <= self.duration / 2:
            self.color = ika.RGB(200 - self.time, 200 - self.time / 2, 255,
                                 160 - self.time)
        elif self.time < self.duration:
            self.color = ika.RGB(150 + self.time - 50,
                                 175 + (self.time - 50) / 2, 255,
                                 110 + self.time - 50)
        else:
            self.time = 0
            #self.color = color.white

    def draw(self):
        # Background scrolls according to parallax.
        if self.scroll:
            ika.Video.TintBlit(self.bg, int(self.xoffset -
                                            (ika.Map.xwin * self.xparallax)),
                               int(self.yoffset -
                                   (ika.Map.ywin * self.yparallax)),
                               self.color)
        # Stationary background.
        else:
            ika.Video.TintBlit(self.bg, self.xoffset, self.yoffset, self.color)
