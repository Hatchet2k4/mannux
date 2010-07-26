import ika
import engine

from color import ColorCode
import fonts
from hud import DrawEnergy
from process import Process
from video import TintBlit

def Image(n):
    return ika.Image("img/sub_screen/%s.png" % n)

images = {}
images["visor"] = Image("visor")
images["shoulders"] = Image("L_and_R")
images["borders"] = (Image("border"), Image("border_inv"))
images["page_icons"] = {"inv": (Image("icon_inv"), Image("icon_inv2")), "log": (Image("icon_log"), Image("icon_log2")), "map": (Image("icon_map"), Image("icon_map2")), "optn": (Image("icon_optn"), Image("icon_optn2"))}
#Images for page headings.
images["txt"] = {"inv": (Image("txt_stat"), Image("txt_status")), "log": (Image("txt_log"), Image("txt_logbook")), "map": [Image("txt_map"), 0], "optn": (Image("txt_optn"), Image("txt_options"))}
images["txt"]["map"][1] = images["txt"]["map"][0]

class Subscreen(Process):
    def __init__(self):
        Process.__init__(self)
        self.block_render = True
        self.ticks = 0

        self.page = 0
        self.dest_page = 0
        self.state = 0#0 = zoom out, 1 = control, 2 = zoom in, 3 = change page

    cur_page = property(lambda self: pages[self.page])

    def Start(self):
        self.started = True

        self.state = 0
        self.ticks = 0

    def Draw(self, top):
        if self.state == 0 or self.state == 2:
            if self.state == 0:
                scale = 1.2 - (self.ticks * 0.2 / 25)
                color = 255 - (self.ticks * 160 / 25)

            else:
                scale = 1 + (self.ticks * 0.2 / 25)
                color = 95 + (self.ticks * 160 / 25)

            TintBlit(self.map_image, 0, 0, ika.RGB(color, color, color))

            #Draw current page.
            if self.state == 0:
                self.cur_page.Draw(ika.RGB(255, 255, 255, self.ticks * 255 / 25))
            else:
                self.cur_page.Draw(ika.RGB(255, 255, 255, 255 - (self.ticks * 255 / 25)))

            images["visor"].ScaleBlit(-(int(320 * scale) - 320) / 2, -(int(240 * scale) - 240) / 2, int(320 * scale), int(240 * scale))

        #Draw non-scaled visor.
        else:
            TintBlit(self.map_image, 0, 0, ika.RGB(95, 95, 95))

            #Static layout.
            if self.state == 1:
                #Draw current page.
                pages[self.page].Draw(ika.RGB(255, 255, 255))


            #Change page.
            elif self.state == 3:
                #Draw current page fade out.
                pages[self.page].Draw(ika.RGB(255, 255, 255, 255 - self.ticks * 255 / 25))
                #Draw dest page fade in.
                pages[self.dest_page].Draw(ika.RGB(255, 255, 255, self.ticks * 255 / 25))

            #Page selection.
            for name, i in zip(("log", "map", "inv", "optn"), range(4)):
                if self.page == i:
                    images["page_icons"][name][0].Blit(116 + i * 22, 222)
                else:
                    images["page_icons"][name][1].Blit(116 + i * 22, 222)

            images["visor"].Blit(0, 0)

            #Draw nav stuff.
            images["shoulders"].Blit(0, 0)
            self.cur_page.txt_image.Blit(160 - self.cur_page.txt_image.width / 2, 3)
            self.cur_page.left_image.Blit(12, 3)
            self.cur_page.right_image.Blit(306 - self.cur_page.right_image.width, 3)

    def Update(self):
        self.ticks += 1
        if not self.state == 1:
            if self.ticks == 25:
                if self.state == 2:
                    self.started = False
                    engine.processor.Set(engine.engine)

                else:
                    self.ticks = 0
                    self.state += 1
                    if self.state == 4:
                        self.state = 1
                        self.page = self.dest_page

    def Input(self, position, pressed):
        if "aim_down" in pressed:
            if self.page == 3:
                self.dest_page = 0
            else:
                self.dest_page += 1
            pages[self.dest_page].Start()
            self.state = 3
            self.ticks = 0

        elif "aim_up" in pressed:
            if self.page == 0:
                self.dest_page = 3
            else:
                self.dest_page -= 1
            pages[self.dest_page].Start()
            self.state = 3
            self.ticks = 0

        if "start" in pressed and self.state == 1:
            self.state = 2
            self.ticks = 0

        if self.state == 1:
            self.cur_page.Input(position, pressed)

subscreen = Subscreen()


class Page(object):
    def __init__(self, name, other_names, border):
        self.txt_image = images["txt"][name][1]
        self.left_image = images["txt"][other_names[0]][0]
        self.right_image = images["txt"][other_names[1]][0]
        self.border = images["borders"][border]

    def Start(self):
        pass

    def Draw(self, color):
        TintBlit(self.border, 0, 0, color)

    def Input(self, position, pressed):
        pass

class Map(Page):
    def __init__(self):
        Page.__init__(self, "map", ("log", "inv"), 0)

        self.offset = [0, 0]

        self.images = {}
        self.images["grid"] = Image("map_grid")
        self.images["windows"] = (Image("map_box1"), Image("map_box2"))
        self.images["arrows"] = (Image("icon_arrowup"), Image("icon_arrowdown"), Image("icon_arrowleft"), Image("icon_arrowright"))

    def Start(self):
        x = min(max(engine.engine.automap.cur_map_x - 17, 0), engine.engine.automap.width - 37)
        y = min(max(engine.engine.automap.cur_map_y - 11, 0), engine.engine.automap.height - 24)
        self.offset = [x, y]

    def Draw(self, color):
        Page.Draw(self, color)
        #Draw background grid.
        TintBlit(self.images["grid"], 0, 0, color)

        #Draw automap.
        engine.engine.automap.Draw(17, 32, (self.offset[0], self.offset[1]), (36, 23), color = color, flash = False)

        #Draw area name and window.
        TintBlit(self.images["windows"][0], 205, 28, color)
        area = engine.engine.automap.GetAreaName()
        if " " in area:
            area = area.split(" ")
            fonts.bold.Print(210, 33, ColorCode(color) + area[0] + "\n" + area[1])
        else:
            fonts.bold.Print(210, 33, ColorCode(color) + area)

        #Draw items and window.
        if True:
            TintBlit(self.images["windows"][1], 13, 173, color)

        #Draw arrows.
        able = (self.offset[1] - 1 > -1, self.offset[1] + 1 < engine.engine.automap.width - 23, self.offset[0] - 1 > -1, self.offset[0] + 1 < engine.engine.automap.width - 36)
        for image, x, y, able in zip(self.images["arrows"], (153, 153, 11, 302), (25, 213, 115, 115), able):
            if able:
                TintBlit(image, x, y, color)

    def Input(self, position, pressed):
        if "right" in position and subscreen.ticks % 10 == 0:
            if self.offset[0] + 1 < engine.engine.automap.width - 36:
                self.offset[0] += 1
        elif "left" in position and subscreen.ticks % 10 == 0:
            if self.offset[0] - 1 > -1:
                self.offset[0] -= 1

        if "down" in position and subscreen.ticks % 10 == 0:
            if self.offset[1] + 1 < engine.engine.automap.width - 23:
                self.offset[1] += 1
        elif "up" in position and subscreen.ticks % 10 == 0:
            if self.offset[1] - 1 > -1:
                self.offset[1] -= 1

class Inventory(Page):
    def __init__(self):
        Page.__init__(self, "inv", ("map", "optn"), 1)

        self.images = {}
        self.images["hexagons"] = Image("inv_hexagons")
        self.images["suits"] = (Image("samus_power"), Image("samus_varia"), Image("samus_gravity"), Image("samus_aero"), Image("samus_nosuit"))
        self.images["energy"] = (Image("ebar"), Image("etank_empty"), Image("etank_full"))
        self.images["item"] = (Image("inv_box"), Image("inv_box_sel"), Image("inv_box_checked"), Image("inv_box_empty"))

        self.windows = []
        #Beam window.
        self.windows.append((Image("inv_beam"), 31, ("Charge Beam", "Spazer", "Wave", "Plasma", "Ice Beam", "Pulse Beam")))
        #Missile window.
        self.windows.append((Image("inv_missile"), 116, ("Missiles", "Super Missiles")))
        #Bomb window.
        self.windows.append((Image("inv_bomb"), 157, ("Bombs", "Power Bombs")))
        #Misc. window.
        self.windows.append((Image("inv_misc"), 198, ("Screw Attack", )))
        #Suit window.
        self.windows.append((Image("inv_suit"), 42, ("Varia Suit", "Gravity Suit", "Aero Suit")))
        #Morph ball window.
        self.windows.append((Image("inv_morphball"), 94, ("Spider Ball", "Boost Ball", "Spring Ball")))
        #Arms window.
        self.windows.append((Image("inv_arms"), 145, ("Power Grip", "Grapple Beam")))
        #Legs window.
        self.windows.append((Image("inv_legs"), 186, ("Hi-Jump Boots", "Space Jump")))

    def Start(self):
        self.selection = [0, 0]
        self.GetNextSelection(0, 1)

    def Draw(self, color):
        Page.Draw(self, color)
        #Draw hexagon background.
        TintBlit(self.images["hexagons"], 0, 0, color)

        #Draw energy display.
        DrawEnergy(101, 25, engine.engine.player.energy, engine.engine.player.max_energy, color)

        #Draw Samus picture depending on suit.
        if True:
            suit = 0
            if engine.engine.player.equipment.Enabled("Varia Suit"):
                suit = 1
            elif engine.engine.player.equipment.Enabled("Gravity Suit"):
                suit = 2
            elif engine.engine.player.equipment.Enabled("Aero Suit"):
                suit = 3
        else:
            suit = 3
        TintBlit(self.images["suits"][suit], 0, 0, color)

        #Draw items.
        w = 0
        ika.Video.ClipScreen(10, 31, 310, 220)
        for image, window_y, items in self.windows:
            #Check if this window even needs to be displayed.
            if filter(lambda x: engine.engine.player.equipment[x].obtained, items):
                if w < 4:
                    x = 10 - (96 - ika.GetRGB(color)[3] * 96 / 255)
                else:
                    x = 234 + (96 - ika.GetRGB(color)[3] * 96 / 255)

                TintBlit(image, x, window_y, color)
                i = 0
                item_index = 0
                for item_num, item in enumerate(items):
                    selected = w == self.selection[0] and item_num == self.selection[1]
                    item = engine.engine.player.equipment[item]
                    if item.obtained:
                        y = window_y + 8 + i * 11
                        if selected:
                            TintBlit(self.images["item"][1], x, y, color)
                        else:
                            TintBlit(self.images["item"][0], x, y, color)

                        #Display on/off icon.
                        if item.enabled:
                            TintBlit(self.images["item"][2], x + 2, y + 1, color)
                        else:
                            TintBlit(self.images["item"][3], x + 2, y + 1, color)

                        #Display text.
                        if selected:
                            item.Draw(x + 11, y + 2, fonts.thin, ColorCode(ika.RGB(0, 0, 0, ika.GetRGB(color)[3])))
                        else:
                            item.Draw(x + 11, y + 2, fonts.thin, ColorCode(color))

                        i += 1
                    item_index += 1

            w += 1

        ika.Video.ClipScreen()

    def Input(self, position, pressed):
        if "up" in pressed:
            self.GetNextSelection(items=-1)
        elif "down" in pressed:
            self.GetNextSelection(items=1)
        elif "left" in pressed:
            pass
        elif "right" in pressed:
            pass

        if "jump" in pressed:
            item = engine.engine.player.equipment[self.windows[self.selection[0]][2][self.selection[1]]]
            if item.enabled:
                item.enabled = False
            else:
                item.enabled = True


    def GetNextSelection(self, windows=0, items=0):
        w, i = self.selection[0] + windows, self.selection[1] + items
        while True:
            if [w, i] == self.selection:
                return
            else:
                if windows > 0 or items > 0:
                    i += 1
                    if i > len(self.windows[w][2]) - 1:
                        w += 1
                        if w > 7:
                            w = 0
                        i = 0

                else:
                    i -= 1
                    if i < 0:
                        w -= 1
                        if w < 0:
                            w = 7
                        i = len(self.windows[w][2]) - 1

                if engine.engine.player.equipment[self.windows[w][2][i]].obtained:
                    break

        print "Final", w, i

        self.selection = [w, i]



class Logbook(Page):
    def __init__(self):
        Page.__init__(self, "log", ("optn", "map"), 0)

        self.images = {}
        self.images["bg"] = Image("log_bg")
        self.images["sel"] = Image("log_sel")
        self.images["scrollbar"] = (Image("scrollbar_box"), Image("scrollbar"), Image("scrollbar_down"), Image("scrollbar_up"))

        self.cur_category = 0
        self.categories = ("locations", "enemies", "lore")
        self.cur_selection = ([0, 0], [0, 0], [0, 0])

    def __len__(self):
        return len(engine.engine.logbook.order[self.categories[self.cur_category]])

    def __SetCurEntry(self, entry):
        self.cur_selection[self.cur_category][0] = entry

    def __SetCurTop(self, top):
        self.cur_selection[self.cur_category][1] = top

    cur_entry = property(lambda self: self.cur_selection[self.cur_category][0], __SetCurEntry)
    cur_top = property(lambda self: self.cur_selection[self.cur_category][1], __SetCurTop)

    def Draw(self, color):
        Page.Draw(self, color)

        ika.Video.TintBlit(self.images["bg"], 0, 0, color)

        #Display category names.
        for i, name in enumerate(self.categories):
            name = name[0].upper() + name[1:]
            if self.cur_category != i:
                fonts.bold.Print(104 + i * 60, 32, ColorCode(ika.RGB(0, 0, 0, ika.GetRGB(color)[3])) + name)
            else:
                fonts.bold.Print(104 + i * 60, 32, ColorCode(color) + name)

        #Display selection box.
        ika.Video.TintBlit(self.images["sel"], 12, 45 + (self.cur_entry - self.cur_top) * 11, color)

        #Display entries for the category.
        ika.Video.ClipScreen(12, 45, 81, 219)
        logbook = engine.engine.logbook
        for i in range(16):
            #Get top selection
            top = i + self.cur_top
            if i == len(logbook.order[self.categories[self.cur_category]]):
                break

            name = logbook.order[self.categories[self.cur_category]][top]
            if logbook.data[self.categories[self.cur_category]][name][0] == 1:
                if top == self.cur_entry:
                    fonts.thin.Print(14, 47 + i * 11, ColorCode(color) + name)
                else:
                    fonts.thin.Print(14, 47 + i * 11, ColorCode(ika.RGB(0, 0, 0, ika.GetRGB(color)[3])) + name)
        ika.Video.ClipScreen()

        #Draw scrollbar.
        for image, x, y, able in zip(self.images["scrollbar"][1:], (83, 83, 83), (54, 212, 45), (True, self.cur_entry + 1 == len(engine.engine.logbook.order[self.categories[self.cur_category]]), self.cur_entry == 0)):
            if able:
                ika.Video.TintBlit(image, x, y, ika.RGB(127, 127, 127, ika.GetRGB(color)[3]))
            else:
                ika.Video.TintBlit(image, x, y, color)

        ika.Video.TintBlit(self.images["scrollbar"][0], 83, 54 + self.cur_top * (152 / (len(self) - 17)), color)

    def Input(self, position, pressed):
        if "up" in position and subscreen.ticks % 10 == 0:
            if self.cur_entry > 0:
                self.cur_entry -= 1
                if self.cur_entry < self.cur_top:
                    self.cur_top -= 1
        elif "down" in position and subscreen.ticks % 10 == 0:
            if self.cur_entry + 1 < len(engine.engine.logbook.order[self.categories[self.cur_category]]):
                self.cur_entry += 1
                if self.cur_top + 15 < self.cur_entry:
                    self.cur_top += 1
        elif "left" in pressed:
            if self.cur_category > 0:
                self.cur_category -= 1
        elif "right" in pressed:
            if self.cur_category + 1 < len(self.categories):
                self.cur_category += 1



class Options(Page):
    def __init__(self):
        Page.__init__(self, "optn", ("inv", "log"), 0)

    def Draw(self, color):
        Page.Draw(self, color)
        fonts.bold.CenterPrint(160, 32, ColorCode(color) + "lolz")

map_page = Map()
inventory_page = Inventory()
logbook_page = Logbook()
options_page = Options()
pages = (logbook_page, map_page, inventory_page, options_page)
