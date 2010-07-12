#!/usr/bin/env python

import ika
import video
import controls
from engine import engine
from sounds import sound


class TitleScreen(object):

    def __init__(self):
        super(TitleScreen, self).__init__()
        self.tabby = [ika.Image('images/title/bg_good.png'),
                      ika.Image('images/title/bg_evil.png')]
        self.items = [[ika.Image('images/title/newgame.png'),
                       ika.Image('images/title/newgame2.png')],
                      [ika.Image('images/title/continue.png'),
                       ika.Image('images/title/continue2.png')],
                      [ika.Image('images/title/quit.png'),
                       ika.Image('images/title/quit2.png')]]
        self.logo = ika.Image('images/title/logo.png')
        self.border = ika.Image('images/title/border.png')
        self.fade_opacity = 0
        self.fade_opacity_inc = 0.025
        self.fade_end_action = None
        self.items_x = 189
        self.items_y = 175
        self.items_x_space = 0
        self.items_y_space = 16
        self.selected_item = 0
        self.tabby_y_min = -(449 - 240)
        self.tabby_y_max = 0
        self.tabby_y_inc = 0.085
        self.tabby_y = self.tabby_y_min
        self.tabby_pause_length = 450
        self.tabby_pause = 0
        self.tabby_opacity = 0.50
        self.tabby_opacity_min = 0.0
        self.tabby_opacity_max = 0.55
        self.tabby_opacity_inc = -0.0008
        self.closed = False
        self.item_scripts = [engine.newgame, engine.loadgame, ika.Exit]
    
    def show(self):
        time = ika.GetTime()
        ika.Input.Unpress()
        ika.Input.Update()
        self.closed = False
        engine.music = ika.Music('music/test3.ogg')
        engine.music.loop = True
        engine.music.Play()
        while not self.closed:
            t = ika.GetTime()
            while t > time:
                time += 1
                engine.ticks += 1
                if self.tabby_pause > 0:
                    self.tabby_pause -= 1
                else:
                    self.tabby_y += self.tabby_y_inc
                self.tabby_opacity += self.tabby_opacity_inc
                self.fade_opacity += self.fade_opacity_inc
            if self.fade_opacity > 1:
                self.fade_opacity = 1
                self.fade_opacity_inc = 0
                if self.fade_end_action is not None:
                    self.closed = True
            if self.fade_opacity < 0:
                self.fade_opacity = 0
                self.fade_opacity_inc = 0
                if self.fade_end_action is not None:
                    self.closed = True
            if self.tabby_opacity > self.tabby_opacity_max:
                self.tabby_opacity_inc = -self.tabby_opacity_inc
                self.tabby_opacity = self.tabby_opacity_max
            if self.tabby_opacity < self.tabby_opacity_min:
                self.tabby_opacity_inc = -self.tabby_opacity_inc
                self.tabby_opacity = self.tabby_opacity_min
            if self.tabby_y > self.tabby_y_max:
                self.tabby_y_inc = -self.tabby_y_inc
                self.tabby_y = self.tabby_y_max
                self.tabby_pause += self.tabby_pause_length
            if self.tabby_y < self.tabby_y_min:
                self.tabby_y_inc = -self.tabby_y_inc
                self.tabby_y = self.tabby_y_min
                self.tabby_pause += self.tabby_pause_length
            self.draw_menu()
            ika.Video.ShowPage()
            ika.Input.Update()
            if controls.up.Pressed():
                self.selected_item -= 1
                if self.selected_item < 0:
                    self.selected_item = 2
                sound.play('Menu')
            if controls.down.Pressed():
                self.selected_item += 1
                if self.selected_item > 2:
                    self.selected_item = 0
                sound.play('Menu')
            if controls.confirm.Pressed():
                if self.item_scripts[self.selected_item] is not None:
                    sound.play('Menu')
                    self.fade_end_action = \
                        self.item_scripts[self.selected_item]
                    self.fade_opacity_inc = -0.025
        if self.fade_end_action is not None:
            self.closed = True
            self.fade_end_action()

    def draw_menu(self):
        ika.Video.Blit(self.tabby[0], 0, int(self.tabby_y))
        ika.Video.TintBlit(self.tabby[1], 0, int(self.tabby_y),
                           ika.RGB(255, 255, 255,
                                   int(self.tabby_opacity * 255)))
        ika.Video.Blit(self.border, 0, 0)
        ika.Video.Blit(self.logo, 320 - self.logo.width, 0)
        x = self.items_x
        y = self.items_y
        i = 0
        for item in self.items:
            ika.Video.Blit(self.items[i][i == self.selected_item], x, y)
            i += 1
            x += self.items_x_space
            y += self.items_y_space
        video.clear(ika.RGB(0, 0, 0, int((1.0 - self.fade_opacity) * 255)))
