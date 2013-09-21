#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog
from engine.turret import Turret

from engine.splash import Splash

def AutoExec():
    e.camera.reset_borders()
    #e.foreground_things.append(Fog(0.3, -0.08))


    e.AddEntity(Door(37 * ika.Map.tilewidth,
                         24 * ika.Map.tileheight, 'door_left'))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 8 * ika.Map.tileheight,
                         'door_right', locked=True))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_right'))
    #e.AddEntity(Turret(52 * ika.Map.tilewidth, 15 * ika.Map.tileheight))

    #e.AddEntity(Splash(74 * ika.Map.tilewidth, 20 * ika.Map.tileheight, "water"))


toDockControl2 = engine.mapscript.Warp(1, 6, 'dockingcontrolroom2.ika-map') #map not added yet...
toAirlock3 = engine.mapscript.Warp(18, 10, 'airlock3.ika-map')
toStorage1 = engine.mapscript.Warp(1, 10, 'storage1.ika-map')
toSecretDuct = engine.mapscript.Warp(57, 25, 'secretduct3.ika-map')
