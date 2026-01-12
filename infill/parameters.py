# infill/parameters.py

from dataclasses import dataclass

@dataclass
class InfillParams:
    spacing: float          # distance between infill lines
    angle_deg: float        # infill angle in degrees
