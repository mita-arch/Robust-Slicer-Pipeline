from typing import List, Tuple
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import substring
from math import hypot

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

# ---------------------------
# Utility
# ---------------------------
def _dist(a: Point2D, b: Point2D) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])

# ---------------------------
# Ring path
# ---------------------------
def _ring_path(ring_ls: LineString, p_from: Point2D, p_to: Point2D) -> List[Segment2D]:
    """Shortest path along a ring (wrap-around supported)."""
    if p_from == p_to:
        return []

    d_from = ring_ls.project(Point(p_from))
    d_to = ring_ls.project(Point(p_to))
    total_len = ring_ls.length

    dist_a = abs(d_to - d_from)
    dist_b = total_len - dist_a

    if dist_a <= dist_b:
        chosen = substring(ring_ls, min(d_from, d_to), max(d_from, d_to))
    else:
        if d_from < d_to:
            part1 = substring(ring_ls, d_to, total_len)
            part2 = substring(ring_ls, 0.0, d_from)
        else:
            part1 = substring(ring_ls, d_from, total_len)
            part2 = substring(ring_ls, 0.0, d_to)
        chosen = LineString(list(part1.coords) + list(part2.coords))

    # Ensure it starts from p_from
    coords = list(chosen.coords)
    if _dist(coords[0], p_from) > _dist(coords[-1], p_from):
        coords = coords[::-1]

    segments = [(coords[i], coords[i + 1]) for i in range(len(coords) - 1)]
    return segments

# ---------------------------
# Boundary path
# ---------------------------
def boundary_path(p_from: Point2D, p_to: Point2D, polygon: Polygon, tol: float = 1e-4) -> Tuple[str, List[Segment2D]]:
    """
    Evaluates exterior and relevant holes to find the shortest boundary path.
    Discard zero-length paths and holes not adjacent to the endpoints.
    """
    candidates = []

    # 1. ALWAYS EVALUATE EXTERIOR
    # We assume the exterior is always a valid "highway" for the nozzle.
    ext_segments = _ring_path(LineString(polygon.exterior.coords), p_from, p_to)
    if ext_segments:
        ext_len = sum(_dist(a, b) for a, b in ext_segments)
        if ext_len > 0.01: # Discard zero-length
            candidates.append(("exterior", ext_len, ext_segments))

    # 2. EVALUATE RELEVANT HOLES
    for i, hole in enumerate(polygon.interiors):
        hole_ls = LineString(hole.coords)
        
        # --- NEW DISTANCE CHECK ---
        # Only consider the hole if both points are nearly touching it.
        # This prevents the nozzle from "teleporting" to a hole in the middle 
        # of the part that isn't connected to these infill lines.
        dist_from = hole_ls.distance(Point(p_from))
        dist_to = hole_ls.distance(Point(p_to))
        
        if dist_from < tol and dist_to < tol:
            h_segments = _ring_path(hole_ls, p_from, p_to)
            
            if h_segments:
                h_len = sum(_dist(a, b) for a, b in h_segments)
                
                # Discard holes where path length is effectively 0
                if h_len > 1e-6:
                    candidates.append((f"hole_{i}", h_len, h_segments))

    if not candidates:
        return "none", []

    # 3. PICK THE SHORTEST VALID CANDIDATE
    # This now compares the Exterior vs. only the relevant/adjacent Holes.
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0], candidates[0][2]