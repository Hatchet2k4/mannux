#!/usr/bin/env python

import ika
import math


def _rotate_point(x, y, angle):
    r = math.hypot(x, y)
    theta = math.atan(float(y) / float(x))
    if x < 0:
        theta += math.pi
    theta += angle
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y


def RotateBlit(image, cx, cy, angle, scale=1.0, color=None, blendmode=ika.AlphaBlend, mirror_x=False, mirror_y=False, ):
    # To do: use a matrix to make this more efficient.
    while angle < 0: angle+=360
    while angle > 0: angle-=360

    angle = angle * math.pi / 180.0
    halfx = image.width / 2.0
    halfy = image.height / 2.0

    p=[]
    if mirror_y == False and mirror_x == False:
        p = [_rotate_point(-halfx, -halfy, angle),
             _rotate_point( halfx, -halfy, angle)]
    elif mirror_y == True and mirror_x == False:
        p = [_rotate_point(-halfx, halfy, angle),
             _rotate_point( halfx, halfy, angle)]
    elif mirror_y == False and mirror_x == True:
        p = [_rotate_point(halfx, -halfy, angle),
             _rotate_point(-halfx, -halfy, angle)]
    else:
        p = [_rotate_point(halfx, halfy, angle),
             _rotate_point(-halfx, halfy, angle)]


    p += [[-i for i in p[0]], [-i for i in p[1]]]

    if color == None:
        p = [(int(x * scale + cx), int(y * scale + cy)) for x, y in p]
        ika.Video.DistortBlit(image, *p + [blendmode])
    else:
        p = [(int(x * scale + cx), int(y * scale + cy), color) for x, y in p]
        ika.Video.TintDistortBlit(image, *p + [blendmode])
