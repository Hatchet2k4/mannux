#!/usr/bin/env python

import ika
import config


class Window(object):

    def __init__(self, width=1, height=1):
        super(Window, self).__init__()
        self.corners = [ika.Image('%s/box-top-left.png' % config.image_path),
                        ika.Image('%s/box-top-right.png' % config.image_path),
                        ika.Image('%s/box-bot-left.png' % config.image_path),
                        ika.Image('%s/box-bot-right.png' % config.image_path)]
        self.canvas_sides = [ika.Canvas('%s/box-top.png' % config.image_path),
                             ika.Canvas('%s/box-bot.png' % config.image_path),
                             ika.Canvas('%s/box-left.png' % config.image_path),
                             ika.Canvas('%s/box-right.png' % config.image_path)]
        self.sides = [None] * 4
        self.color = ika.RGB(0, 0, 0, 150)
        self.border_size = 32
        self.resize(width, height)

    def resize(self, width, height):
        if width <= 0:
            width = 1
        if height <= 0:
            height = 1
        self.width = width
        self.height = height
        temp = ika.Canvas(width, self.border_size)
        for i in range(2):
            self.canvas_sides[i].Blit(temp, 0, 0, ika.Opaque)
            self.sides[i] = ika.Image(temp)
        temp = ika.Canvas(self.border_size, height)
        for i in range(2, 4):
            self.canvas_sides[i].Blit(temp, 0, 0, ika.Opaque)
            self.sides[i] = ika.Image(temp)

    def draw(self, x, y):
        ika.Video.DrawRect(x + 10, y + 10, x + self.width + 54,
                           y + self.height + 54, self.color, True)
        ika.Video.Blit(self.corners[0], x, y)
        ika.Video.Blit(self.corners[1], x + self.width + self.border_size, y)
        ika.Video.Blit(self.corners[2], x, y + self.height + self.border_size)
        ika.Video.Blit(self.corners[3], x + self.width + self.border_size,
                       y + self.height + self.border_size)
        ika.Video.Blit(self.sides[0], x + self.border_size, y)
        ika.Video.Blit(self.sides[1], x + self.border_size,
                       y + self.height + self.border_size)
        ika.Video.Blit(self.sides[2], x, y + self.border_size)
        ika.Video.Blit(self.sides[3], x + self.width + self.border_size,
                       y + self.border_size)
