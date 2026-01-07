import trimesh
from typing import List
from tqdm import tqdm
from collections import defaultdict
from slicer.slicer_layer import SliceLayer, Segment3D
from slicer.mesh_io import compute_z_bounds
from slicer.slicing_planes import generate_slicing_planes
from slicer.intersection import _intersect_triangle_plane
from slicer.cleanup import cleanup_raw_segments
EPSILON = 1e-6
# -------------------------------------------------
# Full Mesh Slicing Integration
# -------------------------------------------------
def z_to_layer_index(
    z: float,
    z_min: float,
    layer_height: float,
    first_layer_height: float,
    num_layers: int,
) -> int:
    if z < z_min + first_layer_height:
        return 0
    idx = int((z - (z_min + first_layer_height)) / layer_height) + 1
    return max(0, min(idx, num_layers - 1))

def slice_mesh(
    mesh: trimesh.Trimesh,
    layer_height: float,
    first_layer_height: float
) -> List[SliceLayer]:
    """
    Slice a mesh into horizontal layers using triangle bucketing
    (fast, Cura-like approach).
    """
    # -------------------------
    # Generate slicing planes
    # -------------------------
    z_min, z_max = compute_z_bounds(mesh)
    planes = generate_slicing_planes(
        z_min, z_max, layer_height, first_layer_height
    )

    triangles = mesh.triangles
    num_layers = len(planes)

    # -------------------------
    # Bucket triangles by layer
    # -------------------------
    layer_triangles = defaultdict(list)

    for tri in triangles:
        tz_min = float(tri[:, 2].min())
        tz_max = float(tri[:, 2].max())

        i0 = z_to_layer_index(
            tz_min, z_min, layer_height, first_layer_height, num_layers
        )
        i1 = z_to_layer_index(
            tz_max, z_min, layer_height, first_layer_height, num_layers
        )

        for layer_idx in range(i0, i1 + 1):
            layer_triangles[layer_idx].append(tri)

    # -------------------------
    # Slice layers
    # -------------------------
    layers: List[SliceLayer] = []

    for layer_idx, plane_z in enumerate(
        tqdm(planes, desc="Slicing layers", unit="layer")
    ):
        raw_segments: List[Segment3D] = []

        for tri in layer_triangles.get(layer_idx, []):
            raw_segments.extend(
                _intersect_triangle_plane(tri, plane_z)
            )

        cleaned_2d = cleanup_raw_segments(raw_segments)

        layers.append(
            SliceLayer(
                z_height=plane_z,
                raw_curves=raw_segments,
                geometry_2d=cleaned_2d,
            )
        )

    return layers
