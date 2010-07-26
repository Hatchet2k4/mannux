import ika
import riptiles
import rotateblit
import sparser

#This dict holds ALL the loaded images for sprites.
sprite_images = dict()

class State(list):
    def __init__(self):
        self.id = "None"
        self.layers = []

class Layer(object):
    def __init__(self, frame="None", visible=False, z_index=0, x_offset=0, y_offset=0, rotate=True):
        self.frame    = frame
        self.visible  = False
        self.z_index  = z_index
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.rotate   = rotate

class Frame(object):
    def __init__(self):
        self.id = "None"
        self.image = 0
        self.delay = 0
        self.x_offset = 0
        self.y_offset = 0
        self.next_frame = 0

class FrameIterator(object):
    def __init__(self, frame=None, delay=0, active=False, state=None, layer=None):
        self.frame_counter = delay
        self.cur_frame = frame
        self.cur_state = state
        self.cur_layer = layer
        self.active = active


class Sprite(object):
    def __init__(self, name):

        self.width  = 0                  # width of sprite
        self.height = 0                  # height of sprite
        self.layers = 0                  # number of layers

        self.states = []                 # animation states
        self.frames = []                 # animation frames
        self.frame_iterators = []        # frame iterators

        self.anim_done = False           # for hatchet <3

        self.Load(name)                  # load data and graphics
        self.SetState(self.states[0].id) # default state is the first state

        ## old sprite.py stuff below ##

        #Sprite visibility.
        self.visible = True

        #Set some cool stuff here.
        self.angle = 0
        self.scale = 1.0
        self.color = None
        self.mirror_x = False
        self.mirror_y = False
        self.blendmode = ika.AlphaBlend
        self.forcerotblit = False


    def Draw(self, x, y):
        for iter in self.frame_iterators:
            if iter.active:
                if iter.cur_frame.image != -1:
                    image = self.images[iter.cur_frame.image]
                    cur_x = x + iter.cur_frame.x_offset + iter.cur_layer.x_offset
                    cur_y = y + iter.cur_frame.y_offset + iter.cur_layer.y_offset
                    if self.forcerotblit == False and self.angle == 0 and self.scale == 1.0 \
                    and self.mirror_x == False and self.mirror_y == False:
                        if self.color == None:
                            ika.Video.Blit(image, cur_x, cur_y)
                        else:
                            ika.Video.TintBlit(image, cur_x, cur_y, self.color)
                    else:
                        if iter.cur_layer.rotate == True:
                            rotateblit.RotateBlit(image, cur_x + self.width/2, cur_y + self.height/2, self.angle, self.scale, self.color, self.blendmode, self.mirror_x, self.mirror_y)
                        else:
                            rotateblit.RotateBlit(image, cur_x + self.width/2, cur_y + self.height/2, 0, self.scale, self.color, self.blendmode, self.mirror_x, self.mirror_y)



    def Update(self):
        for iter in self.frame_iterators:
            if iter.active:
                if iter.frame_counter <= 0:
                    for i in self.frames:
                        if iter.cur_frame.next_frame == i.id:
                            iter.cur_frame = i
                            iter.frame_counter = i.delay
                            break
                if iter.frame_counter > 0:
                    iter.frame_counter -= 1

        # horrible hack thingy fix this.
        self.anim_done = 0
        for iter in self.frame_iterators:
            if iter.active:
                if iter.cur_frame.next_frame == iter.cur_frame.id:
                    self.anim_done += 1
                    iter.active == 0
            else:
                self.anim_done += 1
        if self.anim_done >= len(self.frame_iterators):
            self.anim_done = True
        # horrible hack thingy fix this.


    def SetState(self, new_state):
        for cur_state in self.states:
            if cur_state.id == new_state:
                for cur_layer in cur_state.layers:
                    if cur_layer.visible:
                        for cur_frame in self.frames:
                            if cur_frame.id == cur_layer.frame:
                                if  self.frame_iterators[cur_layer.z_index].cur_state != new_state:
                                    self.frame_iterators[cur_layer.z_index].cur_frame     = cur_frame
                                    self.frame_iterators[cur_layer.z_index].cur_state     = new_state
                                    self.frame_iterators[cur_layer.z_index].frame_counter = cur_frame.delay
                                    self.frame_iterators[cur_layer.z_index].active        = True
                                    self.frame_iterators[cur_layer.z_index].cur_layer     = cur_layer
                                break
                    else:
                        self.frame_iterators[cur_layer.z_index].active = False
                        self.frame_iterators[cur_layer.z_index].cur_state = ""
                break


    def Load(self, name):
        sprite_file = sparser.load("sprites/%s.sprite" % name)["sprite"]

        # Load image data
        self.width  = int(sprite_file.get("metadata").value("w", 0))
        self.height = int(sprite_file.get("metadata").value("h", 0))
        self.layers = int(sprite_file.get("metadata").value("layers", 1))
        for i in range(self.layers):
            self.frame_iterators.append(FrameIterator())

        sheet  = sprite_file.get("metadata").value("sheet", None)
        if sheet != None:
            self.LoadImages(sprite_file.get("metadata").get("sheet")[0], self.width, self.height)

        # Load animation states
        for state in sprite_file.get("states"):
            new_state    = State()
            new_state.id = state.get("id")[0]
            for layer in state.get("layers"):
                new_layer = Layer()
                new_layer.frame    = layer.value("frame", "None")
                new_layer.visible  = int(layer.value("visible" , 1))
                new_layer.rotate   = int(layer.value("rotate"  , 1))
                new_layer.z_index  = int(layer.value("z_index" , 0))
                new_layer.x_offset = int(layer.value("x_offset", 0))
                new_layer.y_offset = int(layer.value("y_offset", 0))
                new_state.layers.append(new_layer)
            self.states.append(new_state)

        # Load animation frames
        for frame in sprite_file.get("frames"):
            new_frame = Frame()
            new_frame.id         = frame.get("id")[0]
            new_frame.next_frame = frame.value("next_frame", new_frame.id)
            new_frame.image      = int(frame.value("image", -1))
            new_frame.delay      = int(frame.value("delay", -1))
            new_frame.x_offset   = int(frame.value("x_offset", 0))
            new_frame.y_offset   = int(frame.value("y_offset", 0))

            self.frames.append(new_frame)


    def LoadImages(self, name, w = None, h = None):
        if name not in sprite_images:
            images = riptiles.RipTiles("sprites/%s.png" % name, w, h)
            sprite_images[name] = images
            #LoadImages(name, w, h, span, num)
        self.images = sprite_images[name]



class StaticSprite(object):
    def __init__(self, name):
        self.image = ika.Image("sprites/%s.png" % name)

    def Draw(self, x, y):
        self.image.Blit(x, y)

    def Update(self):
        pass
