from typing import List, Tuple
from math import hypot
from shapely.geometry import Polygon, LineString
from .parameters import ConnectorParams
from .boundary_connector import boundary_path

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

# ---------------------------
# Utilities
# ---------------------------
def _dist(a: Point2D, b: Point2D) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])

def _path_length(segments: List[Segment2D]) -> float:
    return sum(_dist(a, b) for a, b in segments)

def is_boundary_valid(segments: List[Segment2D], polygon: Polygon) -> bool:
    """Check if all boundary segments are within polygon."""
    poly = polygon.buffer(1e-8)
    return all(poly.contains(LineString([a, b])) for a, b in segments)

# ---------------------------
# Hybrid connector selection
# ---------------------------
def choose_connector(p_from, p_to, polygon, params: ConnectorParams):
    # 1. Calculate Travel Cost
    travel_dist = _dist(p_from, p_to)
    # Travel Cost = Distance + Retraction Penalty
    travel_cost = travel_dist + params.retract_cost

    # 2. Calculate Boundary Cost
    boundary_type, boundary_segments = boundary_path(p_from, p_to, polygon)
    
    if boundary_segments and is_boundary_valid(boundary_segments, polygon):
        boundary_len = _path_length(boundary_segments)
        
        # Determine the factor based on inner vs outer boundary (Hole Bias)
        # Holes (inner rings) are usually preferred over the visible exterior.
        specific_factor = params.boundary_factor 
        if "hole" in boundary_type:
            specific_factor *= 0.9  # Apply a 10% "discount" to holes to keep nozzle inside

        boundary_cost = boundary_len * specific_factor

        # 3. Decision Logic
        # Rule A: Is the boundary path physically too long? (Safety cutoff)
        # Rule B: Is the boundary cost better than the travel cost?
        if (boundary_len <= params.max_boundary_ratio * travel_dist and 
            boundary_cost <= travel_cost):
            return f"boundary_{boundary_type}", boundary_segments

    # Fallback to Travel
    return "travel", [(p_from, p_to)]