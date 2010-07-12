#!/usr/bin/env python

import ika
import color


def clear(c=color.black):
    ika.Video.DrawRect(0, 0, ika.Video.xres - 1, ika.Video.yres - 1, c, True)


def grab_screen():
    return ika.Video.GrabImage(0, 0, ika.Video.xres, ika.Video.yres)


def fade(duration=100, start_color=color.transparent, end_color=color.black,
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
        clear(ika.RGB(*[int(a + b * saturation)
                        for a, b in zip(start_color, delta_color)]))
        draw_after()
        ika.Video.ShowPage()
        ika.Input.Update
        while time == ika.GetTime():
            ika.Input.Update()


def fade_in(duration=100, c=color.black, draw=ika.Map.Render,
            draw_after=lambda: None):
    fade(duration, c, color.transparent, draw, draw_after)


def fade_out(duration=100, c=color.black, draw=ika.Map.Render,
             draw_after=lambda: None):
    fade(duration, color.transparent, c, draw, draw_after)
