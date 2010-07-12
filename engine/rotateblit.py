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


def rotate_blit(image, cx, cy, angle, scale=1.0, blendmode=ika.AlphaBlend):
    # To do: use a matrix to make this more efficient.
    angle = angle * math.pi / 180
    halfx = image.width / 2
    halfy = image.height / 2
    p = [_rotate_point(-halfx, -halfy, angle),
         _rotate_point( halfx, -halfy, angle)]
    p += [[-i for i in p[0]], [-i for i in p[1]]]
    p = [(x * scale + cx, y * scale + cy) for x, y in p]
    ika.Video.DistortBlit(image, *p + [blendmode])
