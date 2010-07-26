import ika
import color
import controls
import engine
import fonts
import parser
import riptiles
import rotateblit
import window

import math

#Try to import the os module for file deletion.
try:
    import os
except:
    os = False

from hud import DrawEnergy


def ProcessStarted(p):
    return not p.started

#Functions for filter calls for input processing.
def ControlPosition(c):
    return abs(c.Position()) >= controls.deadzone

def ControlPressed(c):
    return c.Pressed()



class Processor(object):
    """Processor class. Big Daddy that runs all the other pieces of the game. Goes through a list of processes, calling their Render, Update, and Input methods."""

    def __init__(self):
        self.processes = ()
        self.new_processes = None
        self.position = ()
        self.pressed = ()
        self.cur_time = 0
        self.running = False
        self.dstimer = 0

    def __iadd__(self, process):
        if self.new_processes:
            self.new_processes = self.new_processes + (process, )
        else:
            self.new_processes = self.processes + (process, )
        return self

    def __isub__(self, process):
        new_processes = list()

        #Grab a different tuple depending on pending processes.
        if self.new_processes:
            processes = self.new_processes
        else:
            processes = self.processes

        for p in processes:
            if p is not process:
                new_processes.append(p)

        self.new_processes = tuple(new_processes)
        return self

    def __contains__(self, process):
        return process in self.processes

    def Set(self, *processes):
        print "Set processes: " + str(processes)
        self.new_processes = processes

    def Run(self):
        """Main processing loop."""
        self.running = True
        self.cur_time = ika.GetTime()

        while self.running:
            ika.Input.Update()
            while ika.GetTime() - self.cur_time > 0:
                #Update music and sounds.
                engine.music.Update()

                #Update input.
                if self.processes: #only last process gets input.
                    position = []
                    pressed = []
                    for name, button in zip(controls.names, controls.buttons):
                        if button.Position() > controls.deadzone:
                            position.append(name)
                        if button.Pressed():
                            pressed.append(name)
                    self.position = tuple(position)
                    self.pressed = tuple(pressed)
                    self.processes[-1].Input(self.position, self.pressed)

                #Update processes.
                for p in self.processes:
                    p.Update()
                    #fucking block_update breaks shit godamnit fuck fuck.
                    #also!
                    #engine.processor -= self
                    #engine.processor += SaveAnim()
                    #doesn't work like it should when updates are blocked. figure out why when it's NOT 5:30AM.
                    #if p.block_update: #If process blocks further updates, break here.
                    #    break

                #slowmo!
                #ika.Delay(1)
                #self.cur_time += 1
                self.cur_time += 1

            #Draw all processes.
            for p in self.processes:
                p.Draw(True)
                #if p.block_render: #If process blocks further renders, break here.
                #    break

            ### hacky hacky hacky hacky hacky hacky ###
            self.dstimer = self.dstimer + 1
            if self.dstimer >= 720:
                self.dstimer = 0
            #
            """
            src = ika.Video.GrabImage(0, 0, 320, 240)
            ika.Video.DrawRect(0, 0, 320, 240, ika.RGB(0, 0, 0), 1)
            for i in range(15):
                ika.Video.ClipBlit(src, math.cos(math.pi / 360 * (i+self.dstimer)/15*360) * 16, (14 - i) * 16, 0, i * 16, 320, 16)
                #ika.Video.ClipBlit(src, math.cos(math.pi / 360 * (i+self.dstimer)/15*360) * 16, 0, 0, (i*16), 320, (i + 1) * 16)
            ### hacky hacky hacky hacky hacky hacky ###
            """

            fonts.bold.Print(0, 220, "FPS: %s" % ika.GetFrameRate())
            #Show the drawing.
            ika.Video.ShowPage()

            #Check for a new process listing. If so, change the current list to the new one.
            if self.new_processes:
                self.processes = self.new_processes

                #Call Start methods if needed.
                for p in filter(ProcessStarted, self.processes):
                    p.Start()

                self.new_processes = None





class Process(object):
    """Base class of processes. A process is an object that is placed onto the process list."""
    __slots__ = (
        "block_render",     #Boolean. If True, none of the lower objects are rendered.
        "block_update",     #Boolean. If True, none of the lower objects are updated.
        "ticks",            #Integer. Ticks.
        "started"           #Boolean. If False, Process.Start needs to be called.
        )

    def __init__(self):
        self.block_render = False
        self.block_update = True
        self.ticks = 0
        self.started = False


    def Start(self):
        self.started = True

    def Draw(self, var):
        """Called for all objects in the process list."""
        pass

    def Update(self):
        """Called in the limiter area of Processor."""
        self.ticks += 1

    def Input(self, position, pressed):
        """Only the top process has this method called."""
        pass



class Disclaimer(Process):
    """Samus and all related intellectual properties
pertaining to the Metroid franchise belong solely to
Nintendo and ONLY Nintendo. We do not claim ownership
of said properties.


Metroid Extinction is a derivative work of the original
Metroid 2: Return of Samus. It is solely a fan's
expression of the original ideas. It was not created
for personal gain or profit and should NOT be considered
an official Nintendo creation.
"""
    def Draw(self, arg):
        if self.ticks < 100:
            text_color = color.ColorCode(ika.RGB(255, 255, 255, self.ticks * 255 / 100))
        elif self.ticks > 1100:
            text_color = color.ColorCode(ika.RGB(255, 255, 255, 255 - (self.ticks - 1100) * 255 / 100))
        else:
            text_color = ""

        #Print an assload of text.
        fonts.tiny.CenterPrint(160, 60, text_color + self.__doc__)

    def Update(self):
        self.ticks += 1
        if self.ticks == 1200:
            engine.processor.Set(title_screen)

disclaimer = Disclaimer()

class TitleScreen(Process):
    def __init__(self):
        Process.__init__(self)
        self.block_render = True

        self.images = {"pixelgasm": ika.Image("img/title_screen/pixelgasm.png"), "logo": ika.Image("img/title_screen/logo2.png"), "metroids": ika.Image("img/title_screen/metroids.png"), "background": ika.Image("img/title_screen/background.png")}
        self.state = 0#0 = background scroll, 1 = no scroll

    def Start(self):
        print "Start titlescreen"
        self.started = True

    def Draw(self, arg):
        if self.state == 0:
            if self.ticks < 600:
                ika.Video.TintBlit(self.images["background"], 0, -self.ticks * 360 / 1000, ika.RGB(255, 255, 255, 128))
            else:
                ika.Video.TintBlit(self.images["background"], 0, -self.ticks * 360 / 1000, ika.RGB(255, 255, 255, 128 + (self.ticks - 600) * 127 / 400))

            #Draw pixelgasm logo.
            if self.ticks < 200:
                ika.Video.TintBlit(self.images["pixelgasm"], 70, 88, ika.RGB(255, 255, 255, self.ticks * 255 / 200))
            elif self.ticks < 500:
                self.images["pixelgasm"].Blit(70, 88)
            elif self.ticks < 700:
                ika.Video.TintBlit(self.images["pixelgasm"], 70, 88, ika.RGB(255, 255, 255, 255 - (self.ticks - 500) * 255 / 200))

        else:
            self.images["background"].Blit(0, - 360)

            #Draw game logo.
            if self.ticks < 200:
                ika.Video.TintBlit(self.images["metroids"], 3, 61, ika.RGB(255, 255, 255, self.ticks * 255 / 200))
            else:
                self.images["metroids"].Blit(3, 61)

            if self.ticks > 100 and self.ticks < 200:
                ika.Video.TintBlit(self.images["logo"], 0, 30, ika.RGB(255, 255, 255, (self.ticks - 100) * 255 / 100))

            elif self.ticks >= 200:
                self.images["logo"].Blit(0, 30)


    def Update(self):
        self.ticks += 1
        if self.ticks == 1000 and self.state == 0:
            self.ticks = 0
            self.state += 1

    def Input(self, position, pressed):
        if "start" in pressed:
            if self.state == 0:
                self.state = 1
                self.ticks = 0
            elif self.state == 1:
                engine.processor.Set(file_menu)

title_screen = TitleScreen()



def EmptyFile(item):
    return item is not None

class FileMenu(Process):
    def __init__(self):
        Process.__init__(self)
        self.selection = 0      #0-2 are for files, 3 for Erase, 4 for Copy, and 5 for Options.
        self.mode = 0           #0 base selection, 1 erase, 2 copy
        self.files = []
        self.windows = []       #Window listing.

        #Cursor images for each suit.
        self.cursor_images = dict()
        for name in ("power", "varia", "gravity", "aero"):
            self.cursor_images[name] = riptiles.RipTiles("sprites/morphball-%s.png" % name, 18, 18, 4, 12)
        #((5, 20), (6, 20), (7, 20), (6, 20)))

        #Images.
        self.images = {}
        self.images["extra_cursor"] = ika.Image("img/file_menu/extra_cursor.png")
        self.images["background"] = ika.Image("img/file_menu/background.png")
        self.images["border"] = ika.Image("img/file_menu/border.png")
        self.images["slots"] = ((ika.Image("img/file_menu/slot1_norm.png"), ika.Image("img/file_menu/slot1_hard.png")), (ika.Image("img/file_menu/slot2_norm.png"), ika.Image("img/file_menu/slot2_hard.png")), (ika.Image("img/file_menu/slot3_norm.png"), ika.Image("img/file_menu/slot3_hard.png")), (ika.Image("img/file_menu/slot4_norm.png"), ika.Image("img/file_menu/slot4_hard.png")))

    def DrawCursor(self, x, y, suit):
        #self.cursor.Draw(x, y)
        self.cursor_images[suit][2].Blit(x, y)
        rotateblit.RotateBlit(self.cursor_images[suit][5], x + 9, y + 9, (self.ticks % 80) * 360 / 80)
        #self.cursor[1].Draw(x+9, y+9, angle=(self.ticks % 80) * 360 / 80)

    def Load(self):
        """Load up all the save files in the save folder, minus the default.save."""
        self.files = []
        for name in ("save/file1.save", "save/file2.save", "save/file3.save", "save/file4.save"):
            try:
                f = parser.load(name)
            except IOError:
                self.files.append(None)
            else:
                energy = f["metroid2-save"]["equipment"]["energy"].todict()
                clock = f["metroid2-save"]["clock"].todict()
                self.files.append({"mode": f["metroid2-save"].get("mode"), "energy": int(energy["current"]), "max_energy": int(energy["max"]), "hours": int(clock["hours"]), "minutes": int(clock["minutes"]), "area": f["metroid2-save"].get("area_name"), "file": f})
                #Determine which suit graphic to use for cursor.
                obtained = f["metroid2-save"]["equipment"].todict()["obtained"]
                if "Aero Suit" in obtained:
                    self.files[-1]["suit"] = "aero"
                elif "Gravity Suit" in obtained:
                    self.files[-1]["suit"] = "gravity"
                elif "Varia Suit" in obtained:
                    self.files[-1]["suit"] = "varia"
                else:
                    self.files[-1]["suit"] = "power"

    def Start(self):
        self.Load()
        engine.music.name = "load_stereo.ogg"
        #self.music.Play() ## infey
        self.started = True

    def Draw(self, arg):
        self.images["background"].Blit(0, 0)
        self.images["border"].Blit(3, 0)

        for f, save in enumerate(self.files):
            #Draw file info.
            h = f * 36
            if save is None:
                fonts.bold.Print(68, 68 + h, "Empty")
                self.images["slots"][f][0].Blit(38, 65 + h)
            else:
                if save["mode"] == "hard":
                    self.images["slots"][f][1].Blit(38, 65 + h)
                else:
                    self.images["slots"][f][0].Blit(38, 65 + h)
                DrawEnergy(68, 64 + h, save["energy"], save["max_energy"])

                # Display clock.
                fonts.bold.Print(192, 64 + h, engine.GetClockString(save["hours"], save["minutes"]))

                # Display saved area.
                area = save["area"]
                if " " in area:
                    area = area.split(" ")
                    fonts.bold.RightPrint(290, 64 + h, area[0] + "\n" + area[1])
                else:
                    fonts.bold.RightPrint(290, 66 + h, area)

        #Draw selection cursor.
        if self.files[self.selection]:
            suit = self.files[self.selection]["suit"]
        else:
            suit = "power"
        self.DrawCursor(20, 63 + self.selection * 36, suit)


        #Draw windows.
        for w in self.windows:
            pass

    def Input(self, position, pressed):
        if self.mode == 0:
            if "down" in pressed:
                if self.selection < 3:
                    self.selection += 1
            elif "up" in pressed:
                if self.selection > 0:
                    self.selection -= 1
            elif "start" in pressed or "fire" in pressed:
                #Open up file.
                engine.engine.Start()
                engine.processor.processes = (engine.engine,)
                if self.files[self.selection] is not None:
                    engine.engine.LoadGame("save/file%s.save" % (self.selection + 1), self.files[self.selection]["file"])
                else:
                    engine.engine.player.energy = 59
                    engine.engine.player.equipment.Obtain("Power Suit")
                    engine.engine.player.equipment.Obtain("Power Beam")
                    engine.engine.player.equipment.Obtain("Morph Ball")
                    engine.engine.filename = "save/file" + str(self.selection + 1) + ".save"

                    #Add a logbook entry, so it saves properly.
                    engine.engine.logbook.Obtain("locations", "SR388 Underworld", False)

                    engine.engine.MapSwitch(0, 0, "000.ika-map", fadeout=False)
                    engine.engine.automap.EnterRoom("000.ika-map")
                engine.engine.player.SetSuit()
                #engine.music.name = "met2_b.ogg"


        elif self.mode == 1 or self.mode == 2:
            if "down" in pressed:
                s = self.selection + 1
                while s < 3:
                    if self.files[s]:
                        self.selection = s
                        break
                    else:
                        s += 1
            elif "up" in pressed:
                s = self.selection - 1
                while s > -1:
                    if self.files[s]:
                        self.selection = s
                        break
                    else:
                        s -= 1
            elif "a" in pressed:
                #Go back to main mode.
                if self.mode == 1:
                    self.selection = 3
                else:
                    self.selection = 4
                self.mode = 0
            elif "start" in pressed or "b" in pressed:
                pass

file_menu = FileMenu()


class SaveAnim(Process):
    def __init__(self):
        Process.__init__(self)

    def Start(self):

        self.started = True


    def Draw(self, m):
        fonts.tiny.Print(20, 140, str(self.ticks))

    def Update(self):
        from savelight import SaveFlash
        if self.ticks == 0 or self.ticks == 64 or self.ticks == 128:
            x = engine.engine.cur_zone[0]-8
            y = engine.engine.cur_zone[1]-16
            engine.engine.AddEntity(SaveFlash(x, y))
        self.ticks += 1

        if self.ticks>240:
            engine.processor -= self
            engine.processor.Set(engine.engine, Message("Save completed!"))
            engine.engine.player.stand_straight = False
            engine.engine.allowprompt = False



#Save message.
class SaveMessage(Process):
    def __init__(self):
        Process.__init__(self)
        self.selection = 0 #0 = yes, 1 = no

    def Start(self):
        self.started = True
        self.selection = 0
        self.saveanim = None


    def Draw(self, m):
        ika.Video.DrawRect(32, 120, 288, 152, ika.RGB(0, 0, 0, 127), 1)
        fonts.tiny.CenterPrint(160, 130, "Would you like to save your game?")
        if self.selection == 0:
            fonts.tiny.Print(100, 140, "Yes")
            fonts.tiny.Print(180, 140, color.ColorCode(color.trans_white) + "No")
        else:
            fonts.tiny.Print(100, 140, color.ColorCode(color.trans_white) + "Yes")
            fonts.tiny.Print(180, 140, "No")

        fonts.tiny.Print(20, 40, str(self.ticks))

    def Input(self, position, pressed):

        if "right" in pressed:
            self.selection = min(self.selection + 1, 1)
        elif "left" in pressed:
            self.selection = max(self.selection - 1, 0)

        if "jump" in pressed or "start" in pressed:
            if self.selection == 0:
                engine.engine.SaveGame()
                #Show funny save flash thing.
                engine.engine.player.stand_straight = True
                engine.engine.player.Input((), ())
                engine.engine.player.x = engine.engine.cur_zone[0]
                engine.processor -= self
                engine.processor += SaveAnim()

            else:
                engine.processor.Set(engine.engine)
                engine.engine.allowprompt = False

save_message = SaveMessage()

#Message box.
class Message(Process):
    def __init__(self, message):
        Process.__init__(self)
        self.block_update = False
        self.message = message

    def Draw(self, m):
        ika.Video.DrawRect(32, 32, 288, 64, ika.RGB(0, 0, 0), 1)
        print >> fonts.tiny(160, 32, "center"), self.message

    def Input(self, position, pressed):
        if "jump" in pressed:
            #Close window.
            engine.processor -= self

#Powerup acquired process.
class PowerupMessage(Process):
    def __init__(self, item, message, item_id = None):
        Process.__init__(self)

        self.item = item
        self.message = message
        self.item_id = item_id

    def Start(self):
        engine.engine.can_update = False
        #Check what to play: item fanfare, or collection sound.
        if hasattr(engine.engine.player.equipment[self.item], "acquired"):
            if engine.engine.player.equipment[self.item].max > 0:
                #Play just a sound.
                pass

            else:
                #Play new item fanfare.
                engine.music.name = "item_fanfare.ogg"
                engine.music.loop = False
        else:
            #Play new item fanfare.
            engine.music.name = "item_fanfare.ogg"
            engine.music.loop = False

        self.started = True

    def Draw(self, m):
        ika.Video.DrawRect(32, 32, 288, 64, ika.RGB(0, 0, 0), 1)
        fonts.tiny.CenterPrint(160, 32, self.item)
        fonts.tiny.Print(32, 44, self.message)

    def Input(self, position, pressed):
        print self.ticks
        if self.ticks >= 600 and "jump" in pressed:
            engine.music.name = "met2_b.ogg"
            engine.processor -= self
            engine.engine.player.equipment.Obtain(self.item, self.item_id)
            engine.engine.can_update = True
