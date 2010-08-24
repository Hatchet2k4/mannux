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
    #e.foreground_things.append(Fog(-0.6, 0.2))

toSupplyBay = engine.mapscript.Warp(11, 8, 'supplybay1.ika-map')

