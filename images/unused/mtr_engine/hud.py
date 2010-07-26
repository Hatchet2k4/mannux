import ika
import color
from color import ColorCode
import fonts
import riptiles
from video import TintBlit

def Image(name):
    return ika.Image("img/hud/%s.png" % name)

def LoadBeamImages(name):
    return Image(name + "_disabled"), Image(name)

def LoadItemImages(name):
    return Image(name + "_disabled"), Image(name + "_armed")


#Energy bar value
e_bar_value = 99

#Images!
energy = Image("energy")
#E-Tank
e_tank_fill = (Image("e_tank_fill"), Image("e_tank_fill2"))
e_tank_frame = (Image("e_tank_frame"), Image("e_tank_frame2"))
e_bar = Image("e_bar")
#Missiles
missile = LoadItemImages("missile")
#Super Missiles
smissile = LoadItemImages("smissile")
#Power Bombs
pbomb = LoadItemImages("pbomb")
#Minimap
minimap = Image("radar")
#Metroid counter
metroid = riptiles.Animation(riptiles.RipTiles("sprites/metroid.png", 32, 25, 3, 3), ((0, 80), (1, 15), (2, 15), (1, 15)))
#Power Beam
power_beam = LoadBeamImages("power_beam")
#Ice Beam
ice_beam = LoadBeamImages("ice_beam")
#Pulse Beam
pulse_beam = LoadBeamImages("pulse_beam")
#Grapple Beam
grapple_beam = LoadBeamImages("grapple_beam")

def DrawEnergy(x, y, cur, max_energy, color = ika.RGB(255, 255, 255), disp = None, style = 0):
    """Make this a function, so other parts of the game can access it."""
    alpha = ika.GetRGB(color)[3]

    if disp is None:
        disp = cur - (cur / 100 * 100)

    if style == 0:
        #TintBlit(energy, x - 2, y - 2, color)

        #Draw numbers.
        if cur < 50:
            fonts.hud_big.Print(x - 1, y - 1, ColorCode(ika.RGB(255, 63, 63, ika.GetRGB(color)[3])) + str(disp).zfill(2))
        else:
            fonts.hud_big.Print(x - 1, y - 1, ColorCode(color) + str(disp).zfill(2))

        #Draw tanks.
        for i in range(max_energy / 100):
            if (i + 1) * 100 <= cur:
                TintBlit(e_tank_frame[1], x + 18 + (i % 7) * 7, y + 7 - (i / 7) * 7, color)
                TintBlit(e_tank_fill[1], x + 18 + (i % 7) * 7, y + 7 - (i / 7) * 7, color)
            else:
                TintBlit(e_tank_frame[1], x + 18 + (i % 7) * 7, y + 7 - (i / 7) * 7, ika.RGB(255, 255, 255))

    else:
        #Draw base energy bar.
        TintBlit(e_bar, x + 18, y + 9, color)
        #Draw big numbers.
        if cur < 50:
            fonts.hud_big.Print(x - 1, y - 1, ColorCode(ika.RGB(255, 63, 63, ika.GetRGB(color)[3])) + str(disp).zfill(2))
            if disp > 0:
                ika.Video.DrawRect(x + 18, y + 9, x + 18 + (disp * 96 / 99), y + 11, ika.RGB(255, 63, 63, alpha), 1)
        else:
            fonts.hud_big.Print(x - 1, y - 1, ColorCode(color) + str(disp).zfill(2))
            if disp > 0:
                ika.Video.DrawRect(x + 18, y + 9, x + 18 + (disp * 96 / 99), y + 11, color, 1)

        #Draw tanks.
        for i in range(max_energy / 100):
            if (i + 1) * 100 <= cur:
                TintBlit(e_tank_frame[0], x + 18 + i * 7, y, color)
                TintBlit(e_tank_fill[0], x + 18 + i * 7, y, color)
            else:
                TintBlit(e_tank_frame[0], x + 18 + i * 7, y, ika.RGB(255, 255, 255))

def DrawHUDPiece(x, y, offset, icons, num, armed):
    if armed:
        icons[1].Blit(x, y)
        fonts.hud_small.RightPrint(x + 30, y + 4, str(num))
    else:
        icons[0].Blit(x, y)
        fonts.hud_small_disabled.RightPrint(x + 30, y + 4, str(num)), color.ColorCode(ika.RGB(191, 191, 191)) + str(num)

def DrawBeamIcon(x, y, images, alpha, bool):
    if bool:
        ika.Video.TintBlit(images[1], x, y, ika.RGB(255, 255, 255, alpha))
    else:
        ika.Video.TintBlit(images[0], x, y, ika.RGB(255, 255, 255, alpha))

class HUD(object):
    def __init__(self):
        self.display_beam = False
        self.beam_ticks = 0
        self.display_metroid = False
        self.metroid_ticks = 0
        self.display_scan = False
        self.__scan = None
        self.scan_ticks = 0
        self.e_bar_value = 0

    def __SetScanString(self, string):
        self.__scan = (string, len(string), len(string) * 5)
        self.scan_ticks = 0
        self.display_scan = True

    scan_data = property(lambda self: self.__scan, __SetScanString)

    def Draw(self, samus = None, automap = None):
        if samus is None:
            import engine
            samus = engine.engine.player
            automap = engine.engine.automap
        DrawEnergy(4, 4, samus.energy, samus.max_energy, disp=self.e_bar_value)
        #Draw missiles.
        if samus.equipment["Missiles"].max > 0:
            DrawHUDPiece(150, 4, 16, missile, str(samus.equipment["Missiles"].cur).zfill(3), samus.cur_state not in samus.morph_states and samus.equipment["Missiles"].cur > 0 and samus.cur_missile == 0 and samus.sec_armed)

        #Draw super missiles.
        if samus.equipment["Super Missiles"].max > 0:
            DrawHUDPiece(183, 4, 11, smissile, str(samus.equipment["Super Missiles"].cur).zfill(2), samus.cur_state not in samus.morph_states and samus.equipment["Super Missiles"].cur > 0 and samus.cur_missile == 1 and samus.sec_armed)

        #Draw power bombs.
        if samus.equipment["Power Bombs"].max > 0:
            DrawHUDPiece(216, 4, 11, pbomb, str(samus.equipment["Power Bombs"].cur).zfill(2), samus.cur_state in samus.morph_states and samus.equipment["Power Bombs"].cur > 0 and samus.sec_armed)

        #Draw minimap.
        minimap.Blit(280, 0)
        automap.Draw(280, 0, (automap.cur_map_x - 2, automap.cur_map_y - 1), (5, 3))


        #Draw beam selection
        if self.display_beam:
            if self.beam_ticks > 200:
                a = 255 - min((self.beam_ticks - 200) * 255 / 100, 255)
            else:
                a = 255
            #Display beam graphics.
            for i, img, name in zip(range(4), (power_beam, ice_beam, pulse_beam, grapple_beam), ("Power Beam", "Ice Beam", "Pulse Beam", "Grapple Beam")):
                if name in samus.equipment:
                    DrawBeamIcon(8, 200, img, a, samus.cur_beam == i)


        #Draw metroid counter.
        if self.display_beam:
            if self.metroid_ticks < 100:
                c = ika.RGB(255, 255, 255, max(self.metroid_ticks * 255 / 100, 0))
            elif self.metroid_ticks > 800:
                c = ika.RGB(255, 255, 255, 255 - min((self.metroid_ticks - 800) * 255 / 100, 255))
            else:
                c = ika.RGB(255, 255, 255)
            metroid.Draw(285, 212, c)
            print >> fonts.hud_big(300, 220, "center"), color.ColorCode(c) + str(samus.metroids_killed)

        #Draw scan string.
        if self.display_scan:
            string, length, ticks = self.__scan
            if self.scan_ticks > ticks + 100:
                c = ika.RGB(255, 255, 255, 255 - min((self.scan_ticks - (ticks + 100)) * 255 / 100, 255))
            else:
                c = ika.RGB(255, 255, 255)
            print >> fonts.bold(316, 30, "right"), color.ColorCode(c) + string[:self.scan_ticks * length / ticks]

    def Update(self, samus):
        disp = samus.energy - (samus.energy / 100 * 100)
        if self.e_bar_value < disp:
            self.e_bar_value += 1
        elif self.e_bar_value > disp:
            self.e_bar_value -= 1

        if self.display_beam:
            self.beam_ticks += 1
            if self.beam_ticks == 300:
                self.display_beam = False

        if self.display_metroid:
            self.metroid_ticks += 1
            metroid.Update()
            if self.metroid_ticks == 900:
                self.metroid_display = False

        if self.display_scan:
            self.scan_ticks += 1
            if self.scan_ticks == self.__scan[2] + 200:
                self.display_scan = False
