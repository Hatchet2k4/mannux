#!/usr/bin/env python

import ika
from entity import Entity
from engine import engine
import fonts
from sprite import Sprite
from blockbreak import Block
numbombs = 0

class Bomb(Entity):
    def __init__(self, x, y):
        global numbombs
        Entity.__init__(self, x, y, Sprite("bombs"), (6, 0, 20, 16))

        self.ticks = 45  # 30 ticks 'till kaboooom!

        numbombs += 1
        if numbombs > 3:
            self._destroy()


    def _destroy(self):
        global numbombs
        super(Bomb, self)._destroy()
        numbombs -= 1


    def Update(self):
        super(Bomb, self).Update()

        self.ticks -= 1

        if self.ticks == 0:
            self.sprite.SetState("explode")

            # check for a bomb jump!
            self.layer -= 1 #move back to player's layer for proper collision detection
            for ent in self.detect_collision():
                if ent == engine.player:
                    ent.BombJump(self.x+self.width/2)
            self.layer += 1
            self.DetectBlocks()



        #if we are done espllooooding, then we can go home.
        if self.sprite.anim_done:
            self._destroy()

    def DetectBlocks(self):
        blocks = []
        tx = int(self.x/16)
        ty = int(self.y/16)
        for x in range(tx, tx+3):
            for y in range(ty, ty+3):
                b = ika.Map.GetObs(x, y, self.layer)
                if b > 1: # breakable block!
                    ika.Map.SetObs(x, y, self.layer, 0)
                    ika.Map.SetTile(x, y, self.layer, 0)
                    engine.AddEntity(Block(x * 16, y * 16, b))





