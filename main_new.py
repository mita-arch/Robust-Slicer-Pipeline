from pathlib import Path
from tqdm import tqdm
from math import hypot
from shapely.geometry import Polygon, MultiPolygon
from slicer.mesh_io import load_mesh
from slicer.slicer_engine import slice_mesh
from polygon_processing.topology_graph import TopologyGraph
from polygon_processing.polygon_builder import build_polygons_from_loops
from output_helpers.save_data import (
    prepare_layer_dir,
    save_outer_boundaries,
    save_inner_boundaries,
    save_layer_metadata,
)
from output_helpers.visualise import (
    visualize_segments,
    visualize_loops,
    visualize_polygon,
)
from output_helpers.visualise_3d import visualize_3d_layers
from infill.infill_engine import generate_infill_for_polygon
from infill.parameters import InfillParams
from infill.visualise_infill import visualize_polygon_with_infill
from pathplanning.path_engine import connect_infill_segments
from pathplanning.visualise_path import visualize_connected_infill
from pathplanning.parameters import ConnectorParams


# =====================================================
# Input / output paths
# =====================================================
stl_path = "C:\\Users\\hp\\Downloads\\Main\\Week 1\\Models\\cluster.stl"
output_root = Path("output")
model_name = Path(stl_path).stem

print("\n[1/5] Loading mesh...")
mesh = load_mesh(str(stl_path))

# =====================================================
# Slicing
# =====================================================
print("\n[2/5] Slicing mesh into layers...")
slices = slice_mesh(
    mesh=mesh,
    layer_height=0.2,
    first_layer_height=0.3,
)

if not slices:
    raise RuntimeError("No slices generated")

print(f"Generated {len(slices)} slices")

# =====================================================
# Parameters (GLOBAL)
# =====================================================
infill_params = InfillParams(
    spacing=2.0,
    angle_deg=45.0,
)

connector_params = ConnectorParams(
    retract_cost=5.0,
    boundary_factor=1.3,
    max_boundary_ratio=3.0,
)

# =====================================================
# FULL PIPELINE – ALL LAYERS
# =====================================================
print("\n[3/5] Processing all layers...")

layer_geometries = []

for layer_idx, layer in enumerate(
    tqdm(slices, desc="Processing layers", unit="layer")
):
    if not layer.geometry_2d:
        continue

    # -------------------------
    # Layer directory
    # -------------------------
    layer_dir = prepare_layer_dir(
        output_root,
        model_name,
        layer_idx,
        layer.z_height,
    )


    # -------------------------
    # Topology → loops
    # -------------------------
    topo = TopologyGraph(
        segments=[
            ((seg.p0[0], seg.p0[1]), (seg.p1[0], seg.p1[1]))
            for seg in layer.geometry_2d
        ],
        tol=1e-5,
    )

    loops = topo.extract_loops()

    visualize_loops(
        loops,
        title="Extracted Loops",
        show=False,
    )

    # -------------------------
    # Polygon building
    # -------------------------
    result = build_polygons_from_loops(
        loops=loops,
        nozzle_width=0.4,
    )

    geometry = result["geometry"]
    if geometry is None:
        continue

    visualize_polygon(
        geometry,
        title=f"Final Polygon – Layer {layer_idx}",
        save_path=layer_dir / "final_polygon.png",
        show=False,
    )

    # -------------------------
    # Infill + Path planning (NEW)
    # -------------------------
    if isinstance(geometry, MultiPolygon):
        islands = list(geometry.geoms)
    else:
        islands = [geometry]

    all_raw_infill = []
    all_connected_infill = []

    for island in islands:
        island_infill = generate_infill_for_polygon(
            island,
            infill_params,
        )
        all_raw_infill.extend(island_infill)

        island_connected = connect_infill_segments(
            infill_segments=island_infill,
            polygon=island,
            spacing=infill_params.spacing,
            angle_deg=infill_params.angle_deg,
            params=connector_params,
        )
        all_connected_infill.extend(island_connected)

    visualize_polygon_with_infill(
        geometry=geometry,
        infill_segments=all_raw_infill,
        title=f"Polygon + Infill – Layer {layer_idx}",
        save_path=layer_dir / "infill.png",
        show=False,
    )

    visualize_connected_infill(
        geometry=geometry,
        connected_segments=all_connected_infill,
        title=f"Polygon + Connected Infill – Layer {layer_idx}",
        save_path=layer_dir / "connected_infill.png",
        show=False,
    )

    # -------------------------
    # Metadata
    # -------------------------
    save_layer_metadata(
        layer,
        loops,
        result,
        layer_dir / "metadata.json",
    )

    # Collect for 3D visualization
    layer_geometries.append((layer.z_height, geometry))


# =====================================================
# 3D Visualization
# =====================================================
print("\n[5/5] Generating 3D visualization...")

model_dir = output_root / model_name
model_dir.mkdir(parents=True, exist_ok=True)

visualize_3d_layers(
    layer_geometries=layer_geometries,
    title=f"3D Slice Stack – {model_name}",
    save_path=model_dir / "3d_output.png",
)
