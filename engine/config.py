#!/usr/bin/env python

import ika
import parser


game_config = 'game.cfg'


def init():
    global screen_width, screen_height
    config = parser.load(game_config)
    # Turn engine.cfg definitions into global variables.
    globals().update(config.todict())
    screen_width = int(screen_width)
    screen_height = int(screen_height)
    try:
        f = open(ika_config)
    except IOError:
        pass
    else:
        # Turn user.cfg definitions into global variables.
        lines = f.readlines()
        for line in lines:
            line = line.split()
            globals()[line[0]] = int(line[1])
        f.close()
    if 'xres' not in globals() or 'yres' not in globals():
        try:
            last_character = open(ika_config, 'rt').read()[-1]
        except IOError:
            last_character = '\n'
        f = open(ika_config, 'aU')
        if last_character != '\n':
            print >> f, '\n',
        if 'xres' not in globals():
            print >> f, 'xres', screen_width
        if 'yres' not in globals():
            print >> f, 'yres', screen_height
        f.close()
        import os
        os.spawnl(os.P_NOWAIT, 'ika.exe')
        ika.Exit()
