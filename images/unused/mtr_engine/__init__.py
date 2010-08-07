#!/usr/bin/env python

import ika

import automap
import logbook
import controls
#import parser
import video
import fonts
import process

from entity import Entity
#from window import Window

from camera import Camera
#from sounds import sound
#from field import Field
from hud import HUD
from splash import Splash
#import os

import math

"""
<Hatchet> andy: what would happen if you tried to set a value other than 0 or 1 on the obstruction layer?
<andy> Probably nothing amazing.
<andy> Try it.
<Hatchet> Good. because if you could, you could just assign "groups". when you destroy a tile of value x, it'll search around for all tiles of the same value adjacent to it
<Hatchet> that would be the simplest way of pulling it off. but it would require a mapscript to place them
<MyNameIsJeff> ah, yes, use the obstruction property for linked tiles!
<Hatchet> Jeff: I'm talking about having values other than 0 or 1 in the obstruction layer :)
<Hatchet> if > 1, then search out all tiles near it that have the same value, and blow up those too!
<MyNameIsJeff> hm, yeah
<MyNameIsJeff> you could probably just link any touching tiles that have obstructions though.
<Hatchet> well, you don't want all blocks that just happen to be touching each other to be destroyed
<MyNameIsJeff> yeah
<MyNameIsJeff> doh, naruto will be done downloading in 45 minutes, might as well stay up and code
<Hatchet> also, you could even do some crazy things... like destroy tile x this frame.. tile x+1 a couple frames later... x+2 after that...
<Hatchet> so you could do things like in Zero Mission where you have that spiraling destroying block thing

"""

def CheckPoint(x, y, box):
    """Checks if a point is inside a box."""
    return x >= box[0] and x < box[0] + box[2] and y >= box[1] and y < box[1] + box[3]

def CheckBoxes(box1, box2):
    if box1[0] < box2[0] + box2[2]:
        if box1[1] < box2[1] + box2[3]:
            if box1[0] + box1[2] > box2[0]:
                if box1[1] + box1[3] > box2[1]:
                    return True
    return False



def GetClockString(hours, minutes):
    return '%02d:%02d' % (hours, minutes)

class Clock(object):
    """Simple clock to keep track of game time."""
    def __init__(self):
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.tick = ika.GetTime()

    def __str__(self):
        return GetClockString(self.hours, self.minutes)

    def Update(self):
        self.seconds += 1
        if self.seconds == 60:
            self.seconds = 0
            self.minutes += 1
            if self.minutes == 60:
                self.minutes = 0
                self.hours += 1
        self.tick = ika.GetTime()



class Music(object):
    """Music controller."""
    def __init__(self):
        self.__name = ""
        self.old_music = None
        self.__music = None
        self.inc = 0.01

    def Set(self, name, loop=True):
        pass

    def __SetLoop(self, value):
        self.__music.loop = value

    def __SetName(self, value):
        if value != self.__name:
            if self.__music is not None:
                self.old_music = self.__music

            self.__name = value
            self.__music = ika.Music("music/" + value)
            self.__music.loop = True

            if self.old_music:
                self.__music.Play()

    def __GetName(self):
        return self.__name

    def Update(self):
        if self.old_music:
            self.old_music.volume -= self.inc
            if self.old_music.volume <= 0:
                self.old_music = None
                self.__music.volume = 0
                self.__music.Play()

        elif self.__music:
            if self.__music.volume < 1:
                self.__music.volume += self.inc

    name = property(__GetName, __SetName)
    loop = property(lambda x: self.__music.loop, __SetLoop)

music = Music()



#Terrain effects
def AcidTerrain(engine, samus):
    if engine.ticks % 2:
        samus.energy -= 1

def WaterTerrain(engine, samus):
    pass

def LavaTerrain(engine, samus):
    pass

def WindTerrain(engine, samus, direction):
    pass



def LogbookFilter(entry):
    return entry[1] > 0

class GameEngine(process.Process):
    def __init__(self):
        process.Process.__init__(self)
        self.block_update = False

        self.flags = {'notloaded': 'yep'}
        self.dif_mode = "norm"
        self.cur_map = ''
        self.player = None
        # Flag to update or not.
        self.can_update = True
        # Not loading a map at this time.
        self.loading = False
        # Game clock.
        self.clock = Clock()
        # Ticks to keep clock time accurate.
        self.ticks = 0
        # Temporary Things, erased on each mapswitch.
        self.background_things = []
        self.foreground_things = []
        self.zones = []
        # Current zone.
        self.cur_zone = None
        # Permanent Things, never erased (not currently used.)
        self.permanent_things = []
        self.fields = []

        self.entities = []
        self.add_list = []
        self.kill_list = []

        # Wave Effect (infey)
        self.waveticks = 0
        self.wavewidth = 2
        self.wavespeed = 90
        self.wavecohesion = 2
        self.waveresolution = 4

        # Current secret layer.
        self.cur_secret = None
        # List of secret layers in map.
        self.secret_layers = []

        #Currently touched entity.
        self.cur_entity = None

        #Current terrain (acid, lava, water) layer.
        self.cur_terrain = None

        #try:
        #    ika.Map.Switch('amap.ika-map')
        #except ImportError:
        #    # Probably should do something here.
        #    pass
        self.automap = automap.Automap()
        self.logbook = logbook.Logbook()
        #self.automap.load_automap()
        #self.meta = ika.Map.GetMetaData()

        self.allowprompt = True #allow the save prompt to come up



    def Start(self):
        self.player = Samus(16*4, 16*4)
        self.hud = HUD()
        #self.pause = Pause()
        self.camera = Camera(self.player)
        self.camera.ResetBorders()
        self.cameratarget = self.player
        self.entities.append(self.player)
        self.started = True

    def Draw(self, arg = False):
        for thing in self.background_things:
            thing.Draw()
        for i in range(ika.Map.layercount):
            ika.Render(i)
            for ent in self.entities:
                if ent.layer == i and ent.visible:
                    ent.Draw() #draw each individual entity.. whee. :P
            if self.cur_terrain:
                if self.cur_terrain[1] == i + 1:
                    # ===================
                    # Waves Documentation
                    # ===================
                    # self.waveticks      self.ticks is <= 100 and that was limiting.
                    # self.wavewidth      width of the waves in both directions from the origin
                    # self.wavespeed      speed at which the wave wiggles
                    # self.wavecohesion   how close each quad strip is to the next one, after adding waveticks as an index to all strips. (wiggle wiggle)
                    # self.waveresolution how many pixels per quad strip.  (less == more quad strips == looks better == runs slower)
                    #
                    # cos of  (3.141.. / half of _our_ circle * normalized ratio of i * apply cohesion (less extreme waves)   + angular offset  % keep it within range * apply size of sine
                    # math.cos(math.pi / (self.wavespeed / 2) * (((float(i) / numrows * (self.wavespeed / self.wavecohesion)) + self.waveticks) % self.wavespeed))     * self.wavewidth

                    #print >> fonts.tiny(200, 20), 'WAVE SYSTEM'
                    #print >> fonts.tiny(200, 30), 'self.cur_terrain[2]:'+ str(self.cur_terrain[2])
                    #print >> fonts.tiny(200, 40), 'ika.Map.ywin:'+ str(ika.Map.ywin)
                    """
                    if ika.Map.ywin + 240 > self.cur_terrain[2]:
                        self.waveticks = (self.waveticks + 1) % self.wavespeed
                        yoffset = self.cur_terrain[2] - ika.Map.ywin    #first line of terrain in camera space
                        numrows = (240 - yoffset) / self.waveresolution #number of quad strips
                        #print >> fonts.tiny(200, 50), 'waveticks:'+ str(self.waveticks)
                        #print >> fonts.tiny(200, 60), 'yoffset:'+ str(yoffset)
                        #print >> fonts.tiny(200, 70), 'numrows:'+ str(numrows)
                        src = ika.Video.GrabImage(0, yoffset, 320, 240)
                        for i in range(numrows):
                            ika.Video.ClipBlit(src,
                                               math.cos(math.pi / (self.wavespeed / 2) * (((float(i) / numrows * (self.wavespeed /  self.wavecohesion)) + self.waveticks) % self.wavespeed)) * self.wavewidth,
                                               (240 - self.waveresolution) - (i * self.waveresolution),
                                               0, i * (self.waveresolution),
                                               319, self.waveresolution)
                        print >> fonts.tiny(200, 20), 'Rendering Wave Effect'


                    """
                    #WIPS WAVE STUFF OF VERY USEFUL TO ME IN MY WAVE STUFFNESS
                    #h = self.cur_terrain[2] - ika.Map.ywin
                    #src = ika.Video.GrabImage(0, h, 320, 240)
                    #lines = int((240 - h) / 8.0 + 0.5)
                    #for i in range(lines):
                    #    ika.Video.ClipBlit(src, math.cos(math.pi / 180 * (((i * 4 + self.ticks) % 100) * 3.6)) * 4, h + (lines - 1 - i) * 8, 0, i * 8, 320, 8)
                    #    #ika.Video.ClipBlit(src, math.cos(math.pi / 360 * (i+(self.ticks % 720))/lines*360) * 4, h + (lines - i) * 8, 0, i * 8, 320, 16)

        #Test zone data by drawing.
        for zx, zy, zw, zh, zs, zn in self.zones[self.player.layer]:
            ika.Video.DrawRect(zx - ika.Map.xwin, zy - ika.Map.ywin, zx + zw - 1 - ika.Map.xwin, zy + zh - 1 - ika.Map.ywin, ika.RGB(255, 127, 127))

        for thing in self.foreground_things:
            thing.Draw()

        if arg:
            self.hud.Draw(self.player, self.automap)

        #print >> fonts.thin(10, 10), "vy: %s" % self.player.vy

    def Update(self):
        if self.can_update:
            self.automap.Update((self.player.x + 8) / 16, (self.player.y + 16) / 16)
            self.camera.Update()
            self.hud.Update(self.player)

            #Update things. Expunge them if their Update methods return True.
            for thing in self.background_things[:]:
                if thing.Update():
                    self.background_things.remove(thing)
            for thing in self.foreground_things[:]:
                if thing.Update():
                    self.foreground_things.remove(thing)

            for ent in self.add_list:
                self.entities.append(ent)
            self.add_list = []

            for entity in self.entities:
                if entity.active:
                    entity.Update()

            for ent in self.kill_list:
                self.entities.remove(ent)
            self.kill_list = []

            for f in self.fields:
                if f.test(self.player) and not f.runnable:
                    f.fire()

            self.ticks += 1

        #Update clock.
        while self.ticks >= 100:
            self.ticks -= 100
            self.clock.Update()

    def Input(self, position, pressed):
        self.UpdateTerrain()
        self.UpdateLayers()
        self.UpdateZones()
        if "start" in pressed:
            self.Draw(False)
            subscreen.subscreen.map_image = ika.Video.GrabImage(0, 0, 320, 240)
            processor.Set(subscreen.subscreen)
        self.player.Input(position, pressed)

    def UpdateTerrain(self):
        """Updates terrain layer."""
        if self.cur_terrain:
            name, layer, h = self.cur_terrain
            #Because of the way corey has the lava/acid layers setup, we have to detect them like this.
            #If we want more complex terrain layers, we'll need to 'fill in' the terrain layers in the maps.
            if ika.Map.GetObs(0, int(self.player.y + 31) / 16, layer):
                if self.player.cur_terrain == None:
                    self.AddEntity(Splash(self.player.x, self.player.y, name.lower()))
                self.player.cur_terrain = name
                globals()[name + "Terrain"](self, self.player)
            else:
                if self.player.cur_terrain: #should include regular entities too...
                    self.AddEntity(Splash(self.player.x+self.player.vx, self.player.y, name.lower()))
                self.player.cur_terrain = None

    def UpdateLayers(self):
        if self.cur_secret is not None:
            layer, mode, ticks = self.secret_layers[self.cur_secret]
            #Check if Samus is still in this area.
            if ika.Map.GetObs(int(self.player.x + 8) / 16, int(self.player.y + 16) / 16, layer):
                if mode == 0:
                    #Fade out!
                    alpha = 255 - min((ika.GetTime() - ticks) * 127 / 20, 127)
                    ika.Map.SetLayerTint(layer, ika.RGB(255, 255, 255, alpha))
                    if alpha == 0:
                        mode = 1
                elif mode == 2:
                    #Stop and fade back in.
                    ticks += ika.GetTime() - ticks
                    mode = 0

            #Check if layer is already fading out.
            elif mode < 2:
                mode = 2
                ticks = ika.GetTime()

            else:
                #Fade in!
                alpha = 128 + min((ika.GetTime() - ticks) * 127 / 20, 127)
                ika.Map.SetLayerTint(layer, ika.RGB(255, 255, 255, alpha))
                if alpha == 255:
                    mode = 3

            self.secret_layers[self.cur_secret] = (layer, mode, ticks)

            #Erase current layer if finished fading in.
            if mode == 3:
                self.cur_secret = None

        else:
            #Attempt to get a new secret layer!
            for i, v in enumerate(self.secret_layers):
                layer, mode, ticks = v
                if ika.Map.GetObs(int(self.player.x + 8) / 16, int(self.player.y + 16) / 16, layer):
                    self.cur_secret = i
                    self.secret_layers[i] = (layer, 0, ika.GetTime())
                    self.UpdateLayers()


    def UpdateZones(self):
        x, y, w, h = int(self.player.x), int(self.player.y), int(self.player.width), int(self.player.height)

        #CRAZY MORPH BALL HACK.
        if self.player.cur_state in (self.player.MorphState,):
            y += 16

        if self.cur_zone:
            zx, zy, zw, zh, zscript, zname = self.cur_zone

            if CheckBoxes((x, y, w, h), (zx, zy, zw, zh)):
                #Call repeat.
                zscript(1)
            else:
                #Leaving zone.
                zscript(2)
                self.cur_zone = None
        else:
            #Check for zone entry.
            for zx, zy, zw, zh, zscript, zname in self.zones[self.player.layer]:
                if CheckBoxes((x, y, w, h), (zx, zy, zw, zh)):
                    #Zone entry.
                    self.cur_zone = (zx, zy, zw, zh, zscript, zname)
                    zscript(0)



    def MapSwitch(self, x, y, m, layer="Background",direction=0, fadeout=True, fadein=True, scroll=False, camera=None):
        # Save the current map.
        self.cur_map = m

        if fadeout:
            self.FadeOut(20)
        video.Clear()
        # Destroy entities.

        #BAD
        for e in self.entities[:]:
            if e is not self.player:
                e._destroy()
        self.entities = [self.player]
        self.kill_list = []
        self.add_list = []

        self.background_things = []
        self.foreground_things = []
        self.player.x = x
        self.player.y = y
        self.player.morph_trail = []

        #Load actual map, but first change CWD to maps so ika loads the tileset properly.
        #os.chdir("maps")
        ika.Map.Switch("maps/"+m)
        #os.chdir("..")

        #Grab terrain layer.
        tlayer = ika.Map.layercount - 1
        name = ika.Map.GetLayerName(tlayer)
        #Check the last layer's name to see if it's a terrain type.
        if name in ("Lava", "Acid", "Water") or name[:4] == "Wind":
            print "Terrain Detected. Type: " + name
            for i in range(ika.Map.GetLayerProperties(tlayer)[2]):
                if ika.Map.GetObs(0, i, tlayer):
                    ty = i
                    break
            self.cur_terrain = (name, tlayer, ty * 16)
        else:
            self.cur_terrain = None

        # Music check.
        meta = ika.Map.GetMetaData()
        if "music" in meta:
            globals()["music"].name = meta["music"]


        #Update automapper.
        #self.automap.EnterRoom(m)

        self.camera.ResetBorders()
        self.camera.Update()

        self.player.layer = ika.Map.FindLayerByName(layer)
        self.player.sprite.layer = self.player.layer

        #Load up entities from the saved map.
        """
        enemies = filter(EnemyEntityFilter, ika.Map.GetAllEntities())
        modules = {}
        #Iterate over enemies.
        for entity in enemies:
            #Remove 'EN_' from first of name.
            name = entity.name[3:]
            #Check if this enemy's module has already been loaded.
            if name in modules:
                module = modules[name]
            else:
                #Hasn't, so load it.
                module = getattr(__import__("engine." + name.lower()), name.lower())
                modules[name] = module

            self.AddEntity(getattr(module, name)(entity.x, entity.y))
        """
        for e in ika.Map.GetAllEntities():
            #Check the first part of the entity's label.
            type = e.name[:2]
            if type in ("DR", "PW"):
                #Determine type number.
                p = e.name[3:].find("_") + 3
                name = e.name[3:p]
                num = int(e.name[p + 1:])
            else:
                name = e.name[3:] 

            if type == "EN":
                #Load enemy.
                self.AddEntity(getattr(enemies, name)(e.x, e.y))
            elif type == "DR":
                #Load door.
                pass
            elif type == "PW":
                #Load powerup.
                if hasattr(self.player.equipment[name], "acquired"):
                    if self.player.equipment[name].acquired[num] == 0:
                        self.AddEntity(entity.Powerup(e.x, e.y, name, num))
                elif not self.player.equipment[name].obtained:
                    self.AddEntity(entity.Powerup(e.x, e.y, name))
            elif type == "PL":
                #Load platform.
                pass
            else:
                #Load generic entity.
                pass
        #Erase the old map's entities.
        ika.Map.entities.clear()


        #Module stuff.
        m = "maps/"+m
        moduleName = m[:m.rfind('.')].replace('/', '.')
        map_module = self.map_script = __import__(moduleName, globals(), locals(), [''])
        for a in dir(map):
            if a[0] != "_":
                setattr(map_module, a, getattr(map, a))

        self.ReadZones(map_module)
        self.GetSecretLayers()

        #Call Update once to set everything.
        self.Update()

        video.Clear()
        if fadein:
            self.FadeIn(20)
        processor.cur_time = ika.GetTime()

        self.allowprompt = True #changed maps, allow the save prompt to appear


    def GameOver(self):
        t = ika.GetTime()
        while True:
            self.draw()
            a = min(100, ika.GetTime() - t)
            if a == 100:
                print >> fonts.one.center(), 'G A M E  O V E R'
            video.clear(ika.RGB(10, 10, 10, a))
            ika.Video.ShowPage()
            ika.Input.Update()
            if controls.confirm.Pressed() or \
               controls.cancel.Pressed():
                break
        t = ika.GetTime()
        while True:
            self.draw()
            a = min(255, ika.GetTime() - t + 100)
            video.clear(ika.RGB(10, 10, 10, a))
            ika.Video.ShowPage()
            ika.Input.Update()
            if a == 255:
                break
        ika.Exit('')

    def ReadZones(self, mapModule):
        """Read all the zones on the map, and create fields."""
        self.cur_zone = None
        self.zones = []
        for layer in range(ika.Map.layercount):
            zones = ika.Map.GetZones(layer)
            self.zones.append([])
            for zx, zy, zw, zh, zscript in zones:
                if hasattr(mapModule, zscript):
                    self.zones[-1].append((zx, zy, zw, zh, getattr(mapModule, zscript), zscript))
                else:
                    self.zones[-1].append((zx, zy, zw, zh, None, None))

    def GetSecretLayers(self):
        """Creates a listing for all secret layers."""
        layers = []
        for l in range(ika.Map.layercount):
            if ika.Map.GetLayerProperties(l)[0][:6] == "Secret":
                layers.append([l, 0, 255])
        self.secret_layers = layers
        self.cur_secret = None

    def FadeOut(self, time=50):
        video.FadeOut(time, draw=self.Draw, draw_after=self.hud.Draw)

    def FadeIn(self, time=50):
        video.FadeIn(time, draw=self.Draw, draw_after=self.hud.Draw)

    def AddEntity(self, ent):
        self.add_list.append(ent)

    def RemoveEntity(self, ent):
        self.kill_list.append(ent)



    def SaveGame(self):
        main = parser.Node("metroid2-save")
        main.append(parser.Node("version").append(0.3))

        # Map node.
        map = parser.Node("map")
        map.append(parser.Node("file").append(self.cur_map))
        map.append(parser.Node("x").append(int(self.player.x)))
        map.append(parser.Node("y").append(int(self.player.y)))
        main.append(map)

        main.append(parser.Node("mode").append(self.dif_mode))

        #Equipment node.
        equipment_node = parser.Node("equipment")
        for name, e_name in zip(("energy", "missiles", "super_missiles", "power_bombs"), ("E-Tank", "Missiles", "Super Missiles", "Power Bombs")):
            node = parser.Node(name)
            item = self.player.equipment[e_name]
            node.append(parser.Node("current").append(item.cur))
            node.append(parser.Node("max").append(item.max))
            node.append(parser.Node("acquired").append(",".join([str(x) for x in item.acquired])))
            equipment_node.append(node)

        obtained = list()
        enabled = list()
        for name, item in self.player.equipment.items.iteritems():
            if item.obtained:
                obtained.append(name)
                if item.enabled:
                    enabled.append(name)
        equipment_node.append(parser.Node("obtained").append(",".join(obtained)))
        equipment_node.append(parser.Node("enabled").append(",".join(enabled)))
        main.append(equipment_node)

        #Save control key strings.
        control_node = parser.Node("controls")
        for name, control in zip(controls.names, controls.buttons):
            control_node.append(parser.Node(name).append(control.GetControls()))
        main.append(control_node)

        # Logbook node.
        log_node = parser.Node("logbook")
        for type in self.logbook.data:
            print type, self.logbook.data[type]
            entries = filter(lambda x: self.logbook.data[type][x][1] == True, self.logbook.data[type].keys())
            if entries:
                log_node.append(parser.Node(type).append(",".join(entries)))
            else:
                log_node.append(parser.Node(type).append("0"))
        main.append(log_node)

        # Clock node.
        clock_node = parser.Node("clock")
        clock_node.append(parser.Node("hours").append(self.clock.hours))
        clock_node.append(parser.Node("minutes").append(self.clock.minutes))
        clock_node.append(parser.Node("seconds").append(self.clock.seconds))
        main.append(clock_node)

        # Save current area string.
        main.append(parser.Node("area_name").append(self.automap.GetAreaName()))
        # Save automap data!
        automap_node = parser.Node("automap")
        for l in range(len(self.automap.data)):
            automap_node.append(parser.Node(l).append(",".join([str(x[0]) for x in self.automap.data[l][4]])))

        # Save automap overlays!
        overlays = []
        for o in self.automap.overlays:
            overlays.append("%s,%s,%s,%s" % (o[0], o[1], o[2], self.automap.overlays[o]))
        automap_node.append(parser.Node("overlays").append("|".join(overlays)))
        main.append(automap_node)

        #Uncomment this to allow compressed save files.
        #print >> open(self.filename, 'wt'), parser.Compress(str(main))
        print >> open(self.filename, 'wt'), str(main)

    def LoadGame(self, filename, d):
        self.loading = True
        self.filename = filename

        #Load up current map data.
        map_data = d["metroid2-save"]["map"].todict()
        self.cur_map = map_data["file"]
        mx = int(map_data["x"])
        my = int(map_data["y"])

        self.dif_mode = d["metroid2-save"].get("mode")

        equipment = d["metroid2-save"]["equipment"].todict()
        for name, e_name in (("energy", "E-Tank"), ("missiles", "Missiles"), ("super_missiles", "Super Missiles"), ("power_bombs", "Power Bombs")):
            item = self.player.equipment[e_name]
            node = equipment[name]
            item.max = int(node["max"])
            item.cur = int(node["current"])
            item.acquired = [int(x) for x in node["acquired"].split(",")]
        #Set obtained and enabled equipment.
        enabled = equipment["enabled"].split(",")
        for name in equipment["obtained"].split(","):
            self.player.equipment[name].obtained = 1
            if name not in enabled:
                self.player.equipment[name].enabled = False

        #Load up saved control scheme.
        saved_controls = d["metroid2-save"]["controls"].todict()
        for key in saved_controls:
            getattr(controls, key).Set(*tuple(saved_controls[key].split(",")))

        # Load up logbook data.
        logbook = d["metroid2-save"]["logbook"].todict()
        for type in logbook.keys():
            self.logbook.LoadDataString(type, logbook[type])

        # Load up clock data.
        clock = d["metroid2-save"]["clock"].todict()
        self.clock.hours = int(clock["hours"])
        self.clock.minutes = int(clock["minutes"])
        self.clock.seconds = int(clock["seconds"])

        #Load up automap data.
        automap = d["metroid2-save"]["automap"].todict()
        for i in range(1):
            saved_data = automap[str(i)].split(",")
            map_data = []
            for tile in self.automap.data[i][4]:
                if saved_data:
                    color = int(saved_data.pop(0))
                    if color == 2 and tile[2] == 1:
                        map_data.append((2, tile[1] + 126, 2))
                    else:
                        map_data.append((color, tile[1], tile[2]))
                else:
                    map_data.append(tile)
            self.automap.data[i][4] = map_data

        #Load automap overlays.
        for o in automap["overlays"].split("|"):
            x, y, l, i = o.split(",")
            self.automap.overlays[(int(x), int(y), int(l))] = int(i)

        #print self.curmap
        self.MapSwitch(mx, my, self.cur_map, fadeout=False)
        self.automap.EnterRoom(self.cur_map)
        self.loading = False
        self.allowprompt = False #just loaded, don't allow the save prompt to appear

processor = process.Processor()
engine = GameEngine()

from samus import Samus
import enemies
import map
import subscreen
