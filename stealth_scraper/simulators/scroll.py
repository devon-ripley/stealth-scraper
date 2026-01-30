import random
import time
from typing import Optional
from selenium import webdriver
from ..config import HumanBehaviorConfig

class HumanScrollSimulator:
    """Simulate realistic human scrolling behavior."""
    
    def __init__(self, driver: webdriver.Chrome, config: HumanBehaviorConfig):
        self.driver = driver
        self.config = config
    
    def scroll_to(self, target_y: int, style: Optional[str] = None) -> None:
        """Scroll to a vertical position with human-like behavior."""
        style = style or self.config.scroll_style
        current_y = self.driver.execute_script("return window.pageYOffset;")
        distance = target_y - current_y
        
        if style == "smooth":
            self._smooth_scroll(current_y, target_y)
        elif style == "stepped":
            self._stepped_scroll(current_y, target_y)
        else:
            # Mixed - randomly choose
            if random.random() < 0.5:
                self._smooth_scroll(current_y, target_y)
            else:
                self._stepped_scroll(current_y, target_y)
    
    def _smooth_scroll(self, start_y: int, end_y: int) -> None:
        """Smooth scrolling with easing."""
        distance = end_y - start_y
        duration = abs(distance) / random.uniform(800, 1500)  # pixels per second
        steps = max(10, int(duration * 60))  # ~60fps
        
        for i in range(steps + 1):
            t = i / steps
            # Ease out cubic
            eased_t = 1 - (1 - t) ** 3
            current = start_y + distance * eased_t
            
            self.driver.execute_script(f"window.scrollTo(0, {int(current)});")
            
            # Variable frame timing
            base_delay = duration / steps
            actual_delay = base_delay * random.uniform(0.8, 1.2)
            time.sleep(actual_delay)
            
            # Occasional micro-pause
            if random.random() < 0.05:
                time.sleep(random.uniform(0.05, 0.15))
    
    def _stepped_scroll(self, start_y: int, end_y: int) -> None:
        """Stepped scrolling like mouse wheel."""
        distance = end_y - start_y
        direction = 1 if distance > 0 else -1
        remaining = abs(distance)
        current = start_y
        
        while remaining > 0:
            # Variable scroll step (like mousewheel)
            base_step = random.randint(80, 150)
            variance = base_step * self.config.scroll_variance
            step = int(base_step + random.gauss(0, variance))
            step = min(step, remaining)
            
            current += step * direction
            self.driver.execute_script(f"window.scrollTo(0, {int(current)});")
            remaining -= step
            
            # Pause between steps
            pause = random.uniform(
                self.config.min_scroll_pause,
                self.config.max_scroll_pause
            )
            time.sleep(pause)
            
            # Occasional longer pause (reading)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 2.0))
    
    def scroll_page(self, direction: str = "down", amount: float = 0.7) -> None:
        """Scroll by a portion of the viewport."""
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        current_y = self.driver.execute_script("return window.pageYOffset;")
        
        scroll_amount = int(viewport_height * amount * random.uniform(0.8, 1.2))
        
        if direction == "down":
            target_y = current_y + scroll_amount
        else:
            target_y = max(0, current_y - scroll_amount)
        
        self.scroll_to(target_y)
    
    def scroll_to_element(self, element, align: str = "center") -> None:
        """Scroll to bring an element into view."""
        location = element.location
        size = element.size
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        
        if align == "center":
            target_y = location['y'] - (viewport_height - size['height']) / 2
        elif align == "top":
            target_y = location['y'] - 100
        else:  # bottom
            target_y = location['y'] - viewport_height + size['height'] + 100
        
        target_y = max(0, int(target_y))
        self.scroll_to(target_y)
