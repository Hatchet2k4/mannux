#!/usr/bin/env python

import ika
from engine import engine
from entity import Entity
from sprite import Sprite
from const import Dir

class Block(Entity):
    def __init__(self, x, y, b, delay=None):
        Entity.__init__(self, x, y, Sprite("blockbreak"))
        self.check_obs = False

        self.b = b
        self.tx = int(x/16)
        self.ty = int(y/16)
        if delay == None:
            self.delay = 5
        else:
            self.delay = delay
        self.ticks = 0
        if b > 2 and b < 10: #blocks between 2 and 10 mean search for nearby blocks of the same number.. and destroy them!
            self.SearchBlocks(self.tx, self.ty, b)


    def Update(self):
        super(Block, self).Update()
        self.ticks += 1
        if self.b >= 10 and self.ticks == self.delay: #blocks >10 "snake"
            self.SearchBlocks(self.tx, self.ty, self.b)
        elif self.b >= 20: #reserved for more advanced snaking... (those that can touch themselves)
            pass

        if self.sprite.anim_done:
            self._destroy()






    def SearchBlocks(self, tx, ty, b):

        for (dx, dy) in Dir.VECTOR:
            x=tx+dx
            y=ty+dy
            if ika.Map.GetObs(x, y, self.layer) == b:
                ika.Map.SetObs(x, y, self.layer, 0)
                ika.Map.SetTile(x, y, self.layer, 0)
                engine.AddEntity(Block(x * 16, y * 16, b, self.delay))




