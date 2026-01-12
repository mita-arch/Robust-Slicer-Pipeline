# pathplanning/vectors.py

import math

def direction_vector(angle_deg: float):
    theta = math.radians(angle_deg)
    return (math.cos(theta), math.sin(theta))

def normal_vector(angle_deg: float):
    theta = math.radians(angle_deg + 90.0)
    return (math.cos(theta), math.sin(theta))

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]
