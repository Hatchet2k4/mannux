import ika

def Draw(x, y, w, h):
    ika.Video.DrawRect(x, y, x + w, y + h, ika.RGB(0, 0, 0), True)
    ika.Video.DrawRect(x, y, x + w, y + h, ika.RGB(255, 255, 255))
