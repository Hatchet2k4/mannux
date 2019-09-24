#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.const import Dir
from engine.door import Door
from engine.fog import Fog


def AutoExec():
    e.camera.reset_borders()




secretArea = engine.mapscript.LayerFader('Secret Layer', 255, 0, 25)
