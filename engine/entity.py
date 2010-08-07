#!/usr/bin/env python

import ika
from anim import Anim, make_anim
import engine as e

class Entity(object):

    def __init__(self, sprite):
        super(Entity, self).__init__()
        self.sprite = sprite
        self.sprite.isobs = False
        self.x__ = self.sprite.x
        self.y__ = self.sprite.y
        self.state__ = None
        self.vx = 0
        self.vy = 0
        self.left_wall = 0
        self.right_wall = 0
        self.ceiling = 0
        self.floor = 0
        self.check_obs = True
        self.hurtable = False
        self.anim = Anim()
        self.state = self.null_state
        self.touchable = False
        self.destroy = False
        self.active = True
        
        
        # Hack so that ika can detect entity collisions for us.
        #ika.Map.entities[id(self.sprite)] = self.sprite

    def draw(self):
        pass

    def touch(self, entity):
        pass

    def set_animation_state(self, first, last, delay, loop=True, reset=True):
        # Reverse order.
        if first > last:
            strand = range(last, first + 1)
            strand.reverse()
            self.anim.set_anim(make_anim(strand, delay), loop, reset)
        else:
            self.anim.set_anim(make_anim(range(first, last + 1), delay), loop,
                               reset)

    def animation(self):
        self.anim.update(1)
        self.sprite.specframe = self.anim.cur_frame

    def update(self):
        # Because it could have been destroyed already.
        if self.sprite is None:
            return
        self.state__()
        self.animation()
        self.x += self.vx
        self.y += self.vy
        self.sprite.x = int(self.x)
        self.sprite.y = int(self.y)
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
        layer = 1
        self.left_wall = self.check_v_line(x + self.vx - 2, y,
                                           y + self.sprite.hotheight - 2)
        self.right_wall = self.check_v_line(x + self.sprite.hotwidth +
                                            self.vx + 1, y,
                                            y + self.sprite.hotheight - 2)
        self.ceiling = self.check_h_line(x + 1, y + self.vy,
                                         x + self.sprite.hotwidth - 1)
        self.floor = self.check_h_line(x, y + self.sprite.hotheight + self.vy,
                                       x + self.sprite.hotwidth - 1)

    def detect_collision(self):
        result = []
        for entity in e.engine.entities:
            if entity is not self and entity.sprite and \
               entity.y + entity.sprite.hotheight > self.y and \
               entity.y < self.y + self.sprite.hotheight and \
               entity.x + entity.sprite.hotwidth > self.x and \
               entity.x < self.x + self.sprite.hotwidth:
                   result.append(entity)
        return result

    def check_v_line(self, x1, y1, y2):
        x1 = int(x1)
        y1 = int(y1)
        y2 = int(y2)
        for y in range(y1, y2, 4):
            if self.get_obstruction(x1, y, self.layer):
                return True
        return self.get_obstruction(x1, y2, self.layer)

    def check_h_line(self, x1, y1, x2):
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        for x in range(x1, x2, 4):
            if self.get_obstruction(x, y1, self.layer):
                return True
        return self.get_obstruction(x2, y1, self.layer)

    def get_obstruction(self, x, y, layer):
        return ika.Map.GetObs(int(x / ika.Map.tilewidth),
                              int(y / ika.Map.tileheight), layer)

    def _set_state(self, new_state):
        self.state__ = new_state().next

    def _set_x(self, value):
        self.sprite.x = self.x__ = value

    def _set_y(self, value):
        self.sprite.y = self.y__ = value

    def _set_layer(self, value):
        self.sprite.layer = value

    def _set_position(self, (x, y)):
        self.x, self.y = x, y

    def _set_isobs(self, value):
        self.sprite.isobs = value

    def _set_visible(self, value):
        self.sprite.visible = value

    state = property(fset=_set_state)
    x = property(lambda self: self.x__, _set_x)
    y = property(lambda self: self.y__, _set_y)
    height = property(lambda self: self.sprite.hotheight)
    width = property(lambda self: self.sprite.hotwidth)
    position = property(lambda self: (self.x, self.y), _set_position)
    layer = property(lambda self: self.sprite.layer, _set_layer)
    isobs = property(lambda self: self.sprite.isobs, _set_isobs)
    visible = property(lambda self: self.sprite.visible, _set_visible)

    #def set_frame(self, f):
    #    self.set_animation_state(self, f, f, 1, loop=False, reset=False)



