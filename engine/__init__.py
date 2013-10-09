#!/usr/bin/env python

import config
config.init()

import ika
import automap
import controls
import parser
import video
import fonts
import fog


from entity import Entity
from window import Window

from camera import Camera
from sounds import sound
from field import Field


from splash import Splash #should move later...


class Message(object):
    def __init__(self, text, duration):
        self.text = text
        self.duration = duration

class Engine(object):

    def __init__(self):
        self.music = None
        ika.SetCaption('%s - Mannux' % ika.GetCaption())
        video.clear()
        print >> fonts.big.center(), 'Loading . . .'
        ika.Video.ShowPage()
        self.window = Window()
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.ticks = 0
        self.time = ''
        self.flags = {'notloaded': True, 'shiplanded': False}
        self.curmap = ''
        # Not loading a map at this time.
        self.loading = False
        # Temporary Things, erased on each mapswitch.
        self.background_things = []
        self.foreground_things = []
        # Permanent Things, never erased (not currently used.)
        self.permanent_things = []
        self.fields = []

        self.entities = []
        self.effects = []
        self.add_list = []
        self.kill_list = []
        self.addeffect_list = []
        self.killeffect_list = []


        self.messages = []

        # Current layer.
        self.cur_secret = None
        self.cur_terrain = None #for splash/water effects, mostly
        # List of layers in map.
        self.secret_layers = []
        self.terrain_layers = []

        try:
            ika.Map.Switch('amap.ika-map')
        except ImportError:
            # Probably should do something here.
            pass
        self.automap = automap.AutoMap()
        self.automap.load_automap()
        #self.meta = ika.Map.GetMetaData()
        # DO NOT PUT RUN HERE
        # If run is put here, the engine object is never returned.

        self.lights=True #lights activated
        self.lightcanvas=ika.Canvas(320,240)
        self.lightcanvas.Clear(ika.RGB(255,255,255,128))
        self.circleimage = ika.Image('%s/circle_gradient.png'  % config.image_path)
        self.bigcircleimage = ika.Image('%s/circle320.png' % config.image_path)
        self.smallcircle = ika.Image('%s/circle32.png' % config.image_path)


    def GetFlag(self, key):
        return self.flags.get(key, False)

    def SetFlag(self, key, value):
        self.flags[key] = value

    def GetLayers(self):
        """Creates a listing for all secret/terrain layers."""
        s_layers = [] #secret
        t_layers = [] #terrain
        lname = ''



        for l in range(ika.Map.layercount):
            #complex line for grabbing all layers that start with the word secret :)
            lname = ika.Map.GetLayerName(l)
            if lname[:6].lower() == "secret":
                s_layers.append([l, 0, 255])
            elif lname in ("Lava", "Acid", "Water"): #add more later, possibly..
                #get the layer height and scroll through it to find where it starts
                #terrain layers
                #for i in range(ika.Map.GetLayerProperties(l)[2]):
                #    if ika.Map.GetTile(0, i, l): #find where the layer actually begins... may need to change later
                t_layers.append( ( lname, l ) ) #name, layer #
                print "Terrain Detected. Type: " + lname + "  "+str(l)
                #break





        self.secret_layers = s_layers
        self.terrain_layers = t_layers
        self.cur_secret = None
        self.cur_terrain = None


         #       #Grab terrain layer.
         #      tlayer = ika.Map.layercount - 1
         #       name = ika.Map.GetLayerName(tlayer)
         #       #Check the last layer's name to see if it's a terrain type.
         #       if name in ("Lava", "Acid", "Water") or name[:4] == "Wind":
         #           print "Terrain Detected. Type: " + name
         #           for i in range(ika.Map.GetLayerProperties(tlayer)[2]):
         #               if ika.Map.GetObs(0, i, tlayer):
         #                   ty = i
         #                   break
         #           self.cur_terrain = (name, tlayer, ty * 16)
         #       else:
         #   self.cur_terrain = None


    def initialize(self):
        self.player = Tabby(0, 0)
        self.hud = Hud()
        self.pause = Pause()
        self.title = TitleScreen()
        self.camera = Camera(self.player.sprite)
        self.cameratarget = self.player
        self.entities.append(self.player) #player should always be the first in the list

    def newgame(self):
        self.load('%s/default.save' % config.save_path)

    def loadgame(self, f='%s/savegame.save' % config.save_path):
        try:
            #sf = file(f)
            #close(f)
            self.load(f)
        except:
            self.newgame()


    def Run(self):
        #self.title.show()
        self.newgame() #only comment out if not showing title
        self.hud.resize()
        self.automap.update_room()
        time = ika.GetTime()
        done = False
        self.music = ika.Music('%s/00_-_zaril_-_close_to_the_core.xm' %
                               config.music_path)
        self.music.loop = True
        self.music.Play()
        while not done:
            t = ika.GetTime()
            while t > time:
                # Uncomment for slow motion.
                #ika.Delay(2)
                self.tick()
                time += 1
            time = ika.GetTime()
            self.update_time()
            self.camera.update()
            self.draw()
            #print >> fonts.one(0, 40), 'FPS:', ika.GetFrameRate()

            #for i, e in enumerate(self.entities):
            #    print >> fonts.one(0, 50 + 10*i), 'sprite', e.sprite

            ika.Input.Update()
            if controls.pause.Pressed():
                self.pause.menu()
                ika.Input.Unpress()
                # Make sure the engine doesn't have to play 'catchup'.
                time = ika.GetTime()
            #screenshot key
            if False:  #controls.confirm.Pressed(): #screenshot
                #self.text('This is a textbox.')
                ika.Input.Unpress()
                time = ika.GetTime()
                c = ika.Video.GrabCanvas(0, 0, ika.Video.xres, ika.Video.yres)
                c2 = ika.Image(c)
                c2.Blit(0, 0)
                c.Save('blah1.png')
            ika.Video.ShowPage()

    def draw(self):
        for thing in self.background_things:
            thing.draw()
        #if self.background:
        #    ika.Video.Blit(self.background, 0, 0)
        for i in range(ika.Map.layercount):
            ika.Map.Render(i)
            for ent in self.entities:
                if ent.layer == i and ent.visible:
                    ent.draw()
                    #inefficient as it loops through each entity multiple times depending on # of layers, but works for now...
                    #if performance becomes an issue will refactor to multiple lists per layer.
            for eff in self.effects:
                if eff.layer == i and eff.visible:
                    eff.draw() #for special effects, may behave differntly for entities so putting them here instead.

        #video.clear(ika.RGB(0, 255, 0))
        #ika.Map.Render()
        for thing in self.foreground_things:
            try:
                thing.draw()
            except AttributeError:
                # This is retarded.
                pass

        if self.lights: #lightmap check
            #self.lightcanvas.Clear(ika.RGB(255,0,255,128))
            p=self.player
            x=int(p.x + p.width/2 - ika.Map.xwin) - 320
            y=int(p.y + p.height/2 - ika.Map.ywin) - 240

            #print >> fonts.tiny(0,80), 'x: '+str(x)
            #print >> fonts.tiny(0,90), 'y: '+str(y)

            #self.bigcircleimage.Blit(self.lightcanvas, 0, -40, 4)
            #self.lightcanvas.Blit(self.image, x , y, ika.RGB(255, 255, 255, self.opacity), ika.SubtractBlend)
            #img=ika.Image(self.lightcanvas)
            ika.Video.TintBlit(self.circleimage, x,y, ika.RGB(255,255,255,192), ika.SubtractBlend)
            #ika.Video.DrawEllipse(x+160, y+160, 50, 40, ika.RGB(100,100,100,128), 1, ika.AddBlend)
            #ika.Video.TintBlit(img, 0 , 0, ika.RGB(255, 255, 255, 128))

            #ika.Video.TintBlit(img, 0 , 0)

        self.hud.draw()

        x = 10
        y = 230
        for m in self.messages:
            print >> fonts.one(x, y), m.text
            y -= 10


        #font.Print(0, 80, self.meta['testing'])
        #font.Print(240, 0, 'xwin: %s' % ika.Map.xwin)
        #font.Print(240, 10, 'ywin: %s' % ika.Map.ywin)
        #font.Print(240, 30, 'vx: %s' % self.player.vx)
        #font.Print(240, 40, 'floor: %s' % self.player.floor)
        #font.Print(10, 60, 'x: %s' % self.player.x)
        #font.Print(10, 70, 'y: %s' % self.player.y)
        #font.Print(10, 80, 'slope: %s' % self.player.in_slope)
        #font.Print(10, 90, 'floor: %s' % self.player.floor)
        #font.Print(10, 100, 'jumps: %s' % self.player.jump_count)
        #font.Print(10, 70, 'vy: %s' % self.player.vy)
        #font.Print(10, 80,  self.player.msg)
        #font.Print(10, 80, str(ika.Input.joysticks[0].axes[0].Position()))
        #font.Print(10, 80, str(len(entities)))
        #x = int(self.player.x + self.player.sprite.hotwidth / 2 +
        #        self.player.vx)
        #y = int(self.player.y + self.player.sprite.hotheight - 1 +
        #        self.player.vy)
        #tx = x / 16
        #ty = y / 16
        #ika.Video.DrawPixel(x - ika.Map.xwin, y - ika.Map.ywin,
        #                    color.white)
        #ika.Video.DrawRect(tx * 16 - ika.Map.xwin, ty * 16 - ika.Map.ywin,
        #                   tx * 16 + 16 - ika.Map.xwin,
        #                   ty * 16 + 16 - ika.Map.ywin,
        #                   ika.RGB(255, 0, 0, 128), True)
        #font.Print(240, 40, str(self.player.right_wall))

    #main engine processing
    def tick(self):
        self.UpdateTerrain()

        for thing in self.background_things:
            try:
                thing.update()
            except AttributeError:
                pass
        for thing in self.foreground_things:
            try:
                thing.update()
            except AttributeError:
                pass

        for entity in self.add_list:
            self.entities.append(entity)
        self.add_list = []

        for effect in self.addeffect_list:
            self.effects.append(effect)
        self.addeffect_list = []

        for entity in self.entities:
            if entity.active:
                entity.update()

        for effect in self.effects:
            if effect.active:
                effect.update()

        for entity in self.kill_list:
            self.entities.remove(entity)
        self.kill_list = []

        for effect in self.killeffect_list:
            self.effects.remove(effect)
        self.killeffect_list = []

        for f in self.fields:
            if f.test(self.player) and not f.runnable:
                f.fire()

        mlist = []
        for m in self.messages:
            m.duration -= 1
            if m.duration <= 0:
                mlist.append(m)
        for m in mlist:
            self.messages.remove(m)

        self.ticks += 1



    def map_switch(self, x, y, m, direction=0, fadeout=True, fadein=True,
                   scroll=False):
        # Update the current map.
        self.curmap = m
        m = 'maps/%s' % m
        if fadeout:
            self.FadeOut(16)
        video.clear()
        # Destroy entities.
        for e in self.entities[:]:
            if e is not self.player:
                e._destroy()

        for e in self.effects[:]:
            e._destroy()

        self.background_things = []
        self.foreground_things = []
        self.player.x = x
        self.player.y = y
        ika.Map.Switch(m)
        self.automap.update_room()
        self.camera.reset_borders()
        self.camera.update()


        self.player.layer = ika.Map.FindLayerByName('Walls')
        self.player.sprite.layer = self.player.layer


        moduleName = m[:m.rfind('.')].replace('/', '.')
        mapModule = __import__(moduleName, globals(), locals(), [''])
        self.readZones(mapModule)

        self.GetLayers()

        #if True: #check for flag for lighting... eventually..
         #   self.foreground_things.append(fog.Darkness())
        video.clear()
        if fadein:
            self.FadeIn(16)

    def GameOver(self):
        t = ika.GetTime()
        while True:
            self.draw()
            a = min(100, ika.GetTime() - t)
            if a == 100:
                print >> fonts.big.center(), 'G A M E  O V E R'
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

    def update_time(self):
        while self.ticks >= 100:
            self.ticks -= 100
            self.seconds += 1
        while self.seconds >= 60:
            self.seconds -= 60
            self.minutes += 1
        while self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1
        self.time = '%03d:%03d:%03d' % (self.hours, self.minutes, self.seconds)

    def UpdateTerrain(self):
        #Updates terrain layer. For water effects, currently
        for l in self.terrain_layers:
            name, layer = l

            #going in
            if ika.Map.GetTile(int(self.player.x+1) / 16, int(self.player.y + 31) / 16, layer):
                if self.player.cur_terrain == None:
                    self.AddEntity(Splash(int(self.player.x - 12), int(self.player.y), name.lower(), layer))
                self.player.cur_terrain = name


                #globals()[name + "Terrain"](self, self.player)
            else: #jumping out
                if self.player.cur_terrain: #should include regular entities too...
                    self.AddEntity(Splash(int(self.player.x - 12), int(self.player.y), name.lower(), layer))
                self.player.cur_terrain = None

    #def UpdateTerrain(self):
    #
    #    if self.cur_terrain:
    #        name, l = self.cur_terrain
    #
    #        #jumping out
    #        if ika.Map.GetTile(0, int(self.player.y + 31) / 16, layer):
    #            if self.player.cur_terrain == None:
    #                self.AddEntity(Splash(self.player.x, self.player.y, name.lower(), layer=l ))
    #            self.player.cur_terrain = name
    #
    #            #globals()[name + "Terrain"](self, self.player)
    #        else: #going in
    #            if self.player.cur_terrain: #should include regular entities too...
    #                self.AddEntity(Splash(self.player.x+self.player.vx, self.player.y, name.lower()))
    #            self.player.cur_terrain = None


    def text(self, txt):
        done = 0
        state = 0
        h = 0
        arrow = ika.Image('%s/arrow.png' % config.image_path)
        lines = wrap(txt, 360, fonts.big)
        scrolling = 1
        scroll = [0] * len(lines)
        current = 0
        offset = 0
        t = ika.GetTime()
        while not done:
            ika.Map.Render()
            while t == ika.GetTime():
                pass
            for i in range(ika.GetTime() - t):
                for entity in self.entities:
                    entity.update()
                if state == 0:
                    h += 2
                if state == 1 and scrolling == 1:
                    scroll[current + offset] += 1
                if state == 2:
                    h -= 2
            t = ika.GetTime()
            if state == 0:
                if h >= 40:
                    h = 40
                    state = 1
                    self.window.resize(h * 8, h, 0)
                else:
                    self.window.resize(h * 8, h, 0)
                    self.window.draw(168 - h * 4, 200 - h / 2, 0)
            if state == 1:
                self.window.draw(8, 180, 0)
                for i in range(len(lines[offset:])):
                    print >> fonts.big(20, 190 + 12 * i), lines[i + offset][:scroll[i + offset]]
                    if scroll[current + offset] >= \
                       len(lines[current + offset]):
                        if current + offset < len(lines) - 1:
                            current += 1
                        else:
                            scrolling = 0
                    if current == 7:
                        scrolling = 0
                        # Put blinking arrow or whatever here.
                        if ika.GetTime() % 50 < 40:
                            ika.Video.Blit(arrow, 192,
                                           280 + ika.GetTime() % 50 / 10)
            if state == 2:
                if h <= 0:
                    done = True
                else:
                    self.window.resize(h * 8, h, 0)
                    self.window.draw(168 - h * 4, 200 - h / 2, 0)
            print >> fonts.one(0, 0), 'lines:', '%s'
            ika.Video.ShowPage()
            ika.Input.Update()
            if ika.Input.keyboard['RETURN'].Pressed() and state == 1 and \
               scrolling == 0:
                ika.Input.Unpress()
                if current + offset < len(lines) - 1:
                    scrolling = 1
                    offset += 7
                    current = 0
                else:
                    state = 2

    def addField(self, field):
        assert field not in self.fields
        self.fields.append(field)

    def destroyField(self, field):
        self.fields.remove(field)

    def readZones(self, mapModule):
        """Read all the zones on the map, and create fields."""
        self.fields = []
        for layer in range(ika.Map.layercount):
            zones = ika.Map.GetZones(layer)
            for x, y, w, h, script in zones:
                self.addField(Field((x, y, w, h), layer,
                              mapModule.__dict__[script], str(script)))

    def FadeOut(self, time=50):
        video.fade_out(time, draw=self.draw, draw_after=self.hud.draw)

    def FadeIn(self, time=50):
        video.fade_in(time, draw=self.draw, draw_after=self.hud.draw)

    def SavePrompt(self, heal=True):
        if heal:
            self.player.dhp = self.player.maxhp
            self.player.dmp = self.player.maxmp
        selected = 0

        while not controls.confirm.Pressed():

            self.player.update()
            self.draw()

            Window(150, 0).draw(52, 60)
            print >> fonts.one(68, 80), 'Do you want to save?'

            x = 100
            y = 98
            for i, option in enumerate(['Yes', 'No']):
                f = [fonts.five, fonts.three][i == selected]
                print >> f(x, y), option
                x += 100


            self.hud.draw()
            #ika.Video.DrawRect(80 + 110 * selected, 92, 120 + 110 * selected,
            #                   108, ika.RGB(128, 192, 128))
            ika.Video.ShowPage()
            ika.Input.Update()
            if controls.left.Pressed():
                sound.play('Menu')
                selected -= 1
                if selected < 0:
                    selected = 1
            if controls.right.Pressed():
                sound.play('Menu')
                selected += 1
                if selected > 1:
                    selected = 0

        #for c in controls.control_list:
        #    c.Release()


        if selected == 0:
            self.Save()
            return True

        return False







    #saving incomplete, does not save map data
    def Save(self, filename='%s/savegame.save' % config.save_path):
        flagnode = parser.Node('flags')
        for key, value in self.flags.iteritems():
           flagnode.append(parser.Node(key).append(value))


        #mapnode = parser.Node('amap')
        #for n in self.automap.amap:
        #    mapnode.append(n)

        foo = (parser.Node('mannux-save')
               .append(parser.Node('version').append(1))
               .append(parser.Node('map').append(self.curmap))
               .append(parser.Node('hp').append(self.player.maxhp)) #always save with full health
               .append(parser.Node('maxhp').append(self.player.maxhp))
               .append(parser.Node('mp').append(self.player.maxmp))
               .append(parser.Node('maxmp').append(self.player.maxmp))
               .append(flagnode)
               .append(parser.Node('amap1').append(str(self.automap.amap)))


               )


        print >> open(filename, 'wt'), foo



        self.messages.append(Message("Game saved", 300))

    #for some reason misses some flags..
    def load(self, filename='%s/default.save' % config.save_path):
        self.loading = True
        d = parser.load(filename)
        self.curmap = d['mannux-save'].get('map')
        self.player.hp = int(d['mannux-save'].get('hp'))
        self.player.maxhp = int(d['mannux-save'].get('maxhp'))
        self.player.mp = int(d['mannux-save'].get('mp'))
        self.player.maxmp = int(d['mannux-save'].get('maxmp'))
        self.flags = d['mannux-save']['flags'].todict()

        a = d['mannux-save'].get('amap1')


        print 'testing: '
        print d['mannux-save'].get('map')
        print d['mannux-save'].get('amap1')

        #print a


        #if 'amap1' in d['mannux-save']:
        #    print 'yes!'
        #    a = d['mannux-save']['amap1']
        #    b = ''
        #    for c in a:
        #        b+=str(c)
        #    print "Load test:"
        #
        #    test = eval(b)
        #    self.automap.amap = test
        #else:
        #    print 'wtf!'



        #b = d['mannux-save']['amap']

        #self.automap.amap = []
        #i=0
        #for y in range(50): #need to change so it's not just 50x50...
        #    for x in range(50):
                #self.automap.amap.append(a[i])

        #for i in a:
        #    ika.Log('i: '+str(i))
        #        i+=1


            #for i in d['mannux-save']['amap']:
            #    self.automap.amap.append(i)


        self.hud.resize()



        #print self.curmap
        self.map_switch(0, 0, self.curmap, fadeout=False)
        self.loading = False

    def AddEntity(self, ent):
        self.add_list.append(ent)

    def RemoveEntity(self, ent):
        self.kill_list.append(ent)

    def AddEffect(self, effect):
        self.addeffect_list.append(effect)

    def RemoveEffect(self, effect):
        self.killeffect_list.append(effect)

def wrap(text, width, font):
    start = 0
    end = 1
    lastspace = 0
    lines = []
    while end < len(text):
        if text[end] in (' ', '-'):
            lastspace = end + 1
        if text[end] == '\n':
            lines.append(text[start:end])
            start = end
        if font.string_width(text[start:end]) >= width:
            lines.append(text[start:lastspace])
            start = lastspace
        end += 1
    lines.append(text[start:end])
    return lines


def detect_in_y_coordinates(entity):
    for e in engine.entities:
        if entity is not e:
            if entity.y + entity.sprite.hotheight > e.y and \
               entity.y < e.y + e.sprite.hotheight:
                return e
    return None


engine = Engine()

#needs engine initialized to import the rest
from tabby import Tabby
from pause import Pause
from title import TitleScreen
from hud import Hud

engine.initialize()

# KEEP engine.Run() HERE.
engine.Run()
