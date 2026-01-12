from pathlib import Path
from math import hypot
from shapely.geometry import Polygon, MultiPolygon
from polygon_processing.topology_graph import TopologyGraph
from polygon_processing.polygon_builder import build_polygons_from_loops
from output_helpers.save_data import prepare_layer_dir
from output_helpers.visualise import visualize_polygon
from infill.infill_engine import generate_infill_for_polygon
from infill.parameters import InfillParams
from infill.visualise_infill import visualize_polygon_with_infill 
from pathplanning.path_engine import connect_infill_segments
from pathplanning.visualise_path import visualize_connected_infill
from pathplanning.parameters import ConnectorParams

# =====================================================
# Utility helpers
# =====================================================
def centroid(poly: Polygon):
    c = poly.centroid
    return (c.x, c.y)


def dist(a, b):
    return hypot(a[0] - b[0], a[1] - b[1])


def order_islands_nearest(islands):
    """
    Simple nearest-neighbor island ordering.
    """
    if not islands:
        return []

    ordered = [islands[0]]
    remaining = islands[1:]

    while remaining:
        last_c = centroid(ordered[-1])
        next_island = min(
            remaining,
            key=lambda p: dist(last_c, centroid(p))
        )
        ordered.append(next_island)
        remaining.remove(next_island)

    return ordered

# =====================================================
# DEBUG SINGLE SLICE
# =====================================================
def debug_single_slice(
    slices,
    output_root: Path,
    model_name: str,
    slice_id: int | None = None,
):
    if slice_id is None:
        slice_id = len(slices) // 2

    layer = slices[slice_id]

    print(f"\n[DEBUG] Slice index = {slice_id}, Z = {layer.z_height:.4f}")

    debug_root = output_root / "debug" / model_name
    layer_dir = prepare_layer_dir(
        base_output=debug_root,
        model_name=model_name,
        layer_idx=slice_id,
        z_height=layer.z_height,
    )

    # -------------------------------------------------
    # Topology → Polygon
    # -------------------------------------------------
    topo = TopologyGraph(
        segments=[
            ((seg.p0[0], seg.p0[1]), (seg.p1[0], seg.p1[1]))
            for seg in layer.geometry_2d
        ],
        tol=1e-5,
    )

    loops = topo.extract_loops()

    result = build_polygons_from_loops(
        loops=loops,
        nozzle_width=0.4,
    )

    geometry = result["geometry"]
    if geometry is None:
        print("[DEBUG] No valid geometry")
        return

    visualize_polygon(
        geometry,
        title="Final Polygon",
        save_path=layer_dir / "final_polygon.png",
        show=True,
    )

    # -------------------------------------------------
    # Extract islands
    # -------------------------------------------------
    if isinstance(geometry, MultiPolygon):
        islands = list(geometry.geoms)
    else:
        islands = [geometry]

    islands = order_islands_nearest(islands)
    print(f"[DEBUG] Islands detected: {len(islands)}")

    # -------------------------------------------------
    # Infill parameters (alternate direction)
    # -------------------------------------------------
    infill_params = InfillParams(
        spacing=2.0,
        angle_deg=45.0 if slice_id % 2 == 0 else 135.0,
    )

    connector_params = ConnectorParams(
        retract_cost=5.0,
        boundary_factor=1.3,
        max_boundary_ratio=3.0,
    )

    all_raw_infill = []
    all_connected_infill = []

    # -------------------------------------------------
    # Process each island independently
    # -------------------------------------------------
    for idx, island in enumerate(islands):
        print(f"[DEBUG] Processing island {idx}")

        # -------- Part A: raw infill --------
        island_infill = generate_infill_for_polygon(
            island,
            infill_params,
        )
        all_raw_infill.extend(island_infill)

        # -------- Part B: connected infill --------
        island_connected = connect_infill_segments(
            infill_segments=island_infill,
            polygon=island,                      
            spacing=infill_params.spacing,
            angle_deg=infill_params.angle_deg,
            params=connector_params,
        )
        all_connected_infill.extend(island_connected)

    # -------------------------------------------------
    # Visualization
    # -------------------------------------------------
    visualize_polygon_with_infill(
        geometry=geometry,
        infill_segments=all_raw_infill,
        title="Polygon + Infill (Part A)",
        save_path=layer_dir / "polygon_with_infill.png",
        show=True,
    )

    visualize_connected_infill(
        geometry=geometry,
        connected_segments=all_connected_infill,
        title="Polygon + Connected Infill (Part B)",
        save_path=layer_dir / "polygon_with_connected_infill.png",
        show=True,
    )

    print(f"[DEBUG] Debug output saved to: {layer_dir}")
