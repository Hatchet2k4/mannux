#!/usr/bin/env python

import ika
import config
from entity import Entity


class DockWindow(Entity):

    def __init__(self, x, y, layer=2):
        super(DockWindow, self).__init__(ika.Entity(x, y, layer,
                                                    '%s/dockwindow.ika-sprite'
                                                    % config.sprite_path))
