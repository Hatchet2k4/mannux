#!/usr/bin/env python

import ika
import config


class Sounds(object):

    def __init__(self):
        super(Sounds, self).__init__()
        self.sounds = {'Whoosh': ika.Sound('%s/whoosh.wav' %
                                           config.sound_path),
                       'Whoosh2': ika.Sound('%s/whoosh2.wav' %
                                            config.sound_path),
                       'Open': ika.Sound('%s/open.wav' % config.sound_path),
                       'Close': ika.Sound('%s/close.wav' % config.sound_path),
                       'Step': ika.Sound('%s/step.wav' % config.sound_path),
                       'Land': ika.Sound('%s/land.wav' % config.sound_path),
                       'Menu': ika.Sound('%s/menuclick.wav' %
                                         config.sound_path),
                       'Shoot': ika.Sound('%s/shoot4.ogg' % config.sound_path),
                       'Boom': ika.Sound('%s/hit1.ogg' % config.sound_path),
                       'Zombie-die': ika.Sound('%s/zombie-die.ogg' %
                                               config.sound_path),
                       'Zombie-groan': ika.Sound('%s/zombie-groan.ogg' %
                                                 config.sound_path),

                       'Scan': ika.Sound('%s/XRay.mp3' %
                                                 config.sound_path),
                       'Beam': ika.Sound('%s/beam.wav' %
                                                 config.sound_path)}                                                 
                                                 
                                                 
                                                 
                                                 

    def play(self, sound, volume=1.0):
        sound = self.sounds[sound]
        sound.volume = volume
        sound.Play()
        return sound



sound = Sounds()
