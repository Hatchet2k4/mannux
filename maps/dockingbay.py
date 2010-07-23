#!/usr/bin/env python

import ika
import engine.mapscript
from engine import engine as e
from engine.ship import Ship, ShipLanded, ShipLanding, Doors
from engine.background import Background, GlowBG
from engine.fade import FadeIn, FadeOut
from engine.door import Door
from engine.fog import Fog
from engine.zombie import Zombie
from engine.dockwindow import DockWindow
from engine.turret import Turret
#from globalvars import font
from engine.const import Dir


def landing_animation():
    xwin = 232
    ywin = 100
    bg = [Background(ika.Image('images/bg_planetstars1.png'), 364, 128 + 56),
          Background(ika.Image('images/bg_planetstars2.png'), 364, 128 + 56),
          Background(ika.Image('images/bg_docking_bay.png'), 208, 128),
          GlowBG(ika.Image('images/bg_glow.png'), 208 + 122, 128 + 44)]
    fg = [Background(ika.Image('images/elevator.png'), 336, 384), Fog(),
          FadeIn(300)]
    done = False
    time = ika.GetTime()
    starttime = time
    sh = Ship()
    
    elapsed = 0
    while not done:
        t = ika.GetTime()
        while t > time:
            #if ika.Input.keyboard['SPACE'].Position():
            #    ika.Delay(1)
            time += 1
            elapsed += 1
            if ika.Input.keyboard['ESCAPE'].Pressed():
                done = True
            if elapsed < 300:
                xwin += 0.30
                ywin += 0.15
            if elapsed == 200:
                # Insert the ship between the two star layers.
                bg[1:1] = [sh]
                sh.x = 370
                sh.y = 230
                sh.vx = 0.5
                sh.vy = 0.08
                sh.size = 0.1
                sh.va = 0.30
                sh.vs = 0.0006
            if elapsed > 350 and elapsed < 420:
                sh.va -= 0.006
                sh.vx -= 0.006
                sh.vy = 0.04
                sh.vs = 0.001
            if elapsed > 500 and elapsed < 600:
                sh.va += 0.001
                sh.vx = 0.016
                sh.vs = 0.0012
            if elapsed == 600:
                bg.remove(sh)
                # Put the ship in front of all bg layers now.
                bg.append(sh)
            if elapsed > 600 and elapsed < 700:
                sh.va += 0.001
                ywin += 0.15
                sh.vs = 0.0015
            if elapsed >= 700 and elapsed < 1000:
                #sh.vy = 0
                #sh.va = 0
                #sh.angle = 0
                ywin += 0.15
                if sh.angle + sh.va >=0:
                    sh.angle = 0
                    sh.va = 0
                if sh.x + sh.vx >= 480:
                    sh.x = 480
                    sh.vx=0
                if sh.size + sh.vs >= 1:
                    sh.size = 1
                    sh.vs = 0
                if sh.y + sh.vy >= 264:
                    sh.y = 264
                    sh.vy = 0
            if elapsed == 1000:
                # Switch to landing gear animation.
                bg.remove(sh)
                sh = ShipLanding(344, 207)
                bg.append(sh)
                
                
                
            if elapsed > 1000 and elapsed < 1250:
                sh.geary += 0.2
                sh.y += 0.112
                if elapsed in [1030, 1060, 1090, 1120, 1150, 1180, 1210]:
                    sh.gearframe -= 1
            if elapsed == 1260:                    
                sh.jets=False
            if elapsed == 1300:
            
                bg.remove(sh)
                sh = ShipLanded(344, 234, state=2, tabin=True)
                bg.append(sh)            
            
                
                
            if elapsed == 1800:    
                fg.append(FadeOut(300))
            
            if elapsed == 2100:
                done = True

            for thing in bg:
                thing.update()
            for thing in fg:
                thing.update()
        time = ika.GetTime()
        #video.clear(ika.RGB(0, 200, 0))
        ika.Map.xwin = int(xwin)
        ika.Map.ywin = int(ywin)
        for thing in bg:
            thing.draw()
        ika.Map.Render(*range(ika.Map.layercount))
        for thing in fg:
            thing.draw()
        #font.Print(0, 0, str(elapsed / 100.0))
        #font.Print(0, 10, str(ika.Map.xwin))
        #font.Print(0, 20, str(ika.Map.ywin))
        #font.Print(0, 40, 'x: %s' % sh.x)
        #font.Print(0, 50, 'y: %s' % sh.y)
        #font.Print(0, 60, 'a: %s' % sh.angle)
        #font.Print(0, 70, 's: %s' % sh.size)
        #font.Print(80, 40, 'vx: %s' % sh.vx)
        #font.Print(80, 50, 'vy: %s' % sh.vy)
        #font.Print(80, 60, 'va: %s' % sh.va)
        #font.Print(80, 70, 'vs: %s' % sh.vs)
        ika.Video.ShowPage()
        ika.Input.Update()
        # Pause.
        if ika.Input.keyboard['A'].Pressed():
            while not ika.Input.keyboard['A'].Pressed():
                ika.Input.Update()
            time = ika.GetTime()




def AutoExec():
    if not e.GetFlag('shiplanded'):
        landing_animation()
        e.SetFlag('shiplanded', True)
        
        
    e.camera.reset_borders()
    e.background_things.append(Background(ika.Image('images/bg_planetstars2.png'),
                                          364, 128 + 56))
    e.background_things.append(Background(ika.Image('images/bg_docking_bay.png'),
                                          208, 128))
    e.background_things.append(GlowBG(ika.Image('images/bg_glow.png'),
                                                208 + 122, 128 + 44))
    e.background_things.append(ShipLanded(344, 235))
    e.foreground_things.append(Background(ika.Image('images/elevator.png'),
                                          336, 384))
    e.foreground_things.append(Fog())
    
    
    
    #e.foreground_things.append(Fog(-0.2, 0.1))
    #if not landed:
    #    landed = True
    #    e.foreground_things.append(FadeIn())
    if e.loading:
        e.player.position = (25 * ika.Map.tilewidth, 21 * ika.Map.tileheight)
    e.AddEntity(Door(2 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_right'))
    e.AddEntity(Door(57 * ika.Map.tilewidth, 24 * ika.Map.tileheight,
                         'door_left', locked=True))
    #e.AddEntity(Zombie(40 * ika.Map.tilewidth, 21 * ika.Map.tileheight))
    #e.AddEntity(Zombie(30 * ika.Map.tilewidth, 21 * ika.Map.tileheight))
    e.AddEntity(DockWindow(9 * ika.Map.tilewidth, 4 * ika.Map.tileheight))
    e.AddEntity(Turret(9 * ika.Map.tilewidth, 15 * ika.Map.tileheight,
                           Dir.LEFT))
    #entities.append(Turret(9 * ika.Map.tilewidth, 12 * ika.Map.tileheight,
    #                       Dir.LEFT))
    secretArea.activated = False

    #ika.Map.SetLayerTint(1, ika.RGB(255,100, 100, 127))

#map scripts
toDockControl = engine.mapscript.Warp(17, 7, 'dockingcontrolroom.ika-map', Dir.LEFT)
toAirlock1 = engine.mapscript.Warp(17, 10, 'airlock1.ika-map', Dir.LEFT)
secretArea = engine.mapscript.LayerFader('Secret Overlay', 255, 0, 25)




