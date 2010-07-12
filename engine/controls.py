#!/usr/bin/env python

import ika


# Just display strings now.
up_key = 'UP'
down_key = 'DOWN'
left_key = 'LEFT'
right_key = 'RIGHT'
attack_key = 'X'
jump_key = 'Z'
aim_up_key = 'C'
aim_down_key = 'LSHIFT'
pause_key = 'ESCAPE'
confirm_key = 'RETURN'
cancel_key = 'ESCAPE'


# Analog deadzone.
deadzone = 0.5


controlnames = ['BACKSPACE', 'TAB', 'CLEAR', 'RETURN', 'PAUSE', 'ESCAPE',
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

def StringToControl(string):
    """Returns a control object based on the passed control string."""
    if not string:
        return None
    #Split into base and value.
    base, value = string.split(":", 1)
    #Check for keyboard.
    if base == "key":
        #Check to see if value is a valid button.
        if True:
            return ika.Input.keyboard[value.upper()]
    #Must be a joystick button.
    elif base == "joy":
        #Split into joystick, attr, and value.
        try:
            joystick, attr, index = value.split(":")
            joystick = int(joystick)
            index = int(index)
        except:
            return None
        else:
            #Check to see if joystick number is valid.
            if len(ika.Input.joysticks) > joystick:
                #Check to see if joystick object has attr.
                if hasattr(ika.Input.joysticks[joystick], attr):
                    #Check to see if index is a valid index.
                    if len(getattr(ika.Input.joysticks[joystick], attr)) > index:
                        #Everything seems good, so return the control.
                        return getattr(ika.Input.joysticks[joystick], attr)[index]
            return None

class Button:
    __slots__ = (
        "key",              #String. Name of current control.
        "control",          #Control. Current set control.
        "first_delay",      #Integer. Tick delay for first repeat.
        "repeat_delay", #Integet. Tick delay for subsequent repeats.
        "pressed",          #Integer. Button press state (0 = unpressed, 1 = pressed, 2 = repeating).
        "onpress",          #Function. Called when button is pressed and repeated.
        "onrelease",        #Function. Called when button is released.
        "time"              #Integer. Ticks at last repeat.
        )

    def __init__(self, key = None):
        self.key = key
        self.control = None
        if key:
            self.Set(key)
        self.first_delay = 25
        self.repeat_delay = 9
        self.pressed = 0
        self.onpress = None
        self.onrelease = None

    def Set(self, key = None):
        if self.control:
            self.control.onpress = None
            self.control.onunpress = None
        if key:
            control = StringToControl(key)
            if control:
                control.onpress = self.Press
                control.onunpress = self.Release
            self.key = key
            self.control = control

    def Position(self):
        if self.control:
            return self.control.Position()
        else:
            return 0

    def Pressed(self):
        p = self.Position()
        if self.pressed:
            if p < deadzone:
                self.pressed = 0
            return False
        else:
            if p >= deadzone:
                self.pressed = 1
                return True
            else:
                return False

    def Press(self):
        self.pressed = 1
        if self.onpress:
            self.onpress()

    def Release(self):
        self.pressed = 0
        if self.onrelease:
            self.onrelease()

    def Update(self):
        if self.Pressed():
            self.Press()
            self.time = ika.GetTime()
        elif self.pressed:
            if self.pressed == 1:
                if self.time + self.first_delay <= ika.GetTime():
                    self.Press()
                    self.pressed = 2
                    self.time = ika.GetTime()
            elif self.time + self.repeat_delay <= ika.GetTime():
                self.Press()
                self.time = ika.GetTime()
        else:
            self.Release()

usejoystick = False

if len(ika.Input.joysticks) > 0 and usejoystick == True:
    up = Button("joy:0:reverseaxes:1")
    down = Button("joy:0:axes:1")
    left = Button("joy:0:reverseaxes:0")
    right = Button("joy:0:axes:0")
    attack = Button("joy:0:buttons:3")
    jump = Button("joy:0:buttons:2")
    confirm = Button("joy:0:buttons:2")
    cancel =Button("joy:0:buttons:1")
    aim_up = Button("joy:0:buttons:6")
    aim_down = Button("joy:0:buttons:7")
    pause = Button("joy:0:buttons:5")
else:

    up = Button("key:UP")
    down = Button("key:DOWN")
    left = Button("key:LEFT")
    right = Button("key:RIGHT")
    attack = Button("key:X")
    jump = Button("key:Z")
    confirm = Button("key:X")
    cancel =Button("key:ESCAPE")
    aim_up = Button("key:D")
    aim_down = Button("key:C")
    pause = Button("key:ESCAPE")


