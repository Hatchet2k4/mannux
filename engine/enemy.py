#!/usr/bin/env python

from entity import Entity


class Enemy(Entity):

    def __init__(self, sprite):
        super(Enemy, self).__init__(sprite)
        self.hp = 1
        self.hurt = False
        self.sightrange = 120
