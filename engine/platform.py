#!/usr/bin/env python

import ika
from entity import Entity
from engine import engine
import fonts
from sprite import Sprite

class Platform(Entity):
    def __init__(self, x, y, vx=.25, vy=-.25, duration=200, delay=50):
        super(Platform, self).__init__(ika.Entity(int(x), int(y),
                                                ika.Map.FindLayerByName('Walls'), 'sprites/platform.ika-sprite'
                                                ))

        
        self._vx = vx
        self._vy = vy #for storing the "original" directions
        
        self.vx = vx
        self.vy = vy
        
        
        self.ticks = 0
        self.delay = 0
        self.delduration = delay #how long to wait
        self.duration = duration #need to change to be more of a pattern eventually...
        self.touchable = True
        self.set_animation_state(0, 0, delay=5, loop=True)


        self.sprite.mapobs = False
        self.sprite.entobs = False
        self.sprite.isobs = True
        self.touching = False
        self.visible = True
        self.platform = True #is a platform!

    def draw(self):
        #print >> fonts.tiny(200, 50), "x:", str(self.x)
        
        x=int(self.x)-ika.Map.xwin
        y=int(self.y)-ika.Map.ywin
        
        #print >> fonts.tiny(x, y), "vy:", str(self.vy)
        #print >> fonts.tiny(x, y+10), "ticks:", str(self.ticks)
        #ika.Video.DrawRect(x, y, x+48, y+16, ika.RGB(255, 0, 0, 128), True)


    def touch(self, ent):
        pass
        #if not self.touching:
        #    self.touching = True

        
        #if not engine.player.cur_platform:  #just landed on it      
        #    engine.player.SetPlatform(self)
            

        
    def update(self):
        super(Platform, self).update() 


        #standard back/forth motion
        self.ticks += 1
        if self.ticks > self.duration:
            self.vx=0
            self.vy=0
            self.delay += 1
            if self.delay > self.delduration: 
                self._vx *= -1
                self._vy *= -1
                self.vx = self._vx
                self.vy = self._vy
                self.ticks = 0
                self.delay = 0



