import json
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon


# -------------------------------------------------
# Plot helpers
# -------------------------------------------------

def _plot_polygon_edges(ax, poly, color):
    xs, ys = poly.exterior.xy
    ax.plot(xs, ys, color=color, linewidth=2)

    for hole in poly.interiors:
        xs, ys = hole.xy
        ax.plot(xs, ys, color=color, linestyle="--", linewidth=1)


def plot_outer_boundaries(geometry, save_path: Path):
    fig, ax = plt.subplots(figsize=(6, 6))

    if isinstance(geometry, Polygon):
        _plot_polygon_edges(ax, geometry, "black")

    elif isinstance(geometry, MultiPolygon):
        for poly in geometry.geoms:
            _plot_polygon_edges(ax, poly, "black")

    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Outer Boundaries")
    ax.grid(True)

    fig.savefig(save_path, dpi=200)
    plt.close(fig)


def plot_inner_boundaries(geometry, save_path: Path):
    fig, ax = plt.subplots(figsize=(6, 6))

    def plot_holes(poly):
        for hole in poly.interiors:
            xs, ys = hole.xy
            ax.plot(xs, ys, color="red", linewidth=2)

    if isinstance(geometry, Polygon):
        plot_holes(geometry)

    elif isinstance(geometry, MultiPolygon):
        for poly in geometry.geoms:
            plot_holes(poly)

    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Inner Boundaries")
    ax.grid(True)

    fig.savefig(save_path, dpi=200)
    plt.close(fig)


# -------------------------------------------------
# Export API
# -------------------------------------------------

def export_layer_geometry(
    output_root: Path,
    model_name: str,
    z_height: float,
    geometry: Union[Polygon, MultiPolygon]
):
    """
    Export one slice layer:
    - outer plot
    - inner plot
    - metadata json
    """

    model_dir = output_root / model_name
    layer_dir = model_dir / f"layer_{z_height:.3f}"

    layer_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Plots
    # -------------------------
    plot_outer_boundaries(
        geometry,
        layer_dir / "outer.png"
    )

    plot_inner_boundaries(
        geometry,
        layer_dir / "inner.png"
    )

    # -------------------------
    # Metadata
    # -------------------------
    if isinstance(geometry, Polygon):
        polygons = [geometry]
    else:
        polygons = list(geometry.geoms)

    num_holes = sum(len(p.interiors) for p in polygons)
    area_total = sum(p.area for p in polygons)

    layer_meta = {
        "z_height": z_height,
        "num_outer_polygons": len(polygons),
        "num_holes": num_holes,
        "area_total": area_total,
        "valid": geometry.is_valid
    }

    with open(layer_dir / "layer.json", "w") as f:
        json.dump(layer_meta, f, indent=2)
