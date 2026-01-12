from typing import Tuple

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]


def dist2(a: Point2D, b: Point2D) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def orient_segment(
    seg: Segment2D,
    start: Point2D | None,
) -> Segment2D:
    """
    Orients segment to start closest to `start`.
    """
    if start is None:
        return seg

    if dist2(start, seg[1]) < dist2(start, seg[0]):
        return (seg[1], seg[0])

    return seg
