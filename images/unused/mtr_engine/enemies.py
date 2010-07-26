#!/usr/bin/env python

import ika
from entity import Entity
from sprite import Sprite
from enemy import Enemy
import fonts
import math

# ==============
# Wallfire Logic
# ==============
class Wallfire(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, Sprite("gullug"), (0, 1, 24, 32))
        self.set_animation_state(first=0, last=0, delay=1, loop=False)
        self.ticks = 0
        self.hp = 24
        self.hurtable = True


    def Update(self):
        Enemy.Update(self)
        if not self.dead:
            self.ticks += 1
            if self.ticks == 200:
                self.set_animation_state(first=1, last=8, delay=6, loop=False)
            elif self.ticks > 200:
                if self.anim.kill:
                    self.set_animation_state(first=0, last=0, delay=1, loop=False)
                    self.ticks = 0

    def Hurt(self, dmg):
        Enemy.Hurt(self, dmg)
        if self.dead == True:
            self.set_animation_state(first=9, last=9, delay=1, loop=True)



# ============
# Gullug Logic
# ============
class Gullug(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, Sprite("gullug"))
        self.set_animation_state(first=0, last=2, delay=6, loop=True)
        self.ticks = 0
        self.hp = 24
        self.hurtable = True
        self.radius = 50    # how large a circle from his origin he flies in
        self.speed = 1.5    # how fast he flies his circular path
        self.ox = self.x    # origin point x
        self.oy = self.y    # origin point y

    def Update(self):
        Enemy.Update(self)
        if not self.dead:
            self.ticks += self.speed
            if self.ticks > 360:
                self.ticks = 0
            self.x = self.ox + self.radius * math.cos(math.pi / 180 * self.ticks)  # optimize this later
            self.y = self.oy + self.radius * math.sin(math.pi / 180 * self.ticks)  # perhaps...

    def Hurt(self, dmg):
        Enemy.Hurt(self, dmg)
        if self.dead == True:
            self.visible = False

# =============
# Hornoad Logic
# =============
class Hornoad(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, Sprite("gullug"))

        # state variables
        self.set_animation_state(first=4, last=6, delay=32, loop=True)
        self.hurtable = True
        self.ticks = 0
        self.hp = 24

        # do we have some kind of system in place to easily do states?
        # shouldn't we?  I know we do for that cute girl next door, Sammy.
        self.sleep_state = 1
        self.jump_state = 4
        self.shake_state = 2
        self.taunt_state = 3
        self.cur_state = self.sleep_state

        # logic variables
        self.radius = 50    # how large a circle from his origin he flies in
        self.speed = 1.5    # how fast he flies his circular path
        self.ox = self.x    # origin point x
        self.oy = self.y    # origin point y

    def Update(self):
        Enemy.Update(self)
        if not self.dead:
            if self.cur_state == self.sleep_state:
                pass

    def Hurt(self, dmg):
        Enemy.Hurt(self, dmg)
        if self.dead == True:
            self.visible = False
