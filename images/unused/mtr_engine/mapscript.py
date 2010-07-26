#!/usr/bin/env python

import ika
from engine import engine


def Warp(x, y, map, direction=0, fadein=True, fadeout=True, scroll=False):
    return lambda: engine.map_switch(x * ika.Map.tilewidth,
                                     y * ika.Map.tileheight, map, direction,
                                     fadeout, fadein, scroll)


class LayerFader(object):

    def __init__(self, name, start_alpha, end_alpha, length):
        super(LayerFader, self).__init__()
        self.name = name
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.length = length
        self.activated = False

    def __call__(self):
        if not self.activated:
            self.activated = True
            engine.foreground_things.append(FaderThing(self.name,
                                                       self.start_alpha,
                                                       self.end_alpha,
                                                       ika.GetTime(),
                                                       ika.GetTime() +
                                                       self.length))


class FaderThing(object):

    def __init__(self, name, start, end, start_time, end_time):
        super(FaderThing, self).__init__()
        self.layer = ika.Map.FindLayerByName(name)
        self.start = start
        self.end = end
        self.start_time = start_time
        self.length = end_time - start_time

    def update(self):
        position = (ika.GetTime() - self.start_time) / float(self.length)
        if position > 1:
            position = 1
        current = self.start + ((self.end - self.start) * position)
        ika.Map.SetLayerTintColour(self.layer, ika.RGB(255, 255, 255, current))
        if position >= 1:
            engine.foreground_things.remove(self)


def Save():
    return lambda: engine.SavePrompt()
