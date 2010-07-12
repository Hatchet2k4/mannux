#!/usr/bin/env python

import ika
import config


class Fog(object):

    def __init__(self, vx=0.5, vy=0.25, opacity=132):
        super(Fog, self).__init__()
        self.image = ika.Image('%s/fog.png' % config.image_path)
        self.x = 0
        self.y = 0
        self.vx = vx
        self.vy = vy
        self.opacity = 132

    def update(self):
        self.x = (self.x + self.vx) % 512
        self.y = (self.y + self.vy) % 512

    def draw(self):
        x = int(self.x) - ika.Map.xwin
        y = int(self.y) - ika.Map.ywin
        # Make sure the fog is always on screen.
        while x < 0:
            x += 512
        while x > 512:
            x -= 512
        while y < 0:
            y += 512
        while y > 512:
            y -= 512
        # Need to change to wrapblit.
        ika.Video.TintBlit(self.image, x, y,
                           ika.RGB(255, 255, 255, self.opacity))
        ika.Video.TintBlit(self.image, x - 512, y,
                           ika.RGB(255, 255, 255, self.opacity))
        ika.Video.TintBlit(self.image, x, y - 512,
                           ika.RGB(255, 255, 255, self.opacity))
        ika.Video.TintBlit(self.image, x - 512, y - 512,
                           ika.RGB(255, 255, 255, self.opacity))
