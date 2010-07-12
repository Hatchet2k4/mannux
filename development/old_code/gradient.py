# Gradient renderer
#  --tSB

import ika

#--------------------------------------------------------------------

def _MixColours(c1,c2,weight):
   r1, g1, b1, a1 = ika.GetRGB(c1)
   r2, g2, b2, a2 = ika.GetRGB(c2)

   r = (r1 * (1 - weight)) + (r2 * weight)
   g = (g1 * (1 - weight)) + (g2 * weight)
   b = (b1 * (1 - weight)) + (b2 * weight)
   a = (a1 * (1 - weight)) + (a2 * weight)

   return ika.RGB(r,g,b,a)

#--------------------------------------------------------------------

def MakeGradient(width,height,c1,c2,c3,c4):
   canvas = ika.Canvas(width, height)

   for y in range(height):
      xstart = _MixColours(c1, c3, float(y) / height)
      xend = _MixColours(c2, c4, float(y) / height)

      for x in range(width):
         colour = _MixColours(xstart, xend, 1.0 * x / width)
         canvas.SetPixel(x, y, colour)

   return canvas

#--------------------------------------------------------------------

