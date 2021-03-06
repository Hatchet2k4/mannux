#!/usr/bin/env python

import ika

xres = ika.Video.xres
yres = ika.Video.yres

class Camera(object):

    def __init__(self, target=None):
        self.target = target
        self.xoffset = 0
        self.yoffset = 0

        self.drift = False
        self.ResetBorders()
        self.camspeed = 3

        self.x = self.y = 0
        self.xfix=self.yfix=self.borderfix=1


    def Update(self):
        if self.target is not None:
            #center of target
            y = self.target.y + self.target.sprite.height / 2 - yres/2
            x = self.target.x + self.target.sprite.width / 2 - xres/2

            if not self.drift:
                if x < self.left:
                    x = self.left
                elif x + ika.Video.xres > self.right:
                    x = self.right - ika.Video.xres

                if y < self.top:
                    y = self.top
                elif y + ika.Video.yres > self.bottom:
                    y = self.bottom - ika.Video.yres

                self.x = x
                self.y = y

            else:
                #hacky, but seems to work. o_O
                if self.borderfix==1:
                    if self.x < x:
                        self.x += self.camspeed
                        if self.x >= x:
                            self.x = x
                            if self.borderfix==1:
                                self.xfix=1
                    elif self.x > x:
                        self.x -= self.camspeed
                        if self.x <= x:
                            self.x = x
                            if self.borderfix==1:
                                self.xfix=1
                    else:
                        if self.borderfix==1:
                            self.xfix=1

                if self.borderfix==1:
                    if self.y < y:
                        self.y += self.camspeed
                        if self.y > y:
                            self.y = y
                            if self.borderfix==1:
                                self.yfix=1
                    elif self.y + y:
                        self.y -= self.camspeed
                        if self.y <= y:
                            self.y = y
                            if self.borderfix==1:
                                self.yfix=1
                    else:
                        if self.borderfix==1:
                            self.yfix=1

                d=0
                if self.y < self.top:
                    self.y += self.camspeed
                    d+=1
                    if self.y >= self.top:
                        self.y = self.top

                elif self.y + yres > self.bottom:
                    self.y -= self.camspeed
                    d+=1
                    if self.y + yres <= self.bottom:
                        self.y = self.bottom-yres

                if self.x < self.left:
                    self.x += self.camspeed
                    d+=1
                    if self.x >= self.left:
                        self.x = self.left

                elif self.x + xres > self.right:
                    self.x -= self.camspeed
                    d+=1
                    if self.x + xres <= self.right:
                        self.x = self.right-xres

                if d==0:
                    self.borderfix=1

                #Camera locked on.
                if self.xfix>0 and self.yfix>0 and self.y >= self.top and self.y + yres <= self.bottom and self.x >= self.left and self.x+xres <=self.right:
                    self.drift = False

            ika.Map.ywin = int(self.y)
            ika.Map.xwin = int(self.x)





    def ResetBorders(self):
        self.SetBorders(0, 0, ika.Map.width, ika.Map.height)

    def SetBorders(self, x, y, width, height, drift=False):
        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height
        self.width = width
        self.height = height
        self.drift = drift
        if drift:
            self.xfix=self.yfix=self.borderfix=0

