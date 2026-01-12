# infill/transform.py

import math
from shapely.affinity import rotate

def rotate_geometry(geom, angle_deg: float, origin):
    """
    Rotate geometry about a given origin (centroid).
    """
    return rotate(
        geom,
        angle_deg,
        origin=(origin.x, origin.y),
        use_radians=False
    )
