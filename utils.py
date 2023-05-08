import math

def coordinates_to_cartesian(radius: float, latitude: float, longitude: float):
    """
    Convert spherical coordinates to cartesian coordinates
    """
    x = radius * math.sin(latitude) * math.sin(longitude)
    y = radius * math.cos(latitude)
    z = radius * math.sin(latitude) * math.cos(longitude)
    return x, y, z