#!/usr/bin/env python

class Field(object):
    """A field is just a big invisible thing that does something if the
    player walks on to it.

    Warp points can be fields, as can plot-based zone things.
    """

    def __init__(self, rectangle, layer, script, name):
        super(Field, self).__init__()
        self.position = rectangle[:2]
        self.size = rectangle[2:]
        self.layer = layer
        self.script = script
        self.rectangle = rectangle
        self.name = name
        # If it starts with run, then you activate it by pressing up,
        # instead of entering it.
        self.runnable = name.startswith('run') 

    def fire(self):
        self.script()

    def test(self, entity):
        if entity.layer != self.layer:
            return False
        x, y = self.position
        width, height = self.size
        if x - entity.sprite.hotwidth  < entity.x < x + width and \
           y - entity.sprite.hotheight < entity.y < y + height:
            return True
        else:
            return False
