from typing import List, Tuple
from math import hypot
from shapely.geometry import Polygon

from .scanlines import group_by_scanlines
from .ordering import sort_segments_along_direction
from .connectivity import orient_segment
from .connector_cost import choose_connector
from .parameters import ConnectorParams

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]
TypedSegment = Tuple[str, Segment2D]

def connect_infill_segments(
    infill_segments: List[Segment2D],
    polygon: Polygon,
    spacing: float,
    angle_deg: float,
    params: ConnectorParams,
    connector_tol: float = 1e-4,
) -> List[TypedSegment]:
    """
    Connects infill segments using a greedy nearest-neighbor search within 
    scanlines to prevent long travel jumps to alternate segments.
    """
    scanlines = group_by_scanlines(infill_segments, spacing, angle_deg)
    ordered_scan_ids = sorted(scanlines.keys())

    connected_path: List[TypedSegment] = []
    last_endpoint: Point2D | None = None
    min_infill_length = spacing * 1.2 

    for scan_id in ordered_scan_ids:
        # Get segments for this scanline and filter runts
        remaining_segments = [
            s for s in scanlines[scan_id] 
            if hypot(s[1][0]-s[0][0], s[1][1]-s[0][1]) >= min_infill_length
        ]

        # GREEDY RE-ORDERING:
        # Instead of a fixed 'reverse' sort, always pick the segment 
        # whose endpoint is closest to our current nozzle position.
        while remaining_segments:
            best_idx = 0
            if last_endpoint is not None:
                # Find the segment that has the closest point (either start or end)
                min_dist_sq = float('inf')
                for i, s in enumerate(remaining_segments):
                    # Check distance to both ends of the segment
                    d0 = (last_endpoint[0]-s[0][0])**2 + (last_endpoint[1]-s[0][1])**2
                    d1 = (last_endpoint[0]-s[1][0])**2 + (last_endpoint[1]-s[1][1])**2
                    local_min = min(d0, d1)
                    if local_min < min_dist_sq:
                        min_dist_sq = local_min
                        best_idx = i
            
            # Pop the best segment and orient it correctly
            seg = remaining_segments.pop(best_idx)
            seg = orient_segment(seg, last_endpoint)
            start_pt = seg[0]

            # Connect from last position to this segment
            if last_endpoint is not None:
                gap = hypot(last_endpoint[0] - start_pt[0], last_endpoint[1] - start_pt[1])

                if gap > connector_tol:
                    conn_type, conn_segments = choose_connector(
                        last_endpoint, start_pt, polygon, params
                    )
                    for cseg in conn_segments:
                        connected_path.append((conn_type, cseg))
                    if conn_segments:
                        last_endpoint = conn_segments[-1][1]

            # Add the infill segment
            connected_path.append(("direct", seg))
            last_endpoint = seg[1]

    return connected_path