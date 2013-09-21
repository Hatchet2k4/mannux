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


    e.AddEntity(Door(2 * ika.Map.tilewidth, 9 * ika.Map.tileheight,
                         'door_right'))
    #e.AddEntity(Turret(8 * ika.Map.tilewidth,
    #                       9 * ika.Map.tileheight))


toSupplyBay1 = engine.mapscript.Warp(37, 25, 'supplybay1.ika-map', Dir.LEFT)

