# output_utils.py

import matplotlib.pyplot as plt
from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon

def prepare_layer_output_dir(
    base_output: Path,
    model_name: str,
    layer_z: float
) -> Path:
    """
    Creates:
    output/<model_name>/layer_<z>/
    """
    layer_dir = (
        base_output
        / model_name
        / f"layer_{layer_z:.3f}"
    )

    layer_dir.mkdir(parents=True, exist_ok=True)
    return layer_dir



def _setup_axes(title: str):
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(title)
    plt.grid(True)
    plt.margins(0.05)


def save_outer_boundaries(geometry, out_path: Path):
    """
    Save only outer boundaries (exteriors).
    Blue = outer perimeters
    """
    if geometry is None or geometry.is_empty:
        return

    plt.figure(figsize=(6, 6))

    if isinstance(geometry, Polygon):
        x, y = geometry.exterior.xy
        plt.plot(x, y, color="blue", linewidth=2)

    elif isinstance(geometry, MultiPolygon):
        for poly in geometry.geoms:
            x, y = poly.exterior.xy
            plt.plot(x, y, color="blue", linewidth=2)

    _setup_axes("Outer Boundaries")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def save_inner_boundaries(geometry, out_path: Path):
    """
    Save only inner boundaries (holes).
    Red = holes / voids
    """
    if geometry is None or geometry.is_empty:
        return

    plt.figure(figsize=(6, 6))

    if isinstance(geometry, Polygon):
        for hole in geometry.interiors:
            x, y = hole.xy
            plt.plot(x, y, color="red", linewidth=2)

    elif isinstance(geometry, MultiPolygon):
        for poly in geometry.geoms:
            for hole in poly.interiors:
                x, y = hole.xy
                plt.plot(x, y, color="red", linewidth=2)

    _setup_axes("Inner Boundaries")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def prepare_layer_dir(base_output, model_name, layer_idx, z_height):
    layer_dir = (
        base_output
        / model_name
        / f"layer_{layer_idx:03d}_Z{z_height:.2f}"
    )
    layer_dir.mkdir(parents=True, exist_ok=True)
    return layer_dir\
    
import json

def save_layer_metadata(layer, loops, result, path):
    metadata = {
        "z_height": layer.z_height,
        "raw_segments": len(layer.raw_curves),
        "cleaned_segments": len(layer.geometry_2d),
        "loops_extracted": len(loops),
        "rejected_loops": len(result["rejected"]),
        "geometry_type": (
            result["geometry"].geom_type
            if result["geometry"] else None
        ),
        "valid_geometry": (
            result["geometry"].is_valid
            if result["geometry"] else False
        ),
    }

    with open(path, "w") as f:
        json.dump(metadata, f, indent=2)
