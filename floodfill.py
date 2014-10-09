'''A simple recursive flood fill tool. Easy to use, simply import
it into ikaMap, turn on ikaMap's script mode, select the tile 
you want to fill with, and click. :)

Because it's recursive, if you're filling into a large area, 
and your system doesn't have a lot of memory, it might crash. 
Not to mention take a long time to run. So be conservative 
with the size of the areas you're filling.

Special thanks to Zaratustra and andy for help with the 
original algorithm.

-Hatchet
hatchet2k2@hotmail.com
'''

import ikamap
import sys

rtile = w = h = layer = tile = 0
depth = maxdepth = recursions = 0

def Fill(tx, ty):
   global depth, maxdepth, recursions
   recursions += 1
   depth += 1
   if depth>maxdepth: maxdepth = depth #just a way of keeping track how far we recursed
      
   if depth == sys.getrecursionlimit()-1: #recursion limit reached      
      sys.setrecursionlimit (sys.getrecursionlimit()*2) #double the recursion limit
      ikamap.Log("Recursion limit reached. Limit now set to "+str(sys.getrecursionlimit())) 
   
   left = right = tx #left and right edges of the horizontal line to recurse from

   for x in range(tx, w): #drawing a line to the right of the given point         
      if ikamap.Map.GetTile(x,ty,layer) == rtile or ikamap.Map.GetTile(x,ty,layer) == tile: #tile is fillable, fill it.
         ikamap.Map.SetTile(x,ty,layer,tile)
         right+=1
      else: 
         if x != tx:         
            break #hit a tile that doesn't match, stop here.

   for x in range(tx-1, -1, -1): #drawing a line to the left      
      if ikamap.Map.GetTile(x,ty,layer) == rtile or ikamap.Map.GetTile(x,ty,layer) == tile: #tile is fillable, fill it.
         ikamap.Map.SetTile(x,ty,layer,tile)
         left -= 1
      else:  
         #left = x+1
         break #hit a tile that doesn't match, stop here.

   for x in range(left, right): #search the line for possible paths up or down
      if ty-1>=0 and ikamap.Map.GetTile(x,ty-1,layer) == rtile:
         Fill(x,ty-1) #upwards
      if ty+1<h and ikamap.Map.GetTile(x,ty+1,layer) == rtile:
         Fill(x,ty+1) #recurse downwards
   
   depth -= 1

def OnMouseDown(mx, my): #called when the mouse is clicked
   global rtile, w, h, layer, tile, maxdepth, recursions

   maxdepth = recursions = 0

   tx, ty = ikamap.Editor.MapToTile(mx, my)  #gets the x/y position in tiles of where we clicked.
   layer = ikamap.Editor.curlayer            #get the current layer that we will be filling to
   w, h = ikamap.Map.GetLayerSize(layer)     #width and height of the layer
   rtile = ikamap.Map.GetTile(tx, ty, layer) #tile we are replacing
   tile = ikamap.Editor.curtile              #tile we are filling with
   
   Fill(tx,ty)                            #start filling!
   
   
   #uncomment for recursion info
   ikamap.Log("Maximum recursion depth: "+str(maxdepth))
   ikamap.Log("Number of recursions: "+str(recursions))
   
     
   

