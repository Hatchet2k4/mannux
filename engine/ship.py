#!/usr/bin/env python

import ika
import config
from riptiles import rip_tiles
from rotateblit import rotate_blit


# Probably can turn this into a generator function if it takes too much
# memory.
#def interpolate(val1, val2, length, style='linear'):
#    return [((length - i) * val1 + val2 * i) * 1.0 / length
#            for i in range(length)]


class Ship(object):

    def __init__(self, x=370, y=260):
        super(Ship, self).__init__()
        self.ship = [ika.Image('%s/ship/ship%s.png' % (config.image_path, i))
                     for i in range(1, 6)]
        self.frames = [2, 3, 4]
        self.time = 0
        self.x = x
        self.y = y
        self.frame = 0
        self.mapy = ika.Map.ywin
        self.mapx = ika.Map.xwin
        self.angle = -40
        self.size = 1
        self.curframe = 0
        self.rotated = True
        self.vx = 0
        self.vy = 0
        self.va = 0
        self.vs = 0

    def update(self):
        self.time += 1
        self.frame = self.frames[self.time / 4 % len(self.frames)]
        self.x += self.vx
        self.y += self.vy
        self.angle += self.va
        self.size += self.vs
        # Finish at: 344, 235 (+136, +57)

    def draw(self):
        if self.rotated:
            rotate_blit(self.ship[self.frame], self.x - ika.Map.xwin,
                        self.y - ika.Map.ywin, self.angle, self.size)
        else:
            ika.Video.Blit(self.ship[self.frame], self.x - ika.Map.xwin,
                           self.y - ika.Map.ywin)


class ShipLanding(object):

    def __init__(self, x, y):
        super(ShipLanding, self).__init__()
        self.ship = ika.Image('%s/ship/ship_hull.png' % config.image_path)
        self.landinggear = rip_tiles('%s/ship/ship_lgear2.png' %
                                     config.image_path, 27, 41, 8, 8)
        self.interior = ika.Image('%s/ship/ship_interior.png' %
                                  config.image_path)
        self.chair = ika.Image('%s/ship/ship_chair.png' % config.image_path)
        self.lgear = ika.Image('%s/ship/ship_lgear1.png' % config.image_path)
        
        self.ljet = rip_tiles('%s/ship/jet_left.png' %
                                     config.image_path, 16, 16, 3, 3)
        self.rjet = rip_tiles('%s/ship/jet_right.png' %
                                     config.image_path, 16, 16, 3, 3)        
                                     
                                     
        self.tabby = ika.Image('%s/ship/ship_tabby.png' % config.image_path)                                           
        self.x = x
        self.y = y
        self.geary = 0
        self.gearframe = 7
        self.time=0
        self.jetframe=0
        self.jets=True

    def draw(self):
        self.interior.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)
        self.chair.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)
        self.tabby.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)
        
        self.landinggear[self.gearframe].Blit(self.x - ika.Map.xwin + 62,
                                              self.y - ika.Map.ywin + 88)
        self.landinggear[self.gearframe].Blit(self.x - ika.Map.xwin + 183,
                                              self.y - ika.Map.ywin + 88)
        self.ship.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)
        self.lgear.Blit(self.x - ika.Map.xwin,
                        self.y - ika.Map.ywin + self.geary)
        if self.jets==True:
            self.ljet[self.jetframe].Blit(self.x - ika.Map.xwin + 32,
                        self.y - ika.Map.ywin + 94)
            self.rjet[self.jetframe].Blit(self.x - ika.Map.xwin + 220,
                        self.y - ika.Map.ywin + 94)                        

    def update(self): #could be better coded but I'm lazy :P
        self.time+=1
                
        if self.time>=5:
            self.time=0
            self.jetframe+=1
            if self.jetframe==3:
                self.jetframe=0






class ShipLanded(object):

    def __init__(self, x, y):
        super(ShipLanded, self).__init__()
        self.ship = ika.Image('%s/ship/ship_hull.png' % config.image_path)
        self.landinggear = rip_tiles('%s/ship/ship_lgear2.png' %
                                     config.image_path, 27, 41, 8, 8)[0]
        self.interior = ika.Image('%s/ship/ship_interior.png' %
                                  config.image_path)
        self.chair = ika.Image('%s/ship/ship_chair.png' % config.image_path)
        self.lgear = ika.Image('%s/ship/ship_lgear1.png' % config.image_path)
        
        self.rjet = rip_tiles('%s/ship/jet_right.png' %
                                     config.image_path, 16, 16, 3, 3)        
                                     
                                     
        self.tabby = rip_tiles('%s/ship/tab_shiplanding.png' %    
                                    config.image_path, 48, 64, 4, 4)               
        self.x = x
        self.y = y
        self.tabframe = 0

        self.chairx = 112
        self.chairy = 42
        #difference to bottom, 42 pixels   
        
        self.time = 0
        self.chairanimation = 0 #0=stationary, 1=going down, 2=going up, 3=on ground, empty
        self.chairstart = 0
        self.timeleft = 0

    def draw(self):            
        self.landinggear.Blit(self.x - ika.Map.xwin + 62,
                              self.y - ika.Map.ywin + 88)
        self.landinggear.Blit(self.x - ika.Map.xwin + 183,
                              self.y - ika.Map.ywin + 88)

        
        self.interior.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)        
        #self.chair.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)

        self.tabby[self.tabframe].Blit(self.x - ika.Map.xwin + self.chairx, 
                                       self.y - ika.Map.ywin + self.chairy)

        self.ship.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin)

        self.lgear.Blit(self.x - ika.Map.xwin, self.y - ika.Map.ywin + 50)
        
    def ChairDown(self):
        self.time = self.chairstart = ika.GetTime()
        self.chairanimation = 1
        self.timeleft = 210

    def update(self):
        
        if self.timeleft > 0:
            self.timeleft -=1
        elif self.chairanimation == 1:
            self.chairanimation = 3
        elif self.chairanimation == 2:
            self.chairanimation = 0
                
        if self.chairanimation == 1:                
            #if self.timeleft / 5
            pass
        
        
        
        





class Doors(object):

    def __init__(self):
        super(Doors, self).__init__()
        self.leftdoor = ika.Image('%s/leftdoor.png' % config.image_path)
        self.rightdoor = ika.Image('%s/rightdoor.png' % config.image_path)
        self.x = 355
        self.y = 195

    def draw(self):
        ika.Video.Blit(self.leftdoor, self.x - ika.Map.xwin,
                       self.y - ika.Map.ywin)
        ika.Video.Blit(self.rightdoor, self.x + 107 - ika.Map.xwin,
                       self.y - ika.Map.ywin)

    def update(self):
        pass