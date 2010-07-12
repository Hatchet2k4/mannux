import system
import ika
import engine
import math
from rotateblit import RotateBlit


def ShipLanding():
	bg=ika.Image('bg_planetstars.png')
	leftdoor=ika.Image('leftdoor.png')
	rightdoor=ika.Image('rightdoor.png')
	d=0

	def DrawSpace():
		ika.Video.DrawRect(0, 0, ika.Video.xres, ika.Video.yres, ika.RGB(0,0,0), 1)
		ika.Video.Blit(bg, 70, 40)	
		if d < 1300:
			ika.Video.Blit(leftdoor, -30, 40)
			ika.Video.Blit(rightdoor, 288, 40)
		elif d < 1830:
			ika.Video.Blit(leftdoor, -30 + ((d - 1300) / 5), 40)
			ika.Video.Blit(rightdoor, 287 - ((d - 1300) / 5), 40)
		else:
			ika.Video.Blit(leftdoor, 75, 40)		
			ika.Video.Blit(rightdoor, 182, 40)

	ika.Map.Switch('dock.map')

	ship = [ ika.Image('tab_ship%i.png' % x) for x in (1, 2, 3, 2, 4, 5) ]
	
	done = False
	ika.Map.xwin, ika.Map.ywin = 80, 16
	
	t = ika.GetTime()
	ika.HookRetrace(DrawSpace)
	angle = -30
	
	while d < 2000:
		d = ika.GetTime() - t
		
		size = d / 1000.0

		ika.Map.Render()	
				
		if d < 1000: #ship coming in
			if d < 500:
				angle = -30 + size * 100	
			elif d < 700:
				#if angle<20: angle=20
				angle = 20 + 5 * math.sin((size - 0.5) * 900 * math.pi / 180)
			elif d < 900:
				angle = 20 - (size - 0.7) * 100	
			RotateBlit(ship[(d / 2) % 4], 275 - (size * 90), 45 + (size * 60), angle, size)
		elif d < 1500: 
			ika.Video.Blit(ship[(d / 2) % 4], 49, 47 + (size - 1) * 100)	
		elif d < 1520:
			ika.Video.Blit(ship[3], 49, 97)
		elif d < 1540:
			ika.Video.Blit(ship[4], 49, 97)
		else:
			ika.Video.Blit(ship[5], 49, 97)
			#s = ika.Entity(49 + 80, 97 + 16, "ship.ika-sprite")
		
		ika.Input.Update()	
		if ika.Input['ESCAPE'].Position():
			done = True
		ika.Video.ShowPage()

	engine.FadeOut()

	ika.UnhookRetrace(DrawSpace)
