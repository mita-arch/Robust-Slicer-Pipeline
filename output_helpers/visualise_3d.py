import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa


def visualize_3d_layers(layer_geometries, title, save_path=None):
    """
    layer_geometries: List of (z_height, shapely geometry)
    """

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    for z, geometry in layer_geometries:
        if geometry is None:
            continue

        if geometry.geom_type == "Polygon":
            _plot_polygon_3d(ax, geometry, z)

        elif geometry.geom_type == "MultiPolygon":
            for poly in geometry.geoms:
                _plot_polygon_3d(ax, poly, z)

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_box_aspect([1, 1, 0.5])

    if save_path:
        plt.savefig(save_path, dpi=200)
        print(f"✔ Saved 3D plot to {save_path}")

    plt.show()


def _plot_polygon_3d(ax, poly, z):
    # Outer boundary
    x, y = poly.exterior.xy
    z_vals = [z] * len(x)
    ax.plot(x, y, z_vals, color="blue", linewidth=1)

    # Holes
    for hole in poly.interiors:
        hx, hy = hole.xy
        hz = [z] * len(hx)
        ax.plot(hx, hy, hz, color="red", linewidth=1)
