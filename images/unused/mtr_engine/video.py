#!/usr/bin/env python

import ika
import color
#from things import Thing


def TintBlit(image, x, y, color):
    if color == ika.RGB(255, 255, 255):
        image.Blit(x, y)
    else:
        ika.Video.TintBlit(image, x, y, color)


def Clear(c=color.black):
    ika.Video.DrawRect(0, 0, ika.Video.xres - 1, ika.Video.yres - 1, c, True)


def GrabScreen():
    return ika.Video.GrabImage(0, 0, ika.Video.xres, ika.Video.yres)


def Fade(duration=100, start_color=color.transparent, end_color=color.black,
         draw=ika.Map.Render, draw_after=lambda: None):
    start_color = ika.GetRGB(start_color)
    delta_color = [s - e for e, s in zip(start_color, ika.GetRGB(end_color))]
    time = ika.GetTime()
    end_time = time + duration
    saturation = 0.0
    while time < end_time:
        i = ika.GetTime() - time
        time = ika.GetTime()
        saturation = min(saturation + float(i) / duration, 1.0)
        draw()
        Clear(ika.RGB(*[int(a + b * saturation)
                        for a, b in zip(start_color, delta_color)]))
        draw_after()
        ika.Video.ShowPage()
        ika.Input.Update()


def FadeIn(duration=100, c=color.black, draw=ika.Map.Render,
            draw_after=lambda: None):
    Fade(duration, c, color.transparent, draw, draw_after)


def FadeOut(duration=100, c=color.black, draw=ika.Map.Render,
             draw_after=lambda: None):
    Fade(duration, color.transparent, c, draw, draw_after)
