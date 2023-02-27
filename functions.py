from math import pow


def sign(x):
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0


def lerp(a, b, c):
    return a + (b - a) * c


def lerpDt(a, b, c, delta_time):
    return lerp(a, b, 1 - pow(1 - c, delta_time))


def clamp(v, mi, ma):
    if v > ma:
        return ma
    if v < mi:
        return mi
    return v


def Annulate(val, amount):
    return max(0, abs(val) - amount) * sign(val)


def Approach(fromVal, toVal, amount):
    if abs(toVal - fromVal) < amount:
        return toVal
    else:
        return fromVal + sign(toVal - fromVal) * amount


def SmoothStep(t, t1, t2):
    k = clamp((t - t1) / (t2 - t1), 0, 1)
    return k * k * (3 - 2 * k)


def SmoothLerp(start, end, t, t1, t2):
    return lerp(start, end, SmoothStep(t, t1, t2))


from random import random


def randomRange(a, b):
    return a + (b - a) * random()
