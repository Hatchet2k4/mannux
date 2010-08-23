#!/usr/bin/env python

import ika
import engine
import config
from engine import engine, detect_in_y_coordinates
from entity import Entity
from sounds import sound


class Door(Entity):

    def __init__(self, x, y, s, layer=None, locked=False):
        super(Door, self).__init__(ika.Entity(x, y,
                                              ika.Map.FindLayerByName('Doors'),
                                              '%s/%s.ika-sprite' %
                                              (config.sprite_path, s)))
        if layer is None:
            layer = ika.Map.FindLayerByName('Doors')
        self.anim.kill = True
        self.locked = locked
        self.layer = layer
        # Start door open.
        if abs(self.x - engine.player.x) < 72 and not locked and \
           detect_in_y_coordinates(self) is engine.player:
            self.anim.cur_frame = 8
            self.sprite.specframe = 8
            self.dopen = True
            self.isobs = False
            for i in range(4):
                ika.Map.SetObs(self.x / ika.Map.tilewidth,
                               self.y / ika.Map.tileheight + i, self.layer,
                               False)
        # Start door closed.
        else:
            self.anim.cur_frame = 0
            self.sprite.isobs = True
            self.dopen = False
            for i in range(4):
                ika.Map.SetObs(self.x / ika.Map.tilewidth,
                               self.y / ika.Map.tileheight + i, self.layer,
                               True)
        self.animation()
        ika.ProcessEntities()
        self.state = self.door_state
        self.check_obs = False

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
