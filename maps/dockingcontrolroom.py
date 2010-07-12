#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog


def AutoExec():
    e.camera.reset_borders()
    e.foreground_things.append(Fog(-0.3, -0.05))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 5 * ika.Map.tileheight,
                        'door_right'))
    #e.AddEntity(Door(77 * ika.Map.tilewidth,
    #                     24 * ika.Map.tileheight, 'door_left'))
    #e.AddEntity(Door(2 * ika.Map.tilewidth, 5 * ika.Map.tileheight,
    #                    'door_right'))
    #e.AddEntity(Door(2 * ika.Map.tilewidth,
    #                     24 * ika.Map.tileheight, 'door_right'))


toDock1 = engine.mapscript.Warp(1, 7, 'dockingbay.ika-map', Dir.LEFT)
#toDock1lower = engine.mapscript.Warp(1, 25, 'dockingbay.ika-map', Dir.LEFT)
toBay1 = engine.mapscript.Warp(77, 6, 'cargobay1.ika-map', Dir.LEFT)
#toBay2lower = engine.mapscript.Warp(77, 25, 'cargobay2.ika-map', Dir.LEFT)
