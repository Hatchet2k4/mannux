#!/usr/bin/env python

import ika
import math
import config
from const import Dir
from entity import Entity
from enemy import Enemy
from engine import engine
from boom import Boom
from sounds import sound


class Turret(Enemy):

    def __init__(self, x, y, direction=Dir.DOWN):
        super(Turret, self).__init__(ika.Entity(x, y,
                                                ika.Map.FindLayerByName('Walls'),
                                                '%s/turret.ika-sprite' % config.sprite_path))
        self.direction = direction
        self.sprite.isobs = False
        self.touchable = False 
        self.damage = 25
        self.hp = 32
        self.state = self.hide_state
        self.ticks = 0

    def touch(self, other): 
        if other is engine.player:
            other.Hurt(self.damage)

    def Hurt(self, amount):
        self.hp -= amount
        if self.hp <= 0: 
            self.state = self.death_state
        else:
            self.hurt = True

    def death_state(self):
        self.set_animation_state(14 + 15 * self.direction,
                                 14 + 15 * self.direction, 4)
        engine.AddEntity(Boom(int(self.x - 8), int(self.y - 8),
                             'explode.ika-sprite', 6))
        self.hurtable = False
        self.destroy = True
        while not self.anim.kill:
            yield None
        yield None

    def fire(self):
        self.set_animation_state(self.direction * 15 + 13,
                                 self.direction * 15 + 13, 10, loop=False)
        dx = self.x - engine.player.x - engine.player.width / 2 + 8
        dy = self.y - engine.player.y - engine.player.height / 2 + 8
        angle = math.atan2(dy, dx) + math.pi
        engine.AddEntity(Laser(self.x + 8, self.y + 8, angle, self))

    def hide_state(self):
        while not (abs(engine.player.x - self.x) <= self.sightrange and
                   abs(engine.player.y - self.y) <= self.sightrange / 2):
            yield None
        self.set_animation_state(self.direction * 15 + 1,
                                 self.direction * 15 + 9, 4, loop=False)
        while not self.anim.kill:
            yield None
        self.state = self.fire_state
        yield None

    def fire_state(self):
        self.hurtable = True
        while True:
            if not self.anim.kill:
                self.set_animation_state(self.direction * 15 + 10,
                                         self.direction * 15 + 12, 8,
                                         reset=False)
            self.ticks += 1
            if self.ticks == 15 or self.ticks == 30 or self.ticks == 45: #fire in bursts of 3
                self.fire()
            elif self.ticks == 180: #Reset every 1.8 seconds. May need to adjust this...
                self.ticks = 0
            yield None


class Laser(Entity):

    def __init__(self, x, y, angle, spawner, damage=8):
        super(Laser, self).__init__(ika.Entity(int(x), int(y),
                                    ika.Map.FindLayerByName('Walls'),
                                    '%s/blank.ika-sprite' %
                                    config.sprite_path))
        self.phantom = True
        self.check_obs = False
        self.ticks = 0
        self.angle = angle
        sound.play('Shoot', 0.2)
        self.set_animation_state(first=0, last=0, delay=1)
        self.state = self.fly_state
        self.damage = damage
        self.spawner = spawner
        self.length = 16
        self.a = 255
        self.d = -1

    def draw(self):
        x1 = int(self.x - ika.Map.xwin)
        y1 = int(self.y - ika.Map.ywin)
        x2 = int(self.x + self.length * math.cos(self.angle) - ika.Map.xwin)
        y2 = int(self.y + self.length * math.sin(self.angle) - ika.Map.ywin)
        x3 = int(self.x + self.length / 2 *
                 math.cos(self.angle - math.pi / 24) - ika.Map.xwin)
        y3 = int(self.y + self.length / 2 *
                 math.sin(self.angle - math.pi / 24) - ika.Map.ywin)
        x4 = int(self.x + self.length / 2 *
                 math.cos(self.angle + math.pi / 24) - ika.Map.xwin)
        y4 = int(self.y + self.length / 2 *
                 math.sin(self.angle + math.pi / 24) - ika.Map.ywin)
        c = ika.RGB(255, 255, 255 - self.a / 2, self.a)
        #ika.Video.DrawLine(x1, y1, x2, y2, c)
        #ika.Video.DrawTriangle((x1, y1, c), (x4, y4, c), (x3, y3, c))
        ika.Video.DrawTriangle((x1, y1, c), (x2, y2, c), (x3, y3, c))
        ika.Video.DrawTriangle((x1, y1, c), (x2, y2, c), (x4, y4, c))

    def fly_state(self):
        while True:
            if self.d == -1:
                self.a -= 10
                if self.a <= 105:
                    self.d = 1
            elif self.d == 1:
                self.a += 10
                if self.a >= 255:
                    self.a = 255
                    self.d = -1
            self.x += 3 * math.cos(self.angle)
            self.y += 3 * math.sin(self.angle)
            hitwall = self.get_obstruction(int(self.x + self.length *
                                               math.cos(self.angle)),
                                           int(self.y + self.length *
                                               math.sin(self.angle)),
                                           self.layer)
            hitent = False
            #ent = engine.player
            for ent in engine.entities:
                if ent.hurtable and ent not in [self, self.spawner]:
                    for x, y in [(self.x, self.y), 
                                 (self.x + self.length * math.cos(self.angle),
                                  self.y + self.length *
                                  math.sin(self.angle))]:
                        if ent.y + ent.height > y and ent.y < y and \
                           ent.x + ent.width > x and ent.x < x:
                            ent.Hurt(self.damage)
                            hitent = True
                            break
            if hitent or hitwall:
                self.destroy = True 
                engine.AddEntity(Boom(int(self.x + (self.length - 4) *
                                         math.cos(self.angle)),
                                     int(self.y + (self.length - 4) *
                                         math.sin(self.angle)),
                                     'boom2.ika-sprite'))
                yield None
            self.ticks += 1
            if self.ticks > 250: 
                self.destroy = True
                yield None
            yield None
