#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog, Darkness
from engine.healthup import Healthup


def AutoExec():
    e.camera.reset_borders()
    e.foreground_things.append(Darkness())
    #e.foreground_things.append(Fog(-0.6, 0.2))
    if not 'SecretDuct3HealthUp' in e.flags:
        e.AddEntity(Healthup(8 * ika.Map.tilewidth,
                                 8 * ika.Map.tileheight,
                                 flag='SecretDuct3HealthUp'))    


toSupplyBay = engine.mapscript.Warp(11, 8, 'supplybay1.ika-map')

