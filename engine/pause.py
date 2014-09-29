#!/usr/bin/env python

import ika
import controls
import config
import video
import fonts
from engine import engine
from sounds import sound


class Pause(object):

    def __init__(self):
        self.mapw = ika.Image('%s/menu2.png' % config.image_path)
        self.menu1 = ika.Image('%s/menu1.png' % config.image_path)
        self.menu2 = ika.Image('%s/menu25.png' % config.image_path)
        self.menu3 = ika.Image('%s/menu3.png' % config.image_path)
        self.menu4 = ika.Image('%s/menu4.png' % config.image_path)
        #self.face = ika.Image('%s/face.png' % config.image_path)
        self.select = ika.Image('%s/select.png' % config.image_path)
        self.select2 = ika.Image('%s/select2.png' % config.image_path)
        self.icons = [ika.Image('%s/icon-pistol.png' % config.image_path),
                      ika.Image('%s/icon-shotgun.png' % config.image_path),
                      ika.Image('%s/icon-flame.png' % config.image_path),
                      ika.Image('%s/icon-lightning.png' % config.image_path),
                      ika.Image('%s/icon-rocket.png' % config.image_path),
                      ika.Image('%s/icon-blade.png' % config.image_path)]
        self.menuselected = 0
        self.mapx = 0
        self.mapy = 0
        self.options = ['Map', 'Weapons', 'Skills', 'Config', 'Quit']
        self.enabled = ['Map', 'Config', 'Quit']
        self.configkeys = ['attack', 'jump', 'aim_up', 'aim_down', 'dash'] #add dash, updownleftright
        self.mapname = ''

    def menu(self):
        controls.cancel.Pressed()
        self.mapname = ika.Map.GetMetaData()['name']
        sound.play('Whoosh')
        self.menuselected = 0
        time = ika.GetTime()
        ika.Input.Unpress()
        ika.Input.Update()
        while not controls.cancel.Pressed():
            t = ika.GetTime()
            while t > time:
                time += 1
                engine.ticks += 1
            engine.update_time()
            self.draw_menu()
            if self.menuselected == 0:
                print >> fonts.two(160, 30, align='center'), self.mapname
                engine.automap.draw_automap(self.mapx, self.mapy)
            if self.menuselected == 3:
                self.draw_options()
            ika.Video.ShowPage()
            ika.Input.Update()
            if controls.right.Pressed():
                i = 0
                while self.options[self.menuselected] not in self.enabled or i == 0:
                    i=1
                    self.menuselected += 1
                    if self.menuselected > 4:
                        self.menuselected = 0
                sound.play('Menu')
            if controls.left.Pressed():
                i = 0
                while self.options[self.menuselected] not in self.enabled or i == 0:
                    i = 1
                    self.menuselected -= 1
                    if self.menuselected < 0:
                        self.menuselected = 4
                sound.play('Menu')
            if controls.confirm.Pressed():
                [self.map, lambda: None, lambda: None, self.preferences,
                 ika.Exit][self.menuselected]()
                time = ika.GetTime()
        sound.play('Whoosh2')

    def map(self):
        time = ika.GetTime()
        ika.Input.Unpress()
        ika.Input.Update()
        scrolltime = 0
        while not (controls.cancel.Pressed() or controls.confirm.Pressed()):
            t = ika.GetTime()
            while t > time:
                time += 1
                engine.ticks += 1
                if scrolltime > 0:
                    scrolltime -= 1
            engine.update_time()
            self.draw_menu()
            print >> fonts.two(160, 30, align='center'), self.mapname
            engine.automap.draw_automap(self.mapx, self.mapy)
            c1 = ika.RGB(0, 200, 255, 200)
            c2 = ika.RGB(200, 200, 255, 200)

            #scroll triangles
            if self.mapx > 0:
                ika.Video.DrawTriangle((10, 100, c1), (20, 90, c2),
                                       (20, 110, c2))
            if self.mapx + 37 < 50:
                ika.Video.DrawTriangle((310, 100, c1), (300, 90, c2),
                                       (300, 110, c2))
            if self.mapy > 0:
                ika.Video.DrawTriangle((160, 40, c1), (150, 50, c2),
                                       (170, 50, c2))
            if self.mapy + 23 < 50:
                ika.Video.DrawTriangle((160, 185, c1), (150, 175, c2),
                                       (170, 175, c2))
            ika.Video.ShowPage()
            ika.Input.Update()
            if scrolltime == 0:
                if controls.right.Position() > controls.deadzone and self.mapx + 37 < 50:
                    self.mapx += 1
                    scrolltime = 5
                elif controls.left.Position() > controls.deadzone and self.mapx > 0:
                    self.mapx -= 1
                    scrolltime = 5
                elif controls.down.Position() > controls.deadzone and self.mapy + 23 < 50:
                    self.mapy += 1
                    scrolltime = 5
                elif controls.up.Position() > controls.deadzone and self.mapy > 0:
                    self.mapy -= 1
                    scrolltime = 5

    def preferences(self): #control config menu

        time = ika.GetTime()
        ika.Input.Unpress()
        ika.Input.Update()
        scroll = True
        optselected = 0
        selectmode=0 #0=selecting which control, 1=waiting for key to replace
        while not controls.cancel.Pressed():
             #

            t = ika.GetTime()
            while t > time:
                time += 1
                engine.ticks += 1


            engine.update_time()
            self.draw_menu()
            self.draw_options()

            #ika.Video.Blit(self.select2, 14, 46 + 12 * optselected) #ugly
            ika.Video.DrawRect(17, 49 + 12 * optselected, 100, 57+12*optselected, ika.RGB(100,255,100,64),1)

            ika.Video.ShowPage()

            ika.Input.Update()

            #select up/down
            opt = controls.down.Pressed() - controls.up.Pressed()
            if opt:
                optselected += opt
                optselected %= len(self.configkeys)
                sound.play('Menu')

            if controls.confirm.Pressed():
                ika.Input.Unpress()
                ika.Input.keyboard.ClearKeyQueue()
                done = False
                #select controls
                while not done:
                    t = ika.GetTime()
                    while t > time:
                        time += 1
                        engine.ticks += 1
                    time = ika.GetTime()
                    engine.update_time()

                    self.draw_menu()
                    self.draw_options(optselected)

                    #ika.Video.Blit(self.select2, 14, 46 + 12 * optselected) #ugly rectangle.
                    ika.Video.DrawRect(17, 49 + 12 * optselected, 100, 57+12*optselected, ika.RGB(100,255,100,128),1)

                    ika.Video.ShowPage()
                    ika.Input.Update()


                    if len(ika.Input.joysticks) > 0:
                        newKey = None
                        newString = ''
                        for i in range(len(ika.Input.joysticks[0].axes)):
                            if (abs(ika.Input.joysticks[0].axes[i].Position())
                                > controls.deadzone):
                                newKey = ika.Input.joysticks[0].axes[i]
                                newString = 'JOYAXIS%i %s' % (i, '-+'[ika.Input.joysticks[0].axes[i].Position() > 0])
                                break
                        for i in range(len(ika.Input.joysticks[0].buttons)):
                            if ika.Input.joysticks[0].buttons[i].Pressed():
                                newKey = ika.Input.joysticks[0].buttons[i]
                                newString = 'JOY%s' % i
                                break
                        if newKey:
                            done = True
                            key = self.configkeys[optselected].replace(' ', '')
                            controls.__dict__[key] = newString
                            engine.player.__dict__[key] = newKey
                    newKey = ika.Input.keyboard.GetKey()
                    #if newKey:


                        #done = True
                        #key = self.configkeys[optselected].replace(' ', '')
                        #controls.__dict__[key] = newKey.upper()
                        #engine.player.__dict__[key] = \
                        #    ika.Input.keyboard[newKey.upper()]




    def draw_menu(self): #main menu draw
        #ika.Video.Blit(self.face, 11, 25)
        ika.Map.Render()
        ika.Video.Blit(self.menu1, 0, 0)
        ika.Video.Blit(self.menu3, 0, 190)
        ika.Video.Blit(self.menu4, 100, 190)
        if self.menuselected == 0:
           ika.Video.Blit(self.mapw, 0, 22)
        else:
           ika.Video.Blit(self.menu2, 0, 22)
           if self.menuselected == 4:
               print >> fonts.one(50, 100), "Press X to quit the game."


        x = 10
        y = 10
        for i, option in enumerate(self.options):
            #if option in self.enabled:
            #    if i == self.menuselected:
            #        f = fonts.three
            #    else: f = fonts.two
            #else:
            #    f = fonts.five
            f = [fonts.five, fonts.two][option in self.enabled]
            f = [f, fonts.three][i == self.menuselected]
            print >> f(x, y), option
            x += (len(option) + 1) * 10

        print >> fonts.one(10, 200), 'HEALTH'
        print >> fonts.tiny(40, 208), '%i/%i' % (engine.player.hp,
                                                 engine.player.maxhp)
        print >> fonts.one(10, 216), 'ENERGY'
        print >> fonts.tiny(40, 224), '%i/%i' % (engine.player.mp,
                                                 engine.player.maxmp)
        print >> fonts.one(105, 200), 'TIME:', engine.time

    def draw_options(self, selected=-1):
        print >> fonts.three(70, 34), 'CONTROL CONFIGURATION'
        print >> fonts.three(30, 47), 'ACTION'
        print >> fonts.three(132, 47), 'KEY'
        print >> fonts.three(196, 47), 'GAMEPAD'

        # x-pos of key name, x-pos of key, y-pos of first, y-inc, space
        # between first and '-'
        x1, x2, x3, y, h, optlen = 20, 140, 220, 60, 12, 11


        for i, option in enumerate(self.configkeys):

            print >> fonts.one(x1, y + i * h), '%s' % option.ljust(optlen)
            f = [fonts.one, fonts.three][selected == i] #select the item that's been highlighted
            print >> f(x2, y + i * h),  controls.control_list[option].buttons['key'].value
            if controls.usejoystick:
                print >> f(x3, y + i * h),  controls.control_list[option].buttons['joy'].value
            #print >> f(x2, y + i * h), controls.__dict__['%s_key' % option.replace(' ', '')]
