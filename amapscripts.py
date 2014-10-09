'''Map script to turn grey tiles on
Automap layer to Blue tiles on layer 2'''

import ikamap
import sys

def MakeMapBlue():
    for x in range(50):
        for y in range(50):
            t = ikamap.Map.GetTile(x, y, 0)
            if t>0:
                ikamap.Map.SetTile(x,y,1,t+126)

def OnMouseDown(mx,my):
    ikamap.MessageBox('Test!')
    MakeMapBlue()
