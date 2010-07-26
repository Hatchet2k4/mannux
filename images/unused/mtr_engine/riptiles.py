import ika

def RipTiles(image, width, height, span=None, tilecount=None):
    """This is a simple function that takes any image that is formatted
    like a tileset and rips the tiles into a list which is then
    returned.

    image - image to rip from
    width/height - width and height of a single tile
    span - how many tiles per row
    tilecount - number of tiles to rip
    """
    tiles = []
    big_image = ika.Canvas(image)

    # do some figurin:) ~infey
    if span == None and tilecount == None:
        span = (big_image.width - 1) / (width + 1)
        tilecount = span * ((big_image.height - 1) / (height + 1))

    for i in range(tilecount):
        tile = ika.Canvas(width, height)
        big_image.Blit(tile, -1 - (i % span * (width + 1)),
                       -1 - (i / span * (height + 1)), ika.Opaque)
        tiles.append(ika.Image(tile))
    return tiles



class Animation(object):
    def __init__(self, images, anim):
        self.images = images
        self.anim = anim
        self.ticks = 0
        self.tick_mod = 0
        self.frame = 0

    def __GetImage(self):
        return self.images[self.anim[self.frame][0]]

    image = property(__GetImage)

    def Draw(self, x, y, tint=None, angle=None):
        if tint:
            ika.Video.TintBlit(self.image, x, y, tint)
        else:
            self.image.Blit(x, y)

    def Update(self, ticks=None):
        if ticks is None:
            ticks = self.ticks
            self.ticks += 1
        if ticks - self.tick_mod > self.anim[self.frame][1]:
            self.tick_mod += self.anim[self.frame][1]
            self.frame += 1
            if self.frame == len(self.anim):
                self.frame = 0

