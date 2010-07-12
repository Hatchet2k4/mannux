#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog
from engine.healthup import Healthup


def AutoExec():
    e.camera.reset_borders()
    e.foreground_things.append(Fog(-0.6, 0.2))
    e.AddEntity(Door(37 * ika.Map.tilewidth, 2 * ika.Map.tileheight,
                         'door_left'))
    if not 'SecretDuctHealthUp' in e.flags:
        e.AddEntity(Healthup(6 * ika.Map.tilewidth,
                                 4 * ika.Map.tileheight,
                                 flag='SecretDuctHealthUp'))


toSecretDuct1 = engine.mapscript.Warp(1, 3, 'secretduct1.ika-map', Dir.RIGHT)
# Add powerup.
