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
    Connects infill segments into a continuous toolpath while ignoring segments
    smaller than spacing (infill gap).
    """

    # Define the minimum threshold for an infill segment to be kept
    min_infill_length =  spacing

    scanlines = group_by_scanlines(
        infill_segments,
        spacing,
        angle_deg,
    )

    ordered_scan_ids = sorted(scanlines.keys())

    connected_path: List[TypedSegment] = []
    last_endpoint: Point2D | None = None

    for idx, scan_id in enumerate(ordered_scan_ids):
        # Alternating direction for S-pattern
        reverse = (idx % 2 == 1)

        segments = sort_segments_along_direction(
            scanlines[scan_id],
            angle_deg,
            reverse=reverse,
        )

        if not segments:
            continue

        for seg in segments:
            # --- NEW FILTERING LOGIC ---
            # Calculate length of the current infill segment
            seg_len = hypot(seg[1][0] - seg[0][0], seg[1][1] - seg[0][1])
            
            # Skip segments that are too small (1.2 * infill gap)
            if seg_len < min_infill_length:
                continue
            # ---------------------------

            # Orient segment to minimize jump from previous point
            seg = orient_segment(seg, last_endpoint)
            start_pt = seg[0]

            if last_endpoint is not None:
                gap = hypot(
                    last_endpoint[0] - start_pt[0],
                    last_endpoint[1] - start_pt[1],
                )

                if gap > connector_tol:
                    conn_type, conn_segments = choose_connector(
                        last_endpoint,
                        start_pt,
                        polygon,
                        params,
                    )

                    for cseg in conn_segments:
                        connected_path.append((conn_type, cseg))
                    
                    if conn_segments:
                        last_endpoint = conn_segments[-1][1]

            # Add the valid infill extrusion
            connected_path.append(("direct", seg))
            last_endpoint = seg[1]

    return connected_path