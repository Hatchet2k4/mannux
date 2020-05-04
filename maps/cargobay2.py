#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog, Darkness


def AutoExec():
    e.camera.reset_borders()
    e.foreground_things.append(Fog(-0.3, 0.1))
    e.AddEntity(Door(77 * ika.Map.tilewidth, 5 * ika.Map.tileheight,
                         'door_left'))
    e.AddEntity(Door(77 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_left'))
    e.AddEntity(Door(2 * ika.Map.tilewidth, 22 * ika.Map.tileheight,
                         'door_right'))
    #e.AddEntity(Door(2 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
    #                     'door_right', locked=True))
    e.foreground_things.append(Darkness())


toBay1upper = engine.mapscript.Warp(1, 6, 'cargobay1.ika-map', Dir.LEFT)
toBay1lower = engine.mapscript.Warp(1, 25, 'cargobay1.ika-map', Dir.LEFT)
toSave1 = engine.mapscript.Warp(17, 8, 'saveroom1.ika-map', Dir.LEFT)
toSecretDuct1 = engine.mapscript.Warp(20.5, 1, 'secretduct1.ika-map') #original

#toSecretDuct1 = engine.mapscript.Warp(24, 2, 'cave1.ika-map')


