#!/usr/bin/env python

import ika
import vecmath
import config
import controls
import parser
from entity import Entity
from engine import engine
from bullet import Bullet, Beam
from anim import make_anim
from sounds import sound
from const import Dir
import fonts

slopeTiles = {Dir.LEFT:  [347, 623, 746, 885, 876],  # / #hack! need to make part of tileset metadata..
              Dir.RIGHT: [346, 622, 749, 889, 878]}  # \
halfSlopeTiles = {(Dir.LEFT,  'top'):    [465, 473],   # /
                  (Dir.LEFT,  'bottom'): [464, 472],   # /
                  (Dir.RIGHT, 'top'):    [468, 470],   # \
                  (Dir.RIGHT, 'bottom'): [469, 471]}   # \
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



        self.SetPhysics('normal')
        self.abilities = {'sexy': True, 'wall-jump': True, 'double-jump': False}
        self.weapons = ['Bullet', 'Beam']
        self.curweapon = 'Bullet'

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
        self.msgtime = 0

        self.checkslopes = True
        self.was_in_slope = False
        self.wallcounter = 0 #0 if not on a wall, >0 will be number of ticks to remember that she was touching a wall.
        self.platformcounter = 0 #similar to wall counter
        self.floorcounter = 0
        #self.wallticks = 3 #number of ticks to remember that a wall had been touched, for wall jumping purposes
        self.jumpticks = 0 #number of ticks to remember that we just started a jump...
        self.lastpos = (0, 0) #last x,y position

        self.phantom = False
        self.fired = False

        self.cur_terrain = None
        self.cur_platform = None

        self.ledge=False

        #extra platform speeds
        self.pvx = 0
        self.pvy = 0
        self.platform
        #self.testimg = ika.Image("sprites/platform.png")
        self.animspeed=5 #base animation speed
        self.animspeed_multiplier=1

    def SetPhysics(self, terrain='normal'):
        if terrain=='normal':
            self.ground_friction = 0.32
            self.air_friction = 0.125
            self.ground_accel = 0.5
            self.air_accel = 0.0625
            self.max_vx = 1.6
            self.max_vy = 6.0
            self.gravity = 0.1
            self.jump_speed = 4.8
            self.animspeed_multiplier=1

        elif terrain=='water':
            self.ground_friction = 0.15
            self.air_friction = 0.20
            self.ground_accel = 0.20
            self.air_accel = 0.032
            self.max_vx = 1.2
            self.max_vy = 4.0
            self.gravity = 0.04
            self.jump_speed = 3.2
            self.animspeed_multiplier=2

        else:
            pass #no valid physics set!

    def draw(self):
        #print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+40), "x:", str(self.x)
        #print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+50), "vx:", str(self.vx)
        #print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+60), "pvx:", str(self.pvx)
        #print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+70), "platform:", str(self.cur_platform is not None)


        #tx = x / ika.Map.tilewidth
        #ty = y / ika.Map.tileheight
        #tile = ika.Map.GetTile(tx, ty, self.layer)

        pass
        #ika.Video.DrawRect(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin, int(self.x)-ika.Map.xwin+self.sprite.hotwidth, int(self.y)-ika.Map.ywin+self.sprite.hotheight, ika.RGB(0,250,100,200))
        #self.testimg.Blit(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin)



    def HasAbility(self, name):
        if name in self.abilities:
            return self.abilities[name]
        return False

    def Animate(self, strand, delay=10, loop=True, reset=True, reverse=False, mult=True):
        strand = self.animations[strand]
        if reverse:
            strand = strand[:]
            strand.reverse()
        if mult: #apply animspeed modifier, water slows you down
            self.anim.set_anim(make_anim(strand, delay*self.animspeed_multiplier), loop, reset)
        else:
            self.anim.set_anim(make_anim(strand, delay), loop, reset)

    def Fire(self, direction, offx=0, offy=0):
        if self.curweapon=='Bullet':
            if not self.fire_delay:
                bullet_x = self.x + offx
                bullet_y = self.y + offy
                #if self.direction == Dir.RIGHT:
                #    bullet_x += self.sprite.hotwidth + 2
                #if self.direction == Dir.LEFT:
                #    bullet_x -= 10
                engine.AddEntity(Bullet(bullet_x, bullet_y, direction))
                self.fire_delay = self.firing_rate
        elif self.curweapon=='Beam':
            if not self.fire_delay:
                bullet_x = self.x + offx
                bullet_y = self.y + offy
                engine.AddEntity(Beam(bullet_x, bullet_y, direction))
                self.fire_delay = self.firing_rate    
            

    def ProcessAirMovement(self):
        if controls.left.Pos():
            if not self.left_wall:
                self.vx -= self.air_accel
                self.direction = Dir.LEFT
                
            #else: #pressing against left wall
            #    if not self.check_v_line(self.x-1, self.y-4, self.y) and self.check_v_line(self.x-1, self.y+1, self.y+6):
            #        sound.play('Land') #connected to left ledge!
            #        self.vy=0
            #        self.state = self.LedgeState
                    #todo: snap to tile completely

        if controls.right.Pos():
            if not self.right_wall:
                self.vx += self.air_accel
                self.direction = Dir.RIGHT
            #else: #pressing against right wall
            #    if not self.check_v_line(self.x+self.w+1, self.y-4, self.y) and self.check_v_line(self.x+self.w+1, self.y+1, self.y+6):
            #        sound.play('Land') #connected to right ledge!
            #        self.vy=0
            #        self.state = self.LedgeState

    #not currently used..
    def LadderState(self):
        self.Animate(('stand', self.direction), delay=self.animspeed, loop=False)
        on_ladder = True
        self.jump_count = 0
        self.vx = 0
        self.vy = 0
        while on_ladder:
            if controls.down.Pos():
                if not self.floor:
                    self.y += 0.50
                else:
                    self.state = self.StandState
            if controls.up.Pos():
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
        self.Animate(('crouch', self.direction), delay=self.animspeed, loop=False)
        fired = False
        while True:
            if controls.up.Pos():
                break


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
            if controls.left.Pos():
                self.direction = Dir.LEFT
            elif controls.right.Pos():
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
        self.Animate(('crouch', 'stand', self.direction), delay=self.animspeed, loop=False)
        self.state = self.StandState
        yield None

    #TODO: only works with tiles, not platforms or obstructable entities right now
    def LedgeState(self):
        self.checkslopes=False
        self.Animate(('stand','aim_up', self.direction))
        while True:
            if self.anim.kill:
                self.Animate(('stand','aim_up', self.direction))
            if controls.down.Pos():
                self.state=self.FallState #need to change to aim down later

            if controls.up.Pos():
                #climb state eventually, but for now placing directly on ledge tile. Animate later.
                #TODO: make sure there is enough room for Tabby before climbing.
                if self.direction==Dir.LEFT:
                    tilex=int((self.x-1)/16) #hack, should be tile width
                    tiley=int(self.y/16)+1
                    self.x=tilex*16
                    self.y=tiley*16-self.h
                else: #right
                    tilex=int((self.x+self.w+1)/16) #hack, should be tile width
                    tiley=int(self.y/16)+1
                    self.x=tilex*16
                    self.y=tiley*16-self.h

                self.state=self.StandState

            if controls.jump.Pos():
                if controls.left.Pos() and self.direction==Dir.RIGHT: #grabbing ledge from left side, jump left
                    self.vx = -1.5
                    self.direction=Dir.LEFT #face other direction now
                    self.state=self.RunJumpState

                elif controls.right.Pos() and self.direction==Dir.LEFT: #grabbing ledge from right side, jump right
                    self.vx = 1.5
                    self.direction=Dir.RIGHT
                    self.state=self.RunJumpState
                else:   #climb or fall? need to decide what feels best
                    pass
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




            if controls.up.Position() < controls.deadzone:
                upPressed = False

            if self.anim.loop:
                if controls.up.Pos():
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
                if self.cur_platform is None:
                    self.state = self.FallState
                    self.jump_count = 1
            else:
                self.vx = vecmath.decrease_magnitude(self.vx,
                                                     self.ground_friction)
            # There's gotta be a better way to do this than putting it
            # in every state.
            if controls.attack.Pressed():
                fired = True
                if controls.up.Pos():
                    if self.direction == Dir.RIGHT:
                        self.Fire(Dir.UP, offx=3, offy=-8)
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
            if controls.left.Pos():
                if not self.left_wall:
                    if self.direction == Dir.LEFT:
                        self.Animate(('stand', 'run', self.direction), delay=self.animspeed,
                                     loop=False, mult=False)
                    else:
                        self.direction = Dir.LEFT
                        self.Animate(('stand', 'turn'), delay=self.animspeed, loop=False,
                                     reverse=True, mult=False)
                    self.state = self.WalkState
            elif controls.right.Position() > controls.deadzone and \
                 not self.right_wall:
                if self.direction == Dir.RIGHT:
                    self.Animate(('stand', 'run', self.direction), delay=self.animspeed,
                                 loop=False)
                else:
                    self.direction = Dir.RIGHT
                    self.Animate(('stand', 'turn'), delay=self.animspeed, loop=False, mult=False)
                self.state = self.WalkState
                #self.Animate(('stand', 'run', self.direction), delay=self.animspeed,
                #              loop=False)
            if controls.down.Pos():
                self.state = self.CrouchState
            elif controls.jump.Pressed() and not self.ceiling:
                self.jump_count = 1
                self.state = self.JumpState
                if self.cur_platform:
                    self.cur_platform=None
                    self.pvx=0
                    self.pvy=0
                    self.floor=False
                #controls.jump.Unpress()
            yield None

    def WalkState(self):
        self.jump_count = 0
        self.checkslopes = True
        if self.anim.loop:
            self.Animate(('run', self.direction), self.animspeed+2)
        fired = False
        self.checkslopes=True
        while True:
            if self.anim.kill:
                self.Animate(('run', self.direction), self.animspeed+2)
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
                    self.Animate(('run', 'aim_dup', self.direction), self.animspeed+2,
                                 reset=False)
                elif controls.down.Position() > controls.deadzone or \
                     controls.aim_down.Position():
                    self.Animate(('run', 'aim_ddown', self.direction), self.animspeed+2,
                                 reset=False)
                elif fired:
                    self.Animate(('run', 'aim', self.direction), self.animspeed+2,
                                 reset=False)
                else:
                    self.Animate(('run', self.direction), self.animspeed+2, reset=False)
            if controls.left.Pos():
                if not self.left_wall:
                    self.vx -= self.ground_accel
                    self.direction = Dir.LEFT
                else:
                    self.Animate(('run', 'turn', self.direction), delay=self.animspeed,
                                 loop=False)
                    self.state = self.StandState
                    sound.play('Step', 0.5)
            elif controls.right.Pos():
                if not self.right_wall:
                    self.vx += self.ground_accel
                    self.direction = Dir.RIGHT
                else:
                    self.Animate(('run', 'turn', self.direction), delay=self.animspeed+2,
                                 loop=False)
                    self.state = self.StandState
                    sound.play('Step', 0.5)
            else:
                if abs(self.vx) >= 1.8:
                    self.Animate(('run', 'turn', self.direction), delay=self.animspeed+2,
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
        #if controls.up.Pos():
        #     if controls.right.Pos():
        #        self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT), loop=False)
        #     elif controls.left.Pos():
        #        self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT), loop=False)
        #     else:
        #        self.Animate(('jump', 'fall', 'aim_up', self.direction), loop=False)
        #elif controls.down.Pos():
        #     if controls.right.Pos():
        #        self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT), loop=False)
        #     elif controls.left.Pos():
        #        self.Animate(('jump', 'fall', 'aim_ddown', Dir.LEFT), loop=False)
        #     else:
        #        self.Animate(('jump', 'fall', 'aim_down', self.direction), loop=False)
        #else:
        #     self.Animate(('jump', 'fall',  self.direction), loop=False)

        self.checkslopes=True
        while True:
            if self.HasAbility('double-jump') and controls.jump.Pressed() \
                and not self.ceiling and self.jump_count < self.max_jumps:
                if self.jump_count == 0: # Didn't jump bfore, fell off something, so you only get the one jump.
                    self.jump_count = 2
                else: #had jumped at least once before.
                    self.jump_count += 1
                self.state = self.JumpState
                self.vy = -self.jump_speed
                yield None
            if self.ceiling:
                self.vy = 0
                self.y += 1 #move down one pixel when hitting a cieling... hack
            if self.floor or self.cur_platform:
                self.vy = 0

                self.Animate(('jump', 'stand', self.direction), delay=self.animspeed+1,
                             loop=False)
                if controls.left.Position() > controls.deadzone or \
                   controls.right.Pos():
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

                #air movement and ledge grabbing
                self.ProcessAirMovement()


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
                    elif controls.up.Pos():
                        if controls.right.Pos():
                            self.Animate(('fall', 'aim_dup', Dir.RIGHT),
                                         reset=False)
                        elif controls.left.Pos():
                            self.Animate(('fall', 'aim_dup', Dir.LEFT),
                                         reset=False)
                        else:
                            self.Animate(('fall', 'aim_up', self.direction),
                                         reset=False)
                    elif controls.down.Pos():
                        if controls.right.Pos():
                            self.Animate(('fall', 'aim_ddown', Dir.RIGHT),
                                         reset=False)
                        elif controls.left.Pos():
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
                    if controls.up.Pos():
                        if controls.right.Pos():
                            self.Fire(Dir.UPRIGHT, offx=21, offy=-2)
                        elif controls.left.Pos():
                            self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                        elif self.direction == Dir.RIGHT:
                            self.Fire(Dir.UP, offx=9 - 6, offy=-10)
                        else:
                            self.Fire(Dir.UP, offx=9, offy=-10)
                    elif controls.down.Pos():
                        if controls.right.Pos():
                            self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                        elif controls.left.Pos():
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
        self.checkslopes = False
        self.vy = -self.jump_speed
        self.jumpticks=3 #Just started jumping
        self.fired = False
        jumplength=5 #must jump for at least 5 ticks



        """STAND->JUMP"""
        #self.Animate(('stand', 'jump', self.direction), loop=False)
        if controls.aim_up.Position():
            self.Animate(('stand', 'jump', 'aim_dup', self.direction),
                         loop=False)
        elif controls.aim_down.Position():
            self.Animate(('stand', 'jump', 'aim_ddown', self.direction),
                         loop=False)
        elif controls.up.Pos():
            if controls.right.Pos():
                self.Animate(('stand', 'jump', 'aim_dup', Dir.RIGHT),
                             loop=False)
            elif controls.left.Pos():
                self.Animate(('stand', 'jump', 'aim_dup', Dir.LEFT),
                             loop=False)
            else:
                self.Animate(('stand', 'jump', 'aim_up', self.direction),
                             loop=False)
        elif controls.down.Pos():
            if controls.right.Pos():
                self.Animate(('stand', 'jump', 'aim_ddown', Dir.RIGHT),
                             loop=False)
            elif controls.left.Pos():
                self.Animate(('stand', 'jump', 'aim_ddown', Dir.LEFT),
                             loop=False)
            else:
                self.Animate(('stand', 'jump', 'aim_down', self.direction),
                             loop=False)
        else:
            self.Animate(('stand', 'jump',  self.direction), loop=False)



        looping=True
        while looping:

            if jumplength>0: jumplength-=1
            elif not controls.jump.Pos():
                    looping=False

            if self.fired: looping=False #can still break out of jump early by firing



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
                elif controls.up.Pos():
                    if controls.right.Pos():
                        self.Animate(('jump', 'aim_dup', Dir.RIGHT),
                                     reset=False)
                    elif controls.left.Pos():
                        self.Animate(('jump', 'aim_dup', Dir.LEFT),
                                     reset=False)
                    else:
                        self.Animate(('jump', 'aim_up', self.direction),
                                     reset=False)
                elif controls.down.Pos():
                    if controls.right.Pos():
                        self.Animate(('jump', 'aim_ddown', Dir.RIGHT),
                                     reset=False)
                    elif controls.left.Pos():
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
                elif controls.up.Pos():
                    if controls.right.Pos():
                        self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                    elif controls.left.Pos():
                        self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                    elif self.direction == Dir.RIGHT:
                        self.Fire(Dir.UP, offx=9 - 6, offy=-10)
                    else:
                        self.Fire(Dir.UP, offx=9 + 0, offy=-10)
                elif controls.down.Pos():
                    if controls.right.Pos():
                        self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                    elif controls.left.Pos():
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
                break #starting to fall...
            yield None
        # JUMP->FALL
        if self.vy < -1: #bit of a hack, sets vertical speed to be -1 or slower if jump button is released
            self.vy = -1
        #if not fired:
            #self.Animate(('jump', 'fall', self.direction), loop=False)
        if controls.aim_up.Position():
            self.Animate(('jump', 'fall', 'aim_dup', self.direction),
                         loop=False)
        elif controls.aim_down.Position():
            self.Animate(('jump', 'fall', 'aim_ddown', self.direction),
                         loop=False)
        elif controls.up.Pos():
            if controls.right.Pos():
                self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT),
                             loop=False)
            elif controls.left.Pos():
                self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT), loop=False)
            else:
                self.Animate(('jump', 'fall', 'aim_up', self.direction),
                             loop=False)
        elif controls.down.Pos():
            if controls.right.Pos():
                self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT),
                             loop=False)
            elif controls.left.Pos():
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
        self.jumpticks=3
        self.Animate(('run', 'flip', self.direction), delay=self.animspeed, loop=False)
        self.checkslopes = False
        self.vy = -self.jump_speed
        #i = self.jump_height
        while controls.jump.Pos():
            if self.anim.kill:
                self.Animate(('flip', self.direction), delay=4, loop=False)
            self.vy += self.gravity
            if self.vy >= 0:
                break
            old_direction = self.direction

            self.ProcessAirMovement()

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
                elif controls.up.Pos():
                    if controls.right.Pos():
                        self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                    elif controls.left.Pos():
                        self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                    else:
                        self.Fire(Dir.UP, offx=-10, offy=-2)
                elif controls.down.Pos():
                    if controls.right.Pos():
                        self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                    elif controls.left.Pos():
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
            elif controls.up.Pos():
                if controls.right.Pos():
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Pos():
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT),
                                 loop=False)
                else:
                    self.Animate(('jump', 'fall', 'aim_up', self.direction),
                                 loop=False)
            elif controls.down.Pos():
                if controls.right.Pos():
                    self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Pos():
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
                   controls.left.Pos():
                    self.vx = -1.5
                    self.direction = Dir.LEFT
                    walljump = True
                    break
                if self.check_v_line(self.x + self.vx - 2, self.y + 1,
                                     self.y + self.height - 1) and \
                   controls.right.Pos():
                    self.vx = 1.5
                    self.direction = Dir.RIGHT
                    walljump = True
                    break

            if self.floor:
                self.vy = 0
                self.Animate(('flip', 'stand', self.direction), delay=6,
                             loop=False)
                if controls.left.Position() > controls.deadzone or \
                   controls.right.Pos():
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
                self.ProcessAirMovement()



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
                    elif controls.up.Pos():
                        if controls.right.Pos():
                            self.Fire(Dir.UPRIGHT, offx=30, offy=-2)
                        elif controls.left.Pos():
                            self.Fire(Dir.UPLEFT, offx=-10, offy=-2)
                        else:
                            self.Fire(Dir.UP, offx=-10, offy=-2)
                    elif controls.down.Pos():
                        if controls.right.Pos():
                            self.Fire(Dir.DOWNRIGHT, offx=28, offy=20)
                        elif controls.left.Pos():
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
            elif controls.up.Pos():
                if controls.right.Pos():
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Pos():
                    self.Animate(('jump', 'fall', 'aim_dup', Dir.LEFT),
                                 loop=False)
                else:
                    self.Animate(('jump', 'fall', 'aim_up', self.direction),
                                 loop=False)
            elif controls.down.Pos():
                if controls.right.Pos():
                    self.Animate(('jump', 'fall', 'aim_ddown', Dir.RIGHT),
                                 loop=False)
                elif controls.left.Pos():
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

    def IdleState(self, strand = ('stand', 'face'), delay=1 ):
        self.hurtable = False
        self.Animate(strand, delay)


        self.vx = 0
        self.vy = 0

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
        a = (ty + 1) * ika.Map.tileheight #tile underneath tabby
        b = x % ika.Map.tileheight #how far into the tile

        if tile in slopeTiles[Dir.RIGHT]:  # \
            if reposition:
                if self.vx > 0 and self.vy == 0:
                    self.y = a + b - self.sprite.hotheight - ika.Map.tileheight + self.vx
                else:
                    self.y = a + b - self.sprite.hotheight - ika.Map.tileheight
            return True
        elif tile in slopeTiles[Dir.LEFT]:  # /
            if reposition:
                if self.vx < 0 and self.vy == 0:
                    self.y = a - b - self.sprite.hotheight + self.vy
                else:
                    self.y = a - b - self.sprite.hotheight - 1
            return True


        elif tile in halfSlopeTiles[(Dir.RIGHT, 'bottom')]:  # \
            if reposition:
                if self.vx > 0 and self.vy == 0:
                    self.y = a + (b / 2) - self.sprite.hotheight - ika.Map.tileheight + ika.Map.tileheight / 2
                else:
                    self.y = a + (b / 2) - self.sprite.hotheight - ika.Map.tileheight + ika.Map.tileheight / 2 - 1
            return True
        elif tile in halfSlopeTiles[(Dir.RIGHT, 'top')]:  # \
            if reposition:
                if self.vx > 0 and self.vy == 0:
                    self.y = a + (b / 2) - self.sprite.hotheight - ika.Map.tileheight + 1
                else:
                    self.y = a + (b / 2) - self.sprite.hotheight - ika.Map.tileheight
            return True

        elif tile in halfSlopeTiles[(Dir.LEFT, 'bottom')]:  # /
            if reposition:
                if self.vx < 0 and self.vy == 0:
                    self.y = a - (b / 2) - self.sprite.hotheight
                else:
                    self.y = a - (b / 2) - self.sprite.hotheight - 1
            return True
        elif tile in halfSlopeTiles[(Dir.LEFT, 'top')]:  # /
            if reposition:
                if self.vx < 0 and self.vy == 0:
                    self.y = a - (b / 2) - self.sprite.hotheight - ika.Map.tileheight / 2
                else:
                    self.y = a - (b / 2) - self.sprite.hotheight - ika.Map.tileheight / 2 - 1
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
        x2 = x+self.width
        y2 = y+self.height


        self.ceiling = self.check_h_line(x + 1, y - 1, x2 - 1)

        if self.cur_platform:
            self.floor = True
        #already on a platform, no need to check for floor
        else:
            self.floor = self.check_h_line(x + 1,y2, x2 - 1)

            if self.floor and not self.ceiling:
                # Find the tile that the entity will be standing on,
                # and set it to be standing exactly on it:
                tiley = int(y2 / ika.Map.tileheight)
                self.y = tiley * ika.Map.tileheight - self.height
                self.vy = 0


        if self.ceiling and self.vy != 0:
            tiley = int((y - 1) / ika.Map.tileheight)
            self.y = (tiley + 1) * ika.Map.tileheight
            self.vy = 0
        # Reset x / y, in case vy was modified.
        x = round(self.x + self.vx)
        y = round(self.y)
        x2 = x+self.width
        y2 = y+self.height

        self.left_wall = self.check_v_line(x, y + 1, y2 - 1)
        self.right_wall = self.check_v_line(x2, y + 1,
                                            y2 - 1)
        if self.left_wall and not self.phantom:
            tilex = int(x / ika.Map.tilewidth)
            self.x = (tilex + 1) * ika.Map.tilewidth - 1
            self.vx = max(0, self.vx)
        if self.right_wall and not self.phantom:
            tilex = int(x2 / ika.Map.tilewidth)
            self.x = tilex * ika.Map.tilewidth - self.width
            self.vx = min(0, self.vx)

        
        for ents in self.detect_collision():
            entity = ents[0]
            if entity is not None:
                if not entity.destroy and entity.touchable:
                    entity.touch(self)

        """
        on_platform=False
        for entity in self.detect_collision():

            if entity is not None:
                if not entity.destroy and entity.touchable:
                    entity.touch(self)


                if entity.sprite.isobs: #is an obstruction, so obstruct!


                    #if entity.y + entity.sprite.hotheight > self.y: #touching the bottom of the sprite
                    #    self.ceiling = True
                    #    self.y = entity.y + entity.sprite.hotheight
                    #    self.vy=0

                    #if entity.y < self.y + self.sprite.hotheight: #touching the top?
                    #    self.floor = True
                    #    self.y = entity.y - self.sprite.hotheight
                    #    self.vy=0



                    #if x + self.width > entity.x and

                    #(self.y + self.height > entity.y or self.y  entity.y + entity.height):
                    #    self.left_wall = True
                    #    self.x = entity.x - self.width
                    #    self.vx = 0




                    ymove = False
                    if y <= entity.y + entity.height and y2 > entity.y + entity.height:
                        self.ceiling = True # touching bottom  of the box
                        self.y = entity.y + entity.height
                        self.vy = 0
                        ymove = True
                    elif y2 >= entity.y and y < entity.y:
                        self.floor = True # touching top of the box
                        self.y = entity.y - self.height
                        self.vy = 0
                        ymove = True
                        if entity.platform:
                            on_platform=True


                    if not ymove:
                            #inside                          outside
                        if x <= entity.x + entity.width and x2 > entity.x + entity.width:
                            self.left_wall = True # touching RIGHT side of the box
                            self.x = entity.x + entity.width
                            self.vx = 0

                            #inside                  outside
                        elif x2 >= entity.x and x < entity.x: # and not (entity.x + entity.sprite.hotwidth > self.x):
                            self.right_wall = True #touching LEFT side of the box
                            self.x = entity.x - self.width
                            self.vx = 0

        if not on_platform:
            self.cur_platform=False
            self.pvx=0
            self.pvy=0

        """


    def RunnableZone(self):
        """Find if there's any activatable zones near the player."""
        for f in engine.fields:
            if f.test(self) and f.runnable:
                return f #just returns the first activatable found...

    def SetPlatform(self, platform):
        if platform is not None:
            self.cur_platform=platform
            self.pvy = platform.vy
            self.pvx = platform.vx
            self.platformcounter=2
        else:
            self.cur_platform=None
            self.pvy = 0
            self.pvx = 0
            self.vy=0




    def update(self):
        if self.msg:
            pass #do stuff :P
            #self.msg = ''

        #check current terrain to set appropriate terrain speeds, mostly just water for now.
        if self.cur_terrain:
            self.SetPhysics('water')
        else: #defaults to normal
            self.SetPhysics('normal') #for efficiency shouldn't run this every frame..

        if controls.weap_next.Pressed() or controls.weap_prev.Pressed():
            if self.curweapon=='Beam':
                self.curweapon='Bullet'
            else:
                self.curweapon='Beam'

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

        results = self.detect_collision() #entity collisions

        if self.cur_platform is None:
            for colliding in results: #returns tuple of (entity, top, bottom, left, right for sides being touched)
                e,top,bottom,left,right=colliding
                if e.platform:   # and top: #entity is a platform and touching the top
                    if e.y >= self.y:
                        self.SetPlatform(e)
                    elif e.y+e.h <= self.y:
                        self.ceiling=True
                        self.state=self.FallState #hack
                    #only one platform at a time right now, first in the list...
                    #needs logic for not cliping through the bottom
        elif self.cur_platform: #currently standing on a platform
            still_touching=False
            for colliding in results: #returns tuple of (entity, top, bottom, left, right for sides being touched)
                e,top,bottom,left,right=colliding
                if e==self.cur_platform: #still touching the platform!
                    still_touching=True
                    break

            if not still_touching:
                #not touching a platform anymore
                self.pvx=0
                self.pvy=0
                self.cur_platform=None
            else:
                self.pvy = self.cur_platform.vy
                self.pvx = self.cur_platform.vx

		#duplicate code... must refactor later...
        for colliding in results: #returns tuple of (entity, top, bottom, left, right for sides being touched)
            e,top,bottom,left,right=colliding
            if bottom: #touching bottom of an entity...
            	self.ceiling=True
            	#self.vy=0 #was causing getting stuck in the platform...

        self.vx = vecmath.clamp(self.vx, -self.max_vx, self.max_vx)
        self.vy = vecmath.clamp(self.vy, -self.max_vy, self.max_vy)

        if self.cur_platform and self.jumpticks==0:
            #if self.state__ is not self.JumpState:

                self.y=int(self.cur_platform.y-46) #haaaack


        else:
            self.y += self.vy

        if self.jumpticks>0: self.jumpticks-=1

        self.x += self.vx + self.pvx

        self.sprite.x = int(self.x)
        self.sprite.y = int(self.y)
        self.state__()
        self.animation()

    def check_rectangles(self,x1,y1,x2,y2,x3,y3,x4,y4): #top left, bottom right -> top left, bottom right
        return (y2 > y3 and y1 < y4 and x2 > x3 and x1 < x4)

    def detect_collision(self): #entity collisions, Tabby specific
        result = []

        y=self.y + self.vy #+self.pvy
        x=self.x + self.vx #+self.pvx

        for entity in engine.entities:
        	if entity is not self and entity.sprite: #don't check itself and only if it has a sprite
				top = bottom = left = right = False
				etop = entity.y
				ebottom = entity.y + entity.sprite.hotheight
				eleft = entity.x
				eright = entity.x + entity.sprite.hotwidth

				if self.check_rectangles(eleft, etop, eright, ebottom, self.x, self.y, self.x+self.sprite.hotwidth, self.y+self.sprite.hotheight + 1): #within bounding box. Check if it's the top, bottom, left, or right side being collided with.

					#ebottom > y and etop < y + self.sprite.hotheight and \
					#eright > x and eleft < x + self.sprite.hotwidth: #within bounding box. Check if it's the top, bottom, left, or right side being collided with.

					   #need to refactor again to look at bounding rectangles
					   if ebottom > y and ebottom < y + (self.sprite.hotheight/2): top = True #entity touching top side

					   #top = self.check_rectangles()



					   if etop < y + self.sprite.hotheight and top > y + (self.sprite.hotheight/2): bottom = True
					   if eright > x and eright < x + (self.sprite.hotwidth/2): left = True
					   if eleft < x + self.sprite.hotwidth and eleft < x + (self.sprite.hotwidth/2): right = True

					   result.append((entity, top, bottom, left, right))
        return result

        """
        y=self.y+self.vy+self.pvy
        x=self.x+self.vx+self.pvx

        for entity in engine.entities:
            if entity is not self and entity.sprite and \
               entity.y + entity.sprite.hotheight > y and \
               entity.y < y + self.sprite.hotheight and \
               entity.x + entity.sprite.hotwidth > x and \
               entity.x < x + self.sprite.hotwidth:
                   result.append(entity)
        return result
        """




