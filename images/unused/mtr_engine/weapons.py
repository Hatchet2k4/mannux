import ika
import fonts
import math
from engine import engine
from entity import Entity
from enemy import Enemy
from blockbreak import Block
from sprite import Sprite
from const import Dir

class Projectile(Entity):
    def __init__(self, x, y, direction, sprite):
        Entity.__init__(self, x, y, sprite)
        self.ticks = 200    # ticks of life (like grains of sand in the hour glass)
        self.dying = False  # not yet!

        self.sprite.angle = 360 - Dir.ANGLE[direction]
        self.speed = 4     # speed of the shot
        self.vx = self.speed * math.cos(math.pi / 180 * self.sprite.angle)
        self.vy = self.speed * math.sin(math.pi / 180 * self.sprite.angle)
        self.damage = 0

        self.sprite.forcerotblit = True #x/y to be the center of the sprite

        #shift the hotspot to take into account x/y being the center of the sprite.
        self.hotspot = (-self.sprite.width/2, -self.sprite.height/2, self.sprite.width/2, self.sprite.height/2)

    def GetHitCoords(self):
        vy = self.vy
        vx = self.vx #saves typing :P

        tx = int((self.x + self.vx) / 16)
        ty = int((self.y + self.vy) / 16)

        if abs(vy) < 0.1 and vx > 0:
            return tx*16, self.y #hit the left side
        elif abs(vy) < 0.1 and vx < 0:
            return (tx+1)*16, self.y #hit the right side
        elif vy > 0 and abs(vx) < 0.1:
            return self.x, ty*16 #hit the top of the tile
        elif vy < 0 and abs(vx) < 0.1:
            return self.x, (ty+1)*16 #hit the bottom of the tile
        else:
            topleft =  tx*16, ty*16
            topright = (tx+1)*16, ty*16
            botleft =  tx*16, (ty+1)*16
            botright = (tx+1)*16, (ty+1)*16

            if vy > 0 and vx > 0: #downright. possible hits: top, left.
                line2 = ((self.x, self.y), (self.x+vx, self.y+vy))
                lines = [(topleft, topright), (topleft, botleft)]
                sides = [Dir.UP, Dir.LEFT]
            elif vy > 0 and vx < 0: #downleft. possible hits: top, right.
                line2 = ((self.x, self.y), (self.x+vx, self.y+vy))
                lines = [(topleft, topright), (topright, botright)]
                sides = [Dir.UP, Dir.RIGHT]
            elif vy < 0 and vx > 0: #upright. possible hits: bottom, left.
                line2 = ((self.x, self.y), (self.x+vx, self.y+vy))
                lines = [(botleft, botright), (topleft, botleft)]
                sides = [Dir.DOWN, Dir.LEFT]
            elif vy < 0 and vx < 0: #upleft. possible hits: bottom, right.
                line2 = ((self.x, self.y), (self.x+vx, self.y+vy))
                lines = [(botleft, botright), (topright, botright)]
                sides = [Dir.DOWN, Dir.RIGHT]

            intersects = [Intersect(line, line2) for line in lines]
            print intersects
            for i, intersect in enumerate(intersects):
                if intersect is not None:
                    x, y = intersect
                    #print "Intersected line "+str(i)+" "+str(line)
                    #print "Intersected at: "+str((x, y))
                    print "Chose: "+str(i) + " " + str(intersect)
                    return x, y


            return None

class PowerBeam(Projectile):
    def __init__(self, x, y, direction):
        Projectile.__init__(self, x, y, direction, Sprite("power_beam"))

        self.damage = 8

        #instant death check!
        tx = int(self.x / 16)
        ty = int(self.y / 16)
        b = ika.Map.GetObs(tx, ty, self.layer)
        if b > 0:
            self.DetectBlocks(tx, ty)
            self.Die(reposition=False)


    def Update(self):
        Entity.Update(self)
        self.ticks -= 1

        for ent in self.detect_collision():
            if ent is not None and ent is not engine.player:
                if ent.hurtable:
                    ent.Hurt(self.damage)
                    self._destroy()
                    return
                elif ent.isobs:
                    self._destroy()
                    return

        if not self.dying:
            # Check to see if the bullet hit a destructable block
            tx = int((self.x + self.vx) / 16)
            ty = int((self.y + self.vy) / 16)
            b = ika.Map.GetObs(tx, ty, self.layer)
            if b > 0:
                self.DetectBlocks(tx, ty)
                self.Die(reposition=True)

        if self.sprite.anim_done and self.dying:
            self._destroy()

        if self.ticks <= 0:
            self._destroy()

    def Die(self, reposition):
        self.dying = True
        self.sprite.SetState("dying")

        if reposition:
            blah = self.GetHitCoords()
            if blah is not None:
                self.x, self.y = blah

        self.layer+=1 #so the explosion is visible yo!
        self.vx = 0
        self.vy = 0

    def DetectBlocks(self, tx, ty):
        b = ika.Map.GetObs(tx, ty, self.layer)
        if b > 1: # breakable block!
            ika.Map.SetObs(tx, ty, self.layer, 0)
            ika.Map.SetTile(tx, ty, self.layer, 0)
            engine.AddEntity(Block(tx * 16, ty * 16, b))


class Missle(Projectile):
    def __init__(self, x, y, direction):
        Projectile.__init__(self, x, y, direction, Sprite("missile"))

        self.damage = 50

        #instant death check!
        tx = int(self.x / 16)
        ty = int(self.y / 16)
        b = ika.Map.GetObs(tx, ty, self.layer)
        if b > 0:
            self.DetectBlocks(tx, ty)
            self.Die(reposition=False)


    def Update(self):
        Entity.Update(self)
        self.ticks -= 1

        for ent in self.detect_collision():
            if ent is not None and ent is not engine.player:
                if ent.hurtable:
                    ent.Hurt(self.damage)
                    self._destroy()
                    return
                elif ent.isobs:
                    self._destroy()
                    return

        if not self.dying:
            # Check to see if the bullet hit a destructable block
            tx = int((self.x + self.vx) / 16)
            ty = int((self.y + self.vy) / 16)
            b = ika.Map.GetObs(tx, ty, self.layer)
            if b > 0:
                self.DetectBlocks(tx, ty)
                self.Die(reposition=True)

        if self.dying:
            self._destroy()


    def Draw(self):
        Entity.Draw(self)
        #ika.Video.SetPixel(self.x, self.y, ika.RGB(255, 0, 0))


    def Die(self, reposition):
        self.dying = True


        if reposition:
            blah = self.GetHitCoords()
            if blah is not None:
                self.x, self.y = blah


        e=Explosion(self.x-16, self.y-16)
        e.layer+=1 #so the explosion is visible yo!
        engine.AddEntity(e)
        self.vx = 0
        self.vy = 0

    def DetectBlocks(self, tx, ty):
        b = ika.Map.GetObs(tx, ty, self.layer)
        if b > 1: # breakable block!
            ika.Map.SetObs(tx, ty, self.layer, 0)
            ika.Map.SetTile(tx, ty, self.layer, 0)
            engine.AddEntity(Block(tx * 16, ty * 16, b))


class Explosion(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, Sprite("missilexplode"))
        self.sprite.forcerotblit = True

    def Update(self):
        Entity.Update(self)
        if self.sprite.anim_done:
            self._destroy()

def Intersect(line1, line2):
    ((Ax, Ay), (Bx, By)) = line1
    ((Cx, Cy), (Dx, Dy)) = line2
    Ax = float(Ax)
    Bx = float(Bx)
    Cx = float(Cx)
    Dx = float(Dx)
    Ay = float(Ay)
    By = float(By)
    Cy = float(Cy)
    Dy = float(Dy)

    try:
        r = ( (Ay-Cy)*(Dx-Cx)-(Ax-Cx)*(Dy-Cy) ) / ( (Bx-Ax)*(Dy-Cy)-(By-Ay)*(Dx-Cx) )
        s = ( (Ay-Cy)*(Bx-Ax)-(Ax-Cx)*(By-Ay) ) / ( (Bx-Ax)*(Dy-Cy)-(By-Ay)*(Dx-Cx) )
    except ZeroDivisionError:
        return None

    print "r: "+str(r) + "s: "+str(s)
    if r>1 or r < 0  or s > 1 or s < 0: #intersection doesn't exist
        return None



    Px=Ax+r*(Bx-Ax)
    Py=Ay+r*(By-Ay)
    return Px,Py

