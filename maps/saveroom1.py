#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
#from engine.fog import Fog


def AutoExec():
    e.camera.reset_borders()
    #e.foreground_things.append(Fog(0.6, 0.2))
    e.AddEntity(Door(17 * ika.Map.tilewidth, 7 * ika.Map.tileheight,
                               'door_left'))
    # Loading a saved file.
    if e.loading:
        e.player.position = (7 * ika.Map.tilewidth, 8 * ika.Map.tileheight)



toBay2 = engine.mapscript.Warp(1, 23, 'cargobay2.ika-map', Dir.RIGHT)
runSave = engine.mapscript.Save(6*16 + 8,8*16)
