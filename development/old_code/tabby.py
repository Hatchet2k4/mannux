    def CheckObstructions(self):
        x = round(self.x)
        y = int(self.y)
        layer = self.layer

        self.left_wall = self.CheckVLine(x-2+self.vx, y, y+self.sprite.hotheight-1)
        self.right_wall = self.CheckVLine(x+self.sprite.hotwidth+2+self.vx, y, y+self.sprite.hotheight-1)
        
        if self.left_wall and not self.phantom:
            tilex = int((x+1) / ika.Map.tilewidth)
            self.x = tilex * ika.Map.tilewidth
            self.vx = max(0, self.vx)
        if self.right_wall and not self.phantom:
            tilex = int(x/ika.Map.tilewidth)
            self.x = (tilex+1) * ika.Map.tilewidth - ((ika.Map.tilewidth - self.sprite.hotwidth) % ika.Map.tilewidth) 
            self.vx = min(0, self.vx)      
        
        self.ceiling = self.CheckHLine(x, y+self.vy-1, x+self.sprite.hotwidth-1)
        self.floor = self.CheckHLine(x,y+int(self.sprite.hotheight+self.vy), x+self.sprite.hotwidth-1)   
        
        if not self.phantom and self.floor and not self.ceiling:
            # find the tile that the entity will be standing on,
            # and set it to be standing exactly on it:                                    
            tiley = int((self.y + self.height + self.vy+1) / ika.Map.tileheight)
            self.y = (tiley) * ika.Map.tileheight - self.height 
            self.vy = 0
        if not self.phantom and self.ceiling:
            # find the tile that the entity will be standing on,
            # and set it to be standing exactly on it:
            if self.vy != 0:
               tiley = int((y+2) / ika.Map.tileheight)
               self.y = tiley * ika.Map.tileheight + 1
               self.vy = 0
        
        #x = round(self.x)
        #y = round(self.y)        
        #check for entity collisions
        ent = self.DetectCollision()
        if ent is not None and ent.touchable:
           ent.touch(self)
        
        
        #and ent.sprite.isobs:
        #    if ent.x <= x + 2: self.left_wall = True
        #    if ent.x >= x + self.sprite.hotwidth -2: self.right_wall = True
        #    if ent.y <= y + 2: self.ceiling = False #enemies shouldn't be able to climb on you
        #    if ent.y >= y + self.sprite.hotheight -2: self.floor = False #you shouldn't be able to climb on enemies
        # the previous cases can be specialized later with another entity flag.  -- Thrasher

        # You shouldn't get obstructed by enemies, they should just hurt you.
