#!/usr/bin/env python

#for special effects

import ika
import config
from engine import engine
from entity import Entity
from sounds import sound
import math

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

        self.xdiff=target.x-x
        self.ydiff=target.y-y
        #angleInDegrees = atan2(deltaY, deltaX) * 180 / PI
        self.angle=int(math.atan2(self.ydiff, self.xdiff) * 180 / math.pi)

        self.ticks=0

        sound.play('Boom', 0.2)

    def update(self):
        self.ticks+=1
        if self.ticks>64:
            engine.RemoveEffect(self)

    def draw(self):

        #for now, one point is the center of the target entity...
        x1=int(self.target.x+self.target.sprite.hotwidth/2-ika.Map.xwin)
        y1=int(self.target.y+self.target.sprite.hotheight/2-ika.Map.ywin)
        c1=ika.RGB(0,200,100,228-self.ticks*2)

        #need to adjust these points based on direction the shot came from... just numbers for now
        #x2=x1-self.xdiff-8
        #y2=y1-self.ydiff-8
        #c2=ika.RGB(0,250,150,128-self.ticks)

        #x3=x1-self.xdiff+8
        #y3=y1-self.ydiff+8
        #c3=ika.RGB(0,250,150,128-self.ticks)
        ika.Video.DrawArc(x1, y1, 12, 12, 6, 6, self.angle+30, self.angle+90, c1, True)
        #ika.Video.DrawTriangle((x1, y1, c1), (x2, y2, c2), (x3, y3, c3))






