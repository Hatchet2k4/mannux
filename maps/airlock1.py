#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog
from engine.turret import Turret


def AutoExec():
    e.camera.reset_borders()
    e.foreground_things.append(Fog(-0.2, 0.1))
    e.AddEntity(Door(17 * ika.Map.tilewidth, 9 * ika.Map.tileheight,
                         'door_left'))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 9 * ika.Map.tileheight,
                         'door_right'))
    #e.AddEntity(Turret(8 * ika.Map.tilewidth,
    #                       9 * ika.Map.tileheight))


toBay1 = engine.mapscript.Warp(77, 25, 'cargobay1.ika-map', Dir.LEFT)
toDock1 = engine.mapscript.Warp(1, 25, 'dockingbay.ika-map', Dir.RIGHT)
