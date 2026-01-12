# infill/infill_engine.py

from typing import List, Tuple
from shapely.geometry import Polygon

from .parameters import InfillParams
from .line_generator import generate_parallel_lines
from .transform import rotate_geometry
from .clipper import clip_line_to_polygon
from .ordering import order_segments_by_y

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

def generate_infill_for_polygon(
    polygon: Polygon,
    params: InfillParams
) -> List[Segment2D]:
    """
    Generate infill segments for a single slice polygon.
    """
    centroid = polygon.centroid
    bounds = polygon.bounds

    # Expand bounds slightly to ensure full coverage after rotation
    expand = params.spacing * 10
    minx, miny, maxx, maxy = bounds
    expanded_bounds = (
        minx - expand,
        miny - expand,
        maxx + expand,
        maxy + expand
    )

    # Step 1: base horizontal lines
    base_lines = generate_parallel_lines(expanded_bounds, params.spacing)

    # Step 2: rotate lines
    rotated_lines = [
        rotate_geometry(line, params.angle_deg, centroid)
        for line in base_lines
    ]

    # Step 3: clip to polygon
    segments: List[Segment2D] = []
    for line in rotated_lines:
        segments.extend(clip_line_to_polygon(line, polygon))

    # Step 4: basic geometric ordering
    ordered_segments = order_segments_by_y(segments)

    return ordered_segments
