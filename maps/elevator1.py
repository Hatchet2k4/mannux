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
    e.foreground_things.append(Fog(0.3, -0.08))
    e.AddEntity(Door(77 * ika.Map.tilewidth, 5 * ika.Map.tileheight,
                         'door_left'))
    e.AddEntity(Door(77 * ika.Map.tilewidth,
                         24 * ika.Map.tileheight, 'door_left'))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 5 * ika.Map.tileheight,
                         'door_right'))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_right'))
    e.AddEntity(Turret(52 * ika.Map.tilewidth, 15 * ika.Map.tileheight))

    #e.AddEntity(Splash(74 * ika.Map.tilewidth, 20 * ika.Map.tileheight, "water"))


toDockControl = engine.mapscript.Warp(1, 6, 'dockingcontrolroom.ika-map', Dir.LEFT)
toAirlock1 = engine.mapscript.Warp(1, 10, 'airlock1.ika-map', Dir.LEFT)
toBay2upper = engine.mapscript.Warp(77, 6, 'cargobay2.ika-map', Dir.LEFT)
toBay2lower = engine.mapscript.Warp(77, 25, 'cargobay2.ika-map', Dir.LEFT)
