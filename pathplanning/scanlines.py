# pathplanning/scanlines.py

from collections import defaultdict
from typing import List, Tuple

from .vectors import normal_vector, dot

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

def segment_midpoint(seg: Segment2D) -> Point2D:
    (x1, y1), (x2, y2) = seg
    return ((x1 + x2) * 0.5, (y1 + y2) * 0.5)

def group_by_scanlines(
    segments: List[Segment2D],
    spacing: float,
    angle_deg: float,
):
    """
    Returns { scanline_id : [segments] }
    """
    scanlines = defaultdict(list)
    N = normal_vector(angle_deg)

    for seg in segments:
        mid = segment_midpoint(seg)
        coord = dot(mid, N)
        scan_id = int(round(coord / spacing))
        scanlines[scan_id].append(seg)

    return scanlines
