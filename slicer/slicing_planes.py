def generate_slicing_planes(
    z_min: float,
    z_max: float,
    layer_height: float,
    first_layer_height: float,
    epsilon: float = 1e-6
) -> list[float]:
    """
    Generate horizontal slicing planes for a 3D mesh.

    Parameters
    ----------
    z_min : float
        Minimum Z of the mesh bounding box.
    z_max : float
        Maximum Z of the mesh bounding box.
    layer_height : float
        Regular slicing layer height.
    first_layer_height : float
        Height of the first layer (elephant foot control).
    epsilon : float
        Small offset to avoid coplanar slicing at the top surface.

    Returns
    -------
    list[float]
        List of Z heights where slicing planes should be placed.
    """

    if layer_height <= 0 or first_layer_height <= 0:
        raise ValueError("Layer heights must be positive values.")

    if z_max <= z_min:
        raise ValueError("Invalid mesh Z bounds.")

    planes = []

    # ---- First layer (elephant foot control) ----
    current_z = z_min + first_layer_height
    planes.append(current_z)

    # ---- Regular layers ----
    while True:
        next_z = current_z + layer_height

        # Stop before hitting the top exactly
        if next_z >= z_max - epsilon:
            break

        planes.append(next_z)
        current_z = next_z

    # ---- Handle remainder at top (threshold + clamp) ----
    remainder = z_max - planes[-1]

    if remainder > (layer_height * 0.5):
        # Add an extra thin slice just below the top
        planes.append(z_max - epsilon)
    else:
        # Clamp last slice to the very top
        planes[-1] = z_max - epsilon

    return planes

from typing import List
import numpy as np
import trimesh

from slicer.slicer_layer import SliceLayer, Segment3D, Segment2D

EPSILON = 1e-6
