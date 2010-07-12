import ika

# Some neat-O special effects

def blurScreen(factor):
    '''Grabs the screen, blurs it up a bit, then returns the image.
    Returns tinier images.  Use scaleblit to bring them back.

    Grossly inefficient.
    '''

    w = int(ika.Video.xres * factor)
    h = int(ika.Video.yres * factor)

    bleh = ika.Video.GrabImage(0, 0, ika.Video.xres, ika.Video.yres)
    ika.Video.ScaleBlit(bleh, 0, 0, w, h, ika.Opaque)
    return ika.Video.GrabImage(0, 0, w, h)

def createBlurImages(inc=0.1, maxblur=2):
    BLEH = 1
    images = []
    i = 1.0
    while i < maxblur:
        img = blurScreen(1.0 / i)
        images.append(img)
        ika.Video.ScaleBlit(img, 0, 0, ika.Video.xres, ika.Video.yres, ika.Opaque)

        ika.Video.ScaleBlit(img, -BLEH, -BLEH, ika.Video.xres + BLEH * 2, ika.Video.yres + BLEH * 2)

        i += inc

    return images

def blurOut():
    wasteOfMemory = []

    i = 1.0
    while i < 2:
        img = blurScreen(1.0 / i)
        wasteOfMemory.append(img)
        ika.Video.ScaleBlit(img, 0, 0, ika.Video.xres, ika.Video.yres, ika.Opaque)
        ika.Video.ShowPage()
        ika.Input.Update()
        ika.Delay(3)

        BLEH = 1
        ika.Video.ScaleBlit(img, -BLEH, -BLEH, ika.Video.xres + BLEH * 2, ika.Video.yres + BLEH * 2)
        ika.Video.DrawRect(0, 0, ika.Video.xres, ika.Video.yres, ika.RGB(0, 0, 0, 2), True)

        i += 0.1

    return wasteOfMemory

def blurIn(wasteOfMemory):

    for img in wasteOfMemory[::-1]:
        ika.Video.ScaleBlit(img, 0, 0, ika.Video.xres, ika.Video.yres, ika.Opaque)
        ika.Video.ShowPage()
        ika.Input.Update()
        ika.Delay(3)

def crossFade(time, startImage = None, endImage = None):
    '''Crossfades!  Set either startImage or endImage, or both.'''

    assert startImage or endImage, "Don't be a retard."

    if not startImage:
        startImage = ika.Video.GrabImage(0, 0, ika.Video.xres, ika.Video.yres)
    if not endImage:
        endImage = ika.Video.GrabImage(0, 0, ika.Video.xres, ika.Video.yres)

    endTime = ika.GetTime() + time
    now = ika.GetTime()
    while now < endTime:
        opacity = (endTime - now) * 255 / time
        ika.Video.ClearScreen()
        ika.Video.Blit(endImage, 0, 0)
        ika.Video.TintBlit(startImage, 0, 0, ika.RGB(255, 255, 255, opacity))
        ika.Video.ShowPage()
        ika.Input.Update()

        now = ika.GetTime()

def blurFade(time, startImages, endImages):
    startTime = ika.GetTime()
    endTime = ika.GetTime() + time
    now = startTime
    while now < endTime:
        imageIndex = (now - startTime) * len(startImages) / time
        opacity = (now - startTime) * 255 / time
        startfade = ika.RGB(255, 255, 255, 255 - opacity)
        endfade = ika.RGB(255, 255, 255, opacity)

        ika.Video.TintDistortBlit(
            startImages[imageIndex],
            (0, 0, startfade), (ika.Video.xres, 0, startfade),
            (ika.Video.xres, ika.Video.yres, startfade),
            (0, ika.Video.yres, startfade))
        ika.Video.TintDistortBlit(
            endImages[-(imageIndex+1)],
            (0, 0, endfade), (ika.Video.xres, 0, endfade),
            (ika.Video.xres, ika.Video.yres, endfade),
            (0, ika.Video.yres, endfade))

        ika.Video.ShowPage()
        ika.Input.Update()
        now = ika.GetTime()
