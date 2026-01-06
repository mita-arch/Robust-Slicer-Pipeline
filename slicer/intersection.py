import numpy as np
from typing import List

from slicer.slicer_layer import Segment3D

# -------------------------------------------------
# Triangle–Plane Intersection (with AABB filtering)
# -------------------------------------------------
EPSILON = 1e-6
def _classify_vertex(z: float, plane_z: float) -> int:
    if z > plane_z + EPSILON:
        return 1     # above
    elif z < plane_z - EPSILON:
        return -1    # below
    else:
        return 0     # coplanar


def _intersect_triangle_plane(triangle: np.ndarray, plane_z: float) -> List[Segment3D]:
    """
    Intersect a single triangle with a horizontal plane.
    Returns zero or one Segment3D.
    """

    verts = triangle
    classes = [_classify_vertex(v[2], plane_z) for v in verts]

    # Reject triangles fully on one side or fully coplanar
    if all(c >= 0 for c in classes) or all(c <= 0 for c in classes):
        return []

    points = []

    for i in range(3):
        v0 = verts[i]
        v1 = verts[(i + 1) % 3]
        c0 = classes[i]
        c1 = classes[(i + 1) % 3]

        if c0 == c1:
            continue

        if c0 == 0:
            points.append(tuple(v0))
        elif c1 == 0:
            points.append(tuple(v1))
        else:
            t = (plane_z - v0[2]) / (v1[2] - v0[2])
            x = v0[0] + t * (v1[0] - v0[0])
            y = v0[1] + t * (v1[1] - v0[1])
            points.append((x, y, plane_z))

    if len(points) == 2:
        return [Segment3D(points[0], points[1])]

    return []