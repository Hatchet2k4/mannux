#!/usr/bin/env python

import ika
import config
from engine import engine
from entity import Entity
from sounds import sound


class Boom(Entity):

    def __init__(self, x, y, sprite='boom.ika-sprite', framecount=4):
        super(Boom, self).__init__(ika.Entity(x, y, engine.player.layer,
                                              '%s/%s' %
                                              (config.sprite_path, sprite)))
        self.set_animation_state(first=0, last=framecount - 1, delay=4, loop=False)
        self.check_obs = False
        sound.play('Boom', 0.2)

    def update(self):
        super(Boom, self).update()
        if self.anim.kill:
            self._destroy()
