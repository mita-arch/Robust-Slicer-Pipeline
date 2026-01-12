# infill/visualise_infill.py

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon


def _flatten_polygons(geometry):
    """
    Returns a list of Polygon objects from Polygon or MultiPolygon.
    """
    if isinstance(geometry, Polygon):
        return [geometry]

    if isinstance(geometry, MultiPolygon):
        return list(geometry.geoms)

    return []


def visualize_polygon_with_infill(
    geometry,
    infill_segments,
    title,
    save_path,
    show=False,
):
    """
    Visualize polygon boundaries (outer + holes) and infill lines
    in a single plot. Supports Polygon and MultiPolygon.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    polygons = _flatten_polygons(geometry)

    # -------------------------
    # Draw polygon boundaries
    # -------------------------
    for poly in polygons:
        # Outer boundary
        x, y = poly.exterior.xy
        ax.plot(x, y, color="black", linewidth=2)

        # Holes
        for hole in poly.interiors:
            hx, hy = hole.xy
            ax.plot(hx, hy, color="black", linewidth=2)

    # -------------------------
    # Draw infill
    # -------------------------
    for (p0, p1) in infill_segments:
        ax.plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            color="blue",
            linewidth=0.8,
        )

    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path)

    if show:
        plt.show()
    else:
        plt.close(fig)
