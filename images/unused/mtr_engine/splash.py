#!/usr/bin/env python

import ika
from entity import Entity
#from sprite import Sprite
import config
from sounds import sound

class Splash(Entity):
    def __init__(self, x, y, name):
        y+=14 #need to revise...
        if y % 16 < 8:
            y -= y%16
        else:
            y += (16 - y%16)


        super(Splash, self).__init__(ika.Entity(x, y, 1, '%s/splash-"+name+".ika-sprite'
                                                % config.sprite_path)
        Entity2.__init__(self, x-10, y, Sprite("splash-" + name))


        self.state=self.SplashState
        self.set_animation_state(0, 6, 8, loop=False)


    def SplashState(self):
        while not self.anim.kill:
            yield None
        # Destroys the sprite when its state is done.
        self.destroy = True
        yield None
        
        

#    def Update(self):
#        #super(Splash, self).Update()
#        if self.sprite.anim_done:
#            self._destroy()
