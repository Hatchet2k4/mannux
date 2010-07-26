#!/usr/bin/env python

import ika
from entity import Entity
from engine import engine
import fonts
from sprite import Sprite

class Platform(Entity):
    def __init__(self, x, y, vx=1, vy=0, ticks=200):
        #super(Platform, self).__init__(ika.Entity(int(x), int(y),
        #                                        engine.player.layer, 'sprites/platform.ika-sprite'
        #                                        ))
        Entity.__init__(self, x, y, Sprite("gullug"))
        self.vx = vx
        self.vy = vy
        self.ticks = 0
        self.maxticks = ticks
        self.touchable = True
        self.set_animation_state(0, 0, delay=5, loop=True)

        self.sprite.mapobs = False
        self.sprite.entobs = False
        #self.sprite.isobs = True
        self.touching = False
        self.visible = True

    #def draw(self):
        #print >> fonts.tiny(200, 50), "x:", str(self.x)
        #print >> fonts.tiny(200, 60), "y:", str(self.y)
        #print >> fonts.tiny(200, 70), "ticks:", str(self.ticks)
    #    x=int(self.x)-ika.Map.xwin
    #    y=int(self.y)-ika.Map.ywin
    #    ika.Video.DrawRect(x, y, x+64, y+16, ika.RGB(255, 0, 0, 128),True)


    def touch(self, ent):
        #if not self.touching:
        #    self.touching = True
        #    engine.player.floor = True
        #    engine.player.platform = self
        engine.player.platform = self
        #use sprite.height because morph ball height changes
        #add one to ensure the player is still touching ;)
        engine.player.y = self.y - engine.player.height + 1

    def Update(self):
        super(Platform, self).Update()

        self.ticks += 1
        if self.ticks > self.maxticks:
            self.vx *= -1
            self.vy *= -1
            self.ticks = 0




