from typing import List, Tuple
from .vectors import direction_vector, dot

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

def sort_segments_along_direction(
    segments: List[Segment2D],
    angle_deg: float,
    reverse: bool = False,
):
    D = direction_vector(angle_deg)

    def key(seg):
        midx = (seg[0][0] + seg[1][0]) * 0.5
        midy = (seg[0][1] + seg[1][1]) * 0.5
        return dot((midx, midy), D)

    segments = sorted(segments, key=key)
    if reverse:
        segments.reverse()

    return segments
