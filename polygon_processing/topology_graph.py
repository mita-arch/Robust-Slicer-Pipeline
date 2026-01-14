from typing import List, Tuple
import math
from tqdm import tqdm

Point2D = Tuple[float, float]
Segment2D = Tuple[Point2D, Point2D]

class TopologyGraph:
    """
    Directly builds loops by finding the nearest neighbor to the current endpoint.
    This bypasses rigid graph structures to "heal" gaps in messy slice data.
    """
    def __init__(self, segments: List[Segment2D], tol: float = 1e-3):
        self.segments = segments
        self.tol = tol # Increased tolerance to 0.001mm

    def extract_loops(self) -> List[List[Point2D]]:
        # --- CHANGE 1: REMOVAL OF RIGID GRAPH ---
        # We work with a pool of segments. Once a segment is used, it's gone.
        pool = list(self.segments)
        loops = []

        pbar = tqdm(total=len(pool), desc="Greedy Loop Extraction", leave=False)

        while pool:
            # Start a new loop with the first available segment
            first_seg = pool.pop(0)
            pbar.update(1)
            
            # current_loop stores points: [p0, p1]
            current_loop = [first_seg[0], first_seg[1]]
            
            while True:
                last_pt = current_loop[-1]
                best_idx = -1
                best_dist = float('inf')
                flip_needed = False

                # --- CHANGE 2: NEAREST NEIGHBOR SEARCH ---
                # Look through the pool for the segment whose endpoint is 
                # physically closest to our current nozzle position.
                for i, seg in enumerate(pool):
                    d0 = math.hypot(last_pt[0] - seg[0][0], last_pt[1] - seg[0][1])
                    d1 = math.hypot(last_pt[0] - seg[1][0], last_pt[1] - seg[1][1])
                    
                    min_d = min(d0, d1)
                    if min_d < best_dist:
                        best_dist = min_d
                        best_idx = i
                        flip_needed = (d1 < d0) # Flip if the end of the segment is closer

                # --- CHANGE 3: GAP HEALING ---
                # Even if there is a gap (up to 0.1mm), we "snap" to the next segment.
                # This bridges the discontinuities seen in your 'Extracted Loops' image.
                if best_idx != -1 and best_dist < 0.1: 
                    next_seg = pool.pop(best_idx)
                    pbar.update(1)
                    
                    if flip_needed:
                        current_loop.append(next_seg[0])
                    else:
                        current_loop.append(next_seg[1])
                else:
                    # No more nearby segments found. Loop is finished.
                    break

            # --- CHANGE 4: AUTOMATIC CLOSURE ---
            # Check if the start and end of our chain are close enough to close the loop.
            d_to_start = math.hypot(current_loop[-1][0] - current_loop[0][0], 
                                    current_loop[-1][1] - current_loop[0][1])
            
            if d_to_start < 0.5: # Generous closure for perimeters
                current_loop.append(current_loop[0])

            if len(current_loop) > 3:
                loops.append(current_loop)

        pbar.close()
        return loops