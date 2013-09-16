import ika
import config
from engine import engine
from entity import Entity
from enemy import Enemy
from sounds import sound
import math
import vecmath
from boom import Boom
import fonts
from effects import Shield

class Sentry(Enemy):
    
    
    
    def __init__(self, x, y, sprite='needler.ika-sprite', framecount=3):
        super(Sentry, self).__init__(ika.Entity(x, y, ika.Map.FindLayerByName('Walls'),
                                              '%s/%s' %
                                              (config.sprite_path, sprite)))
        self.set_animation_state(first=0, last=framecount-1, delay=16, loop=True)
        #self.check_obs = False
        #self.direction = direction
        self.hurtable=True
        self.sprite.isobs = False
        self.touchable = False
        self.damage = 16
        self.hp = 40
        self.state = self.float_state
        self.ticks=0
        self.floaty = 0
        self.starty = y #haaack
        self.scanning = False
        self.float_ticks=0
        self.scanwidth=0
        self.scandistance=160 #~10 tiles distance to start scanning
        self.shields=True
        self.scansound=ika.Music('sfx/XRay.mp3')

    def update(self):
        super(Sentry, self).update()
        if self.anim.kill:
            self._destroy()

    def touch(self, other):
        if other is engine.player:
            other.Hurt(self.damage)

    def draw(self):
        if self.scanning:
            #center of scanning bot, may need to adjust based on direction
            x1=self.x+self.sprite.hotwidth/2-ika.Map.xwin
            y1=self.y+self.sprite.hotheight/2-ika.Map.ywin
            c1=ika.RGB(50+self.scanwidth*3,50+self.scanwidth*3,0,28+self.scanwidth*2)
            #towards top center of tabby

            h=(engine.player.sprite.hotwidth)*(self.scanwidth/50.0)

            x2=engine.player.x+(engine.player.sprite.hotwidth/2)-ika.Map.xwin
            y2=engine.player.y+(engine.player.sprite.hotheight/2)-h-ika.Map.ywin #opens towards top
            c2=ika.RGB(50+self.scanwidth*3,50+self.scanwidth*3,0,self.scanwidth)

            #towards bottom center of tabby
            x3=engine.player.x+(engine.player.sprite.hotwidth/2)-ika.Map.xwin
            y3=engine.player.y+(engine.player.sprite.hotheight/2)+h-ika.Map.ywin #opens toward bottom
            c3=ika.RGB(50+self.scanwidth*3,50+self.scanwidth*3,0,self.scanwidth)

            ika.Video.DrawTriangle( (x1,y1,c1), (x2, y2, c3),(x3, y3, c3) )
            print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+40), "h:", str(h)
            print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+50), "w:", str(self.scanwidth)


            

    def Hurt(self, bullet):    
        if self.shields:
              engine.AddEffect(Shield(bullet.x,bullet.y,self.sprite.layer, self))
              #no damage, muahaha...  but will reduce shield strength later, with the right weapon...
        else:
            self.hp -= bullet.damage #bad bad bad... yet I do it anyway...
            if self.hp <= 0:
                self.state = self.death_state
            else:
                self.hurt = True

    def float_state(self):
        while True:
            self.ticks+=1
            self.float_ticks+=1
            self.floaty=12*math.cos(math.radians(self.float_ticks))
            self.y=self.starty+self.floaty

            if self.float_ticks > 360:
                self.float_ticks=0

            if vecmath.distance(self.x+self.sprite.hotwidth/2, self.y+self.sprite.hotheight/2,
                             engine.player.x+engine.player.sprite.hotwidth/2, engine.player.y+engine.player.sprite.hotheight/2) < self.scandistance: #within scanning range
                self.state=self.scan_state

                yield None
            yield None

    def scan_state(self):
        self.scanning=True
        self.scanwidth=1

        
        self.scansound.loop=True
        self.scansound.pitchshift=0.5
        self.scansound.Play()
        while True:

            self.scansound.pitchshift=0.5+(self.scanwidth/100.0)
            self.ticks+=1
            self.float_ticks+=1
            self.floaty=12*math.cos(math.radians(self.float_ticks))
            self.y=self.starty+self.floaty

            if self.float_ticks > 360:
                self.float_ticks=0


            if vecmath.distance(self.x+self.sprite.hotwidth/2, self.y+self.sprite.hotheight/2,
                             engine.player.x+engine.player.sprite.hotwidth/2, engine.player.y+engine.player.sprite.hotheight/2) > self.scandistance+16: #player moving out of scanning range, with a bit of buffer...

                if self.scanwidth>0:
                    self.scanwidth-=1
                else: #been out of range, stop scanning
                    self.state=self.float_state
                    self.scanning=False
                    self.scansound.Pause()
                    yield None

            else: #still within scanning range.
                if self.scanwidth<50:
                    self.scanwidth+=1

            yield None

    def death_state(self):

        engine.AddEntity(Boom(int(self.x-3), int(self.y - 3),
                             'explode.ika-sprite', 6))
        self.hurtable = False
        self.destroy = True
        #while not self.anim.kill: #when death animation...
        #    yield None
        yield None

