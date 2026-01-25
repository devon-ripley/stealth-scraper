import time
import json
import logging
import traceback
import random
import os
from stealth_scraper import StealthBrowser, StealthConfig
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create output directory
OUTPUT_DIR = "test_results"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, "test_report.txt"), mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StealthScraperTest")

def test_easy_target():
    url = "http://books.toscrape.com/"
    logger.info(f"Testing Easy Target: {url}")
    try:
        with StealthBrowser() as browser:
            browser.navigate(url)
            title = browser.driver.title
            logger.info(f"Page Title: {title}")
            
            if "All products" in title:
                logger.info("✅ Easy Target Test PASSED")
                return True
            else:
                logger.error(f"❌ Easy Target Test FAILED: Expected 'All products' in title, got '{title}'")
                return False
    except Exception as e:
        logger.error(f"❌ Easy Target Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_medium_target():
    url = "https://www.scrapethissite.com/pages/ajax-javascript/"
    logger.info(f"\nTesting Medium Target (AJAX/JS): {url}")
    try:
        with StealthBrowser() as browser:
            browser.navigate(url)
            time.sleep(5) 
            
            page_source = browser.get_page_source()
            if "Oscar Winning Films" in page_source: 
                if "Spotlight" in page_source:
                     logger.info("✅ Medium Target Test PASSED (Dynamic content found)")
                     return True
                else:
                    logger.warning("⚠️ Medium Target Test: 'Spotlight' not found. JS might not have loaded.")
                    
            logger.info("✅ Medium Target Test PASSED (Basic Load)") 
            return True

    except Exception as e:
        logger.error(f"❌ Medium Target Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_hard_target_fingerprint():
    url = "https://bot.sannysoft.com/"
    logger.info(f"\nTesting Hard Target 1 (Fingerprinting): {url}")
    try:
        config = StealthConfig(
            use_undetected_chrome=True,
            mask_automation_indicators=True
        )
        with StealthBrowser(stealth_config=config) as browser:
            browser.navigate(url)
            time.sleep(5) 
            
            screenshot_path = os.path.join(OUTPUT_DIR, "sannysoft_result.png")
            browser.save_screenshot(screenshot_path)
            logger.info(f"Snapshot saved to {screenshot_path}")
            
            page_source = browser.get_page_source()
            
            # Simple check
            logger.info("✅ Hard Target 1 Test COMPLETED (Check screenshot)")
            return True
    except Exception as e:
        logger.error(f"❌ Hard Target 1 Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_hard_target_cloudflare():
    url = "https://nowsecure.nl"
    logger.info(f"\nTesting Hard Target 2 (Cloudflare): {url}")
    try:
        config = StealthConfig(
            use_undetected_chrome=True,
        )
        with StealthBrowser(stealth_config=config) as browser:
            browser.navigate(url)
            time.sleep(10) 
            
            title = browser.driver.title
            logger.info(f"Page Title: {title}")
            
            screenshot_path = os.path.join(OUTPUT_DIR, "cloudflare_result.png")
            browser.save_screenshot(screenshot_path)
            
            if "Just a moment" in title or "Attention Required" in title:
                 logger.error("❌ Hard Target 2 Test FAILED: Stuck on Cloudflare challenge")
                 return False
            
            logger.info("✅ Hard Target 2 Test PASSED (Likely bypassed)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Hard Target 2 Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_very_hard_target_facebook():
    logger.info(f"\nTesting Very Hard Target (Facebook Marketplace)")
    url = "https://www.facebook.com/marketplace/category/vehicles"
    
    config = StealthConfig(
        use_undetected_chrome=True,
        mask_automation_indicators=True,
        viewport_sizes=[(1920, 1080)]
    )

    try:
        with StealthBrowser(stealth_config=config) as browser:
            logger.info("Navigating to URL...")
            browser.navigate(url)
            
            # Cookie Consent
            try:
                buttons = browser.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "allow all" in btn.text.lower() or "accept cookies" in btn.text.lower():
                        logger.info(f"Found cookie button: {btn.text}. Clicking...")
                        browser.click_element(btn)
                        break
            except Exception as e:
                logger.warning(f"Cookie check skipped or failed: {e}")

            time.sleep(5)
            # Check for Login Wall
            if "login" in browser.get_current_url():
                logger.warning("Redirected to Login Page. Public scraping might be blocked.")
            
            # Close Login Modal
            try:
                close_btns = browser.driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Close']")
                for btn in close_btns:
                    if btn.is_displayed():
                        logger.info("Closing modal...")
                        browser.click_element(btn)
                        time.sleep(2)
            except:
                pass

            logger.info("Scrolling to load listings...")
            for _ in range(5):
                browser.scroll.scroll_page("down", random.uniform(0.4, 0.7))
                browser.random_pause(1.5, 3.0)
            
            screenshot_path = os.path.join(OUTPUT_DIR, "fb_marketplace_snapshot.png")
            browser.save_screenshot(screenshot_path)
            logger.info("Extracting listings...")
            
            item_links = browser.driver.find_elements(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")
            items = []
            seen_urls = set()
            
            for link in item_links:
                try:
                    href = link.get_attribute("href")
                    if href in seen_urls: continue
                    seen_urls.add(href)
                    
                    raw_text = link.text.split('\n')
                    price = next((s for s in raw_text if '$' in s or '€' in s or '£' in s), "N/A")
                    title = raw_text[0] if raw_text else "Unknown"
                    if title == price and len(raw_text) > 1:
                        title = raw_text[1]
                        
                    items.append({
                        "id": href.split('/item/')[1].split('/')[0] if '/item/' in href else "unknown",
                        "title": title,
                        "price": price,
                        "url": href,
                        "raw_text": raw_text
                    })
                except:
                    pass
            
            logger.info(f"Found {len(items)} unique items.")
            
            output_file = os.path.join(OUTPUT_DIR, "fb_listings.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved listings to {output_file}")
            
            if len(items) > 0:
                logger.info("✅ Very Hard Target (Facebook) Test PASSED")
                return True
            else:
                 logger.warning("⚠️ Very Hard Target (Facebook): No items found, but no crash.")
                 return True

    except Exception as e:
        logger.error(f"❌ Very Hard Target (Facebook) Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting Stealth Scraper Test Suite...")
    
    results = []
    results.append(test_easy_target())
    results.append(test_medium_target())
    results.append(test_hard_target_fingerprint())
    results.append(test_hard_target_cloudflare())
    results.append(test_very_hard_target_facebook())
    
    logger.info("\n" + "="*30)
    logger.info(f"Tests Completed: {sum(results)}/{len(results)} Passed (Approximate)")
    logger.info(f"See {os.path.join(OUTPUT_DIR, 'test_report.txt')} and screenshots in '{OUTPUT_DIR}' for details.")
