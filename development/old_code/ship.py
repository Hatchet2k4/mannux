class Ship(Thing):
   def __init__(self):
      self.ship = [ ika.Image('resources/ship/ship%i.png' % x) for x in (1, 2, 3, 4, 5) ]
      self.frames = [2, 3, 4]
      self.time = 0
      self.x = 370
      self.y = 260
      self.frame = 0
      self.mapy = ika.Map.ywin
      self.mapx = ika.Map.xwin
      self.angle = -30
      self.scale = 1
      self.size = 1
      
                                    #time  x    y    angle size
      #self.keyframes = Interpolate( [0,   370, 260, -30,  0.001] +
      #                              [300, 450, 270,  30,  0.3])

      
      self.cur_x = Interpolate(370, 410, 250) \
                  +Interpolate(410, 440, 350) \
                  +Interpolate(440, 470, 400) \
                  +Interpolate(470, 480, 500)

                  
      self.cur_y = Interpolate(260, 270, 600) \
                  +Interpolate(270, 272, 900)  
                  
                
      self.cur_angle = Interpolate(-30, 20, 300) \
                      +Interpolate(20, 25, 50) \
                      +Interpolate(24, 25, 20) \
                      +Interpolate(25, 24, 30) \
                      +Interpolate(24, 20, 50) \
                      +Interpolate(20, 5, 150) \
                      +Interpolate(5, 0, 150) \
                      +Interpolate(0, 0, 750)

      
      #ika.Log(str(Interpolate(30, 35, 100)))
      
      self.cur_size = Interpolate(0.06, 0.2, 400) \
                     +Interpolate(0.2, 0.5, 400) \
                     +Interpolate(0.5, 0.95, 500) \
                     +Interpolate(0.95, 1, 200)
                     
      self.curframe=0
      
   def update(self):
      self.time += 1
      #self.y += 0.05
      #self.mapy+=0.1      
      
      self.frame = self.frames[(self.time/4) % len(self.frames)]      

      

      if self.time < 1500: #ship coming in
         #self.size =  self.time / 2000.0
         if self.time == 1000:
            self.mapy = ika.Map.ywin
         if self.time > 1000:
            self.mapy+=0.1     
            ika.Map.ywin = int(self.mapy)      
         self.x = self.cur_x[self.time]
         self.y = self.cur_y[self.time]
         self.angle = self.cur_angle[self.time]
         self.size = self.cur_size[self.time]
         #if self.time < 400:
      else:
         self.x = 344
         self.y = 215
            
      #   elif d < 700:
      #      #if angle<20: angle=20
      #      angle = 20 + 5 * math.sin((size - 0.5) * 900 * math.pi / 180)
      #   elif d < 900:
      #      angle = 20 - (size - 0.7) * 100  
      #   RotateBlit(ship[(d / 2) % 4], 275 - (size * 90), 45 + (size * 60), angle, size)
      #elif d < 1500: 
      #   ika.Video.Blit(ship[(d / 2) % 4], 49, 47 + (size - 1) * 100)   
      #elif d < 1520:
      #   ika.Video.Blit(ship[3], 49, 97)
      #elif d < 1540:
      #   ika.Video.Blit(ship[4], 49, 97)
      #else:
      #   ika.Video.Blit(ship[5], 49, 97)

      #finish at: 344, 235 (+136, +57)

   def draw(self):
      if self.time < 1500:
         #self.ship[self.frame].Blit(self.x, self.y)
         RotateBlit(self.ship[self.frame], self.x - ika.Map.xwin, self.y - ika.Map.ywin, self.angle, self.size)
      else: 
         ika.Video.Blit(self.ship[self.frame], self.x-ika.Map.xwin, self.y-ika.Map.ywin)
