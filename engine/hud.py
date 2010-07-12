#!/usr/bin/env python

import ika
import color
import config
from engine import engine


class Hud(object):

    def __init__(self):
        super(Hud, self).__init__()
        self.hud_health = ika.Image('%s/hud-health.png' % config.image_path)
        self.hud_healthend = ika.Image('%s/hud-health-end.png' %
                                       config.image_path)
        self.hud_energy = ika.Image('%s/hud-energy.png' % config.image_path)
        self.hud_energyend = ika.Image('%s/hud-energy-end.png' %
                                       config.image_path)
        self.hud_weapon = ika.Image('%s/hud-weapon.png' % config.image_path)
        self.icons = [ika.Image('%s/icon-pistol.png' % config.image_path),
                      ika.Image('%s/icon-shotgun.png' % config.image_path),
                      ika.Image('%s/icon-flame.png' % config.image_path),
                      ika.Image('%s/icon-lightning.png' % config.image_path),
                      ika.Image('%s/icon-rocket.png' % config.image_path),
                      ika.Image('%s/icon-blade.png' % config.image_path)]
        self.hud_icon = self.icons[0]

    def draw(self):
        engine.automap.update(engine.player.x / ika.Map.tilewidth,
                              engine.player.y / ika.Map.tileheight)
        engine.automap.draw_minimap(260, 1)
        ika.Video.Blit(self.hud_health, 0, 0)
        ika.Video.Blit(self.hud_healthend, self.hud_health.width, 0)
        for i, c in enumerate([color.red, ika.RGB(255, 200, 200), color.red]):
            ika.Video.DrawLine(38 - i, 11 + i, engine.player.hp / 3 + 38 - i,
                               11 + i, c)
        if engine.player.showmp:
            ika.Video.Blit(self.hud_energy, 0, 0)
            ika.Video.Blit(self.hud_energyend, self.hud_energy.width, 0)
            for i, c in enumerate([color.blue, ika.RGB(200, 200, 255),
                                   color.blue]):
                ika.Video.DrawLine(30 - i, 22 + i,
                                   engine.player.mp / 3 + 30 - i, 22 + i, c)
        #ika.Video.Blit(self.hud_weapon, 10, 270)
        #ika.Video.Blit(self.hud_icon, 16, 273)

    def resize(self):
        big_image = ika.Canvas('%s/hud-health.png' % config.image_path)
        temp = ika.Canvas(big_image.width - 333 + engine.player.maxhp / 3,
                          big_image.height)
        big_image.Blit(temp, 0, 0, ika.Opaque)
        self.hud_health = ika.Image(temp)
        big_image = ika.Canvas('%s/hud-energy.png' % config.image_path)
        temp = ika.Canvas(big_image.width - 333 + engine.player.maxmp / 3,
                          big_image.height)
        big_image.Blit(temp, 0, 0, ika.Opaque)
        self.hud_energy = ika.Image(temp)
