#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog
from engine.platform import Platform

def AutoExec():
    e.camera.reset_borders()
    e.foreground_things.append(Fog(-0.1, 0.4))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 2 * ika.Map.tileheight,
                         'door_right'))
    #entities.append(Door(77 * ika.Map.tilewidth,
    #                     24 * ika.Map.tileheight, 'door_left'))
    #entities.append(Door(2 * ika.Map.tilewidth, 22 * ika.Map.tileheight,
    #                     'door_right'))
    #entities.append(Door(2 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
    #                     'door_right', locked=True))
    e.AddEntity(Platform(20 * ika.Map.tilewidth, 6 * ika.Map.tileheight-2,vx=0,vy=0.25))

#toBay1upper = engine.mapscript.Warp(1, 6, 'cargobay1.ika-map', Dir.LEFT)
#toBay1lower = engine.mapscript.Warp(1, 25, 'cargobay1.ika-map', Dir.LEFT)
toBay2 = engine.mapscript.Warp(61, 25, 'cargobay2.ika-map')
toSecretDuct2 = engine.mapscript.Warp(37, 3, 'secretduct2.ika-map', Dir.LEFT)
