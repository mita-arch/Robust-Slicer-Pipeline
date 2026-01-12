import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon, LineString


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _flatten_polygons(geom):
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return []


def _extract_segment_coords(seg):
    """
    Supports:
    - ((x1,y1),(x2,y2))
    - objects with .p0 / .p1
    - shapely LineString
    """
    if isinstance(seg, LineString):
        coords = list(seg.coords)
        return coords[0], coords[-1]

    if hasattr(seg, "p0") and hasattr(seg, "p1"):
        return seg.p0, seg.p1

    return seg[0], seg[1]


def _normalize_segment(item):
    """
    Returns:
        seg_type: str
        ((x1,y1),(x2,y2))
    """

    # Typed segment: ("direct", seg)
    if (
        isinstance(item, tuple)
        and len(item) == 2
        and isinstance(item[0], str)
    ):
        seg_type = item[0]
        p0, p1 = _extract_segment_coords(item[1])
        return seg_type, (p0, p1)

    # Untyped → assume direct extrusion
    p0, p1 = _extract_segment_coords(item)
    return "direct", (p0, p1)


# -------------------------------------------------
# Main visualization
# -------------------------------------------------
def visualize_connected_infill(
    geometry,
    connected_segments,
    title,
    save_path,
    show=False,
):
    fig, ax = plt.subplots(figsize=(8, 8))

    # -------------------------------------------------
    # Draw polygon boundaries
    # -------------------------------------------------
    for poly in _flatten_polygons(geometry):
        x, y = poly.exterior.xy
        ax.plot(x, y, color="black", linewidth=1)

        for hole in poly.interiors:
            hx, hy = hole.xy
            ax.plot(hx, hy, color="black", linewidth=1)

    # -------------------------------------------------
    # Style maps (update for new boundary types)
    # -------------------------------------------------
    def get_color(seg_type: str) -> str:
        if seg_type == "direct":
            return "red"
        if seg_type == "travel":
            return "green"
        if seg_type.startswith("boundary_exterior"):
            return "blue"
        if seg_type.startswith("boundary_hole"):
            return "cyan"
        return "gray"

    def get_linewidth(seg_type: str) -> float:
        if seg_type == "direct":
            return 2.0
        if seg_type == "travel":
            return 1.2
        if seg_type.startswith("boundary"):
            return 1.8
        return 1.0

    def get_linestyle(seg_type: str) -> str:
        if seg_type == "travel":
            return "--"
        return "-"

    # -------------------------------------------------
    # Draw segments
    # -------------------------------------------------
    for item in connected_segments:
        seg_type, ((x1, y1), (x2, y2)) = _normalize_segment(item)

        ax.plot(
            [x1, x2],
            [y1, y2],
            color=get_color(seg_type),
            linewidth=get_linewidth(seg_type),
            linestyle=get_linestyle(seg_type),
            zorder=3,
        )

    ax.set_aspect("equal")
    ax.set_title(title)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path)

    if show:
        plt.show()
    else:
        plt.close(fig)
