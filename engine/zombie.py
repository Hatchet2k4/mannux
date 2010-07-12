#!/usr/bin/env python

import ika
import config
from const import Dir
from engine import engine
from enemy import Enemy
from sounds import sound


class Zombie(Enemy):

    def __init__(self, x, y):
        super(Zombie, self).__init__(ika.Entity(x, y, 1, '%s/zombie.ika-sprite'
                                                % config.sprite_path))
        self.anim.kill = True
        self.direction = Dir.LEFT
        self.vx = -0.5
        self.basevx = 0.5
        self.gravity = 0.125
        self.isobs = True
        # Make it touchable so you get hurt by just touching.
        # Set this to false once attacks work.
        self.touchable = True
        self.hurtable = True
        self.damage = 25
        self.hp = 32
        self.state = self.WalkState

    def touch(self, ent):
        if ent is engine.player and ent.hurtable:
           ent.Hurt(self.damage)

    def Hurt(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.state = self.Death
            # Hack so that you can't kill the zombie again, or him hurt
            # you while he's dying.
            self.hurtable = False
        else:
            sound.play('Zombie-groan')
            if abs(self.vx) <= abs(self.basevx):
                self.set_animation_state(3 + self.direction * 3,
                                         3 + self.direction * 3, 12,
                                         loop=False)
            else:
                self.set_animation_state(4 + self.direction,
                                         4 + self.direction, 8, loop=False)
            self.hurt = True

    def Death(self):
        sound.play('Zombie-die')
        self.vx = 0
        self.set_animation_state(8 * self.direction + 56,
                                 8 * self.direction + 63, 5, loop=False)
        while not self.anim.kill:
            yield None
        # Destroys the sprite when its state is done.
        self.destroy = True
        yield None

    def WalkState(self):
        while True:
            # Resets the walk animation, if it got hurt for example.
            if self.anim.kill:
                if self.hurt:
                    if engine.player.x > self.x:
                        self.vx *= -1 * (self.direction != Dir.RIGHT)
                        self.direction = Dir.RIGHT
                    else:
                        self.vx *= -1 * (self.direction != Dir.LEFT)
                        self.direction = Dir.LEFT
                    self.hurt = False
                self.set_animation_state(8 * self.direction + 8,
                                         8 * self.direction + 15, 12)
            if self.left_wall:
                self.direction = Dir.RIGHT
                self.vx *= -1
                self.x += 1
                self.set_animation_state(1, 1, 12, loop=False)
                #self.set_animation_state(8 * self.direction + 8,
                #                         8 * self.direction + 15, 12)
            if self.right_wall:
                self.direction = Dir.LEFT
                self.vx *= -1
                self.x -= 1
                self.set_animation_state(1, 1, 12, loop=False)
                #self.set_animation_state(8 * self.direction + 8,
                #                         8 * self.direction + 15, 12)
            if not self.floor:
                #self.x -= (self.direction * 2 - 1) * 8
                if self.direction == Dir.RIGHT:
                    self.direction = Dir.LEFT
                else:
                    self.direction = Dir.RIGHT
                self.vx *= -1
                self.set_animation_state(1, 1, 12, loop=False)
                #self.set_animation_state(8 * self.direction + 8,
                #                         8 * self.direction + 15, 12)
            if abs(engine.player.x - self.x) <= self.sightrange and \
               abs(engine.player.y - self.y) <= self.sightrange / 2 and \
               (engine.player.x - self.x < 0) == (self.vx < 0):
                self.anim.kill = True
                self.vx *= 3
                self.state = self.RunState
            # Need to add detection for when the zombie "sees" you.
            yield None

    def RunState(self):
        stopcount = 0
        while True:
            # Resets the walk animation, if it got hurt for example.
            if self.anim.kill:
                self.set_animation_state(8 * self.direction + 40,
                                         8 * self.direction + 47, 6, loop=True)
            if self.left_wall:
                self.direction = Dir.RIGHT
                self.vx *= -1
                self.x += 1
                self.set_animation_state(1, 1, 8, loop=False)
                #self.set_animation_state(8 * self.direction + 8,
                #                         8 * self.direction + 15, 12)
                stopcount = 200
            if self.right_wall:
                self.direction = Dir.LEFT
                self.vx *= -1
                self.x -= 1
                self.set_animation_state(1, 1, 8, loop=False)
                #self.set_animation_state(8 * self.direction + 8,
                #                         8 * self.direction + 15, 12)
                stopcount = 200
            if not self.floor:
                self.x -= (self.direction * 2 - 1) * 8
                if self.direction == Dir.RIGHT:
                   self.direction = Dir.LEFT
                else:
                   self.direction = Dir.RIGHT
                self.vx *= -1
                self.set_animation_state(1, 1, 8, loop=False)
                stopcount = 200
                #self.set_animation_state(8 * self.direction + 8,
                #                         8 * self.direction + 15, 12)
            if abs(engine.player.x - self.x) > self.sightrange or \
               (engine.player.x - self.x < 0) != (self.vx < 0) or \
               abs(engine.player.y - self.y) > self.sightrange / 2:
                stopcount += 1
                if stopcount >= 200:
                    self.anim.kill = True
                    self.vx /= 3
                    self.state = self.WalkState
            elif stopcount:
                stopcount = 0
            # Need to add detection for when the zombie "sees" you.
            yield None
