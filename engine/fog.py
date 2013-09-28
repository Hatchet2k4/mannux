#!/usr/bin/env python

import ika
import config
import engine

class Fog(object):

    def __init__(self, vx=0.5, vy=0.25, opacity=132):
        super(Fog, self).__init__()
        self.image = ika.Image('%s/fog.png' % config.image_path)
        self.x = 0
        self.y = 0
        self.vx = vx
        self.vy = vy
        self.opacity = 128

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


        #ika.Video.DrawRect(0,0,319,239, ika.RGB(48,48,32, 64), True, ika.SubtractBlend)
        # Need to change to wrapblit.

        ika.Video.TintBlit(self.image, x, y,
                           ika.RGB(255, 255, 255, self.opacity))
        ika.Video.TintBlit(self.image, x - 512, y,
                           ika.RGB(255, 255, 255, self.opacity))
        ika.Video.TintBlit(self.image, x, y - 512,
                           ika.RGB(255, 255, 255, self.opacity))
        ika.Video.TintBlit(self.image, x - 512, y - 512,
                           ika.RGB(255, 255, 255, self.opacity))


class Darkness(object):
    def __init__(self):
        super(Darkness, self).__init__()
        self.image = ika.Image('%s/circle_gradient.png' % config.image_path)

        self.opacity = 128

    def update(self):
        pass

    def draw(self):
        #x=int(engine.player.x)-ika.Map.xwin-160
        #y=int(engine.player.y)-ika.Map.ywin-160
        x=0
        y=0


        ika.Video.TintBlit(self.image, x , y, ika.RGB(255, 255, 255, self.opacity), ika.SubtractBlend)






