import trimesh
import numpy as np
from typing import Tuple

def load_mesh(file_path: str) -> trimesh.Trimesh:
    """
    Load a triangulated mesh from an STL or OBJ file.

    Parameters
    ----------
    file_path : str

    Returns
    -------
    trimesh.Trimesh
        Loaded mesh object.

    Raises
    ------
    ValueError
        If the mesh is empty or not triangulated.
    """
    mesh = trimesh.load(file_path, force='mesh')
    print(f"Number of mesh faces: {len(mesh.faces)}")


    if len(mesh.faces) > 5000:
    # Reduce to 10% of original count but maintain shape
        mesh = mesh.simplify_quadric_decimation(0.5)
        #mesh = mesh.simplify_quadratic_decimation(20000)

    if mesh.is_empty:
        raise ValueError("Loaded mesh is empty.")

    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("Loaded object is not a valid triangular mesh.")

    return mesh
def compute_z_bounds(mesh: trimesh.Trimesh) -> Tuple[float, float]:
    """
    Compute the minimum and maximum Z values of the mesh
    using its axis-aligned bounding box.

    Parameters
    ----------
    mesh : trimesh.Trimesh

    Returns
    -------
    (z_min, z_max) : Tuple[float, float]
    """
    bounds = mesh.bounds  # shape (2, 3)
    z_min = float(bounds[0][2])
    z_max = float(bounds[1][2])

    return z_min, z_max

