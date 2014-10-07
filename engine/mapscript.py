#!/usr/bin/env python

import ika
from engine import engine
from riptiles import rip_tiles
import config

def Warp(x, y, map, direction=0, fadein=True, fadeout=True, scroll=False):
    return lambda: engine.map_switch(x * ika.Map.tilewidth,
                                     y * ika.Map.tileheight, map, direction,
                                     fadeout, fadein, scroll)


class LayerFader(object):

    def __init__(self, layername, start_alpha, end_alpha, length=50):
        super(LayerFader, self).__init__()
        self.layername = layername
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.length = length
        self.activated = False

    def __call__(self):
        #ika.Log("Layer "+self.layername+" script triggered!")
        if not self.activated:
            self.activated = True       
            ika.Log("Layer "+self.layername+" activated!")
            engine.foreground_things.append(FaderThing(self.layername,
                                                       self.start_alpha,
                                                       self.end_alpha,
                                                       ika.GetTime(),
                                                       ika.GetTime() +
                                                       self.length))

            ika.Log(str(engine.foreground_things))



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
        
        #ika.Log("wtf update! "+str(current) + "layer :"+ str(self.layer))
        
        ika.Map.SetLayerTint(self.layer, ika.RGB(255, 255, 255, current))
        if position >= 1:
            engine.foreground_things.remove(self) #may need to have an engine call for this


def Save(x=0,y=0):
    return lambda: _Save(x,y)   

def _Save(x, y, reposition=True):

    engine.player.state = engine.player.IdleState
    
    if reposition: 
        engine.player.x = x + 9
        engine.player.y = y
        engine.camera.update()
        
    
    saved = engine.SavePrompt()
    if saved:
        saveflash = rip_tiles('%s/save_flash.png' %    
                                    config.image_path, 32, 48, 15, 15) 
        savelight = rip_tiles('%s/savelight.png' %    
                                    config.image_path, 30, 22, 15, 15) 
        time = ika.GetTime()
        ticks = 0
        while ticks < 165:
            t = ika.GetTime()
            while t > time:                         
                ticks+=1
                time +=1
                
            time = ika.GetTime()                
            engine.draw()    
            engine.hud.draw()

            saveflash[int(ticks/12)].TintBlit(x - ika.Map.xwin, y - ika.Map.ywin, ika.RGB(128,128,128,64), ika.AddBlend)
            
            savelight[int(ticks/12)].TintBlit(x - ika.Map.xwin+1, y - ika.Map.ywin+26, ika.RGB(128,128,128,64), ika.AddBlend)
            
            
            ika.Video.ShowPage()
            ika.Input.Update()
        
    
    
    engine.player.state = engine.player.StandState


def ShipSave():
    return lambda: _ShipSave()

def _ShipSave():
    saved = engine.SavePrompt()
    #anim stuff here
    
    
    
    

    
    
    



