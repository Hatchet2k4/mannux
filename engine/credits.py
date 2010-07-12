#!/usr/bin/env python

import ika
import video
import color
import fonts


# JYRUS     -- ARTWORK
# AFTERGLOW -- ARTWORK
# KHADGAR   -- ARTWORK
# RAIDEN    -- MAPS


_text = '''\
PROGRAM  ANDY FRIESEN
         FRANCIS BRAZEAU
         IAN D. BOLLINGER
         KEVIN T. GADD

ARTWORK  J. COREY ANNIS

  MUSIC  BRENT ABBOT
         DAVID CHURCHILL
         HAMPUS BERGGREN

   MAPS  J. COREY ANNIS
         TROY POTTS

 SCRIPT  FRANCIS BRAZEAU
         SEUNG PARK


"TEST3"
WRITTEN BY DAVID CHURCHILL

"SHADE OF NIGHT"
WRITTEN BY HAMPUS BERREGREN


MANNUX
'''.split('\n')


def credits():
    y = -ika.Video.yres
    now = ika.GetTime()
    while True:
        t = ika.GetTime()
        delta = (t - now) / 10.0
        y += delta
        now = t
        video.clear()
        first_line = int(y) / fonts.one.height
        adjust = int(y) % fonts.one.height
        length = ika.Video.yres / fonts.one.height + 1
        print first_line
        Y = -adjust
        while Y < ika.Video.yres and first_line < len(_text):
            if first_line >= 0:
                print >> fonts.one.center(y=Y), _text[first_line]
            Y += font.height
            first_line += 1
        ika.Video.DrawTriangle((0, 0, color.black),
                               (ika.Video.xres, 0, color.transparent,
                               (0, 60, color.transparent))
        ika.Video.DrawTriangle((ika.Video.xres, ika.Video.yres, color.black),
                               (0, ika.Video.yres, color.transparent),
                               (ika.Video.xres, ika.Video.yres - 60,
                                color.transparent))
        ika.Video.ShowPage()
        ika.Input.Update()
