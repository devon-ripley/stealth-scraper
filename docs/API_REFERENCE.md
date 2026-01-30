# API Reference

Complete method listing for core scraper classes.

---

## StealthBrowser

The primary interface for automation.

### `navigate(url: str)`
Navigates to a URL with human-like waits and behavior.

### `wait_for_element(by, value, timeout=10, condition="presence")`
Waits for an element. Conditions: `presence`, `visible`, `clickable`.

### `click_element(element, scroll_first=True)`
Moves mouse to element and clicks.

### `type_into(element, text, scroll_first=True)`
Moves mouse to element, clicks, and types with realistic logic.

### `simulate_reading(word_count=None)`
Simulates reading the page with natural scrolling.

### `simulate_window_switching()`
Simulates tabbing away and back (Focus/Blur events).

### `simulate_shortcut(keys)`
Simulates keyboard shortcuts (e.g., `['Control', 'c']`).

---

## HumanMouseSimulator

Accessible via `browser.mouse`.

### `move_to(x, y, click=False)`
Curved mouse movement to coordinates.

### `move_to_element(element, click=False)`
Curved mouse movement to an element's bounding box.

---

## HumanScrollSimulator

Accessible via `browser.scroll`.

### `scroll_page(direction="down", amount=0.7)`
Scrolls by viewport percentage.

### `scroll_to_element(element, align="center")`
Brings element into view.

---

## HumanTypingSimulator

Accessible via `browser.typing`.

### `type_text(element, text, clear_first=True)`
Types into an element with variable delays and typos.
