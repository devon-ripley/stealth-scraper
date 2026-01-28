---
description: How to develop a stealth scraping script using all stealth levels
---

Follow this workflow to create a robust web scraping script that navigates a website using the `stealth-scraper` package. This workflow ensures you implement all stealth levels (LOW, MEDIUM, HIGH, PARANOID) correctly.

1. **Understand the Goal**: You are building a Python script that will visit a URL and perform actions (scroll, click, read) using different stealth profiles.

2. **Setup the Script Structure**:
   Create a new file (e.g., `stealth_demo.py`) with the necessary imports:
   ```python
   from stealth_scraper import create_browser_with_level, StealthLevel
   import time
   from selenium.webdriver.common.by import By
   ```

3. **Define the Navigation Logic**:
   Create a function `run_stealth_check(level, url)` that:
   - Takes a `StealthLevel` and a `url`.
   - Uses `create_browser_with_level(level)` context manager.
   - Navigates to the URL.
   - Performs human-like actions:
     - `browser.simulate_reading()` (scrolls and reads).
     - `browser.mouse.move_to_element()` (moves mouse to elements).
     - `browser.random_pause()` (waits unpredictably).

4. **Implement PARANOID Specifics**:
   - **CRITICAL**: For `StealthLevel.PARANOID`, the browser MUST NOT be headless. Ensure your script acknowledges this (e.g., print "Starting visible browser for PARANOID mode").
   - Add extra hesitation logic if manual interaction is scripted (though the package handles most of this automatically).

5. **Create the Main Execution Loop**:
   - Define a list of levels: `[StealthLevel.LOW, StealthLevel.MEDIUM, StealthLevel.HIGH, StealthLevel.PARANOID]`.
   - Iterate through them, calling your navigation function.
   - **TIP**: Start with a simple target (e.g., `example.com`) for testing.

6. **Example Implementation Pattern**:
   ```python
   def run_demo():
       url = "https://example.com"
       
       for level in [StealthLevel.LOW, StealthLevel.MEDIUM, StealthLevel.HIGH, StealthLevel.PARANOID]:
           print(f"Running level: {level.name}")
           try:
               with create_browser_with_level(level) as browser:
                   browser.navigate(url)
                   browser.simulate_reading(word_count=50)
                   browser.random_pause(1, 2)
                   print(f" - {level.name} completed successfully")
           except Exception as e:
               print(f" - {level.name} failed: {e}")
   ```

7. **Verification**:
   - Run the script.
   - Observe that `LOW` runs quickly.
   - Observe that `HIGH` and `PARANOID` take longer, scroll smoothly, and (for Paranoid) open a visible window.
