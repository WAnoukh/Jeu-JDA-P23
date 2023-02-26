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
