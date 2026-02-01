import random
import time
from typing import List, Tuple
from selenium import webdriver
from ..config import HumanBehaviorConfig
from ..utils.math import BezierCurve

class HumanMouseSimulator:
    """Simulate realistic human mouse movements."""
    
    def __init__(self, driver: webdriver.Chrome, config: HumanBehaviorConfig):
        self.driver = driver
        self.config = config
        
        # Initialize at random position within viewport
        try:
            viewport = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
            max_x, max_y = viewport[0] - 1, viewport[1] - 1
            self.current_pos = (random.randint(0, max_x), random.randint(0, max_y))
        except:
            # Fallback if driver not ready or script fails
            self.current_pos = (random.randint(0, 1920), random.randint(0, 1080))
    
    def _add_jitter(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Add small random jitter to mouse path."""
        if not self.config.mouse_jitter:
            return path
        
        jittered = []
        for i, (x, y) in enumerate(path):
            if i == 0 or i == len(path) - 1:
                jittered.append((x, y))
            else:
                jx = x + random.randint(-2, 2)
                jy = y + random.randint(-2, 2)
                jittered.append((jx, jy))
        return jittered
    
    def _calculate_speed_curve(self, path_length: int) -> List[float]:
        """Calculate variable speed along path (slow start/end, fast middle)."""
        speeds = []
        for i in range(path_length):
            t = i / max(1, path_length - 1)
            # Ease in-out curve
            if t < 0.5:
                speed = 2 * t * t
            else:
                speed = 1 - (-2 * t + 2) ** 2 / 2
            speeds.append(speed)
        return speeds
    
    def move_to(self, x: int, y: int, click: bool = False) -> None:
        """Move mouse to coordinates with human-like motion."""
        # Get viewport dimensions for clamping
        try:
            viewport = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
            max_x, max_y = viewport[0] - 1, viewport[1] - 1
        except:
            max_x, max_y = 1919, 1079  # Fallback
            
        # Clamp target
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))

        # FAST mode: Teleport instantly via CDP
        if self.config.max_mouse_speed == 0.0:
            self._cdp_move(x, y)
            if click:
                self._human_click()
            return
        
        # Generate curved path for human-like movement
        path = BezierCurve.generate_curve(
            self.current_pos,
            (x, y),
            control_points=random.randint(1, 3),
            intensity=self.config.mouse_curve_intensity
        )
        
        # Add jitter
        path = self._add_jitter(path)
        
        # Clamp path points to viewport
        path = [(max(0, min(px, max_x)), max(0, min(py, max_y))) for px, py in path]
        
        # Calculate timing
        total_time = random.uniform(
            self.config.min_mouse_speed,
            self.config.max_mouse_speed
        )
        speeds = self._calculate_speed_curve(len(path))
        
        # Execute movement via CDP
        for i, (px, py) in enumerate(path[1:], 1):
            # Skip redundant points
            if (px, py) == self.current_pos:
                continue
                
            self._cdp_move(px, py)
            
            # Variable delay based on position in path
            if i < len(path) - 1:
                base_delay = total_time / len(path)
                speed_factor = 0.5 + speeds[i]
                delay = base_delay * speed_factor * random.uniform(0.8, 1.2)
                time.sleep(delay)
        
        # Hesitation logic
        if random.random() < self.config.hesitation_chance:
            self._perform_hesitation()
        
        # Overshoot logic
        if random.random() < self.config.mouse_overshoot_chance:
            overshoot_x = max(0, min(x + random.randint(-20, 20), max_x))
            overshoot_y = max(0, min(y + random.randint(-15, 15), max_y))
            try:
                self._micro_move(overshoot_x, overshoot_y)
                time.sleep(random.uniform(0.1, 0.3))
                self._micro_move(x, y)
            except: pass
        
        if click:
            self._human_click()

    def _cdp_move(self, x: int, y: int) -> None:
        """Move cursor using CDP to avoid Selenium overhead."""
        try:
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mouseMoved",
                "x": x,
                "y": y,
                "button": "none",
                "pointerType": "mouse"
            })
            self.current_pos = (x, y)
        except:
            pass
    
    def _micro_move(self, x: int, y: int) -> None:
        """Small correction movement using CDP."""
        self._cdp_move(x, y)
    
    def _human_click(self) -> None:
        """Simulate a human-like click using CDP."""
        x, y = self.current_pos
        
        # Random pre-click pause (skip in FAST mode)
        if self.config.min_action_pause > 0:
            time.sleep(random.uniform(0.02, 0.08))
            
        try:
            # Mouse Down
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mousePressed",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 1, # Left button pressed
                "clickCount": 1,
                "pointerType": "mouse"
            })
            
            # Short hold time (skip in FAST mode)
            if self.config.min_action_pause > 0:
                time.sleep(random.uniform(0.05, 0.15))
            
            # Mouse Up
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mouseReleased",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 0, # Released
                "clickCount": 1,
                "pointerType": "mouse"
            })
        except:
            pass
            
        # Random post-click pause (skip in FAST mode)
        if self.config.min_action_pause > 0:
            time.sleep(random.uniform(0.1, 0.3))

    def _perform_hesitation(self) -> None:
        """Perform a hesitation movement (stop, micro-move, wait)."""
        time.sleep(random.uniform(0.1, 0.4))
        
        # Small random movement nearby using CDP (Fixes ActionChains crash)
        x, y = self.current_pos
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        
        # Move slightly away
        self._micro_move(x + offset_x, y + offset_y)
        time.sleep(random.uniform(0.2, 0.5))
        
        # Move back (roughly)
        self._micro_move(x, y)
        
        time.sleep(random.uniform(0.1, 0.3))
    
    def move_to_element(self, element, click: bool = False) -> None:
        """Move to a web element with human-like motion."""
        # Use getBoundingClientRect to get viewport-relative coordinates
        # element.location gives document-relative coordinates which fails if scrolled
        rect = self.driver.execute_script("return arguments[0].getBoundingClientRect();", element)
        
        # Calculate target position within the element (with randomness)
        # rect keys: left, top, width, height (viewport relative)
        x = rect['left'] + random.uniform(
            rect['width'] * 0.2,
            rect['width'] * 0.8
        )
        y = rect['top'] + random.uniform(
            rect['height'] * 0.2,
            rect['height'] * 0.8
        )
        
        self.move_to(x, y, click=click)
