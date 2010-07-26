import ika
from riptiles import RipTiles

tiles = RipTiles("img/automap/tiles.png", 8, 8, 9, 756)
overlays = (ika.Image("img/automap/icon_item.png"), ika.Image("img/automap/icon_found.png"), ika.Image("img/automap/icon_save.png"), ika.Image("img/automap/icon_boss.png"))

class Automap(object):
    def __init__(self):
        self.data = []
        self.overlays = {}
        self.cur_area = 0

        # Top-left corner of the map in automap coordinates.
        self.map_x = 0
        self.map_y = 0

        # Current location of the automap.
        self.cur_map_x = 0
        self.cur_map_y = 0

        # Current room index and color.
        self.room_index = 0
        self.room_color = 2

        self.ticks = 0
        self.flash = False

    def GetAreaName(self, area = None):
        if area is None:
            area = self.cur_area
        return self.data[area][0]

    def LoadData(self):
        ika.Map.Switch("amap.ika-map")
        #Load tile and map data.
        for l in range(ika.Map.layercount):
            name, w, h = ika.Map.GetLayerProperties(l)[:3]
            tiles = list()
            for y in range(h):
                for x in range(w):
                    t = ika.Map.GetTile(x, y, l)
                    tiles.append((0, t, 1 + t / 126))
            self.data.append([name, False, w, h, tiles])

        #Load up overlay data.
        meta = ika.Map.GetMetaData()
        for o in meta["overlays"].split("|"):
            x, y, l, i = map(lambda x: int(x), o.split(","))
            self.overlays[(x, y, l)] = i



    def EnterRoom(self, cur_map):
        """Enter a new room."""
        #Get meta data.
        meta = ika.Map.GetMetaData()
        self.map_x = int(meta["map_x"])
        self.map_y = int(meta["map_y"])

        #Check for area switch!
        if int(cur_map[0]) != self.cur_area:
            self.cur_area = int(cur_map[0])

    def Update(self, px, py):
        x = self.map_x + int(px / 20)
        y = self.map_y + int(py / 15)
        if x != self.cur_map_x or y != self.cur_map_y:
            self.cur_map_x = x
            self.cur_map_y = y
            self.room_index = y * self.data[self.cur_area][2] + x
            s, t, o = self.data[self.cur_area][4][self.room_index]
            if s < 2:
                if o == 1:
                    self.data[self.cur_area][4][self.room_index] = (2, t + 126, 2)
                else:
                    self.data[self.cur_area][4][self.room_index] = (o, t, o)

        self.ticks += 1

        if self.ticks / 12 % 2:
            self.flash = True
        else:
            self.flash = False

    def Draw(self, x, y, offset, dimensions, a = None, color = None, flash = True):
        w, h = dimensions

        #Get area to draw.
        if a is None:
            area = self.data[self.cur_area]
            a = self.cur_area
        else:
            area = self.data[a]

        for i in range(w * h):
            dx = x + (i % w) * 8
            dy = y + (i / w) * 8
            tx = (i % w) + offset[0]
            ty = (i / w) + offset[1]
            index = tx + ty * area[2]
            if index < len(area[4]):
                s, t = area[4][index][:2]
                if s > 0:
                    if self.flash and flash and index == self.room_index:
                        tile = tiles[(t % 126) + 630]
                    else:
                        tile = tiles[t]

                    if color:
                        ika.Video.TintBlit(tile, dx, dy, color)
                    else:
                        tile.Blit(dx, dy)

                    ox = index % area[2]
                    oy = index / area[2]
                    if (ox, oy, a) in self.overlays:
                        if color:
                            ika.Video.TintBlit(overlays[self.overlays[(ox, oy, a)]], dx, dy, color)
                        else:
                            overlays[self.overlays[(ox, oy, a)]].Blit(dx, dy)
            else:
                break

    def __GetWidth(self):
        return self.data[self.cur_area][2]

    def __GetHeight(self):
        return self.data[self.cur_area][3]

    width = property(__GetWidth)
    height = property(__GetHeight)
