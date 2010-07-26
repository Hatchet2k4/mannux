#!/usr/bin/env python

import ika
from engine import engine
from entity import Entity
from sprite import Sprite

dooropen = ika.Sound("sfx/dooropen.wav")
doorclose = ika.Sound("sfx/doorclose.wav")

class Door(Entity):

    def __init__(self, x, y, color, direction, dopen, layer=ika.Map.FindLayerByName('Background'), locked=False):
        Entity.__init__(self, x, y, Sprite("door_left"))

        if direction == "right":
            self.sprite.mirror_x = True

        if color == "blue":
            self.sprite.color = ika.RGB(0, 0, 255)
        elif color == "red":
            self.sprite.color = ika.RGB(255, 0, 0)
        elif color == "green":
            self.sprite.color = ika.RGB(0, 255, 0)
        else:
            self.sprite.color = ika.RGB(128, 128, 128)

        self.locked = locked
        self.layer = layer
        self.isobs = True
        self.hurtable = True

        self.open_time = 0

    def Hurt(self, hp):
        ika.Log("Door Hurt")
        self.open_time = 512
        self.hurtable = False
        self.isobs = False
        self.sprite.SetState("opening")
        dooropen.Play()
        for i in range(4):
            ika.Map.SetObs(self.x / 16, self.y / 16 + i, self.layer, False)


    def Update(self):
        Entity.Update(self)
        if self.open_time > 0:
            self.open_time -= 1
            if self.open_time == 0:
                self.sprite.SetState("closing")
                self.hurtable = True
                self.isobs = True 
                doorclose.Play()


"""
    def door_state(self):
        while True:
            while self.locked:
               yield None
            # Delay for a moment.
            i = 2
            while i > 0:
                i -= 1
                yield None
            # If close enough, start opening the door.
            if detect_in_y_coordinates(self) is engine.player and \
               abs(self.x - engine.player.x) < 72:
                if not self.dopen:
                    self.dopen = True
                    sound.play('Open')
                if self.anim.cur_frame < 8:
                    self.anim.cur_frame += 1
                    if self.anim.cur_frame >= 4:
                        # Not an obstruction at this point.
                        self.sprite.isobs = False
                        for i in range(4):
                            ika.Map.SetObs(self.x / ika.Map.tilewidth,
                                           self.y / ika.Map.tileheight + i,
                                           self.layer, False)
            # Or else close if not open.
            elif self.anim.cur_frame > 0:
                if self.anim.cur_frame < 4:
                    # Obstruction now.
                    self.sprite.isobs = True
                    for i in range(4):
                        ika.Map.SetObs(self.x / ika.Map.tilewidth,
                                       self.y / ika.Map.tileheight + i,
                                       self.layer, True)
                if self.dopen:
                    self.dopen = False
                    sound.play('Close')
                self.anim.cur_frame -= 1
            yield None
"""
