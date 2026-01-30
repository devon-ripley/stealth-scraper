import math
import random
from typing import List, Tuple

class BezierCurve:
    """Generate bezier curves for natural mouse movement."""
    
    @staticmethod
    def calculate_point(t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate a point on a bezier curve at parameter t."""
        n = len(points) - 1
        x, y = 0.0, 0.0
        for i, (px, py) in enumerate(points):
            binomial = math.comb(n, i)
            term = binomial * (t ** i) * ((1 - t) ** (n - i))
            x += term * px
            y += term * py
        return x, y
    
    @staticmethod
    def generate_curve(
        start: Tuple[int, int],
        end: Tuple[int, int],
        control_points: int = 2,
        intensity: float = 0.3
    ) -> List[Tuple[int, int]]:
        """Generate a bezier curve path between two points."""
        points = [start]
        
        # Generate control points with some randomness
        for i in range(control_points):
            t = (i + 1) / (control_points + 1)
            base_x = start[0] + (end[0] - start[0]) * t
            base_y = start[1] + (end[1] - start[1]) * t
            
            # Add perpendicular offset for curve
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = math.sqrt(dx * dx + dy * dy)
            
            if length > 0:
                # Perpendicular direction
                perp_x = -dy / length
                perp_y = dx / length
                
                offset = random.gauss(0, length * intensity)
                ctrl_x = base_x + perp_x * offset
                ctrl_y = base_y + perp_y * offset
                points.append((ctrl_x, ctrl_y))
        
        points.append(end)
        
        # Sample the curve
        path = []
        # Optimization: Use larger steps (25px) to reduce Selenium overhead
        # This is overridden by FAST mode teleportation in simulator
        step_size = 25
        num_samples = max(5, int(math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) / step_size))
        
        for i in range(num_samples + 1):
            t = i / num_samples
            x, y = BezierCurve.calculate_point(t, points)
            path.append((int(x), int(y)))
        
        return path
