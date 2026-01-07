from collections import defaultdict
from typing import Dict, List, Tuple
from tqdm import tqdm

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

class TopologyGraph:
    """
    Graph-based representation of slice line segments.
    Used to weld segments and extract closed loops.
    """

    def __init__(self, segments: List[Segment2D], tol: float = 1e-5):
        self.segments = segments
        self.tol = tol

        self.vertex_map: Dict[Point2D, int] = {}
        self.vertices: List[Point2D] = []
        self.adj: Dict[int, List[int]] = defaultdict(list)

        self._build_graph()

    # -----------------------------
    # Quantization / welding
    # -----------------------------

    def _quantize(self, p: Point2D) -> Point2D:
        return (
            round(p[0] / self.tol) * self.tol,
            round(p[1] / self.tol) * self.tol,
        )

    def _get_vertex_id(self, p: Point2D) -> int:
        qp = self._quantize(p)
        if qp not in self.vertex_map:
            vid = len(self.vertices)
            self.vertex_map[qp] = vid
            self.vertices.append(qp)
        return self.vertex_map[qp]

    # -----------------------------
    # Graph construction
    # -----------------------------

    def _build_graph(self):
        for p0, p1 in self.segments:
            v0 = self._get_vertex_id(p0)
            v1 = self._get_vertex_id(p1)

            self.adj[v0].append(v1)
            self.adj[v1].append(v0)

    # -----------------------------
    # Loop extraction
    # -----------------------------

    def extract_loops(self) -> List[List[Point2D]]:
        """
        Traverse graph and extract closed loops.
        """
        visited_edges = set()
        loops = []

        def edge_key(a: int, b: int):
            return tuple(sorted((a, b)))

        # tqdm over vertices
        for start in tqdm(
            range(len(self.vertices)),
            desc="Extracting loops",
            unit="vertex",
            leave=False
        ):
            for nxt in self.adj[start]:
                ek = edge_key(start, nxt)
                if ek in visited_edges:
                    continue

                loop = []
                current = start
                prev = None

                while True:
                    loop.append(self.vertices[current])

                    neighbors = self.adj[current]
                    next_vertex = None

                    for n in neighbors:
                        if n != prev and edge_key(current, n) not in visited_edges:
                            next_vertex = n
                            break

                    if next_vertex is None:
                        break

                    visited_edges.add(edge_key(current, next_vertex))
                    prev, current = current, next_vertex

                    if current == start:
                        loop.append(self.vertices[start])
                        break

                if len(loop) > 3:
                    loops.append(loop)

        return loops

