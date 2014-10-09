#!/usr/bin/env python

import ika
import config
import video
from riptiles import rip_tiles


class AutoMap(object):

    def __init__(self):
        super(AutoMap, self).__init__()
        self.amap = []
        self.amap2 = [] # second layer for secrets
        self.tiles = []
        self.minimap = ika.Image('%s/mapwindow.png' % config.image_path)
        # Top-left corner of the room in automap coordinates.
        self.mapx = 0
        self.mapy = 0
        # Current location on the automap.
        self.curmapx = 0
        self.curmapy = 0
        self.flash = 0
        self.t = ika.GetTime()
        self.roomcolor = 2
        #number of rooms wide/tall for the map
        self.mapw=50
        self.maph=50
        self.tiles_per_group=126 #126 tiles per color section of the tileset

    def load_automap(self):
        self.amap=[]
        for y in range(self.maph):
            for x in range(self.mapw):
                tile = ika.Map.GetTile(x, y, 0)
                self.amap.append((0, tile)) #0 = unvisited
        video.clear(ika.RGB(0, 0, 64))
        self.tiles = rip_tiles('%s/automap.png' % config.image_path, 8, 6, 9,
                               ika.Map.numtiles)

    def update_room(self):
        meta = ika.Map.GetMetaData()
        ika.Log(str(meta))

        self.mapx = int(meta['mapx'])
        self.mapy = int(meta['mapy'])
        if 'color' in meta:
            if meta['color'] == 'Red':
                self.roomcolor = 4
            elif meta['color'] == 'Green':
                self.roomcolor = 3
            else:
                self.roomcolor = 2
        else:
            self.roomcolor = 2

    def update(self, px, py):

        #self.update_room()
        #20x15 room size
        #50x50 automap size

        self.curmapx = self.mapx + int(px / 20)
        self.curmapy = self.mapy + int(py / 15)
        index = self.curmapy*self.maph + self.curmapx
        s, t = self.amap[index]
        if s < 2:
            self.amap[index] = (self.roomcolor, t)
        # s == 0: undiscovered
        # s == 1: revealed
        # s == 2: visited
        # s == 3: visited secret area
        # s == 4: visited save room


    def draw_minimap(self, dx, dy):
        self.update_flash()
        ika.Video.Blit(self.minimap, dx, dy)
        for x in range(5):
            for y in range(5):
                index = (y + self.curmapy - 2) * 50 + x + self.curmapx - 2
                s, t = self.amap[index]
                if s > 0:
                    if x == 2 and y == 2 and self.flash < 10:
                        ika.Video.Blit(self.tiles[t + 126 * 5],
                                       dx + 8 * x + 10, dy + 6 * y + 6)
                    elif self.tiles[t + 126 * (s - 1)]:
                        ika.Video.Blit(self.tiles[t + 126 * (s - 1)],
                                       dx + 8 * x + 10, dy + 6 * y + 6)

    def draw_automap(self, offsetx=0, offsety=0):
        self.update_flash()
        winx = 12
        winy = 40
        #magic numbers.. probably want to make this smaller...
        for x in range(37):
            for y in range(23):
                index = x + offsetx + (y + offsety) * 50
                s, t = self.amap[index]
                if s > 0:
                    if x + offsetx == self.curmapx and \
                       y + offsety == self.curmapy and self.flash < 10:
                        ika.Video.Blit(self.tiles[t + 5 * 126], winx + x * 8,
                                       winy +6  * y)
                    else:
                        ika.Video.Blit(self.tiles[t + (s - 1) * 126],
                                       winx + x * 8, winy + y * 6)

    def update_flash(self):
        time = ika.GetTime()
        self.flash += time - self.t
        if self.flash >= 20:
            self.flash -= 20
        if self.flash < 0:
            self.flash = 0
        self.t = ika.GetTime()
