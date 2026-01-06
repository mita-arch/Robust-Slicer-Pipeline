# debug_slice.py

from pathlib import Path
import matplotlib.pyplot as plt

from polygon_processing.topology_graph import TopologyGraph
from polygon_processing.polygon_builder import build_polygons_from_loops
from output_helpers.save_data import (
    prepare_layer_dir,
    save_outer_boundaries,
    save_inner_boundaries,
)
from output_helpers.visualise import (
    visualize_segments,
    visualize_loops,
    visualize_polygon,
)


def debug_single_slice(
    slices,
    output_root: Path,
    model_name: str,
    slice_id: int | None = None,
):
    """
    Interactive debug for a single slice.
    Shows plots AND saves them to output/debug/.
    """

    if slice_id is None:
        slice_id = len(slices) // 2
        #len(slices) // 2

    layer = slices[slice_id]
    layer_z = layer.z_height

    print(f"\n[DEBUG] Slice index = {slice_id}, Z = {layer.z_height:.4f}")
    print(f"Raw segments     : {len(layer.raw_curves)}")
    print(f"Cleaned segments : {len(layer.geometry_2d)}")

    debug_root = output_root / "debug" / model_name
    layer_dir = prepare_layer_dir(
    base_output=debug_root,
    model_name=model_name,
    layer_idx=slice_id,
    z_height=layer.z_height,
)


    # -------------------------
    # Raw segments
    # -------------------------
    visualize_segments(
        [
            type(layer.geometry_2d[0])(
                (s.p0[0], s.p0[1]),
                (s.p1[0], s.p1[1]),
            )
            for s in layer.raw_curves
        ] if layer.geometry_2d else [],
        "RAW intersection segments",
        save_path=layer_dir / "raw_segments.png",
        show=True,
    )

    # -------------------------
    # Cleaned segments
    # -------------------------
    visualize_segments(
        layer.geometry_2d,
        "CLEANED segments (snapped, deduplicated)",
        save_path=layer_dir / "cleaned_segments.png",
        show=True,
    )

    # -------------------------
    # Topology graph
    # -------------------------
    topo = TopologyGraph(
        segments=[
            ((seg.p0[0], seg.p0[1]), (seg.p1[0], seg.p1[1]))
            for seg in layer.geometry_2d
        ],
        tol=1e-5,
    )

    loops = topo.extract_loops()
    print(f"[DEBUG] Extracted {len(loops)} closed loops")

    visualize_loops(
        loops,
        "Extracted Closed Loops (Topology Graph)",
        save_path=layer_dir / "loops.png",
        show=True,
    )

    # -------------------------
    # Polygon building
    # -------------------------
    result = build_polygons_from_loops(
        loops=loops,
        nozzle_width=0.4,
    )

    geometry = result["geometry"]

    print("[DEBUG] Rejected loops:", len(result["rejected"]))

    if geometry:
        print("[DEBUG] Geometry type :", geometry.geom_type)
        print("[DEBUG] Valid geometry:", geometry.is_valid)

        visualize_polygon(
            geometry,
            "Final Polygon (Outer + Holes)",
            save_path=layer_dir / "final_polygon.png",
            show=True,
        )

        save_outer_boundaries(
            geometry,
            layer_dir / "outer_boundaries.png",
        )

        save_inner_boundaries(
            geometry,
            layer_dir / "inner_boundaries.png",
        )

    print(f"[DEBUG] Saved debug output to: {layer_dir}")

