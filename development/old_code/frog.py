import system
import ika
from entity import Entity, entities
import engine
from const import *
from boom import Boom
import vecmath

class Frog(Entity):
    def __init__(self, x, y):
        super(type(self), self).__init__(ika.Entity(x, y, 1, 'sprites/frog.ika-sprite'))
        self.sprite.x = x
        self.sprite.y = y       
        
        self.x = x
        self.y = y
        self.vy = 0
        self.vx = 0
        self.anim.kill = True

        self.direction = Dir.RIGHT
        self.gravity = 0.125
        self.sprite.isobs = True
        self.etype = e_enemy #enemy
        self.damage = 25
        self.hp = 16
        self.state = self.Jump

    def Hurt(self, amount):
        self.hp -= amount
        if self.hp <=0: 
            entities.append(Boom(self.x, self.y))
            self.Destroy()
        

    def Jump(self):
        while True:
            self.anim.curFrame = 3 + self.direction * 4

            if self.left_wall:
                self.direction = Dir.RIGHT
                self.vx *= -1
                self.x += 1

            if self.right_wall:
                self.direction = Dir.LEFT
                self.vx *= -1
                self.x -= 1

            if self.floor:
                self.vx = vecmath.DecreaseMagnitude(self.vx, 0.2)
                self.vy = 0
                #self.anim.curFrame = 4 * self.direction
                self.SetAnimState(4 * self.direction + 3, 4 * self.direction, 4, loop = False, reset = True)

                # hit the floor.  Hold up a moment. 
                i = 80
                while i > 0:
                    i -= 1
                    yield None

                self.vy = -2
                self.y -= 3
                self.SetAnimState(4 * self.direction, 4 * self.direction + 3, 4, loop = False, reset = True)

                if self.direction == Dir.LEFT:
                    self.vx = -1
                else:
                    self.vx = 1
            else:
                self.vy += self.gravity

            yield None