import ika


o = 0x00
x = 0xFF


transparent = ika.RGB(o, o, o, o)
black = ika.RGB(o, o, o)
blue = ika.RGB(o, o, x)
green = ika.RGB(o, x, o)
aqua = ika.RGB(o, x, x)
red = ika.RGB(x, o, o)
violet = ika.RGB(x, o, x)
yellow = ika.RGB(x, x, o)
white = ika.RGB(x, x, x)
trans_white = ika.RGB(x, x, x, 127)


def ColorCode(color):
    r, g, b, a = ika.GetRGB(color)
    return "#[" + (('%02X' * 4) % (a, b, g, r)) +  "]"

del o, x
