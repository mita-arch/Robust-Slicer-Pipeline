# infill/line_generator.py

from typing import List
from shapely.geometry import LineString, box

def generate_parallel_lines(bounds, spacing: float) -> List[LineString]:
    """
    Generate horizontal parallel lines covering the bounding box.
    """
    minx, miny, maxx, maxy = bounds
    lines = []

    y = miny
    while y <= maxy:
        line = LineString([(minx, y), (maxx, y)])
        lines.append(line)
        y += spacing

    return lines
