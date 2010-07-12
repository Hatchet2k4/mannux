import ika
from entity import Entity, entities
import engine

class Scroll(Entity):
    def __init__(self, x, y, d, f):
        super(type(self), self).__init__(ika.Entity(x, y, 1, 'sprites/Warp.ika-sprite'))
        self.sprite.x = x
        self.sprite.y = y
        self.x = x
        self.y = y
        self.vx = self.vy = 0
        self.anim.kill = True
        self.anim.cur_frame = 0

        self.direction = d #scroll direction
        self.f=f

    def Update(self):
        super(type(self), self).Update()
        #if self.DetectCollision() is engine.engine.player.sprite:
         #   engine.engine.Scroll(self.direction)
         #   self.f()