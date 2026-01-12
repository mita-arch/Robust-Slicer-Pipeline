from dataclasses import dataclass

@dataclass
class ConnectorParams:
    # penalty added for travel moves (retract + unretract)
    retract_cost: float

    # boundary extrusion is slower → higher cost
    boundary_factor: float 
    # reject boundary paths longer than this × direct distance
    max_boundary_ratio: float

    # ignore tiny connectors
    min_connector_length: float = 1e-4