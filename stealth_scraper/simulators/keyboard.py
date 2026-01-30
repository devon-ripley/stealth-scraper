import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from ..config import HumanBehaviorConfig

class HumanTypingSimulator:
    """Simulate realistic human typing behavior."""
    
    def __init__(self, driver: webdriver.Chrome, config: HumanBehaviorConfig):
        self.driver = driver
        self.config = config
        
        # Common typo patterns (wrong key -> intended key)
        self.typo_map = {
            'a': ['s', 'q', 'z'],
            'b': ['v', 'n', 'g'],
            'c': ['x', 'v', 'd'],
            'd': ['s', 'f', 'e'],
            'e': ['w', 'r', 'd'],
            'f': ['d', 'g', 'r'],
            'g': ['f', 'h', 't'],
            'h': ['g', 'j', 'y'],
            'i': ['u', 'o', 'k'],
            'j': ['h', 'k', 'u'],
            'k': ['j', 'l', 'i'],
            'l': ['k', 'o', 'p'],
            'm': ['n', 'k'],
            'n': ['b', 'm', 'j'],
            'o': ['i', 'p', 'l'],
            'p': ['o', 'l'],
            'q': ['w', 'a'],
            'r': ['e', 't', 'f'],
            's': ['a', 'd', 'w'],
            't': ['r', 'y', 'g'],
            'u': ['y', 'i', 'j'],
            'v': ['c', 'b', 'f'],
            'w': ['q', 'e', 's'],
            'x': ['z', 'c', 's'],
            'y': ['t', 'u', 'h'],
            'z': ['a', 'x'],
        }
    
    def type_text(self, element, text: str, clear_first: bool = True) -> None:
        """Type text into an element with human-like behavior."""
        if clear_first:
            element.clear()
            time.sleep(random.uniform(0.1, 0.3))
        
        element.click()
        time.sleep(random.uniform(0.1, 0.3))
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Possible typo
            if (random.random() < self.config.typo_chance and 
                char.lower() in self.typo_map):
                # Make typo
                typo_char = random.choice(self.typo_map[char.lower()])
                if char.isupper():
                    typo_char = typo_char.upper()
                
                element.send_keys(typo_char)
                time.sleep(random.uniform(0.1, 0.4))
                
                # Realize mistake and correct
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Type the correct character
            element.send_keys(char)
            
            # Variable delay
            delay = random.uniform(
                self.config.min_typing_delay,
                self.config.max_typing_delay
            )
            
            # Longer pause after punctuation
            if char in '.!?,;:':
                delay *= random.uniform(1.5, 3.0)
            
            # Longer pause after space (word boundary)
            elif char == ' ':
                delay *= random.uniform(1.2, 2.0)
            
            time.sleep(delay)
            i += 1
            
            # Occasional thinking pause
            if random.random() < 0.02:
                time.sleep(random.uniform(0.5, 1.5))
