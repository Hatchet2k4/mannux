#!/usr/bin/env python

"""Handy functions for manipulating velocity vectors."""


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


#def delta(a, b):
#   return abs(a - b)
