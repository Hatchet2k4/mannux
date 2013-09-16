#!/usr/bin/env python

"""Handy functions for manipulating velocity vectors."""
import math

def increase_magnitude(value, amount):
    if value >= 0:
        return value + amount
    else:
        return value - amount


def decrease_magnitude(value, amount):
    if abs(value) > amount:
        return increase_magnitude(value, -amount)
    else:
        return 0


def clamp(value, lowest, highest):
    return max(lowest, min(value, highest))

def distance(x1,y1,x2,y2):
    sq1 = (x1-x2)*(x1-x2)
    sq2 = (y1-y2)*(y1-y2)
    return math.sqrt(sq1 + sq2)

#def delta(a, b):
#   return abs(a - b)
