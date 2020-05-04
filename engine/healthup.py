#!/usr/bin/env python

import ika
import config
from engine import engine
from entity import Entity


class Healthup(Entity):

    def __init__(self, x, y, flag=None):
        super(Healthup, self).__init__(ika.Entity(x, y, engine.player.layer,
                                                  '%s/healthup.ika-sprite' %
                                                  config.sprite_path))
        self.flag = flag
        self.set_animation_state(first=0, last=6, delay=4)
        self.touchable = True

    def touch(self, entity):
        if entity is engine.player:
            entity.maxhp += 50
            entity.givehp += 50
            #engine.hud.resize()
            if self.flag is not None:
                engine.flags[self.flag] = "True"
            self.destroy = True
