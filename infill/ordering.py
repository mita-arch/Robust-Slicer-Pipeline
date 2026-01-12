# infill/ordering.py

from typing import List, Tuple

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

def segment_midpoint(seg: Segment2D):
    (x1, y1), (x2, y2) = seg
    return ((x1 + x2) * 0.5, (y1 + y2) * 0.5)

def order_segments_by_y(segments: List[Segment2D]) -> List[Segment2D]:
    """
    Simple geometric ordering based on Y of segment midpoint.
    """
    return sorted(segments, key=lambda s: segment_midpoint(s)[1])
