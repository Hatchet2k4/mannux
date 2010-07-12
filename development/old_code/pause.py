    def SlideWindowOut(self, img):
        sound.Play('Whoosh2')
        i=0
        time = ika.GetTime()
        while i < 324:
            t = ika.GetTime()
            while t > time:
                time += 1
                i += 12
                engine.engine.ticks += 1
            time = ika.GetTime()
            engine.engine.draw()
            #engine.engine.draw()
            ika.Video.Blit(self.portw, 0, 15)
            ika.Video.Blit(self.menuw, 0, 135)
            ika.Video.Blit(img, 122+i, 7)
            self.DrawMenu()
            ika.Video.ShowPage()
            ika.Input.Update()

    def SlideWindowIn(self, img):
        sound.Play('Whoosh')
        i = 324
        time = ika.GetTime()
        while i > 0:
            t = ika.GetTime()
            while t > time:
                time += 1
                i -= 12
                engine.engine.ticks += 1
            if i < 0: i = 0
            time = ika.GetTime()

            engine.engine.draw()
            ika.Video.Blit(self.portw, 0, 15)
            ika.Video.Blit(self.menuw, 0, 135)
            ika.Video.Blit(img, 122+i, 7)
            self.DrawMenu()
            ika.Video.ShowPage()
            ika.Input.Update()

    def Weapons(self):

        i = 0
        optselected=0

        self.SlideWindowOut(self.mapw)
        self.SlideWindowIn(self.optw)

        ika.Input.Unpress()
        ika.Input.Update()

        time = ika.GetTime()
        while not ika.Input.keyboard['ESCAPE'].Pressed():

            t = ika.GetTime()
            while t > time:
                time += 1
                engine.engine.ticks+=1

            time = ika.GetTime()
            engine.engine.UpdateTime()

            engine.engine.draw()
            ika.Video.Blit(self.portw, 0, 15)
            ika.Video.Blit(self.menuw, 0, 135)
            ika.Video.Blit(self.optw, 122, 7)

            self.DrawMenu()

            font3.Print(200, 34, "WEAPONS")

            for i, icon in enumerate(self.icons):
                icon.Blit(150+110*(i%2), 50+40*(i/2))


            #ika.Video.Blit(self.select2, 147, 56+15*optselected)

            ika.Video.ShowPage()
            ika.Input.Update()

            if engine.engine.player.downKey.Pressed():
                optselected += 1
                if optselected > 6: optselected = 0
                sound.Play('Menu')
            if engine.engine.player.upKey.Pressed():
                optselected -= 1
                if optselected < 0: optselected = 6
                sound.Play('Menu')
            if engine.engine.player.confirmKey.Pressed():
                pass

        self.SlideWindowOut(self.optw)
        self.SlideWindowIn(self.mapw)

        ika.Input.Unpress()

    def Options(self):
        
        #global upKey, downKey, leftKey, rightKey, attackKey, jumpKey, pauseKey, confirmKey, cancelKey

        i = 0
        optselected=0

        self.SlideWindowOut(self.mapw)
        self.SlideWindowIn(self.optw)

        ika.Input.Unpress()
        ika.Input.Update()
        time = ika.GetTime()
        while not ika.Input.keyboard['ESCAPE'].Pressed():

            t = ika.GetTime()
            while t > time:
                time += 1
                engine.engine.ticks+=1

            time = ika.GetTime()
            engine.engine.UpdateTime()

            engine.engine.draw()
            ika.Video.Blit(self.portw, 0, 15)
            ika.Video.Blit(self.menuw, 0, 135)
            ika.Video.Blit(self.optw, 122, 7)

            self.DrawMenu()

            self.DrawOptions()
            ika.Video.Blit(self.select2, 147, 56+15*optselected)

            ika.Video.ShowPage()
            ika.Input.Update()

            if engine.engine.player.downKey.Pressed():
                optselected += 1
                if optselected > 6: optselected = 0
                sound.Play('Menu')
            if engine.engine.player.upKey.Pressed():
                optselected -= 1
                if optselected < 0: optselected = 6
                sound.Play('Menu')
            if engine.engine.player.confirmKey.Pressed():
                #pass
                ika.Input.Unpress()
                done = False

                engine.engine.draw()
                ika.Video.Blit(self.portw, 0, 15)
                ika.Video.Blit(self.menuw, 0, 135)
                ika.Video.Blit(self.optw, 122, 7)

                self.DrawMenu()

                font3.Print(170, 34, "CONTROL CONFIGURATION")

                font.Print(150, 60,  "ATTACK  -")
                font.Print(150, 75,  "JUMP    -")
                font.Print(150, 90,  "CONFIRM -")
                font.Print(150, 105, "UP      -")
                font.Print(150, 120, "DOWN    -")
                font.Print(150, 135, "LEFT    -")
                font.Print(150, 150, "RIGHT   -")

                font2.Print(240, 60, controls.attackKey)
                font2.Print(240, 72, controls.jumpKey)
                font2.Print(240, 84, controls.confirmKey)
                font2.Print(240, 96, controls.upKey)
                font2.Print(240, 108, controls.downKey)
                font2.Print(240, 120, controls.leftKey)
                font2.Print(240, 132, controls.rightKey)

                if optselected == 0: font4.Print(240, 60, controls.attackKey)
                if optselected == 1: font4.Print(240, 72, controls.jumpKey)
                if optselected == 2: font4.Print(240, 84, controls.confirmKey)
                if optselected == 3: font4.Print(240, 96, controls.upKey)
                if optselected == 4: font4.Print(240, 108, controls.downKey)
                if optselected == 5: font4.Print(240, 120, controls.leftKey)
                if optselected == 6: font4.Print(240, 132, controls.rightKey)

                ika.Video.Blit(self.select2, 147, 56+15*optselected)
                
                ika.Video.ShowPage()

                while not done:
                    ika.Log("blah1")
                    if len(ika.Input.joysticks) > 0:
                       newKey = None
                       newString = ''
                       ika.Log("blah2")
                       for i in range(len(ika.Input.joysticks[0].axes)):
                          if ika.Input.joysticks[0].axes[i].Position() > 0:
                             newKey = ika.Input.joysticks[0].axes[i]
                             newString = 'JOYAXIS'+str(i) +' +'
                             break
                          elif ika.Input.joysticks[0].axes[i].Position() < 0:
                             newKey = ika.Input.joysticks[0].reverseAxes[i]
                             newString = 'JOYAXIS'+str(i) +' -'
                             break
                       for i in range(len(ika.Input.joysticks[0].buttons)):
                          if ika.Input.joysticks[0].buttons[i].Position():
                             newKey = ika.Input.joysticks[0].buttons[i]
                             newString = 'JOY'+str(i)
                             break
                       
                       if newKey:
                         done = True
                         if optselected == 0: 
                            controls.attackKey = newString
                            engine.engine.player.attackKey = newKey
                         elif optselected == 1: 
                            controls.jumpKey = newString
                            engine.engine.player.jumpKey = newKey
                         elif optselected == 2: 
                            controls.confirmKey = newString
                            engine.engine.player.confirmKey = newKey
                         elif optselected == 3: 
                            controls.upKey = newString
                            engine.engine.player.upKey = newKey
                         elif optselected == 4: 
                            controls.downKey = newString
                            engine.engine.player.downKey = newKey
                         elif optselected == 5: 
                            controls.leftKey = newString
                            engine.engine.player.leftKey = newKey
                         elif optselected == 6: 
                            controls.rightKey = newString
                            engine.engine.player.rightKey = newKey                  
                          
                    for i in range(len(controlnames)):
                        if ika.Input.keyboard[controlnames[i]].Pressed():
                            done = True
                            if optselected == 0: 
                               controls.attackKey = controlnames[i]
                               engine.engine.player.attackKey = ika.Input.keyboard[controlnames[i]]
                            elif optselected == 1: 
                               controls.jumpKey = controlnames[i]
                               engine.engine.player.jumpKey = ika.Input.keyboard[controlnames[i]]
                            elif optselected == 2: 
                               controls.confirmKey = controlnames[i]
                               engine.engine.player.confirmKey = ika.Input.keyboard[controlnames[i]]                               
                            elif optselected == 3: 
                               controls.upKey = controlnames[i]
                               engine.engine.player.upKey = ika.Input.keyboard[controlnames[i]]
                            elif optselected == 4: 
                               controls.downKey = controlnames[i]
                               engine.engine.player.downKey = ika.Input.keyboard[controlnames[i]]
                            elif optselected == 5: 
                               scontrols.leftKey = controlnames[i]
                               engine.engine.player.leftKey = ika.Input.keyboard[controlnames[i]]
                            elif optselected == 6: 
                               controls.rightKey = controlnames[i]
                               engine.engine.player.rightKey = ika.Input.keyboard[controlnames[i]]

                    ika.Input.Update()

        self.SlideWindowOut(self.optw)
        self.SlideWindowIn(self.mapw)

        ika.Input.Unpress()
