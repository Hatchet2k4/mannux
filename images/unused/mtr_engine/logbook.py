import parser

class Logbook(object):
    def __init__(self):
        self.data = {}
        self.order = {}
        self.LoadData()

    def LoadData(self):
        for key in ("locations", "enemies", "lore"):
            self.data[key] = {}
            self.order[key] = []
            f = parser.load("data/" + key + ".logs")
            for entry, data in f["metroid2-log"].todict().iteritems():
                entry = entry.replace("_", " ")
                self.order[key].append(entry)
                self.data[key][entry] = (0, data)

    def LoadDataString(self, type, str):
        #If str is empty (just a 0) then return.
        if str == "0":
            return

        logs = str.split(",")
        for entry in logs:
            data = self.data[type][entry]
            self.data[type][entry] = (1, data[1])

    def Obtain(self, type, entry, hud = True):
        from engine import engine
        if entry in self.data[type]:
            data = self.data[type][entry]
            # Set entry to being obtained
            self.data[type][entry] = (1, data[1])
            # Signal game engine to display new entry string.
            if hud:
                engine.hud.scan_data = entry + " added to your logbook"

