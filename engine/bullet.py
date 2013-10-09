#!/usr/bin/env python

import ika
import config
from enemy import Enemy
from entity import Entity
from engine import engine
from boom import Boom
from sounds import sound
from blockbreak import Block


# (vx, vy, frame) for each direction.
data = [(-4, 0, 1), (4, 0, 0), (0, -4, 3), (0, 4, 2), (-4, -4, 6), (4, -4, 7),
        (-4, 4, 5), (4, 4, 4)]


class Bullet(Entity):
    def __init__(self, x, y, direction):
        super(Bullet, self).__init__(ika.Entity(int(x), int(y),
                                                engine.player.layer,
                                                '%s/bullet.ika-sprite' %
                                                config.sprite_path))
        self.vx, self.vy, frame = data[direction]
        self.set_animation_state(first=frame, last=frame, delay=0, loop=False)
        self.ticks = 0
        self.temp = ika.Random(80, 280)
        sound.play('Shoot', 0.2)
        self.damage= 8 #bullet currently does 8hp of damage

    def update(self):
        super(Bullet, self).update()
        if self.sprite is None:
            return
        self.sprite.specframe = self.anim.cur_frame
        collisions = self.detect_collision()
        if len(collisions)>0:

            for ent, top, bottom, left, right in collisions:
                if ent is not None and ent != engine.player and ent is not self:
                    if isinstance(ent, Enemy) and ent.hurtable:
                        ent.Hurt(self) #pass bullet entity so we can get its properties...
                        engine.AddEntity(Boom(int(self.x + self.vx),
                                             int(self.y  + self.vy)))
                        self._destroy()
                    elif ent.isobs:
                        engine.AddEntity(Boom(int(self.x + self.vx),
                                             int(self.y  + self.vy)))
                        self._destroy()
                    return
        if self.left_wall or self.right_wall or self.ceiling or self.floor:
            engine.AddEntity(Boom(int(self.x + self.vx),
                                 int(self.y  + self.vy)))
            self._destroy()
            for dx, dy in [(-8, -8), (8, -8), (8, 8), (-8, 8)]:
               x = int(self.x + self.vx + dx + 4) / 16
               y = int(self.y + self.vy + dy + 4) / 16

               wall_layer = ika.Map.FindLayerByName('Walls')
               door_layer = ika.Map.FindLayerByName('Doors')

               if wall_layer and door_layer and ika.Map.GetObs(x, y, door_layer):


                  ika.Map.SetObs(x, y, door_layer, 0) #hack right now so that obstructions on door layer = destructible block.
                  ika.Map.SetObs(x, y, wall_layer, 0)
                  ika.Map.SetTile(x, y, wall_layer, 0)
                  engine.AddEntity(Block(x * 16, y * 16))
            return
        self.ticks += 1
        if self.ticks > 80:
            self._destroy()

    def draw(self):
        #lighting
        x=self.x-12-ika.Map.xwin
        y=self.y-12-ika.Map.ywin
        #ika.Video.DrawEllipse(self.x+4-ika.Map.xwin, self.y+4-ika.Map.ywin, 8, 8, ika.RGB(100,100,60,80), 1, ika.AddBlend)
        ika.Video.TintBlit(engine.smallcircle, x,y, ika.RGB(64,92,64,128), ika.AddBlend)