import ika
import config
from engine import engine
from entity import Entity
from enemy import Enemy
from sounds import sound
import math
from boom import Boom
import fonts

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
        self.ticks = 0
        self.floaty = 0
        self.starty = y #haaack

    def update(self):
        super(Sentry, self).update()
        if self.anim.kill:
            self._destroy()

    def touch(self, other):
        if other is engine.player:
            other.Hurt(self.damage)

    def draw(self):
        #need if Distance and AI mode:
        ika.Video.DrawTriangle((self.x+self.sprite.hotwidth/2-ika.Map.xwin, self.y+self.sprite.hotheight/2-ika.Map.ywin, ika.RGB(200,200,0,128)), (engine.player.x+(engine.player.sprite.hotwidth/2)-ika.Map.xwin, engine.player.y-ika.Map.ywin, ika.RGB(200,200,0,32)),(engine.player.x+(engine.player.sprite.hotwidth/2)-ika.Map.xwin, engine.player.y+engine.player.sprite.hotheight-ika.Map.ywin, ika.RGB(200,200,0,32)))
        #print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+40), "x:", str(self.x)
        #print >> fonts.tiny(int(self.x)-ika.Map.xwin, int(self.y)-ika.Map.ywin+50), "y:", str(self.y)

    def Hurt(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.state = self.death_state
        else:
            self.hurt = True

    def float_state(self):
        self.ticks=0
        while True:
            self.ticks+=1
            self.floaty=12*math.cos(math.radians(self.ticks))
            self.y=self.starty+self.floaty

            if self.ticks > 360:
                self.ticks=0
            yield None



    def death_state(self):

        engine.AddEntity(Boom(int(self.x-3), int(self.y - 3),
                             'explode.ika-sprite', 6))
        self.hurtable = False
        self.destroy = True
        #while not self.anim.kill: #when death animation...
        #    yield None
        yield None

