from typing import List
from slicer.slicer_layer import Segment3D, Segment2D

CLEAN_EPS = 1e-6
SNAP_TOL = 1e-5

# -------------------------------------------------
# Utility helpers
# -------------------------------------------------

def _dist2(p0, p1):
    return (p0[0] - p1[0])**2 + (p0[1] - p1[1])**2

def snap_xy(pt, eps=1e-4):
    return (
        round(pt[0] / eps) * eps,
        round(pt[1] / eps) * eps
    )

# -------------------------------------------------
# Raw curve cleanup (NO LOOP STITCHING)
# -------------------------------------------------

def cleanup_raw_segments(
    raw_segments: List[Segment3D],
    snap_eps=1e-4
) -> List[Segment2D]:
    """
    Cura-style cleanup:
    - Grid snap XY
    - Remove zero-length
    - Remove duplicates
    """

    unique_segments = set()
    cleaned: List[Segment2D] = []

    for seg in raw_segments:
        p0 = snap_xy((seg.p0[0], seg.p0[1]), snap_eps)
        p1 = snap_xy((seg.p1[0], seg.p1[1]), snap_eps)

        # Remove degenerate segments
        if _dist2(p0, p1) < snap_eps**2:
            continue

        # Canonical ordering
        key = tuple(sorted((p0, p1)))

        if key in unique_segments:
            continue

        unique_segments.add(key)
        cleaned.append(Segment2D(p0, p1))

    return cleaned
