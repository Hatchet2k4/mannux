#!/usr/bin/env python

import ika
import fonts
from entity import Entity
from sprite import Sprite

class SaveLight(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, Sprite("save_light"))
        self.sprite.SetState("glowraise")

    def Update(self):
        super(SaveLight, self).Update()
        if self.sprite.anim_done:
            self._destroy()


class SaveFlash(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, Sprite("save_flash"))


    def Update(self):
        super(SaveFlash, self).Update()
        if self.sprite.anim_done:
            self._destroy()
