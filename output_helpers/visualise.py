import matplotlib.pyplot as plt
# -------------------------------------------------
# Segment visualization
# -------------------------------------------------

import matplotlib.pyplot as plt

def visualize_segments(segments, title, save_path=None, show=True):
    if not segments:
        return

    plt.figure(figsize=(6, 6))

    for seg in segments:
        x = [seg.p0[0], seg.p1[0]]
        y = [seg.p0[1], seg.p1[1]]
        plt.plot(x, y, linewidth=1)

    plt.title(title)
    plt.gca().set_aspect("equal")
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")

  
    if show:
        plt.show()
    else:
        plt.close()


# -------------------------------------------------
# Loop visualization
# -------------------------------------------------

def visualize_loops(loops, title, save_path=None, show=True):
    if not loops:
        return

    plt.figure(figsize=(6, 6))

    for loop in loops:
        xs = [p[0] for p in loop] + [loop[0][0]]
        ys = [p[1] for p in loop] + [loop[0][1]]
        plt.plot(xs, ys)

    plt.title(title)
    plt.gca().set_aspect("equal")
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")

    
    if show:
        plt.show()
    else:
        plt.close()



# -------------------------------------------------
# Polygon visualization
# -------------------------------------------------


def visualize_polygon(geometry, title, save_path=None, show=True):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(6, 6))

    def plot_poly(poly):
        # Outer boundary → BLUE
        x, y = poly.exterior.xy
        plt.plot(x, y, color="blue", linewidth=2)

        # Holes → RED
        for hole in poly.interiors:
            hx, hy = hole.xy
            plt.plot(hx, hy, color="red", linewidth=2)

    if geometry.geom_type == "Polygon":
        plot_poly(geometry)

    elif geometry.geom_type == "MultiPolygon":
        for poly in geometry.geoms:
            plot_poly(poly)

    plt.title(title)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()
