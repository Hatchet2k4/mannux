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



#map scripts
toDockControl = engine.mapscript.Warp(17, 7, 'dockingcontrolroom.ika-map', Dir.LEFT)



toAirlock2 = engine.mapscript.Warp(17, 10, 'airlock1.ika-map', Dir.LEFT) #must rename later...


toAirlock1 = engine.mapscript.Warp(17, 10, 'airlock2.ika-map', Dir.RIGHT)





secretArea = engine.mapscript.LayerFader('Secret Overlay', 255, 0, 25)




