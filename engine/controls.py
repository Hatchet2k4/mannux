#!/usr/bin/env python

import ika


# Just display strings now.
up_key = 'UP'
down_key = 'DOWN'
left_key = 'LEFT'
right_key = 'RIGHT'
attack_key = 'X'
jump_key = 'Z'
aim_up_key = 'D'
aim_down_key = 'C'
pause_key = 'ESCAPE'
confirm_key = 'RETURN'
cancel_key = 'ESCAPE'
usejoystick = True

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
        #TODO: Check to see if passed value is a valid button.
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
        "time",             #Integer. Ticks at last repeat.
        "type",             #String. key or joy
        "value"             #String. Display value for menu system
        )

    def __init__(self, key = None):
        self.key = key
        self.control = None
        self.type=''
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
            self.type, self.value = key.split(":", 1) #return joy or key for type, remainder of key for value
            if self.type=='joy':
                joystick, attr, self.value = self.value.split(":") #grab just the button index for value for display in controls screen.


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

class MButton: #multi button class that supports multiple buttons but acts like a single one. Modified to support one keyboard and one gamepad button each.
    def __init__(self, button=None):
        self.buttons={'key':None,'joy':None}
        self.AddButton(button)

            #self.buttons.append(button)

    def AddButton(self, button):
        if button is not None:
            if button.type=='key':
                self.buttons['key']=button
            elif button.type=='joy':
                self.buttons['joy']=button
        #self.buttons.append(button)

    def RemoveButton(self, button): #will be broken with dict.. will fix
        self.buttons.remove(button) #may need to tweak later if I ever use this...

    def Set(self, key = None):
        for b in self.buttons.itervalues():
            if b: b.Set(key)

    def Position(self):
        for b in self.buttons.itervalues(): #return position if it's more than 0.1 in deadzone... though I only use > 0.5 for now..
            if b:
                p=b.Position()
                if abs(p)>0.1:
                    return p
        return 0


    def Pressed(self):
        press=False
        for b in self.buttons.itervalues():
            if b:
                if b.Pressed(): press=True
        return press

    def Press(self):
        for b in self.buttons.itervalues():
            if b: b.Press()

    def Release(self):
        for b in self.buttons.itervalues():
            if b: b.Release()

    def Update(self):
        for b in self.buttons.itervalues():
            if b: b.Update()

#todo: pull values from save file
up = MButton(Button("key:UP"))
down = MButton(Button("key:DOWN"))
left = MButton(Button("key:LEFT"))
right = MButton(Button("key:RIGHT"))

attack = MButton(Button("key:X"))
jump = MButton(Button("key:Z"))
ability = MButton(Button("key:S"))

dash = MButton(Button("key:A")) #new buttoin, dashing, if ability is gained!

aim_up = MButton(Button("key:D"))
aim_down = MButton(Button("key:C"))

pause = MButton(Button("key:ESCAPE"))

confirm = attack #confirm and attack buttons are the same
cancel = pause # should be menu?


if len(ika.Input.joysticks) > 0 and usejoystick == True:
    try:
        #directions
        up.AddButton(Button("joy:0:reverseaxes:1"))
        down.AddButton(Button("joy:0:axes:1"))
        left.AddButton(Button("joy:0:reverseaxes:0"))
        right.AddButton(Button("joy:0:axes:0"))
        #buttons
        attack.AddButton(Button("joy:0:buttons:0"))
        jump.AddButton(Button("joy:0:buttons:1"))
        ability.AddButton(Button("joy:0:buttons:2"))
        aim_up.AddButton(Button("joy:0:buttons:4"))
        aim_down.AddButton(Button("joy:0:buttons:5"))
        pause.AddButton(Button("joy:0:buttons:9"))
        dash.AddButton(Button("joy:0:buttons:3"))
    except:
        ika.Log('Warning: Attempt to add gamepad controls failed. Continuing.')

control_list = {'up':up, 'down':down, 'left':left, 'right':right,
                'attack':attack, 'jump':jump, 'dash':dash, 'confirm':confirm, 'cancel':cancel, 'aim_up':aim_up, 'aim_down':aim_down, 'pause':pause} #maybe dash/ability button in future update


