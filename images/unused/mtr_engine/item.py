from engine import engine

class Container:
    """Big equipment container for easy item access!"""
    def __init__(self):
        self.items = {}
        #Samus's energy tank.
        self.items["E-Tank"] = AmmoItem("", 14)
        self.items["E-Tank"].cur = 99
        self.items["E-Tank"].max = 99
        self.items["E-Tank"].expand = (100, 50)
        #Suit items.
        self.items["Power Suit"] = Item("")
        self.items["Varia Suit"] = Item("Varia Suit")
        self.items["Gravity Suit"] = Item("Gravity Suit")
        self.items["Aero Suit"] = Item("Aero Suit")
        #Beam items.
        self.items["Power Beam"] = Item("")
        self.items["Ice Beam"] = Item("Ice Beam")
        self.items["Grapple Beam"] = Item("Grapple Beam")
        self.items["Pulse Beam"] = Item("Pulse Beam")
        self.items["Charge Beam"] = Item("Charge")
        self.items["Spazer"] = Item("Spazer")
        self.items["Wave"] = Item("Wave")
        self.items["Plasma"] = Item("Plasma")
        #Missile items.
        self.items["Missiles"] = AmmoItem("Norm", 48)
        self.items["Super Missiles"] = AmmoItem("Super", 15)
        self.items["Super Missiles"].expand = (2, 1)
        #Bomb items.
        self.items["Bombs"] = Item("Norm")
        self.items["Power Bombs"] = AmmoItem("Power", 15)
        self.items["Power Bombs"].expand = (2, 1)
        #Misc. items.
        self.items["Power Grip"] = Item("Power Grip")
        self.items["Hi-Jump Boots"] = Item("Hi-Jump Boots")
        self.items["Space Jump"] = Item("Space Jump")
        self.items["Screw Attack"] = Item("Screw Attack")
        #Morphball items.
        self.items["Morph Ball"] = Item("")
        self.items["Spring Ball"] = Item("Spring Ball")
        self.items["Boost Ball"] = Item("Boost Ball")
        self.items["Spider Ball"] = Item("Spider Ball")

    def __getitem__(self, name):
        return self.items[name]

    def __contains__(self, name):
        return self.items[name].obtained

    def Obtain(self, name, number = None):
        item = self.items[name]
        b = not item.obtained
        if isinstance(item, AmmoItem):
            if engine.dif_mode == "hard":
                item.max += item.expand[1]
                item.cur += item.expand[1]
            else:
                item.max += item.expand[0]
                item.cur += item.expand[0]
            item.acquired[number] = 1
        if b:
            item.obtained = 1
        return b

    def Enabled(self, name):
        if self.items[name].obtained:
            return self.items[name].enabled
        else:
            return False

class Item(object):
    def __init__(self, name):
        self.name = name
        self.obtained = 0
        self.toggle_able = True
        self.enabled = True

    def Draw(self, x, y, font, color):
        font.Print(x, y, color + self.name)


class AmmoItem(Item):
    def __init__(self, description, amount):
        Item.__init__(self, description)
        self.__cur = 0
        self.max = 0
        self.expand = (5, 2)
        self.acquired = list()
        for i in range(amount):
            self.acquired.append(0)

    def Draw(self, x, y, font, color):
        print >> font(x, y), color + self.name
        digits = len(str(self.max))
        print >> font(x + 65, y, "right"), color + "%s/%s" % (str(self.cur).zfill(digits), str(self.max).zfill(digits))

    def GetName(self):
        return self.name + "%s/%s" % (self.cur, self.max)

    def __GetCur(self):
        return self.__cur

    def __SetCur(self, value):
        self.__cur = min(value, self.max)

    cur = property(__GetCur, __SetCur)

beams = ("Power Beam", "Ice Beam", "Pulse Beam", "Grapple Beam")