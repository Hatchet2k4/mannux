#!/usr/bin/env python

class Anim(object):
    """Handles animating sprites, since ika doesn't let you set
       arbitrary animation scripts yet.
    """

    def __init__(self, animation=None, loop=True):
        super(Anim, self).__init__()
        self.__animation = animation
        self.count = 0
        self.cur_frame = 0
        self.index = 0
        self.loop = loop
        self.kill = animation is None

    def set_anim(self, value, loop=True, reset=True):
        self.kill = False
        self.loop = loop
        if self.__animation is not value:
            self.__animation = value
            if reset:
                self.cur_frame = self.__animation[0][0]
                self.count = self.__animation[0][1]
                self.index = 0

    anim = property(lambda self: self.__animation)

    def update(self, time_delta):
        if self.kill:
            return
        self.count -= time_delta
        while self.count < 0:
            self.index += 1
            if self.index >= len(self.anim):
                if self.loop:
                    self.index = 0
                else:
                    self.kill = True
                    return
            self.cur_frame = self.anim[self.index][0]
            self.count += self.anim[self.index][1]

    def stop(self):
        self.kill = True

    def resume(self):
        self.kill = False
        if self.index >= len(self.anim):
            self.restart()

    def restart(self):
        self.index = 0
        self.count = 0
        self.kill = False


def make_anim(strand, delay):
    return zip(strand, [delay] * len(strand))
