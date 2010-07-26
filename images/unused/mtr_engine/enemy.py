import ika
import engine
import entity

def GetDropType(drops):
    """Returns a new pickup object depending on Samus's current equipment."""
    types = []
    samus = engine.engine.player
    #Energy
    if samus.energy < samus.max_energy:
        #Add small energy twice (for more probability) and then large energy.
        types.append(entity.SmallEnergyPickup)
        types.append(entity.SmallEnergyPickup)
        types.append(entity.LargeEnergyPickup)

    #Missiles
    if samus.equipment["Missiles"].cur < samus.equipment["Missiles"].max:
        types.append(entity.MissilePickup)

    #Super Missiles
    if samus.equipment["Super Missiles"].cur < samus.equipment["Super Missiles"].max:
        types.append(entity.SuperMissilePickup)

    #Power Bombs
    if samus.equipment["Power Bombs"].cur < samus.equipment["Power Bombs"].max:
        types.append(entity.PowerBombPickup)

    #Select a type.
    if types:
        return types[ika.Random(0, len(types))]
    else:
        return None

class Enemy(entity.Entity):

    def __init__(self, x, y, sprite, hotspot=None):
        entity.Entity.__init__(self, x, y, sprite, hotspot)
        self.hp = 1
        self.hurt = False
        self.dead = False
        self.sightrange = 120
        self.touchable = True
        self.hurtable = True
        self.drops = ()

    def Hurt(self, damage):
        self.flashticks = 5
        self.hp -= damage
        self.hurt = True
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.hurtable = False

            #Add this enemy into the logbook.
            #engine.engine.logbook.Obtain("enemies", self.name)

            #Item drop.
            drop = GetDropType(self.drops)
            if drop:
                #Returned actual drop, so set it on the map.
                engine.engine.AddEntity(drop(self.x + self.hotspot[2] / 2, self.y + self.hotspot[3] / 2))

    def Touch(self, player):
        pass
        #HURT SAMUS HERE





