#!/usr/bin/env python

import ika
import engine as e
import fonts
import process
from sprite import Sprite, StaticSprite


class Entity(object):
    def __init__(self, x, y, sprite, hotspot=None, layer=None):
        #Set entity sprite.
        self.sprite = sprite

        #Entity hotspot.
        if hotspot == -1:
            pass
        elif hotspot == None:
            self.hotspot = (0, 0, self.sprite.width, self.sprite.height)
        else:
            self.hotspot = hotspot


        #Entity coordinates.
        self.x = x
        self.y = y
        if layer == None:
            self.layer = ika.Map.FindLayerByName("Background")
        else:
            self.layer = layer

        self.state__ = None
        self.cur_state = None
        self.vx = 0
        self.vy = 0

        self.rotation = 0
        self.tint = 0

        self.left_wall = 0
        self.right_wall = 0
        self.ceiling = 0
        self.floor = 0
        self.check_obs = True
        #self.anim = Anim()
        self.state = self.null_state
        self.touchable = False
        self.hurtable = False
        self.destroy = False
        self.active = True
        self.visible = True
        self.isobs = False


        self.flashticks = 0
        self.flashcolor = ika.RGB(255, 0, 0, 255)

        # Hack so that ika can detect entity collisions for us.
        #ika.Map.entities[id(self.sprite)] = self.sprite

        self.gravity = 0.1

    def Draw(self):
        x = int(self.x) - ika.Map.xwin - self.hotx
        y = int(self.y) - ika.Map.ywin - self.hoty
        self.sprite.Draw(x, y)

    def Touch(self, entity):
        pass

    def Hurt(self, hp):
        pass

    def set_animation_state(self, first, last, delay, loop=True, reset=True, pingpong=False):
        pass

    def animation(self):
        self.sprite.Update()

    def Update(self):
        self.state__()
        self.animation()
        self.x += self.vx
        self.y += self.vy

        #breaks doors and you're already doing it in enemy.py anyway?
        #if self.flashticks > 0:
        #    self.flashticks -= 1
        #    self.sprite.color = self.flashcolor
        #elif self.flashticks==0:
        #    self.sprite.color = None

        if self.check_obs:
           self.check_obstructions()
        if self.destroy:
           # Must put this at the end of the update.
           self._destroy()

    def null_state(self):
        """Default entity state.

        The entity does nothing at all in this state.
        """
        while True:
            yield None

    def _destroy(self):
        self.visible = False
        self.active = False
        #self.sprite = None
        e.engine.RemoveEntity(self)

    def check_obstructions(self):
        x = round(self.x)
        y = round(self.y)

        self.left_wall = self.check_v_line(x + self.vx - 1, y,
                                           y + self.hotspot[3] - 1)
        self.right_wall = self.check_v_line(x + self.hotspot[2] +
                                            self.vx + 1, y,
                                            y + self.hotspot[3] - 1)
        self.ceiling = self.check_h_line(x + 1, y + self.vy,
                                         x + self.hotspot[2] - 1)
        self.floor = self.check_h_line(x, y + self.hotspot[3] + self.vy,
                                       x + self.hotspot[2] - 1)

    def detect_collision(self):
        result = []
        for ent in e.engine.entities:
            if ent is not None and ent is not self:
                if ent.y + ent.hotspot[3] < self.y + self.hotspot[1] or \
                   ent.y + ent.hotspot[1] > self.y + self.hotspot[3] or \
                   ent.x + ent.hotspot[2] < self.x + self.hotspot[0] or \
                   ent.x + ent.hotspot[0] > self.x + self.hotspot[2]: pass
                else:
                    result.append(ent)

        #if len(result) > 0:
        #    print result
        return result




    def check_v_line(self, x, y1, y2):
        x = int(x)
        y1 = int(y1)
        y2 = int(y2)
        for y in range(y1, y2, 4):
            if self.get_obstruction(x, y, self.layer):
                return True
        return self.get_obstruction(x, y2, self.layer)

    def check_h_line(self, x1, y, x2):
        x1 = int(x1)
        y = int(y)
        x2 = int(x2)
        for x in range(x1, x2, 4):
            if self.get_obstruction(x, y, self.layer):
                return True
        return self.get_obstruction(x2, y, self.layer)

    def get_obstruction(self, x, y, layer):
        return ika.Map.GetObs(int(x / ika.Map.tilewidth),
                              int(y / ika.Map.tileheight), layer)

    def _set_state(self, new_state):
        self.cur_state = new_state
        self.state__ = new_state().next

    def _set_position(self, (x, y)):
        self.x, self.y = x, y

    def _set_visible(self, value):
        self.sprite.visible = value



    state = property(fset=_set_state)
    width = property(lambda self: self.hotspot[2])
    height = property(lambda self: self.hotspot[3])
    hotx = property(lambda self: self.hotspot[0])
    hoty = property(lambda self: self.hotspot[1])
    hotwidth = property(lambda self: self.hotspot[2]) #redundant, but ah well :P
    hotheight = property(lambda self: self.hotspot[3])
    position = property(lambda self: (self.x, self.y), _set_position)

    visible = property(lambda self: self.sprite.visible, _set_visible)

    #def set_frame(self, f):
    #    self.set_animation_state(self, f, f, 1, loop=False, reset=False)




#Pickups
class Pickup(Entity):
    def __init__(self, name, x, y):
        Entity.__init__(self, x, y, Sprite("powerups/%s-pickup" % name))
        self.touchable = True
        self.ticks = 0

    def Update(self):
        Entity.Update(self)
        self.ticks += 1
        if self.ticks > 900:
            self.sprite.color = ika.RGB(255, 255, 255, 255 - ((self.ticks - 901) * 255 / 100))
        if self.ticks == 1000:
            self.destroy = True


class SmallEnergyPickup(Pickup):
    def __init__(self, x, y):
        Pickup.__init__(self, "smenergy", x, y)
        self.set_animation_state(first=0, last=3, delay=15, loop=True)

    def Touch(self, player):
        self.destroy = True
        player.energy += 5


class LargeEnergyPickup(Pickup):
    def __init__(self, x, y):
        Pickup.__init__(self, "lgenergy", x, y) #hotspot 4,4
        self.set_animation_state(first=0, last=3, delay=15, loop=True)

    def Touch(self, player):
        self.destroy = True
        player.energy += 20


class MissilePickup(Pickup):
    def __init__(self, x, y):
        Pickup.__init__(self, "missile", x, y) #hotspot 2,2

    def Touch(self, player):
        self.destroy = True
        player.equipment["Missiles"].cur += 2


class SuperMissilePickup(Pickup):
    def __init__(self, x, y):
        Pickup.__init__(self, "smissile", x, y) #hotspot 2,2

    def Touch(self, player):
        self.destroy = True
        player.equipment["Super Missiles"].cur += 2


class PowerBombPickup(Pickup):
    def __init__(self, x, y):
        Pickup.__init__(self, "pbomb") #hotspot 2,2

    def Touch(self, player):
        self.destroy = True
        player.equipment["Super Missiles"].cur += 2



class Powerup(Entity):
    def __init__(self, x, y, type, item_id=None):
        Entity.__init__(self, x, y, StaticSprite("items/%s" % type.replace(" ", "").lower()), (0, 0, 16, 16))
        self.touchable = True

        self.type = type
        self.item_id = item_id

    def Touch(self, player):
        self.destroy = True
        e.processor += process.PowerupMessage(self.type, "MESSAGE GOES HERE", self.item_id)



#Enemy stuff.

