#!/usr/bin/env python

import ika
import vecmath
import config
import controls
import parser
from entity import Entity
from engine import engine
from bullet import Bullet
from anim import make_anim
from sounds import sound
from const import Dir


slopeTiles = {Dir.LEFT:  [347, 623, 746, 885, 876],  # /
              Dir.RIGHT: [346, 622, 749, 889, 878]}  # \
halfSlopeTiles = {(Dir.LEFT,  'bottom'): [464],
                  (Dir.LEFT,  'top'):    [465],
                  (Dir.RIGHT, 'bottom'): [468],
                  (Dir.RIGHT, 'top'):    [469]}
ladderTiles = [701]


class Tabby(Entity):

    def __load_animations():
        strands = (parser.
                   load('%s/tabby.anim' % config.data_path)['animation'].
                   get_all('strand'))
        animations = {}
        for strand in strands:
            row = int(strand.get('row'))
            offset = int(strand.get('offset', 0))
            length = int(strand.get('length', 8))
            key = strand['keys'].split()
            direction = strand.get('direction')
            if direction is not None:
                key.append({'up': Dir.UP, 'right': Dir.RIGHT, 'down': Dir.DOWN,
                            'left': Dir.LEFT}[direction])
            animations[tuple(key)] = range(offset + row * 8,
                                           offset + length + row * 8)
        return animations

    animations = __load_animations()

    def __init__(self, x=0, y=0):
        super(Tabby, self).__init__(ika.Entity(x, y, 1,
                                               '%s/tabitha_pistol.ika-sprite' %
                                               config.sprite_path))
        # Constants.               
        
        
        
        
        self.ground_friction = 0.10
        self.air_friction = 0.1
        self.ground_accel = self.ground_friction * 2
        self.air_accel = 0.0625
        self.max_vx = 2.0
        self.max_vy = 8.0
        self.gravity = 0.1
        self.jump_speed = 5
        
        self.abilities = {'sexy': True, 'wall-jump': True, 'double-jump': True}


        self.fire_delay = 0
        self.firing_rate = 8
        self.direction = Dir.LEFT                              
        
        self.hp = 120
        self.maxhp = 120
        self.mp = 100
        self.maxmp = 100
        # Increases max HP.
        self.givehp = 0
        # For dynamic changing of HP.
        self.dhp = 0
        # Increases max MP
        self.givemp = 0
        # For dynamic changing of MP.
        self.dmp = 0
        # Only show the mp bar when you have an ability!
        self.showmp = True
        self.hurt_count = 0
        self.hurtable = True
        # Only used if double-jumping ability enabled.
        self.max_jumps = 1
        self.jump_count = 0
        self.in_slope = False
        self.state = self.StandState
        self.msg = ''
        self.checkslopes = True
        self.was_in_slope = False
        self.lastpos = (0, 0)
        self.phantom = False
        self.fired = False

        self.cur_terrain = None

    def HasAbility(self, name):
        if name in self.abilities:
            return self.abilities[name]
        return False

    def Animate(self, strand, delay=10, loop=True, reset=True, reverse=False):
        strand = self.animations[strand]
        if reverse:
            strand = strand[:]
            strand.reverse()
        self.anim.set_anim(make_anim(strand, delay), loop, reset)

    def Fire(self, direction, offx=0, offy=0):
        if not self.fire_delay:
            bullet_x = self.x + offx
            bullet_y = self.y + offy
            #if self.direction == Dir.RIGHT:
            #    bullet_x += self.sprite.hotwidth + 2
            #if self.direction == Dir.LEFT:
            #    bullet_x -= 10
            engine.AddEntity(Bullet(bullet_x, bullet_y, direction))
            self.fire_delay = self.firing_rate

    def LadderState(self):
        self.Animate(('stand', self.direction), delay=5, loop=False)
        on_ladder = True
        self.jump_count = 0
        self.vx = 0
        self.vy = 0
        while on_ladder:
            if controls.down.Position() > controls.deadzone:
                if not self.floor:
                    self.y += 0.50
                else:
                    self.state = self.StandState
            if controls.up.Position() > controls.deadzone:
                if not self.floor:
                    self.y -= 0.50
                else:
                    self.state = self.StandState
            yield None
        self.state = self.StandState
        yield None

    def CrouchState(self):
        self.jump_count = 0
        self.vx = 0
        self.vy = 0
        self.Animate(('crouch', self.direction), delay=5, loop=False)
        fired = False
        while controls.down.Position() > controls.deadzone:
            if not self.floor:
                self.state = self.FallState
                yield None
            if self.anim.kill:
                self.Animate(('down', self.direction))
            if controls.attack.Pressed():
                fired = True
                if controls.aim_up.Position():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.UPRIGHT, offx=17, offy=10)
                    else:
                        self.Fire(Dir.UPLEFT, offx=-7, offy=10)
                elif controls.aim_down.Position():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.DOWNRIGHT, offx=15, offy=32)
                    else:
                        self.Fire(Dir.DOWNLEFT, offx=-7, offy=32)
                elif self.direction == Dir.RIGHT:
                    self.Fire(self.direction, offx=-8 + 31, offy=26)
                else:
                    self.Fire(self.direction, offx=-8, offy=26)
            if controls.left.Position() > controls.deadzone:
                self.direction = Dir.LEFT
            elif controls.right.Position() > controls.deadzone:
                self.direction = Dir.RIGHT
            if self.anim.loop:
                if controls.aim_up.Position():
                    self.Animate(('crouch', 'aim_dup', self.direction))
                elif controls.aim_down.Position():
                    self.Animate(('crouch', 'aim_ddown', self.direction))
                elif fired:
                    self.Animate(('crouch', 'aim', self.direction))
                else:
                    self.Animate(('down', self.direction))
            yield None
        # CROUCH->STAND
        self.Animate(('crouch', 'stand', self.direction), delay=5, loop=False)
        self.state = self.StandState
        yield None

    def StandState(self):
        if self.anim.loop:
            self.Animate(('stand', self.direction))
        fired = False
        self.jump_count = 0
        self.checkslopes = True
        upPressed = False
        while True:
            if self.anim.kill:
                self.Animate(('stand', self.direction))
            if controls.up.Position() == 0:
                upPressed = False
            if self.anim.loop:
                if controls.up.Position() > controls.deadzone:
                    z = self.RunnableZone()
                    if z is not None:
                        if not upPressed:
                            z.fire()
                            # Make sure you're not constantly refiring
                            # the zone.
                            upPressed = True
                    else:
                        self.Animate(('stand', 'aim_up', self.direction))
                elif controls.aim_up.Position():
                    self.Animate(('stand', 'aim_dup', self.direction))
                elif controls.aim_down.Position():
                    self.Animate(('stand', 'aim_ddown', self.direction))
                elif fired:
                    self.Animate(('stand', 'aim', self.direction))
                else:
                    self.Animate(('stand', self.direction))
            if not self.floor:
                self.state = self.FallState
            else:
                self.vx = vecmath.decrease_magnitude(self.vx,
                                                     self.ground_friction)
            # There's gotta be a better way to do this than putting it
            # in every state.
            if controls.attack.Pressed():
                fired = True
                if controls.up.Position() > controls.deadzone:
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.UP, offx=5 - 2, offy=-8)
                    else:
                        self.Fire(Dir.UP, offx=5, offy=-8)
                elif controls.aim_up.Position():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.UPRIGHT, offx=14, offy=-2)
                    else:
                        self.Fire(Dir.UPLEFT, offx=-4, offy=-2)
                elif controls.aim_down.Position():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.DOWNRIGHT, offx=14, offy=22)
                    else:
                        self.Fire(Dir.DOWNLEFT, offx=-5, offy=22)
                else:
                    if self.direction == Dir.RIGHT:
                        self.Fire(self.direction, offx=-10 + 31, offy=10)
                    else:
                        self.Fire(self.direction, offx=-10, offy=10)
                    self.Animate(('stand', 'aim', self.direction))
            if controls.left.Position() > controls.deadzone:
                if not self.left_wall:
                    if self.direction == Dir.LEFT:
                        self.Animate(('stand', 'run', self.direction), delay=5,
                                     loop=False)
                    else:
                        self.direction = Dir.LEFT
                        self.Animate(('stand', 'turn'), delay=5, loop=False,
                                     reverse=True)
                    self.state = self.WalkState
            elif controls.right.Position() > controls.deadzone and \
                 not self.right_wall:
                if self.direction == Dir.RIGHT:
                    self.Animate(('stand', 'run', self.direction), delay=5,
                                 loop=False)
                else:
                    self.direction = Dir.RIGHT
                    self.Animate(('stand', 'turn'), delay=5, loop=False)
                self.state = self.WalkState
                #self.Animate(('stand', 'run', self.direction), delay=5,
                #              loop=False)
            if controls.down.Position() > controls.deadzone:
                self.state = self.CrouchState
            elif controls.jump.Pressed() and not self.ceiling:
                self.jump_count = 1
                self.state = self.JumpState
                #controls.jump.Unpress()
            yield None

    def WalkState(self):
        self.jump_count = 0
        self.checkslopes = True
        if self.anim.loop:
            self.Animate(('run', self.direction), 7)
        fired = False
        while True:
            if self.anim.kill:
                self.Animate(('run', self.direction), 7)
            if not self.floor:
                self.state = self.FallState
            else:
                self.vx = vecmath.decrease_magnitude(self.vx,
                                                     self.ground_friction)
            if self.anim.cur_frame % 4 == 2 and self.anim.count == 0:
                sound.play('Step', 0.5)
                stepcount = 50
            # Ensure you fire only in looped animations.  Prevents
            # firing while turning.
            if controls.attack.Pressed() and self.anim.loop:
                fired = True
                if controls.up.Position() > controls.deadzone or \
                   controls.aim_up.Position():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.UPRIGHT, offx=21, offy=-2)
                    else:
                        self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                elif controls.down.Position() > controls.deadzone or \
                     controls.aim_down.Position():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.DOWNRIGHT, offx=21, offy=20)
                    else:
                        self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                elif self.direction == Dir.RIGHT:
                    self.Fire(self.direction, offx=-8 + 31, offy=10)
                else:
                    self.Fire(self.direction, offx=-8, offy=10)
            old_direction = self.direction
            if self.anim.loop:
                if controls.up.Position() > controls.deadzone or \
                   controls.aim_up.Position():
                    self.Animate(('run', 'aim_dup', self.direction), 7,
                                 reset=False)
                elif controls.down.Position() > controls.deadzone or \
                     controls.aim_down.Position():
                    self.Animate(('run', 'aim_ddown', self.direction), 7,
                                 reset=False)
                elif fired:
                    self.Animate(('run', 'aim', self.direction), 7,
                                 reset=False)
                else:
                    self.Animate(('run', self.direction), 7, reset=False)
            if controls.left.Position() > controls.deadzone:
                if not self.left_wall:
                    self.vx -= self.ground_accel
                    self.direction = Dir.LEFT
                else:
                    self.Animate(('run', 'turn', self.direction), delay=5,
                                 loop=False)
                    self.state = self.StandState
                    sound.play('Step', 0.5)
            elif controls.right.Position() > controls.deadzone:
                if not self.right_wall:
                    self.vx += self.ground_accel
                    self.direction = Dir.RIGHT
                else:
                    self.Animate(('run', 'turn', self.direction), delay=8,
                                 loop=False)
                    self.state = self.StandState
                    sound.play('Step', 0.5)
            else:
                if abs(self.vx) >= 1.8:
                    self.Animate(('run', 'turn', self.direction), delay=8,
                                 loop=False)
                if self.anim.count == 0:
                    self.state = self.StandState
                    sound.play('Step', 0.5)
            if old_direction != self.direction:
                self.Animate(('run', 'turn', old_direction), loop=False)
                sound.play('Step', 0.5)
            if controls.jump.Pressed() and not self.ceiling:
                self.jump_count = 1
                self.state = self.RunJumpState
                #controls.jump.unpress()
            yield None

    def FallState(self):
        #if controls.up.Position() > controls.deadzone:
        #     if controls.right.Position() > controls.deadzone:
        #        self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT), loop=False)
        #     elif controls.left.Position() > controls.deadzone:
        #        self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT), loop=False)
        #     else:
        #        self.Animate(('jump', 'fall', 'aim_up', self.direction), loop=False)
        #elif controls.down.Position() > controls.deadzone:
        #     if controls.right.Position() > controls.deadzone:
        #        self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT), loop=False)
        #     elif controls.left.Position() > controls.deadzone:
        #        self.Animate(('jump', 'fall', 'aim_ddown', Dir.LEFT), loop=False)
        #     else:
        #        self.Animate(('jump', 'fall', 'aim_down', self.direction), loop=False)
        #else:
        #     self.Animate(('jump', 'fall',  self.direction), loop=False)
        self.checkslopes = True
        while True:
            if controls.jump.Pressed() and not self.ceiling and \
               self.jump_count < self.max_jumps and \
               self.HasAbility('double-jump'):
                if self.jump_count == 0:
                    # Fell off something, so you lose a jump.
                    self.jump_count += 2
                else:
                    self.jump_count += 1
                self.state = self.JumpState
                self.vy = -self.jump_speed
                yield None
            if self.ceiling:
                self.vy = 0
                self.y += 1
            if self.floor:
                self.vy = 0
                self.Animate(('jump', 'stand', self.direction), delay=6,
                             loop=False)
                if controls.left.Position() > controls.deadzone or \
                   controls.right.Position() > controls.deadzone:
                    self.state = self.WalkState
                else:
                    self.state = self.StandState
                # Clear the jump button.
                controls.jump.Pressed()
                sound.play('Land')
            else:
                old_direction = self.direction
                if self.vy < 0 and self.ceiling:
                    self.vy = 0
                self.vy += self.gravity
                if controls.left.Position() > controls.deadzone and \
                   not self.left_wall:
                    self.vx -= self.air_accel
                    self.direction = Dir.LEFT
                if controls.right.Position() > controls.deadzone and \
                   not self.right_wall:
                    self.vx += self.air_accel
                    self.direction = Dir.RIGHT
                if old_direction != self.direction:
                    self.Animate(('fall', self.direction))
                if self.anim.loop or self.anim.kill:
                    #self.Animate(('fall', 'aim_dup', Dir.RIGHT), reset=True)
                    if controls.aim_up.Position():
                        self.Animate(('fall', 'aim_dup', self.direction),
                                     reset=False)
                    elif controls.aim_down.Position():
                        self.Animate(('fall', 'aim_ddown', self.direction),
                                     reset=False)
                    elif controls.up.Position() > controls.deadzone:
                        if controls.right.Position() > controls.deadzone:
                            self.Animate(('fall', 'aim_dup', Dir.RIGHT),
                                         reset=False)
                        elif controls.left.Position() > controls.deadzone:
                            self.Animate(('fall', 'aim_dup', Dir.LEFT),
                                         reset=False)
                        else:
                            self.Animate(('fall', 'aim_up', self.direction),
                                         reset=False)
                    elif controls.down.Position() > controls.deadzone:
                        if controls.right.Position() > controls.deadzone:
                            self.Animate(('fall', 'aim_ddown', Dir.RIGHT),
                                         reset=False)
                        elif controls.left.Position() > controls.deadzone:
                            self.Animate(('fall', 'aim_ddown', Dir.LEFT),
                                         reset=False)
                        else:
                            self.Animate(('fall', 'aim_down', self.direction),
                                         reset=False)
                    elif self.fired:
                        self.Animate(('fall', 'aim', self.direction), reset=False)
                    else:
                        self.Animate(('fall',  self.direction), reset=False)
                if controls.attack.Pressed():
                    self.fired = True
                    if controls.aim_up.Position():
                        if self.direction == Dir.LEFT:
                            self.Fire(Dir.UPLEFT, offx=-10, offy=-5)
                        else:
                            self.Fire(Dir.UPRIGHT, offx=21, offy=-5)
                    elif controls.aim_down.Position():
                        if self.direction == Dir.LEFT:
                            self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                        else:
                            self.Fire(Dir.DOWNRIGHT, offx=21, offy=20)
                    if controls.up.Position() > controls.deadzone:
                        if controls.right.Position() > controls.deadzone:
                            self.Fire(Dir.UPRIGHT, offx=21, offy=-2)
                        elif controls.left.Position() > controls.deadzone:
                            self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                        elif self.direction == Dir.RIGHT:
                            self.Fire(Dir.UP, offx=9 + -2, offy=-10)
                        else:
                            self.Fire(Dir.UP, offx=9, offy=-10)
                    elif controls.down.Position() > controls.deadzone:
                        if controls.right.Position() > controls.deadzone:
                            self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                        elif controls.left.Position() > controls.deadzone:
                            self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                        elif self.direction == Dir.RIGHT:
                            self.Fire(Dir.DOWN, offx=19, offy=15)
                        else:
                            self.Fire(Dir.DOWN, offx=0, offy=15)
                    elif self.direction == Dir.RIGHT:
                        self.Fire(self.direction, offx=-8 + 31, offy=10)
                    elif self.direction == Dir.LEFT:
                        self.Fire(self.direction, offx=-8, offy=10)                        
            yield None
        # FALL->STAND
        self.Animate(('fall', 'stand', self.direction), loop=False)
        #while not self.anim.kill:
        #    yield None
        yield None

    def JumpState(self):
        """STAND->JUMP"""
        #self.Animate(('stand', 'jump', self.direction), loop=False)
        if controls.aim_up.Position():
            self.Animate(('stand', 'jump', 'aim_dup', self.direction),
                         loop=False)
        elif controls.aim_down.Position():
            self.Animate(('stand', 'jump', 'aim_ddown', self.direction),
                         loop=False)
        elif controls.up.Position() > controls.deadzone:
            if controls.right.Position() > controls.deadzone:
                self.Animate(('stand', 'jump', 'aim_dup', Dir.RIGHT),
                             loop=False)
            elif controls.left.Position() > controls.deadzone:
                self.Animate(('stand', 'jump', 'aim_dup', Dir.LEFT),
                             loop=False)
            else:
                self.Animate(('stand', 'jump', 'aim_up', self.direction),
                             loop=False)
        elif controls.down.Position() > controls.deadzone:
            if controls.right.Position() > controls.deadzone:
                self.Animate(('stand', 'jump', 'aim_ddown', Dir.RIGHT),
                             loop=False)
            elif controls.left.Position() > controls.deadzone:
                self.Animate(('stand', 'jump', 'aim_ddown', Dir.LEFT),
                             loop=False)
            else:
                self.Animate(('stand', 'jump', 'aim_down', self.direction),
                             loop=False)
        else:
            self.Animate(('stand', 'jump',  self.direction), loop=False)
        self.checkslopes = False
        self.vy = -self.jump_speed
        self.fired = False
        while controls.jump.Position() > controls.deadzone and not self.fired:
            old_direction = self.direction
            if controls.left.Position() > controls.deadzone and \
               not self.left_wall:
                self.vx -= self.air_accel
                self.direction = Dir.LEFT
            elif controls.right.Position() > controls.deadzone and \
                 not self.right_wall:
                self.vx += self.air_accel
                self.direction = Dir.RIGHT
            if old_direction != self.direction:
                # If the direction changed, update the animation
                # sequence.
                self.Animate(('jump', self.direction))
            if self.anim.loop or self.anim.kill:
                if controls.aim_up.Position():
                    self.Animate(('stand', 'jump', 'aim_dup', self.direction),
                                 reset=False)
                elif controls.aim_down.Position():
                    self.Animate(('stand', 'jump', 'aim_ddown',
                                 self.direction), reset=False)
                elif controls.up.Position() > controls.deadzone:
                    if controls.right.Position() > controls.deadzone:
                        self.Animate(('jump', 'aim_dup', Dir.RIGHT),
                                     reset=False)
                    elif controls.left.Position() > controls.deadzone:
                        self.Animate(('jump', 'aim_dup', Dir.LEFT),
                                     reset=False)
                    else:
                        self.Animate(('jump', 'aim_up', self.direction),
                                     reset=False)
                elif controls.down.Position() > controls.deadzone:
                    if controls.right.Position() > controls.deadzone:
                        self.Animate(('jump', 'aim_ddown', Dir.RIGHT),
                                     reset=False)
                    elif controls.left.Position() > controls.deadzone:
                        self.Animate(('jump', 'aim_ddown', Dir.LEFT),
                                     reset=False)
                    else:
                        self.Animate(('jump', 'aim_down', self.direction),
                                     reset=False)
                else:
                    self.Animate(('jump',  self.direction), reset=False)
            if controls.attack.Pressed():
                self.jump_count = self.max_jumps
                self.fired = True
                if controls.aim_up.Position():
                    if self.direction == Dir.LEFT:
                       self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                    else:
                       self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                elif controls.aim_down.Position():
                    if self.direction == Dir.LEFT:
                       self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                    else:
                       self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                elif controls.up.Position() > controls.deadzone:
                    if controls.right.Position() > controls.deadzone:
                        self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                    elif controls.left.Position() > controls.deadzone:
                        self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                    elif self.direction == Dir.RIGHT:
                        self.Fire(Dir.UP, offx=9 - 2, offy=-10)
                    else:
                        self.Fire(Dir.UP, offx=9 + 0, offy=-10)
                elif controls.down.Position() > controls.deadzone:
                    if controls.right.Position() > controls.deadzone:
                        self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                    elif controls.left.Position() > controls.deadzone:
                        self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                    elif self.direction == Dir.RIGHT:
                        self.Fire(Dir.DOWN, offx=19, offy=15)
                    else:
                        self.Fire(Dir.DOWN, offx=0, offy=15)
                elif self.direction == Dir.RIGHT:
                    self.Fire(self.direction, offx=-8 + 31, offy=10)
                else:
                    self.Fire(self.direction, offx=-8, offy=10)
            if (self.left_wall and self.vx < 0) or \
               (self.right_wall and self.vx > 0):
                self.vx = 0
            if self.ceiling:
                self.vy = 0
                break
            self.vy += self.gravity
            if self.vy >= 0:
                break
            yield None
        # JUMP->FALL
        if self.vy < -1:
            self.vy = -1
        #if not fired:
            #self.Animate(('jump', 'fall', self.direction), loop=False)
        if controls.aim_up.Position():
            self.Animate(('jump', 'fall', 'aim_dup', self.direction),
                         loop=False)
        elif controls.aim_down.Position():
            self.Animate(('jump', 'fall', 'aim_ddown', self.direction),
                         loop=False)
        elif controls.up.Position() > controls.deadzone:
            if controls.right.Position() > controls.deadzone:
                self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT),
                             loop=False)
            elif controls.left.Position() > controls.deadzone:
                self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT), loop=False)
            else:
                self.Animate(('jump', 'fall', 'aim_up', self.direction),
                             loop=False)
        elif controls.down.Position() > controls.deadzone:
            if controls.right.Position() > controls.deadzone:
                self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT),
                             loop=False)
            elif controls.left.Position() > controls.deadzone:
                self.Animate(('jump', 'fall', 'aim_ddown', Dir.LEFT),
                             loop=False)
            else:
                self.Animate(('jump', 'fall', 'aim_down', self.direction),
                             loop=False)
        elif self.fired:
            self.Animate(('jump', 'fall', 'aim', self.direction), loop=False)
        else:
            self.Animate(('jump', 'fall',  self.direction), loop=False)
        self.state = self.FallState
        yield None

    def RunJumpState(self):
        """RUN->FLIP"""
        self.fired = False
        self.jump_count = self.max_jumps
        walljump = False
        self.Animate(('run', 'flip', self.direction), delay=5, loop=False)
        self.checkslopes = False
        self.vy = -self.jump_speed
        #i = self.jump_height
        while controls.jump.Position() > controls.deadzone:
            if self.anim.kill:
                self.Animate(('flip', self.direction), delay=4, loop=False)
            self.vy += self.gravity
            if self.vy >= 0:
                break
            old_direction = self.direction
            if controls.left.Position() > controls.deadzone and \
               not self.left_wall:
                self.vx -= self.air_accel
                self.direction = Dir.LEFT
            elif controls.right.Position() > controls.deadzone and \
                 not self.right_wall:
                self.vx += self.air_accel
                self.direction = Dir.RIGHT
            if old_direction != self.direction:
                # If the direction changed, update the animation sequence.
                self.Animate(('flip', self.direction), delay=4, loop=False,
                             reset=False)
            if controls.attack.Pressed():
                self.fired = True
                if controls.aim_up.Position():
                    if self.direction == Dir.LEFT:
                       self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                    else:
                       self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                elif controls.aim_down.Position():
                    if self.direction == Dir.LEFT:
                       self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                    else:
                       self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                elif controls.up.Position() > controls.deadzone:
                    if controls.right.Position() > controls.deadzone:
                        self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                    elif controls.left.Position() > controls.deadzone:
                        self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                    else:
                        self.Fire(Dir.UP, offx=-10, offy=-2)
                elif controls.down.Position() > controls.deadzone:
                    if controls.right.Position() > controls.deadzone:
                        self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                    elif controls.left.Position() > controls.deadzone:
                        self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                    else:
                        self.Fire(Dir.DOWN, offx=-10, offy=20)
                elif self.direction == Dir.RIGHT:
                    self.Fire(self.direction, offx=-8 + 31, offy=10)
                else:
                    self.Fire(self.direction, offx=-8, offy=10)
                break
            if self.left_wall or self.right_wall:
                self.vx = 0
            if self.ceiling:
                self.vy = 0
                self.y += 1
                break
            yield None
        if self.vy < -1:
            self.vy = -1
        if self.fired:
            if controls.aim_up.Position():
                self.Animate(('jump', 'fall', 'aim_dup', self.direction),
                             loop=False)
            elif controls.aim_down.Position():
                self.Animate(('jump', 'fall', 'aim_ddown', self.direction),
                             loop=False)
            elif controls.up.Position() > controls.deadzone:
                if controls.right.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT),
                                 loop=False)
                else:
                    self.Animate(('jump', 'fall', 'aim_up', self.direction),
                                 loop=False)
            elif controls.down.Position() > controls.deadzone:
                if controls.right.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_ddown', Dir.LEFT),
                                 loop=False)
                else:
                    self.Animate(('jump', 'fall', 'aim_down', self.direction),
                                 loop=False)
            else:
                self.Animate(('jump', 'fall',  'aim', self.direction),
                             loop=False)
            self.state = self.FallState
            yield None
        #Falling now
        self.checkslopes = True
        self.Animate(('flip', self.direction), delay=4)
        while True:
            if self.ceiling:
                self.vy = 0
                self.y += 1
            if controls.jump.Pressed() and self.HasAbility('wall-jump'):  #and (self.right_wall or self.left_wall)
                if self.check_v_line(self.x + self.vx + self.width + 2,
                                     self.y + 1, self.y + self.height - 1) and \
                   controls.left.Position() > controls.deadzone:
                    self.vx = -1.5
                    self.direction = Dir.LEFT
                    walljump = True
                    break
                if self.check_v_line(self.x + self.vx - 2, self.y + 1,
                                     self.y + self.height - 1) and \
                   controls.right.Position() > controls.deadzone:
                    self.vx = 1.5
                    self.direction = Dir.RIGHT
                    walljump = True
                    break
            if self.floor:
                self.vy = 0
                self.Animate(('flip', 'stand', self.direction), delay=6,
                             loop=False)
                if controls.left.Position() > controls.deadzone or \
                   controls.right.Position() > controls.deadzone:
                    self.state = self.WalkState
                else:
                    self.state = self.StandState
                sound.play('Land')
                self.fired = False
            else:
                old_direction = self.direction
                if self.vy < 0 and self.ceiling:
                    self.vy = 0
                self.vy += self.gravity
                if controls.left.Position() > controls.deadzone and \
                   not self.left_wall:
                    self.vx -= self.air_accel
                    self.direction = Dir.LEFT
                if controls.right.Position() > controls.deadzone and \
                   not self.right_wall:
                    self.vx += self.air_accel
                    self.direction = Dir.RIGHT
                if old_direction != self.direction:
                    self.Animate(('flip', self.direction), delay=4)
                if controls.attack.Pressed():
                    self.fired = True
                    if controls.aim_up.Position():
                        if self.direction == Dir.LEFT:
                            self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                        else:
                            self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                    elif controls.aim_down.Position():
                        if self.direction == Dir.LEFT:
                            self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                        else:
                            self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                    elif controls.up.Position() > controls.deadzone:
                        if controls.right.Position() > controls.deadzone:
                            self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                        elif controls.left.Position() > controls.deadzone:
                            self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                        else:
                            self.Fire(Dir.UP, offx=-10, offy=-2)
                    elif controls.down.Position() > controls.deadzone:
                        if controls.right.Position() > controls.deadzone:
                            self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                        elif controls.left.Position() > controls.deadzone:
                            self.Fire(Dir.DOWNLEFT, offx=-10, offy=20)
                        else:
                            self.Fire(Dir.DOWN, offx=-10, offy=20)
                    elif self.direction == Dir.RIGHT:
                        self.Fire(self.direction, offx=-8 + 31, offy=10)
                    else:
                        self.Fire(self.direction, offx=-8, offy=10)
                    break
            yield None
        # FLIP->STAND
        #self.Animate(('flip', 'stand', self.direction), delay=4, loop=False)
        #while not self.anim.kill:
        #    yield None
        #self.state = self.FallState
        if self.fired:
            if controls.aim_up.Position():
                self.Animate(('jump', 'fall', 'aim_dup', self.direction),
                             loop=False)
            elif controls.aim_down.Position():
                self.Animate(('jump', 'fall', 'aim_ddown', self.direction),
                             loop=False)
            elif controls.up.Position() > controls.deadzone:
                if controls.right.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT),
                                 loop=False)
                else:
                    self.Animate(('jump', 'fall', 'aim_up', self.direction),
                                 loop=False)
            elif controls.down.Position() > controls.deadzone:
                if controls.right.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Position() > controls.deadzone:
                    self.Animate(('jump', 'fall', 'aim_ddown', Dir.LEFT),
                                 loop=False)
                else:
                    self.Animate(('jump', 'fall', 'aim_down', self.direction),
                                 loop=False)
            else:
                self.Animate(('jump', 'fall', 'aim', self.direction),
                             loop=False)
            self.state = self.FallState
        if walljump:
            self.state = self.RunJumpState
        yield None

    def Hurt(self, damage):
        if self.hurtable:
            self.dhp -= damage
            # Going to die anyway, bwahaha. :D
            if self.hp + self.dhp <= 0:
                self.hp = 0
                engine.GameOver()
            self.state = self.HurtState

    def HurtState(self):
        # Can't get hurt while you just got hit!
        self.hurtable = False
        self.checkslopes = True
        onground = False
        if self.floor:
            self.Animate(('hurt', self.direction), delay=8, loop=False)
            onground = True
        else:
            self.Animate(('hurt', 'air', self.direction), delay=8, loop=False)
        while not self.anim.kill:
            if self.ceiling:
                self.vy = 0
                self.y += 1
            if self.floor:
                # Was in the air originally, so land.
                if not onground:
                    sound.play('Land')
                    onground = True
                self.vy = 0
                self.vx = 0
            else:
                if self.vy < 0 and self.ceiling:
                    self.vy = 0
                self.vy += self.gravity
            yield None
        if onground:
            self.state = self.StandState
        else:
            self.state = self.FallState
        self.hurt_count = 100
        yield None

    def LoadState(self):
        self.hurtable = False
        self.Animate(('stand', 'face'), delay=1)
        ticks = 0
        #while ticks < 300:
        #    ticks += 1
        #    yield None
        while True:
            yield None
        self.state = self.StandState
        yield None

    def CheckLadderTile(self, x, y):
        tx = x / ika.Map.tilewidth
        ty = y / ika.Map.tileheight
        tile = ika.Map.GetTile(tx, ty, self.layer)
        if tile in ladderTiles:
            return True

    def CheckSlopeTile(self, x, y, reposition=True):
        tx = x / ika.Map.tilewidth
        ty = y / ika.Map.tileheight
        tile = ika.Map.GetTile(tx, ty, self.layer)
        a = (ty + 1) * ika.Map.tileheight
        b = x % ika.Map.tileheight
        if tile in slopeTiles[Dir.RIGHT]:  # \
            if reposition:
                if self.vx > 0 and self.vy == 0:
                    self.y = a + b - self.sprite.hotheight - ika.Map.tileheight + 1
                else:
                    self.y = a + b - self.sprite.hotheight - ika.Map.tileheight
            return True
        elif tile in slopeTiles[Dir.LEFT]:  # /
            if reposition:
                if self.vx < 0 and self.vy == 0:
                    self.y = a - b - self.sprite.hotheight
                else:
                    self.y = a - b - self.sprite.hotheight - 1
            return True
        elif tile in halfSlopeTiles[(Dir.LEFT, 'bottom')]:  # /
            if reposition:
                if self.vx < 0 and self.vy == 0:
                    self.y = a - b / 2 - self.sprite.hotheight
                else:
                    self.y = a - b / 2 - self.sprite.hotheight - 1
            return True
        elif tile in halfSlopeTiles[(Dir.LEFT, 'top')]:  # /
            if reposition:
                if self.vx < 0 and self.vy == 0:
                    self.y = a - b / 2 - self.sprite.hotheight - ika.Map.tileheight / 2
                else:
                    self.y = a - b / 2 - self.sprite.hotheight - ika.Map.tileheight / 2 - 1
            return True
        elif tile in halfSlopeTiles[(Dir.RIGHT, 'bottom')]:  # \
            if reposition:
                if self.vx > 0 and self.vy == 0:
                    self.y = a + b / 2 - self.sprite.hotheight - ika.Map.tileheight + 1
                else:
                    self.y = a + b / 2 - self.sprite.hotheight - ika.Map.tileheight
            return True
        elif tile in halfSlopeTiles[(Dir.RIGHT, 'top')]:  # \
            if reposition:
                if self.vx > 0 and self.vy == 0:
                    self.y = a + b / 2 - self.sprite.hotheight - ika.Map.tileheight / 2 + 1
                else:
                    self.y = a + b / 2 - self.sprite.hotheight - ika.Map.tileheight / 2
            return True
        return False

    def CheckSlopes(self):
        x = int(self.x + self.sprite.hotwidth / 2 + self.vx)
        y = int(self.y + self.sprite.hotheight + self.vy - 1)
        self.in_slope = False
        reposition = True
        if self.vx == 0 and self.vy == 0:
            reposition = False
        if self.CheckSlopeTile(x, y, reposition):
            self.in_slope = True
        if self.CheckSlopeTile(x, y + 1, reposition):
            self.in_slope = True
            y += 1
        if self.CheckSlopeTile(x + 1, y + 1, reposition):
            self.in_slope = True
            y += 1
            x += 1
        if self.CheckSlopeTile(x - 1, y + 1, reposition):
            self.in_slope = True
            y += 1
            x += 1
        if self.in_slope:
            self.msg = 'slope up'
            self.floor=True
            self.left_wall=False
            self.right_wall=False
            self.vx = vecmath.clamp(self.vx, -1.6, 1.6)
            self.vy = 0
            self.was_in_slope = True
            self.lastpos = (x / ika.Map.tilewidth, y / ika.Map.tileheight)
            return True
        self.was_in_slope = False
        return False

    def CheckObstructions(self):
        x = round(self.x)
        y = round(self.y + self.vy)
        self.ceiling = self.check_h_line(x + 1, y - 1, x + self.width - 1)
        self.floor = self.check_h_line(x + 1,y + self.height, x + self.width - 1)
        if self.floor and not self.ceiling:
            # Find the tile that the entity will be standing on,
            # and set it to be standing exactly on it:
            tiley = int((y + self.height) / ika.Map.tileheight)
            self.y = tiley * ika.Map.tileheight - self.height
            self.vy = 0
        if self.ceiling and self.vy != 0:
            tiley = int((y - 1) / ika.Map.tileheight)
            self.y = (tiley + 1) * ika.Map.tileheight
            self.vy = 0
        # Reset y, in case vy was modified.
        x = round(self.x + self.vx)
        y = round(self.y)
        self.left_wall = self.check_v_line(x, y + 1, y + self.height - 1)
        self.right_wall = self.check_v_line(x + self.width, y + 1,
                                            y + self.height - 1)
        if self.left_wall and not self.phantom:
            tilex = int(x / ika.Map.tilewidth)
            self.x = (tilex + 1) * ika.Map.tilewidth - 1
            self.vx = max(0, self.vx)
        if self.right_wall and not self.phantom:
            tilex = int((x + self.width) / ika.Map.tilewidth)
            self.x = tilex * ika.Map.tilewidth - self.width
            self.vx = min(0, self.vx)
        for entity in self.detect_collision():
            if entity is not None and entity.touchable:
                entity.touch(self)

    def RunnableZone(self):
        """Find if there's any activatable zones near the player."""
        for f in engine.fields:
            if f.test(self) and f.runnable:
                return f

    def update(self):
        self.msg = ''
        
        #check current terrain to set appropriate terrain speeds, mostly just water.
        if self.cur_terrain:
            self.ground_friction = 0.15
            self.air_friction = 0.20
            self.ground_accel = 0.20
            self.air_accel = 0.032
            self.max_vx = 1.5
            self.max_vy = 6.0
            self.gravity = 0.05
            self.jump_speed = 3.2
                          
        else: #defaults
            self.ground_friction = 0.10
            self.air_friction = 0.10
            self.ground_accel = self.ground_friction * 2
            self.air_accel = 0.0625
            self.max_vx = 2.0
            self.max_vy = 8.0
            self.gravity = 0.1
            self.jump_speed = 5
        
        
        
        ### hack hack hack ###
        if self.hurt_count > 0:
            # Flash.
            if self.hurt_count / 4 % 2:
                self.sprite.visible = False
            else:
                self.sprite.visible = True
            self.hurt_count -= 1
            # All done.
            if self.hurt_count == 0:
                self.hurtable = True
                self.sprite.visible = True
        # Hurt.
        if self.dhp < 0:
            self.hp -= 1
            self.dhp += 1
            if self.hp <= 0:
                self.hp = 0
                engine.GameOver()
        # Heal.
        if self.dhp > 0:
            self.hp += 1
            self.dhp -= 1
            if self.hp >= self.maxhp:
                self.hp = self.maxhp
        # Hurt.
        if self.dmp < 0:
            self.mp -= 1
            self.dmp += 1
            if self.mp <= 0:
                self.mp = 0
        # Heal.
        if self.dmp > 0:
            self.mp += 1
            self.dmp -= 1
            if self.mp >= self.maxmp:
                self.mp = self.maxmp
        if self.givehp > 0:
            self.maxhp += 1
            self.hp += 1
            self.givehp -= 1
            engine.hud.resize()
        if self.givemp > 0:
            self.maxmp += 1
            self.mp += 1
            self.givemp -= 1
            engine.hud.resize()
        if self.fire_delay > 0:
            self.fire_delay -= 1
        ### end hack hack hack ###
        if self.checkslopes:
            if not self.CheckSlopes():
                self.CheckObstructions()
        else:
            self.CheckObstructions()
        self.vx = vecmath.clamp(self.vx, -self.max_vx, self.max_vx)
        self.vy = vecmath.clamp(self.vy, -self.max_vy, self.max_vy)
        self.x += self.vx
        self.y += self.vy
        self.sprite.x = int(self.x)
        self.sprite.y = int(self.y)
        self.state__()
        self.animation()
