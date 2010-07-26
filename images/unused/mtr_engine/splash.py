#!/usr/bin/env python

import ika
import fonts
from entity import Entity
from sprite import Sprite

class Splash(Entity):
    def __init__(self, x, y, name):
        y+=14
        if y % 16 < 8:
            y -= y%16
        else:
            y += (16 - y%16)

        Entity.__init__(self, x-10, y, Sprite("splash-" + name))

    def Update(self):
        super(Splash, self).Update()
        if self.sprite.anim_done:
            self._destroy()
