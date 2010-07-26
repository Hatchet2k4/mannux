import ika
import vecmath
import controls
import parser
from entity import Entity
from sprite import Sprite
from engine import processor, engine
from bomb import Bomb

from item import Container, beams

from const import Dir
import riptiles
import rotateblit
import math
import fonts
import sprite
import weapons



slopeTiles = {Dir.LEFT:  [5, 7],  # /
              Dir.RIGHT: [4, 6]}  # \


firesound = ika.Sound('sfx/shoot1.wav')
firesound.volume = 0.5

def GetHeight(self):
    if self.cur_state == self.MorphState:
        return 15
    else:
        return self.hotspot[3]


def DrawQuad((x1, y1, c1), (x2, y2, c2), (x3, y3, c3), (x4, y4, c4)):
    ika.Video.DrawTriangle((x1, y1, c1), (x2, y2, c2), (x3, y3, c3))
    ika.Video.DrawTriangle((x4, y4, c4), (x2, y2, c2), (x3, y3, c3))

#def GetOverlayFrame(direction, facing):
#setsuit not getting called when you load a game



class Samus(Entity):
    def __init__(self, x=0, y=0):
        Entity.__init__(self, x, y, Sprite("null"), (12, 16, 16, 32))

        self.suit_sprite  = Sprite("null")
        self.morph_sprite = Sprite("null")

        self.localanim = ""

        # Weapon selection variables.
        self.cur_type = 0#0 = beam, 1 = missile
        # True if secondary weapon is armed.
        self.sec_armed = False
        # Missile selection.
        self.cur_missile = 0#0 = Missile, 1 = Super Missile
        # Beam selection.
        self.cur_beam = 0#0 = Power, 1 = Ice, 2 = Pulse, 3 = Grapple
        # If missile_hold was held.
        self.missile_held = False

        # Metroids killed.
        self.metroids_killed = 0
        # Equipment.
        self.equipment = Container()

        # Constants.
        self.ticks = 20

        self.ground_friction = 0.10
        self.air_friction = 0.10
        self.morph_friction = 0.075
        self.morph_airfriction = 0.05

        self.ground_accel = self.ground_friction + 0.05
        self.morph_accel = self.ground_friction / 2.0
        self.air_accel = 0.125

        self.max_vx = 1.50
        self.max_vy = 3.0
        self.max_morph_vx = 2.0
        self.max_morph_vy = 3.0

        self.gravity = 0.1
        self.jump_speed = 3.0
        self.hijump_speed = 3.5
        self.bombjump_speed = 3.125
        self.hijump_ticks = 18
        self.normjump_ticks = 10


        self.fire_delay = 0
        self.firing_rate = 8
        self.direction = Dir.LEFT

        #morphball frames:
        #self.morph_base = None
        #self.morph_overlay = None

        self.overlay = -1
        self.overlay_offy = 0
        self.overlay_offx = 0
        self.runbob = [1, 0, 0, 1, 1, 1, 0, 0, 0, 0] #y offsets for the overlay when running


        self.hurt_count = 0
        self.hurtable = True


        # Only used if double-jumping ability enabled.
        self.max_jumps = 3
        self.jump_count = 0



        self.state = self.StandState #change later to something better
        self.msg = ''

        self.in_slope = False
        self.cur_terrain = None
        self.checkslopes = True
        self.was_in_slope = False
        self.lastpos = (0, 0)

        self.bombjumping = False
        self.phantom = False
        self.fired = False
        self.spinjump = False
        self.walljump = False
        self.aim = -1


        #morphstate variables
        self.morph_angle = 0
        self.morph_boost = 0
        self.boosting = False
        self.boostticks = 0
        self.morph_trail = []
        self.max_trail_len = 13
        self.morph_states = (self.MorphState, self.BoostState)
        self.stand_straight = False

        #self.aimframes = {
        #"Stand": [   ]
        #}

        self.platform = None
        self.pressed =  ()
        self.pos = ()


    def __GetEnergy(self):
        return self.equipment["E-Tank"].cur

    def __SetEnergy(self, value):
        self.equipment["E-Tank"].cur = value

    height = property(GetHeight)
    energy = property(__GetEnergy, __SetEnergy)
    max_energy = property(lambda self: self.equipment["E-Tank"].max)

    def SetSuit(self):
        """Sets her current suit graphic."""
        if self.equipment.Enabled("Aero Suit"):
            pass
            #self.sprite = Sprite("samus-aero")
            self.morph_sprite = Sprite("morphball-aero")

        elif self.equipment.Enabled("Gravity Suit"):
            self.suit_sprite  = Sprite("samus-gravity")
            self.morph_sprite = Sprite("morphball-gravity")

        elif self.equipment.Enabled("Varia Suit"):
            self.suit_sprite  = Sprite("samus-varia")
            self.morph_sprite = Sprite("morphball-varia")

        else:
            self.suit_sprite  = Sprite("samus-power")
            self.morph_sprite = Sprite("morphball-power")

        #hack so the camera centers
        if self.morph_sprite != None:
            self.morph_sprite.width  = 40
            self.morph_sprite.height = 48


    def HasAbility(self, name):
        if name in self.abilities:
            return self.abilities[name]
        return False

    def Animate(self, strand, delay=10, loop=True, reset=True, reverse=False):

        self.localanim = ""

        #apply action and direction to the state call
        for i in range(len(strand) - 1):
            self.localanim = self.localanim + strand[i] + "_"
        if len(strand) > 1 and strand[len(strand) - 1] == 0:
            self.localanim = self.localanim + "left"
        else:
            self.localanim = self.localanim + "right"


        self.sprite.SetState("overlay_" + str(self.overlay))
        self.sprite.SetState(self.localanim)

    def Draw(self):
        x = self.x - ika.Map.xwin - self.hotspot[0] + self.overlay_offx
        y = self.y - ika.Map.ywin - self.hotspot[1] + self.overlay_offy

        if self.cur_state in self.morph_states:
            if self.sprite.angle == 0:
                y+=33
                x+=12
            else:
                y+=16
                x+=0
            self.DrawTrail()
            self.sprite = self.morph_sprite
            self.sprite.angle = self.morph_angle
        else:
            self.sprite = self.suit_sprite
            self.sprite.angle = 0

        self.sprite.Draw(x, y)


        #print >> fonts.bold(160, 20), self.localanim
        #print >> fonts.bold(160, 40), self.overlay
        #print >> fonts.bold(160, 60), self.aim


            #self.morph_base.Draw(x, y)
            #self.morph_overlay.Draw(x + 9, y + 9, angle=self.morph_angle)
            #ika.Video.Blit(self.morph_frames[0], int(self.x-ika.Map.xwin), int(self.y-ika.Map.ywin))
            #rotateblit.RotateBlit(self.morph_frames[3], int(self.x-ika.Map.xwin+8),
            #                        int(self.y+8-ika.Map.ywin), self.morph_angle)
            #if self.morph_boost > 0:
            #    ika.Video.DrawEllipse(x+9, y+9, 8, 8, ika.RGB(255, 160, 160, self.morph_boost), True)
                #self.sprite.color = ika.RGB(255, 200, 200, self.morph_boost)

        #elif self.overlay >= 0:
        #    x = self.x - ika.Map.xwin - self.hotspot[0] + self.overlay_offx
        #    y = self.y - ika.Map.ywin - self.hotspot[1] + self.overlay_offy
        #    ika.Video.Blit(self.overlays[self.overlay], int(x), int(y) - 1)

        #if self.cur_state in self.morph_states:
        #    y+=16
        #    self.DrawTrail()
        #
        #    self.morph_base.Draw(x, y)
        #    self.morph_overlay.Draw(x + 9, y + 9, angle=self.morph_angle)
        #    #ika.Video.Blit(self.morph_frames[0], int(self.x-ika.Map.xwin), int(self.y-ika.Map.ywin))
        #    #rotateblit.RotateBlit(self.morph_frames[3], int(self.x-ika.Map.xwin+8),
        #    #                        int(self.y+8-ika.Map.ywin), self.morph_angle)
        #    if self.morph_boost > 0:
        #        ika.Video.DrawEllipse(x+8, y+8, 8, 8, ika.RGB(255, 200, 200, self.morph_boost), True)
        #elif self.overlay >= 0:
        #    x = self.x - ika.Map.xwin - self.hotspot[0] + self.overlay_offx
        #    y = self.y - ika.Map.ywin - self.hotspot[1] + self.overlay_offy
        #    ika.Video.Blit(self.overlays[self.overlay], int(x), int(y) - 1)


    def DrawTrail(self):

        #there's gotta be a way to do this without repeating code... but whatever, it works..
        if len(self.morph_trail) > 2:
            prevx = self.morph_trail[0][0]
            prevy = self.morph_trail[0][1]
            x = self.morph_trail[1][0]
            y = self.morph_trail[1][1]

            dx = x - prevx
            dy = y - prevy
            angle = math.atan2(dy, dx) + math.pi/2

            prevx1 = int(prevx + math.cos(angle)*8) - ika.Map.xwin
            prevy1 = int(prevy + math.sin(angle)*8) - ika.Map.ywin
            prevx2 = int(prevx + math.cos(angle-math.pi)*8) - ika.Map.xwin
            prevy2 = int(prevy + math.sin(angle-math.pi)*8) - ika.Map.ywin
            prevc = ika.RGB(0, 0, 0, 0)


            #skip the first coord, make sure the one under the morphball is always drawn
            for i, coord in enumerate(self.morph_trail[1:]+[(self.x+8, self.y+24)]):

                x = coord[0]
                y = coord[1]

                if x == prevx and y == prevy:
                    continue

                #calculate the angle the ball was travelling in... and rotate it 90 degrees
                dx = x - prevx
                dy = y - prevy
                angle = math.atan2(dy, dx) + math.pi/2

                x1 = int(x + math.cos(angle)*8) - ika.Map.xwin
                y1 = int(y + math.sin(angle)*8) - ika.Map.ywin
                x2 = int(x + math.cos(angle-math.pi)*8) - ika.Map.xwin
                y2 = int(y + math.sin(angle-math.pi)*8) - ika.Map.ywin

                alpha = int(200*(i*1.0/self.max_trail_len))
                if abs(self.vx) > self.max_morph_vx:
                    d = (abs(self.vx)-2)*50
                    c = ika.RGB(255, 215-int(min(200,d)), 0, alpha)
                    #still need to adjust for other morph ball colors
                else:
                    if self.equipment.Enabled("Aero Suit"):
                        c = ika.RGB(90, 255, 165, alpha)

                    elif self.equipment.Enabled("Gravity Suit"):
                        c = ika.RGB(97, 212, 255, alpha)

                    elif self.equipment.Enabled("Varia Suit"):
                        c = ika.RGB(255, 212, 97, alpha) #varia trail

                    else:
                        c = ika.RGB(223, 215, 0, alpha) #power trail

                DrawQuad((prevx1, prevy1, prevc), (prevx2, prevy2, prevc),(x1, y1, c),(x2, y2, c))

                prevx = x
                prevy = y
                prevx1 = x1
                prevy1 = y1
                prevx2 = x2
                prevy2 = y2
                prevc = c


############################### STATES ######################################

    def BoostState(self):
        pass

    def MorphState(self):
        self.Animate( ('blank',), loop=False)

        self.morph_trail = []

        X = math.pi*2 #I know this value is way too big, but it seems to fit for some reason...
        self.boosting = False
        self.boostticks = 0
        #self.CheckBallObstructions()
        #self.CheckObstructions()

        self.checkslopes = True

        while True:
            self.ticks += 1
            #self.morph_base.Update()
            #self.morph_overlay.Update()

            if self.boosting:
                max_morph_vx = 8.0 #boost speed!
                max_morph_vy = 8.0
                morph_friction = self.morph_friction
                morph_accel = 0.0
                air_accel = 0.0
                morph_airfriction = self.morph_airfriction * 6
                if abs(self.vx) <= 2.0: #need to fucking find a better way around this for falling vertically... vector perhaps?
                    self.boosting = False
                #self.boostticks -= 1
                #if self.boostticks == 0:
                #    self.boosting = False
            else:
                max_morph_vx = self.max_morph_vx #standard max speed
                max_morph_vy = self.max_morph_vy
                morph_friction = self.morph_friction
                morph_accel = self.morph_accel
                air_accel = self.air_accel
                morph_airfriction = self.morph_airfriction



            #just bomb jumped, and falling again, so check for slopes again.
            if self.bombjumping == True and self.vy >=0:
                self.checkslopes = True
                self.bombjumping = False

            if self.ticks % 2 == 0: #cheap hack to make the trail longer without so many samples
                self.morph_trail.append( (self.x+9, self.y+25) ) #center of morphball
                if len(self.morph_trail) > self.max_trail_len:
                    self.morph_trail = self.morph_trail[1:] #keep list at most len items long

            if "up" in self.pressed and not self.ceiling and not self.boosting:
                #gonna need to edit this mad style, to check for a cieling within 16 pixels.
                #also check for floor and set to fall state if appropriate
                self.state = self.CrouchState
                self.morph_trail = []
                #self.y-=16

            if self.floor:
                self.vy = 0
                if "left" in self.pos and not self.left_wall:
                    if abs(self.vx) < max_morph_vx:
                        self.vx-=morph_accel
                        if self.vx < -max_morph_vx:
                            self.vx = -max_morph_vx
                    self.direction = Dir.LEFT
                    if self.vx > 0 or abs(self.vx) > self.max_morph_vx:
                        self.vx = vecmath.decrease_magnitude(self.vx, morph_friction)
                elif "right" in self.pos and not self.right_wall:
                    if abs(self.vx) < max_morph_vx:
                        self.vx+=morph_accel
                        if self.vx > max_morph_vx:
                            self.vx = max_morph_vx
                    self.direction = Dir.RIGHT
                    if self.vx < 0 or abs(self.vx) > self.max_morph_vx:
                        self.vx = vecmath.decrease_magnitude(self.vx, morph_friction)
                else:
                    self.vx = vecmath.decrease_magnitude(self.vx, morph_friction)
            else:
                self.vy += self.gravity
                if self.vy > max_morph_vy:
                    self.vy = max_morph_vy

                if "left" in self.pos and not self.left_wall:
                    self.vx -= air_accel
                    if self.vx < -max_morph_vx:
                        self.vx = -max_morph_vx
                    self.direction = Dir.LEFT
                elif "right" in self.pos and not self.right_wall:
                    self.vx += air_accel
                    if self.vx > max_morph_vx:
                        self.vx = max_morph_vx
                    self.direction = Dir.RIGHT
                else:
                    self.vx = vecmath.decrease_magnitude(self.vx, morph_airfriction)

            if "boost" in self.pos:
                if self.morph_boost < 100:
                    self.morph_boost += 2
            elif self.morph_boost > 32:
                #boost! terribly hacky
                self.boosting = True

                self.vx = self.vx * (2.5*self.morph_boost/100.0)
                self.vy = self.vy * (1.5*self.morph_boost/100.0)
                self.morph_boost = 0
                #self.boostticks = 20
                max_morph_vx = max_morph_vy = 8.0


            self.vx = vecmath.clamp(self.vx, -max_morph_vx, max_morph_vx)
            self.vy = vecmath.clamp(self.vy, -max_morph_vy, max_morph_vy)
            self.morph_angle = (self.morph_angle + self.vx * X)

            yield None

    def CrouchState(self):
        self.overlay = -1
        self.vx = 0
        self.Animate(('crouch', self.direction), delay=1, loop=False)

        t = 0
        self.checkslopes = True

        while True:
            if self.sprite.anim_done:
                self.Animate(('crouch', self.direction), delay=1, loop=False)


            if not self.floor:
                self.state = self.FallState
                yield None

            if "jump" in self.pressed and not self.ceiling:
                self.state = self.JumpState
                yield None

            if "up" in self.pressed:
                self.state = self.StandState
                yield None

            if "down" in self.pressed:
                #self.Animate(('morph', self.direction), delay=5, reset = True, loop=False)
                #while not self.sprite.anim_done:
                #    yield None

                self.state = self.MorphState
                yield None

            if "left" in self.pos and not self.left_wall:
                t+=1
                if self.direction != Dir.LEFT:
                    self.direction = Dir.LEFT
                    self.Animate(('crouch', 'turn'), delay=3, loop=False,
                                 reverse=True)
                else:
                    if t==5:
                        self.state = self.WalkState


            elif "right" in self.pos and not self.right_wall:
                t+=1
                if self.direction != Dir.RIGHT:
                    self.direction = Dir.RIGHT
                    self.Animate(('crouch', 'turn'), delay=3, loop=False)
                else:
                    if t==5:
                        self.state = self.WalkState
            else:
                t=0 #no longer pressing a key

            yield None

    def StandState(self):
        #self.Animate(('stand', self.direction), delay=5, loop=True)
        self.vx=0
        self.overlay = -1
        self.checkslopes = True

        while True:
            if not self.floor:
                self.state = self.FallState
                yield None

            if "jump" in self.pressed and not self.ceiling:
                if "left" in self.pos or "right" in self.pos:
                    self.spinjump = True
                self.state = self.JumpState
                self.checkslopes=False
                yield None

            if "up" in self.pos:
                if "left" in self.pos:
                    self.aim = Dir.UPLEFT
                elif "right" in self.pos:
                    self.aim = Dir.UPRIGHT
                else:
                    self.aim = Dir.UP
            elif "down" in self.pos:
                if "left" in self.pos:
                    self.aim = Dir.DOWNLEFT
                elif "right" in self.pos:
                    self.aim = Dir.DOWNRIGHT
            elif "aim_up" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.UPLEFT
                else:
                    self.aim = Dir.UPRIGHT
            elif "aim_down" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.DOWNLEFT
                else:
                    self.aim = Dir.DOWNRIGHT
            else:
                self.aim = self.direction

            if self.sprite.anim_done:
                if self.aim == Dir.UP:
                    self.Animate(('stand', 'aim_up', self.direction), delay=1, loop=False)
                elif self.aim == Dir.UPLEFT or self.aim == Dir.UPRIGHT:
                    self.Animate(('stand', 'aim_dup', self.direction), delay=1, loop=False)
                elif self.aim == Dir.DOWNLEFT or self.aim == Dir.DOWNRIGHT:
                    self.Animate(('stand', 'aim_ddown', self.direction), delay=1, loop=False)
                else:
                    if self.stand_straight:
                        self.sprite.SetState("stand")
                    else:
                        self.Animate(('stand', self.direction), delay=1, loop=False)

            if "down" in self.pressed:
                self.state = self.CrouchState
                yield None

            if "left" in self.pos and not self.left_wall:
                if self.direction == Dir.LEFT:
                    #self.Animate(('stand', 'run', self.direction), delay=5,
                    #             loop=False)
                    pass
                    self.state = self.WalkState
                else:
                    self.direction = Dir.LEFT
                    self.Animate(('stand', 'turn'), delay=5, loop=False,
                                 reverse=True)

            elif "right" in self.pos and not self.right_wall:
                if self.direction == Dir.RIGHT:
                    #self.Animate(('stand', 'run', self.direction), delay=5,
                    #             loop=False)
                    pass
                    self.state = self.WalkState
                else:
                    self.direction = Dir.RIGHT
                    self.Animate(('stand', 'turn'), delay=5, loop=False)
            yield None

    def WalkState(self):
        fired = False
        self.checkslopes = True

        while True:
            #self.Animate(('run', self.direction), delay=4, reset=False)

            if "up" in self.pos or "l" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.UPLEFT
                else:
                    self.aim = Dir.UPRIGHT
            elif "down" in self.pos or "r" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.DOWNLEFT
                else:
                    self.aim = Dir.DOWNRIGHT
            else:
                if fired:
                    self.aim = self.direction
                else:
                    self.aim = Dir.NONE


            if self.aim == Dir.UPLEFT or self.aim == Dir.UPRIGHT:
                self.Animate(('run', 'overlay', self.direction), delay=4, reset=False)
                if self.direction == Dir.LEFT: self.overlay = 0
                else: self.overlay = 6
            elif self.aim == Dir.DOWNLEFT or self.aim == Dir.DOWNRIGHT:
                self.Animate(('run', 'overlay', self.direction), delay=4, reset=False)
                if self.direction == Dir.LEFT: self.overlay = 2
                else: self.overlay = 8
            elif self.aim == Dir.LEFT or self.aim == Dir.RIGHT:
                self.Animate(('run', 'aim', self.direction), delay=4, reset=False)
                self.overlay = -1
            else:
                self.Animate(('run', self.direction), delay=4, reset=False)
                self.overlay = -1



            if "fire" in self.pressed:
                fired=True

            #jump
            #May have to do a better cieling check
            if "jump" in self.pressed and self.floor and not self.ceiling:
                self.state = self.JumpState
                self.spinjump = True
                self.checkslopes=False
                yield None

            if "left" in self.pos:
                if self.direction != Dir.LEFT:
                    self.direction = Dir.LEFT
                    self.vx = 0
                if not self.left_wall:
                    self.vx -= self.ground_accel
                else:
                    self.sprite.anim_done = True
                    self.state = self.StandState
            elif "right" in self.pos:
                if self.direction != Dir.RIGHT:
                    self.direction = Dir.RIGHT
                    self.vx = 0
                if not self.right_wall:
                    self.vx += self.ground_accel
                else:
                    self.sprite.anim_done = True
                    self.state = self.StandState
            else:
                self.sprite.anim_done = True
                self.state = self.StandState

            if not self.floor:
                self.state = self.FallState

            yield None


    def JumpState(self):

        self.overlay = -1
        self.checkslopes = False
        if self.equipment.Enabled("Hi-Jump Boots"):
            jumpticks = self.hijump_ticks
            self.vy = -self.hijump_speed
        else:
            jumpticks = self.normjump_ticks
            self.vy = -self.jump_speed


        if self.spinjump:
            if self.walljump:
                self.Animate(('jump', 'wall', self.direction), delay=2, reset=True, loop=False)
            else:
                self.Animate(('jump', 'spinstart', self.direction), delay=4, loop=False)
        else:
            self.Animate(('jump', 'rise', self.direction), delay=8, loop=False)

        self.walljump = False
        turning = False
        while "jump" in self.pos and not self.ceiling:
            old_direction = self.direction
            if "left" in self.pos and not self.left_wall:
                self.vx -= self.air_accel
                self.direction = Dir.LEFT
            elif "right" in self.pos and not self.right_wall:
                self.vx += self.air_accel
                self.direction = Dir.RIGHT

            if "up" in self.pos:
                if "left" in self.pos:
                    self.aim = Dir.UPLEFT
                elif "right" in self.pos:
                    self.aim = Dir.UPRIGHT
                else:
                    self.aim = Dir.UP
            elif "down" in self.pos:
                if "left" in self.pos:
                    self.aim = Dir.DOWNLEFT
                elif "right" in self.pos:
                    self.aim = Dir.DOWNRIGHT
            elif "aim_up" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.UPLEFT
                else:
                    self.aim = Dir.UPRIGHT
            elif "aim_down" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.DOWNLEFT
                else:
                    self.aim = Dir.DOWNRIGHT
            else:
                self.aim = self.direction


            if "fire" in self.pressed:
                self.spinjump = False
                self.sprite.anim_done = True

            if old_direction != self.direction:
                # If the direction changed, update the animation
                if self.spinjump:
                    self.Animate(('jump', 'spin', self.direction), delay=3)
                else:
                    self.Animate(('jump', 'turn', self.direction), delay=3, loop=False)
                    self.overlay=-1
                    turning = True

            if self.sprite.anim_done:
                turning = False
                if self.spinjump:
                    self.Animate(('jump', 'spin', self.direction), delay=3, reset=False)
                else:
                    self.Animate(('jump', self.direction), loop=False)
                    self.overlay = 12+4*self.direction

            if not self.spinjump and not turning:
                if self.aim == Dir.UPLEFT:
                    self.overlay = 11
                elif self.aim == Dir.UPRIGHT:
                    self.overlay = 15
                elif self.aim == Dir.DOWNLEFT:
                    self.overlay = 13
                elif self.aim == Dir.DOWNRIGHT:
                    self.overlay = 17
                elif self.aim == Dir.UP:
                    self.overlay = 10 + 4*self.direction
                elif self.aim == Dir.DOWN:
                    self.overlay = -1
                    #self.Animate(
                else:
                    self.overlay = 12+4*self.direction

            if (self.left_wall and self.vx < 0) or \
               (self.right_wall and self.vx > 0):
                self.vx = 0

            if self.ceiling:
                self.vy = 0
                self.y += 1

            if jumpticks > 0:
                jumpticks -= 1 #gravity defying high jump!
            else:
                self.vy += self.gravity


            if self.vy >= 0:
                break

            yield None

        #starting to fall
        if self.vy < -1:
            self.vy = -1

        self.state = self.FallState
        yield None

    def FallState(self):
        if not self.spinjump:
            self.Animate(('jump', 'fall', self.direction), delay=8, loop=False)
            self.overlay = 12+4*self.direction
        else:
            self.overlay = -1
        self.walljump = False
        self.checkslopes = True
        turning = False

        while True:

            if self.sprite.anim_done:
                turning = False
                if self.spinjump:
                    self.Animate(('jump', 'spin', self.direction), delay=3, reset=False)
                else:
                    self.Animate(('fall', self.direction), loop=False)
                    self.overlay = 12+4*self.direction

            if "up" in self.pos:
                if "left" in self.pos:
                    self.aim = Dir.UPLEFT
                elif "right" in self.pos:
                    self.aim = Dir.UPRIGHT
                else:
                    self.aim = Dir.UP
            elif "down" in self.pos:
                if "left" in self.pos:
                    self.aim = Dir.DOWNLEFT
                elif "right" in self.pos:
                    self.aim = Dir.DOWNRIGHT
            elif "aim_left" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.UPLEFT
                else:
                    self.aim = Dir.UPRIGHT
            elif "aim_right" in self.pos:
                if self.direction == Dir.LEFT:
                    self.aim = Dir.DOWNLEFT
                else:
                    self.aim = Dir.DOWNRIGHT
            else:
                self.aim = self.direction


            if "fire" in self.pressed:
                self.spinjump = False
                self.sprite.anim_done = True

            if not self.spinjump and not turning:
                if self.aim == Dir.UPLEFT:
                    self.overlay = 11
                elif self.aim == Dir.UPRIGHT:
                    self.overlay = 15
                elif self.aim == Dir.DOWNLEFT:
                    self.overlay = 13
                elif self.aim == Dir.DOWNRIGHT:
                    self.overlay = 17
                elif self.aim == Dir.UP:
                    self.overlay = 10 + 4*self.direction
                elif self.aim == Dir.DOWN:
                    self.overlay = -1
                    #self.Animate(
                else:
                    self.overlay = 12+4*self.direction

            if self.floor:
                self.vy = 0
                self.spinjump = False
                self.overlay = -1
                if "left" in self.pos or "right" in self.pos:
                    self.state = self.WalkState
                    self.Animate(('run', self.direction), delay=4, reset=True)

                else:
                    self.state = self.StandState
                    self.Animate(('land', 'stand', self.direction), delay=6, loop=False)
                yield None


            if self.ceiling:
                if self.vy < 0:
                    self.y -= self.vy
                self.vy = 0
            self.vy += self.gravity

            if self.walljump:
                self.Animate(('jump', 'wall', self.direction), delay=2, reset=True, loop=False)
                self.overlay = -1



            elif "jump" in self.pressed:
                self.spinjump = True
                self.Animate(('jump', 'spin', self.direction), delay=3, reset=False)
                self.overlay = -1

            old_direction = self.direction
            if "left" in self.pos and not self.left_wall:
                self.vx -= self.air_accel
                self.direction = Dir.LEFT
            elif "right" in self.pos and not self.right_wall:
                self.vx += self.air_accel
                self.direction = Dir.RIGHT
            elif "left" not in self.pos and "right" not in self.pos and not self.spinjump:
                self.vx = 0
            if old_direction != self.direction:
                if self.spinjump:
                    self.Animate(('jump', 'spin', self.direction), delay=3)
                else:
                    #self.Animate(('fall', self.direction), loop=False)
                    #self.overlay = 12+4*self.direction
                    self.Animate(('jump', 'turn', self.direction), delay=3, loop=False)
                    self.overlay = -1
                    turning = True
            yield None

            if self.spinjump:
                if self.check_v_line(self.x + self.vx + self.width + 5,
                                     self.y + 1, self.y + self.height - 1) and "left" in self.pos \
                                     and not self.left_wall:
                    self.Animate(('jump', 'wall', self.direction), delay=1, reset=True, loop=False)


                    if "jump" in self.pressed:
                        self.vx = -0.25
                        self.x-=1
                        self.direction = Dir.LEFT
                        self.walljump = True
                        break
                if self.check_v_line(self.x + self.vx - 4, self.y + 1,
                                     self.y + self.height - 1) and "right" in self.pos \
                                     and not self.right_wall:
                   self.Animate(('jump', 'wall', self.direction), delay=2, reset=True, loop=False)
                   if "jump" in self.pressed:
                        self.vx = 0.25
                        self.y+=1
                        self.direction = Dir.RIGHT
                        self.walljump = True
                        break

        if self.walljump:
            self.state = self.JumpState


        #self.overlay = -1
        yield None

############################# END STATES ####################################

    def BombJump(self, bx):
        if self.cur_state in self.morph_states and not self.ceiling:
            self.vy = -self.bombjump_speed
            self.bombjumping=True
            self.checkslopes=False
            x = self.x+self.width/2

            if abs(bx-x) > 4:
                if x > bx:
                    self.vx = 1.5
                else:
                    self.vx = -1.5


    """Weapon firing functions."""
    def FireBeam(self, direction, offx=0, offy=0):
        if not self.fire_delay:
            offx = -10 + 28 * self.direction
            bullet_x = self.x + offx
            bullet_y = self.y + 1
            engine.AddEntity(weapons.PowerBeam(bullet_x, bullet_y, direction)) #need to take into account current beam
            self.fire_delay = self.firing_rate
            firesound.Play()

    def FireMissile(self, direction):
        if not self.fire_delay:
            offx = -10 + 28 * self.direction
            bullet_x = self.x + offx
            bullet_y = self.y + 1
            engine.AddEntity(weapons.Missle(bullet_x, bullet_y, direction))
            self.fire_delay = self.firing_rate
            firesound.Play()

    def FireSuperMissile(self, direction):
        pass

    def PlaceBomb(self):
        engine.AddEntity(Bomb(int(self.x-1), int(self.y+12)))

    def PlacePowerBomb(self):
        pass



    def Hurt(self, damage):
        if self.hurtable:
            self.dhp -= damage
            # Going to die anyway, bwahaha. :D
            if self.hp + self.dhp <= 0:
                self.hp = 0
                engine.GameOver()
            self.state = self.HurtState

    def CheckSlopeTile(self, x, y, reposition=True):
        yoffset = 0
        if self.cur_state in self.morph_states:
            yoffset = 17

        for dy in [-1, 0, 1]:
            tx = x / ika.Map.tilewidth
            ty = (y + dy) / ika.Map.tileheight

            tiles = [ika.Map.GetTile(tx, ty, layer) for layer in range(ika.Map.layercount)]



            a = (ty + 1) * ika.Map.tileheight

            b = x % ika.Map.tilewidth #relative x/y locations inside the tile
            c = (y + dy) % ika.Map.tileheight

            for tile in tiles:
                if tile in slopeTiles[Dir.RIGHT]:  # \
                    if reposition:
                        if self.vx > 0 and self.vy == 0: #down the slope
                            self.y = a + b - self.height - ika.Map.tileheight - yoffset + 1
                        else:  #up the slope
                            self.y = a + b - self.height - ika.Map.tileheight - yoffset
                    return True
                elif tile in slopeTiles[Dir.LEFT]:  # /
                    if reposition:
                        if self.vx < 0 and self.vy == 0: #down the slope
                            self.y = a - b - self.height - yoffset
                        else: #up the slope
                            self.y = a - b - self.height - yoffset - 1
                    return True

        return False

    def CheckSlopes(self):
        if self.vy < 0:
            self.was_in_slope = False
            return False


        x = int(self.x + self.hotspot[2] / 2 + self.vx)
        y = int(self.y + self.hotspot[3])

        yoffset = 0
        if self.cur_state in self.morph_states:
            yoffset = 17 #compensate for the morphball's height difference

        self.in_slope = False
        reposition = True

        if self.vx == 0 and self.vy == 0:
            reposition = False
        if self.CheckSlopeTile(x, y, reposition):
            self.in_slope = True


        if self.was_in_slope and not self.in_slope:
            if self.CheckSlopeTile(x, y-16, reposition):
                self.in_slope = True
                y-=16
            if self.CheckSlopeTile(x, y + 17, reposition):
                self.in_slope = True
                y+=17

        if self.in_slope:
            self.floor=True
            self.left_wall=False
            self.right_wall=False
            #self.vx = vecmath.clamp(self.vx, -1.6, 1.6)
            self.vy = 0
            self.was_in_slope = True
            self.lastpos = (x / ika.Map.tilewidth, y / ika.Map.tileheight)
            return True


        self.was_in_slope = False
        return False

    def CheckObstructions(self):
        x = round(self.x)
        y = round(self.y + self.vy)
        yoffset = 0
        if self.cur_state in self.morph_states:
            y += 17
            yoffset = 17 #compensate for the morphball's height difference


        self.ceiling = self.check_h_line(x + 1, y - 1, x + self.width - 1)
        self.floor = self.check_h_line(x + 1, y + self.height, x + self.width - 1)
        if self.floor and not self.ceiling:
            # Find the tile that the entity will be standing on,
            # and set it to be standing exactly on it:
            tiley = int((y + self.height) / ika.Map.tileheight)
            self.y = tiley * ika.Map.tileheight - self.height - yoffset
            self.vy = 0
        if self.ceiling and self.vy != 0:
            tiley = int((y - 1) / ika.Map.tileheight)
            self.y = (tiley + 1) * ika.Map.tileheight - yoffset + 1
            self.vy = 0

        # Reset y, in case vy was modified.
        x = round(self.x + self.vx)
        y = round(self.y + yoffset)
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
                entity.Touch(self)

        if self.platform:
            self.floor = True

    def CheckWall(self, direction):
        x = round(self.x)
        y = round(self.y + self.vy)
        yoffset = 0

        if self.cur_state in self.morph_states:
            y += 17
            yoffset = 17 #compensate for the morphball's height difference


        if direction == Dir.UP:
            return self.check_h_line(x + 1, y - 1, x + self.width - 1)
        elif direction == Dir.DOWN:
            return self.check_h_line(x + 1, y + self.height, x + self.width - 1)
        elif direction == Dir.LEFT:
            return self.check_v_line(x, y + 1, y + self.height - 1)
        elif direction == Dir.RIGHT:
            return self.check_v_line(x + self.width, y + 1,
                                                y + self.height - 1)


    def RunnableZone(self):
        """Find if there's any activatable zones near the player."""
        for f in engine.fields:
            if f.test(self) and f.runnable:
                return f

    def Update(self):
        """Samus is too fragile to be updated here!"""
        pass

    def Input(self, position, pressed): #essentially Update() now.
        self.pos = position
        self.pressed = pressed

        if self.fire_delay > 0:
            self.fire_delay -= 1


        #Missile HOLD button.
        if "missile_hold" in position:
            self.missile_held = True
            if self.sec_armed == False:
                if self.cur_state in self.morph_states and self.equipment["Power Bombs"].cur > 0:
                    self.sec_armed = True
                elif self.cur_state not in self.morph_states and self.equipment[("Missiles", "Super Missiles")[self.cur_missile]].cur > 0:
                    self.sec_armed = True
        elif self.sec_armed and self.missile_held:
            self.sec_armed = False
            self.missile_held = False


        #Item stuff depending on missile_style.
        if controls.missile_style == 0:
            #Dual style.
            if "beam_select" in pressed:
                self.ChangeBeam()

            elif "weapon_select" in pressed:
                self.ChangeMissile()

            if "fire" in pressed:
                print "Fire main weapon"
                self.FireMain()

            elif "fire_missile" in pressed:
                self.sec_armed = True
                self.FireSecondary()

        else:
            #Swap style.
            if "beam_select" in pressed:
                if self.cur_type == 0:
                    #Change beam.
                    self.ChangeBeam()
                else:
                    self.ChangeMissile()

            elif "weapon_select" in pressed:
                #Change between beam and missile.
                self.cur_type = (self.cur_type + 1) % 2

            if "fire" in pressed:
                if self.cur_type == 0:
                    self.FireMain()
                else:
                    self.sec_armed = True
                    self.FireSecondary()

            elif "fire_missile" in pressed:
                if self.cur_type == 0:
                    self.sec_armed = True
                    self.FireSecondary()
                else:
                    self.FireMain()

        if self.checkslopes:
            if not self.CheckSlopes():
                self.CheckObstructions()
        else:
            self.CheckObstructions()



        if self.cur_state not in self.morph_states:
            self.vx = vecmath.clamp(self.vx, -self.max_vx, self.max_vx)
            self.vy = vecmath.clamp(self.vy, -100, self.max_vy) #-100 so WIP can sleep.

        #HACK for getting into morph ball tunnels. surprisingly, it works!
        #optimisation:
        #should only check for whether it'll pass through a tile position...
        tunnelled = False
        temp = -1
        if self.cur_state in self.morph_states:
            if self.right_wall and "right" in position:
                temp = self.y
                self.y = int(self.y)
                for y in range(3):
                    self.y += 1
                    if not self.CheckWall(Dir.RIGHT):
                        self.y+=1
                        if self.CheckWall(Dir.RIGHT): #ensure the passage is *just* big enough
                            self.x+=2
                            tunnelled = True
                        self.y -= 1
                        break
            elif self.left_wall and "left" in position:
                temp = self.y
                self.y = int(self.y)
                for i in range(3):
                    self.y += 1
                    if not self.CheckWall(Dir.LEFT):
                        self.y+=1
                        if self.CheckWall(Dir.LEFT): #ensure the passage is *just* big enough
                            self.x-=2
                            tunnelled = True
                        self.y-=1
                        break




        if not tunnelled:
            if temp != -1:
                self.y = temp
            self.x += self.vx
            self.y += self.vy

        if self.platform is not None:
            if self.platform in self.detect_collision():
                self.x += self.platform.vx
                self.y += self.platform.vy
            else:
                self.platform = None


        self.sprite.x = int(self.x)
        self.sprite.y = int(self.y)
        self.state__()
        self.animation()

        #if self.cur_state == self.WalkState: #do the bob thang. need to put it here so that cur_frame is correct
        #    self.overlay_offy = self.runbob[self.anim.cur_frame % 10]


    def FireMain(self):
        """Fires self's beam/bomb."""
        if self.cur_state in self.morph_states:
            print "Place bomb"
            self.PlaceBomb()
        else:
            if self.aim:
                dir = self.aim
            else:
                dir = self.direction
            self.FireBeam(dir)



    def FireSecondary(self):
        """Fires self's missiles or Power Bombs."""
        if self.cur_state in self.morph_states:
            #Check if she has enough Power Bombs.
            if self.equipment["Power Bombs"].cur > 0:
                self.PlacePowerBomb()
                return
        else:
            if self.aim:
                dir = self.aim
            else:
                dir = self.direction
            #Check if she has enough Missiles or Super Missiles.
            if self.cur_missile == 0:
                #Fire normal Missile.
                if self.equipment["Missiles"].cur > 0:
                    self.FireMissile(dir)
                    return
            else:
                #Fire Super Missile.
                if self.equipment["Super Missiles"].cur > 0:
                    self.FireSuperMissile(dir)
                    return

        #Play error sound here!

    def ChangeBeam(self):
        """Changes self's current beam weapon to the next available."""
        start_beam = self.cur_beam
        self.cur_beam = (self.cur_beam + 1) % 4
        while beams[self.cur_beam] not in self.equipment:
            self.cur_beam = (self.cur_beam + 1) % 4

        if self.cur_beam != start_beam:
            engine.hud.display_beam = True
            engine.hud.beam_ticks = 0

    def ChangeMissile(self):
        """Changes self's current missile type."""
        if self.equipment["Missiles"].max > 0:
            if self.equipment["Super Missiles"].max > 0:
                self.cur_missile = (self.cur_missile + 1) % 2



def sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    return 0

