from typing import List, Tuple, Dict
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

Point2D = Tuple[float, float]

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def signed_area(loop: List[Point2D]) -> float:
    area = 0.0
    for i in range(len(loop)):
        x1, y1 = loop[i]
        x2, y2 = loop[(i + 1) % len(loop)]
        area += (x1 * y2 - x2 * y1)
    return 0.5 * area


def normalize_loop(loop: List[Point2D]) -> List[Point2D]:
    if loop[0] != loop[-1]:
        loop = loop + [loop[0]]
    return loop


def is_degenerate(loop: List[Point2D], area_thresh: float) -> bool:
    if len(set(loop)) < 3:
        return True
    return abs(signed_area(loop)) < area_thresh


def iter_polygons(geom):
    if geom is None:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return []


# -------------------------------------------------
# FINAL Cura-Style Polygon Builder
# -------------------------------------------------

def build_polygons_from_loops(
    loops: List[List[Point2D]],
    nozzle_width: float
) -> Dict:
   
    area_thresh = (0.5 * nozzle_width) ** 2
    merge_eps = 0.02 * nozzle_width

    # -------------------------------------------------
    # 1. Sanitize loops → temporary solids
    # -------------------------------------------------
    base_polys = []
    rejected = []

    for loop in loops:
        loop = normalize_loop(loop)

        if is_degenerate(loop, area_thresh):
            rejected.append(loop)
            continue

        p = Polygon(loop)
        if not p.is_valid:
            p = p.buffer(0)

        if p.is_empty or not p.is_valid:
            rejected.append(loop)
            continue

        base_polys.append(p)

    if not base_polys:
        return {"geometry": None, "polygons": [], "rejected": rejected}

    # -------------------------------------------------
    # 2. EVEN–ODD classification (core Cura logic)
    # -------------------------------------------------
    final_solids = []

    for i, outer in enumerate(base_polys):
        # Count how many loops contain this loop
        depth = 0
        for j, other in enumerate(base_polys):
            if i != j and other.contains(outer):
                depth += 1

        # Odd depth → hole → skip
        if depth % 2 != 0:
            continue

        # Collect holes directly inside
        holes = []
        for j, inner in enumerate(base_polys):
            if i == j:
                continue
            if outer.contains(inner):
                inner_depth = sum(
                    1 for k, p in enumerate(base_polys)
                    if k != j and p.contains(inner)
                )
                if inner_depth == depth + 1:
                    holes.append(list(inner.exterior.coords))

        poly = Polygon(
            list(outer.exterior.coords),
            holes
        )

        if not poly.is_valid:
            poly = poly.buffer(0)

        for p in iter_polygons(poly):
            if not p.is_empty and p.is_valid:
                final_solids.append(p)

    if not final_solids:
        return {"geometry": None, "polygons": [], "rejected": rejected}

    # -------------------------------------------------
    # 3. Union ONLY solid regions
    # -------------------------------------------------
    merged = unary_union(final_solids)

    # -------------------------------------------------
    # 4. Morphological cleanup (very small)
    # -------------------------------------------------
    cleaned = merged.buffer(+merge_eps).buffer(-merge_eps)

    # -------------------------------------------------
    # 5. Final extraction
    # -------------------------------------------------
    final_polys = [
        p for p in iter_polygons(cleaned)
        if not p.is_empty and p.is_valid
    ]

    geometry = (
        final_polys[0]
        if len(final_polys) == 1
        else MultiPolygon(final_polys)
    )

    return {
        "geometry": geometry,
        "polygons": final_polys,
        "rejected": rejected
    }
