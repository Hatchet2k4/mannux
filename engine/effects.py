#!/usr/bin/env python

#for special effects

import ika
import config
from engine import engine
from entity import Entity
from sounds import sound


#Effects are like Entities but do not use the animation script code as they don't have sprites...
class Effect(object):
    def __init__(self, x, y,layer):
        super(Effect, self).__init__()

        self.x=x
        self.y=y
        self.vx = 0
        self.vy = 0
        self.layer = layer

        self.destroy = False
        self.visible = True
        self.active = True


    def touch(self, entity):
        pass

    def draw(self):
        pass
        
    def update(self):
        pass

    def _destroy(self):
        self.visible = False
        self.active = False
        engine.RemoveEffect(self)
        
class Shield(Effect):

    def __init__(self, x, y, layer, target):
        super(Shield, self).__init__(x,y,layer)
        self.target=target #entity that is being shielded
        self.ticks=0
        
        sound.play('Boom', 0.2)

    def update(self):
        self.ticks+=1
        if self.ticks>64:
            engine.RemoveEffect(self)
        
    def draw(self):
        
        #for now, one point is the center of the target entity...
        x1=self.target.x+self.target.sprite.hotwidth/2-ika.Map.xwin
        y1=self.target.y+self.target.sprite.hotheight/2-ika.Map.ywin
        c1=ika.RGB(0,200,100,128-self.ticks*2)

        #need to adjust these poitns based on direction the shot came from... just numbers for now
        x2=self.x-ika.Map.xwin-6
        y2=self.y-ika.Map.ywin+4
        c2=ika.RGB(0,250,150,128-self.ticks)

        x3=self.x-ika.Map.xwin+8
        y3=self.y-ika.Map.ywin+4
        c3=ika.RGB(0,250,150,128-self.ticks)
        
        ika.Video.DrawTriangle((x1, y1, c1), (x2, y2, c2), (x3, y3, c3))
    
    
        
    


