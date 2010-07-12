#!/usr/bin/env python

import ika
import config
from engine import engine
from entity import Entity


class Block(Entity):

    def __init__(self, x, y):
        super(Block, self).__init__(ika.Entity(x, y,
                                               engine.player.layer,
                                               '%s/blockbreak.ika-sprite' %
                                               config.sprite_path))
        self.set_animation_state(first=0, last=3, delay=4, loop=False)
        self.check_obs = False

    def update(self):
        super(Block, self).update()
        if self.anim.kill:
            self._destroy()
