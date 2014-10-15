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

data = [(-1, 0, 1), (1, 0, 0), (0, -1, 3), (0, 1, 2), (-1, -1, 6), (1, -1, 7),
        (-1, 1, 5), (1, 1, 4)]


class Bullet(Entity):
    def __init__(self, x, y, direction):
        super(Bullet, self).__init__(ika.Entity(int(x), int(y),
                                                engine.player.layer,
                                                '%s/bullet.ika-sprite' %
                                                config.sprite_path))
        self.vx, self.vy, frame = data[direction]
            

        self.vx=self.vx*3
        self.vy=self.vy*3 
        
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
        
        
class Beam(Entity):
    
    beam_image = ika.Image("images/beam.png")    
    
    def __init__(self, x, y, direction):
        super(Beam, self).__init__(ika.Entity(int(x), int(y),
                                                engine.player.layer,
                                                '%s/blank.ika-sprite' %
                                                config.sprite_path))   
        self.ticks = 0
        self.temp = ika.Random(80, 280)
        sound.play('Beam', 0.2)
        self.damage = 20 

        self.vx, self.vy, frame = data[direction]
        self.vx=self.vx*4
        self.vy=self.vy*4
                
        self.endx=self.x=int(x)
        self.endy=self.y=int(y)        
        self.moving=True
        self.visible=True
        
    def update(self):
        #super(Beam, self).update()
        
        if self.sprite is None:
            return        
        if self.moving: 
            for i in range(4): #fast moving object, process collisions 4 times
                self.endx+=self.vx
                self.endy+=self.vy

                collisions = self.detect_collision()
                for ent, top, bottom, left, right in collisions:
                    if ent is not None and ent != engine.player and ent is not self:
                        if isinstance(ent, Enemy) and ent.hurtable:
                            ent.Hurt(self) #pass bullet entity so we can get its properties...
                            engine.AddEntity(Boom(int(self.x), int(self.y)))
                            self.moving=False
                        elif ent.isobs:
                            engine.AddEntity(Boom(int(self.x), int(self.y)))
                            self.moving=False
                        
        
        self.ticks += 1
        if self.ticks > 30:
            self._destroy()
            
    def draw(self):
        #lighting
    
        x=self.x-12-ika.Map.xwin
        y=self.y-12-ika.Map.ywin
        
        x1=self.x-ika.Map.xwin
        y1=self.y-ika.Map.ywin
        x2=self.endx-ika.Map.xwin
        y2=self.endy-ika.Map.ywin
        c=ika.RGB(255,255,255,128-4*self.ticks)
        #ika.Video.DrawEllipse(self.x+4-ika.Map.xwin, self.y+4-ika.Map.ywin, 8, 8, ika.RGB(100,100,60,80), 1, ika.AddBlend)
        #ika.Video.TintBlit(engine.smallcircle, x,y, ika.RGB(64,92,64,128), ika.AddBlend)        
        #ika.Video.DrawLine(self.beam_image,x1,y1,x2,y2,ika.RGB(255,0,128,128-3*self.ticks))        
        ika.Video.TintDistortBlit(self.beam_image, (x1,y1-1,c), (x2,y2-1,c), (x2,y2+1,c), (x1,y1+1,c), ika.AddBlend)
        