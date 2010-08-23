#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.ship import Ship, ShipLanded, ShipLanding, Doors
from engine.background import Background, GlowBG
from engine.fade import FadeIn, FadeOut
from engine.door import Door
from engine.fog import Fog
from engine.zombie import Zombie
from engine.dockwindow import DockWindow
from engine.turret import Turret
#from globalvars import font
from engine.const import Dir





def AutoExec():

    e.background_things.append(Background(ika.Image('images/leftdoor1.png'),
                                              208+154, 128+61))
    e.background_things.append(Background(ika.Image('images/rightdoor1.png'),
                                          208+262, 128+61))    
    e.background_things.append(Background(ika.Image('images/bg_docking_bay.png'),
                                          208, 128))
    e.background_things.append(Background(ika.Image('images/cargship.png'),
                                          380, 260))    


    e.foreground_things.append(Background(ika.Image('images/elevator.png'),
                                          336, 384))


    e.foreground_things.append(Fog())
    
    e.AddEntity(Door(2 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_right'))
    e.AddEntity(Door(57 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_left', locked=False))    

toAirlock2 = engine.mapscript.Warp(17, 10, 'airlock2.ika-map', Dir.LEFT) 

toAirlock3 = engine.mapscript.Warp(1, 10, 'airlock3.ika-map', Dir.RIGHT)


#secretArea = engine.mapscript.LayerFader('Secret Overlay', 255, 0, 25)




