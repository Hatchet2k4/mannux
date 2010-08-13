#!/usr/bin/env python

import ika
from entity import Entity
from engine import engine
import fonts
from sprite import Sprite

class Box(Entity):
    def __init__(self, x, y):
        super(Box, self).__init__(ika.Entity(int(x), int(y),
                                                ika.Map.FindLayerByName('Walls'), 'sprites/box.ika-sprite'
                                                ))

        


        self.touchable = True
        self.set_animation_state(0, 0, delay=5, loop=True)

        self.sprite.mapobs = False
        self.sprite.entobs = False
        self.sprite.isobs = True
        self.touching = False
        self.visible = True

    def draw(self):
        pass
        #print >> fonts.tiny(200, 50), "x:", str(self.x)
        
        #x=int(self.x)-ika.Map.xwin
        #y=int(self.y)-ika.Map.ywin
        
        #print >> fonts.tiny(x, y), "vy:", str(self.vy)
        #print >> fonts.tiny(x, y+10), "ticks:", str(self.ticks)
        #ika.Video.DrawRect(x, y, x+48, y+16, ika.RGB(255, 0, 0, 128), True)


    def touch(self, ent):
        
        pass
        #if not self.touching:
        #    self.touching = True
        #    engine.player.floor = True
        #    engine.player.platform = self
        
        #if not engine.player.cur_platform:  #just landed on it      
        #    engine.player.cur_platform = self
            
        
            #add one to ensure the player is still touching ;)
        #    engine.player.y = self.y - 48 + 1
        
        #engine.player.floor = True            
        #engine.player.pvy = self.vy
        #engine.player.pvx = self.vx
        
    def update(self):       
        super(Box, self).update() 






