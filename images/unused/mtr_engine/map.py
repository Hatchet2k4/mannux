import ika
from engine import engine, processor
from savelight import SaveLight
import controls
import process
import video
from engine.savelight import SaveLight, SaveFlash

def MapSwitch(map, zone = None, axis = "x", l = "Background", camera = None):
    """Changes map with a fade transition.

    name - Name of new map.
    zone - Name of destination zone.
    axis - Locked axis ("x" or "y").
    l    - Name of destination layer.
    camera - Camera settings.
    """

    if zone == None:
        zone = "ToMap" + engine.cur_map[:3]

    if axis == "x":
        x = 0
        y = int(engine.player.y) - engine.cur_zone[1]
    else:
        x = int(engine.player.x) - engine.cur_zone[0]
        y = 0
    #print "Exiting Zone", x, y

    engine.MapSwitch(0, 0, map + ".ika-map", layer=l, fadein=False)

    #Get layer index.
    layer = ika.Map.FindLayerByName(l)

    #print "Enter '%s' zone" % zone
    #Get zone info.
    cur_zone = filter(lambda x: x[5] == zone, engine.zones[layer])[0]

    #Set coordinates from zone depending on axis and direction.
    if axis == "y":
        print "Y axis", engine.player.vy
        #print "VY", engine.player.vy
        if engine.player.vy < 0:
            #Moving up!
            y -= engine.player.hotspot[3] - 32
        else:
            #Moving down!
            y += cur_zone[3]

    else:
        #LEFT and RIGHT
        if engine.player.vx > 0:
            #Moving right!
            x += cur_zone[2] + 1
        else:
            #Moving left!
            x -= engine.player.hotspot[2]

    engine.player.x = cur_zone[0] + x
    engine.player.y = cur_zone[1] + y
    #print "X", engine.player.x, cur_zone[0]
    #print "Y", engine.player.y, cur_zone[1]

    #Update camera.
    #If camera coordinates were passed, set those.
    if camera is not None:
        engine.camera.SetBorders(*engine.map_script.cameras[camera])
    engine.camera.Update()

    #Update automap.
    engine.automap.EnterRoom(map + ".ika-map")
    engine.automap.Update(engine.player.x / 16, engine.player.y / 16)

    #Fade In!
    video.FadeIn(20, draw=engine.Draw, draw_after=engine.hud.Draw)
    processor.cur_time = ika.GetTime()

def CameraSwitch(a, b, axis = "x"):
    """If Samus position is < zone origin, set a. If not, set b."""
    if axis == "x":
        origin = engine.cur_zone[0]
        pos = int(engine.player.x)
    else:
        origin = engine.cur_zone[1]
        pos = int(engine.player.y)

    if pos < origin:
        engine.camera.SetBorders(*engine.map_script.cameras[a] + (True,))
    else:
        engine.camera.SetBorders(*engine.map_script.cameras[b] + (True,))

light = None
saved = False
def SavePoint(m):
    global processor, light

    if m == 1 and engine.allowprompt == True and engine.player.cur_state == engine.player.StandState:
        if process.save_message not in processor:
            #Add in message thinger.
            processor += process.save_message
            saved = True
    if m == 1 and engine.player.vy == 0 and light == None and engine.allowprompt:
        x = engine.cur_zone[0]-7
        y = engine.cur_zone[1]+10
        light = SaveLight(x, y)
        engine.AddEntity(light)

    if light and engine.allowprompt == False:
        light.sprite.SetState("glow_down")
        light=None


    if m==2: #player leaving zone
        if light:
            light.sprite.SetState("glow_down")
            light=None
        saved = False



