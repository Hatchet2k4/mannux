#!/usr/bin/env python

import ika

"""
[Controls]
UP
DOWN
LEFT
RIGHT

JUMP
FIRE
MISSILE_FIRE


BOOST
SPIDER_BALL
AIM_UP
AIM_DOWN

BEAM_SELECT
MISSILE_SELECT
MISSILE_HOLD


[Scheme]
Depending on scheme, some of the buttons work differently.

MISSILE_SELECT either changes type of missile (#1) or switches main firing (#2).
BEAM_SELECT either changes type of beam (#1) or switchs main weapon type (#2).
"""



# Analog deadzone.
deadzone = 0.5

raw_controls = dict()
key_names = ['BACKSPACE', 'TAB', 'CLEAR', 'RETURN', 'PAUSE', 'ESCAPE',
                'SPACE', 'EXCLAIM', 'QUOTEDBL', 'HASH', 'DOLLAR', 'AMPERSAND',
                'QUOTE', 'LEFTPAREN', 'RIGHTPAREN', 'ASTERISK', 'PLUS',
                'COMMA', 'MINUS', 'PERIOD', 'SLASH', '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9', 'COLON', 'SEMICOLON', 'LESS',
                'EQUALS', 'GREATER', 'QUESTION', 'AT', 'LEFTBRACKET',
                'BACKSLASH', 'RIGHTBRACKET', 'CARET', 'UNDERSCORE',
                'BACKQUOTE', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                'W', 'X', 'Y', 'Z', 'DELETE', 'KP0', 'KP1', 'KP2', 'KP3',
                'KP4', 'KP5', 'KP6', 'KP7', 'KP8', 'KP9', 'KP_PERIOD',
                'KP_DIVIDE', 'KP_MULTIPLY', 'KP_MINUS', 'KP_PLUS', 'KP_ENTER',
                'KP_EQUALS', 'UP', 'DOWN', 'RIGHT', 'LEFT', 'INSERT', 'HOME',
                'END', 'PAGEUP', 'PAGEDOWN', 'F1', 'F2', 'F3', 'F4', 'F5',
                'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
                'F15', 'NUMLOCK', 'CAPSLOCK', 'SCROLLOCK', 'RSHIFT', 'LSHIFT',
                'RCTRL', 'LCTRL', 'RALT', 'LALT', 'RMETA', 'LMETA', 'LSUPER',
                'RSUPER', 'MODE']

#Load up keyboard controls.
for key in key_names:
    raw_controls["key:" + key] = ika.Input.keyboard[key]

# joystick:
for joyIndex, joy in enumerate(ika.Input.joysticks):
    # joystick axes:
    for axisIndex, axis in enumerate(joy.axes):
        raw_controls['joy:%i:axis:%i+' % (joyIndex, axisIndex)] = axis
    for axisIndex, axis in enumerate(joy.reverseaxes):
        raw_controls['joy:%i:axis:%i-' % (joyIndex, axisIndex)] = axis

    # joystick buttons:
    for buttonIndex, button in enumerate(joy.buttons):
        raw_controls['joy:%i:buttons:%i' % (joyIndex, buttonIndex)] = button



class Button(object):
    __slots__ = (
        "controls",         #List. List of current controls.
        "onpress",          #Function. Called when button is pressed and repeated.
        "onrelease",        #Function. Called when button is released.
        "pressed"
        )

    def __init__(self, *keys):
        self.controls = {}
        for key in keys:
            self.Add(key)
        self.pressed = False

    def GetControls(self):
        keys = []
        for key in self.controls:
            keys.append(key)
        return ",".join(keys)

    def Set(self, *keys):
        self.controls = {}
        for key in keys:
            self.Add(key)

    def Add(self, key):
        if key in raw_controls:
            self.controls[key] = raw_controls[key]

    def Position(self):
        for key in self.controls:
            v = self.controls[key].Position()
            if abs(v) >= deadzone:
                break
        else:
            return 0.0
        return v

    def Pressed(self):
        p = self.Position()
        if self.pressed:
            if abs(p) < deadzone:
                self.pressed = False
            return False
        else:
            if abs(p) >= deadzone:
                self.pressed = True
                return True
            else:
                return False


#Default controls are for: WASD+numpad, arrow keys+ASDF, joystick.
#Directional buttons
up = Button("key:W", "key:UP", "joy:0:axis:1-")
down = Button("key:S", "key:DOWN","joy:0:axis:1+")
left = Button("key:A", "key:LEFT","joy:0:axis:0-")
right = Button("key:D", "key:RIGHT", "joy:0:axis:0+")

#Main functionality buttons.
jump = Button("key:KP0",   "key:PERIOD","joy:0:buttons:1")
fire = Button("key:KP4",  "key:SLASH","joy:0:buttons:0")
aim_up = Button("key:KP8", "key:L", "joy:0:buttons:4")
aim_down = Button("key:KP5", "key:SEMICOLON", "joy:0:buttons:5")
boost = Button("key:KP8", "key:L", "joy:0:buttons:4")
spider_ball = Button("key:KP5", "key:SEMICOLON", "joy:0:buttons:5")

#Item management buttons.
beam_select = Button("key:TAB", "key:QUOTE", "joy:0:buttons:2")
weapon_select = Button("key:LSHIFT", "key:RSHIFT", "joy:0:buttons:8")
missile_hold = Button("key:PLUS", "key:M", "joy:0:buttons:7")
fire_missile = Button("key:KP7", "key:COMMA", "joy:0:buttons:3")

#Classic start button.
start = Button("key:RETURN", "key:SPACE", "joy:0:buttons:9")

#Tuple of all the buttons.
buttons = (up, down, left, right, jump, fire, aim_up, aim_down, boost, spider_ball, beam_select, weapon_select, missile_hold, fire_missile, start)
names = ("up", "down", "left", "right", "jump", "fire", "aim_up", "aim_down", "boost", "spider_ball", "beam_select", "weapon_select", "missile_hold", "fire_missile", "start")

missile_style = 0
#0 = Select: change missile type, A: change beam type
#1 = Select: change weapon type, A: change current weapon's type.
