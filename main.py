from pathlib import Path
from tqdm import tqdm
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
from debug_slicer import debug_single_slice

# ------------------------
# Input / output paths
# -------------------------
stl_path = "C:\\Users\\hp\\Downloads\\Main\\Week 1\\Models\\cluster.stl"
output_root = Path("output")
model_name = Path(stl_path).stem

print("\n[1/5] Loading mesh...")
mesh = load_mesh(str(stl_path))

# -------------------------
# Slicing 
# -------------------------
print("\n[2/5] Slicing mesh into layers...")
slices = slice_mesh(
    mesh=mesh,
    layer_height=0.2,
    first_layer_height=0.3,
)

if not slices:
    raise RuntimeError("No slices generated")

print(f"Generated {len(slices)} slices")


# =================================================
#DEBUG SINGLE SLICE
# ================================================

debug_single_slice(
    slices=slices,
    output_root=output_root,
    model_name=model_name,
)

# =================================================
#FULL MODEL 3D VISUALIZATION
# =================================================
print("\n[5/5] Processing all layers for 3D visualization...")

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
    # Visualize segments
    # -------------------------
    visualize_segments(
        layer.raw_curves,
        title="Raw Segments",
        show=False,
    )

    visualize_segments(
        layer.geometry_2d,
        title="Cleaned Segments",
        show=False,
    )

    # -------------------------
    # Topology
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

    if geometry:
        visualize_polygon(
        geometry,
        title=f"Final Polygon – Layer {layer_idx}",
        save_path=layer_dir / "final_polygon.png",
        show=False,
    )

    save_outer_boundaries(
        geometry,
        layer_dir / "outer_boundaries.png",
    )

    save_inner_boundaries(
        geometry,
        layer_dir / "inner_boundaries.png",
    )

    # Collect for 3D plot
    layer_geometries.append((layer.z_height, geometry))

    # -------------------------
    # Metadata
    # -------------------------
    save_layer_metadata(
        layer,
        loops,
        result,
        layer_dir / "metadata.json",
    )

model_dir = output_root / model_name
model_dir.mkdir(parents=True, exist_ok=True)

visualize_3d_layers(
    layer_geometries=layer_geometries,
    title=f"3D Slice Stack – {model_name}",
    save_path=model_dir / "3d_output.png",
)
