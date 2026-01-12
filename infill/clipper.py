# infill/clipper.py

from typing import List, Tuple
from shapely.geometry import LineString, MultiLineString

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

def clip_line_to_polygon(line: LineString, polygon) -> List[Segment2D]:
    """
    Intersect a line with a polygon (with holes).
    Returns list of valid infill segments.
    """
    clipped = line.intersection(polygon)

    segments = []

    if clipped.is_empty:
        return segments

    if isinstance(clipped, LineString):
        coords = list(clipped.coords)
        if len(coords) == 2:
            segments.append((coords[0], coords[1]))

    elif isinstance(clipped, MultiLineString):
        for geom in clipped.geoms:
            coords = list(geom.coords)
            if len(coords) == 2:
                segments.append((coords[0], coords[1]))

    return segments
