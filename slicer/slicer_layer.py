from dataclasses import dataclass
from typing import List, Tuple


# ----------------------------
# Basic geometry primitives
# ----------------------------

Point3D = Tuple[float, float, float]
Point2D = Tuple[float, float]


@dataclass(frozen=True)
class Segment3D:
    """
    Raw intersection segment produced by slicing a mesh
    with a horizontal plane at z = constant.
    """
    p0: Point3D
    p1: Point3D


@dataclass(frozen=True)
class Segment2D:
    """
    Planar segment obtained after projecting a 3D slice
    onto the XY plane.
    """
    p0: Point2D
    p1: Point2D


# ----------------------------
# Slice container
# ----------------------------

@dataclass
class SliceLayer:
    """
    Represents a single horizontal slice of a 3D mesh.
    """
    z_height: float
    raw_curves: List[Segment3D]
    geometry_2d: List[Segment2D]

    @property
    def is_empty(self) -> bool:
        return len(self.raw_curves) == 0
