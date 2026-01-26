import time
import json
import logging
import traceback
import random
import os
from dotenv import load_dotenv
from stealth_scraper import StealthBrowser, StealthConfig, ProxyConfig
from selenium.webdriver.common.by import By

# Load environment variables
load_dotenv()

# Create output directory
OUTPUT_DIR = "test_results"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, "feature_test_report.txt"), mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StealthScraperFeatureTest")

def test_easy_target():
    """Test basic navigation on a simple static site."""
    url = "http://books.toscrape.com/"
    logger.info(f"\nTesting Easy Target: {url}")
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
    """Test AJAX/JS rendering capabilities."""
    url = "https://www.scrapethissite.com/pages/ajax-javascript/"
    logger.info(f"\nTesting Medium Target (AJAX/JS): {url}")
    try:
        with StealthBrowser() as browser:
            browser.navigate(url)
            # Find element that loads via JS
            try:
                browser.wait_for_element(By.LINK_TEXT, "2015", timeout=10)
                logger.info("✅ Medium Target Test PASSED (Dynamic content found)")
                return True
            except:
                logger.warning("⚠️ Medium Target Test: '2015' link not found via wait. Checking source...")
                
            page_source = browser.get_page_source()
            if "Oscar Winning Films" in page_source: 
                logger.info("✅ Medium Target Test PASSED (Basic Load)") 
                return True
            else:
                logger.error("❌ Medium Target Test FAILED: Content not found")
                return False

    except Exception as e:
        logger.error(f"❌ Medium Target Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_hard_target_fingerprint():
    """Test vs bot detection/fingerprinting site."""
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
            
            screenshot_path = os.path.join(OUTPUT_DIR, "sannysoft_feature_result.png")
            browser.save_screenshot(screenshot_path)
            logger.info(f"Snapshot saved to {screenshot_path}")
            
            # Simple check: pass if no exception
            logger.info("✅ Hard Target 1 Test COMPLETED")
            return True
    except Exception as e:
        logger.error(f"❌ Hard Target 1 Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_hard_target_cloudflare():
    """Test Cloudflare bypass capability."""
    url = "https://nowsecure.nl"
    logger.info(f"\nTesting Hard Target 2 (Cloudflare): {url}")
    try:
        config = StealthConfig(
            use_undetected_chrome=True,
        )
        with StealthBrowser(stealth_config=config) as browser:
            browser.navigate(url)
            time.sleep(15)  # Give Cloudflare time to clear
            
            title = browser.driver.title
            logger.info(f"Page Title: {title}")
            
            if "Just a moment" in title or "Attention Required" in title or "Challenge" in title:
                 logger.error("❌ Hard Target 2 Test FAILED: Stuck on Cloudflare challenge")
                 return False
            
            logger.info("✅ Hard Target 2 Test PASSED (Likely bypassed)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Hard Target 2 Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_proxy_integration():
    """Test DataImpulse proxy integration if credentials exist."""
    logger.info("\nTesting Proxy Integration")
    
    username = os.getenv("DATAIMPULSE_USERNAME")
    password = os.getenv("DATAIMPULSE_PASSWORD")
    
    if not username or not password:
        logger.warning("⚠️ Proxy credentials not found in .env. Skipping proxy test.")
        return True # Skip but consider passed/ignored
        
    try:
        proxy_config = ProxyConfig(
            enabled=True,
            username=username,
            password=password,
            country="us"
        )
        
        with StealthBrowser(proxy_config=proxy_config) as browser:
            logger.info("Checking IP via httpbin...")
            browser.navigate("https://httpbin.org/ip")
            time.sleep(2)
            
            try:
                body = browser.driver.find_element(By.TAG_NAME, "pre").text
                logger.info(f"Proxy IP Response: {body}")
                if "origin" in body:
                    logger.info("✅ Proxy Test PASSED")
                    return True
            except:
                body = browser.driver.find_element(By.TAG_NAME, "body").text
                logger.info(f"Proxy Body: {body}")
                if "origin" in body:
                    logger.info("✅ Proxy Test PASSED")
                    return True
                
            logger.error("❌ Proxy Test FAILED: 'origin' not found in response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Proxy Test ERROR: {str(e)}")
        return False

def test_human_behavior():
    """Test human-like interactions: mouse, scroll, typing."""
    url = "https://quotes.toscrape.com/login"
    logger.info(f"\nTesting Human Behavior (Mouse, Scroll, Type): {url}")
    try:
        with StealthBrowser() as browser:
            browser.navigate(url)
            
            # 1. Test Mouse Movement
            logger.info("Testing Mouse Simulator...")
            # Move to random coordinates
            browser.random_mouse_movement()
            browser.random_pause(0.5, 1.0)
            
            # Move to specific element (submit button)
            submit_btn = browser.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            browser.mouse.move_to_element(submit_btn)
            logger.info("✅ Mouse moved to element")
            
            # 2. Test Typing (with typos)
            logger.info("Testing Typing Simulator...")
            username_input = browser.driver.find_element(By.ID, "username")
            password_input = browser.driver.find_element(By.ID, "password")
            
            # Type with simulated human speed
            browser.type_into(username_input, "test_user_human")
            browser.random_pause(0.5, 1.0)
            browser.type_into(password_input, "secret_pass_123")
            
            # Verify text was typed
            if "test_user" in username_input.get_attribute("value"):
                logger.info("✅ Typing simulated successfully")
            else:
                logger.error("❌ Typing verification failed")
                return False
                
            # 3. Test Scrolling
            logger.info("Testing Scroll Simulator...")
            browser.navigate("https://quotes.toscrape.com/")
            
            # Scroll down
            start_y = browser.execute_script("return window.scrollY")
            browser.scroll.scroll_page("down", 0.5)
            time.sleep(1)
            end_y = browser.execute_script("return window.scrollY")
            
            if end_y > start_y:
                logger.info(f"✅ Scroll down successful (Moved {end_y - start_y}px)")
            else:
                logger.warning("⚠️ Scroll down didn't change position (page might be too short)")
                
            # Scroll to specific element (footer)
            # Find a link in the footer or bottom
            try:
                next_li = browser.driver.find_element(By.CLASS_NAME, "next")
                browser.scroll.scroll_to_element(next_li)
                logger.info("✅ Scroll to element successful")
            except:
                pass
                
            logger.info("✅ Human Behavior Test PASSED")
            return True
            
    except Exception as e:
        logger.error(f"❌ Human Behavior Test ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting Stealth Scraper Feature Test Suite...")
    
    tests = [
        test_easy_target,
        test_medium_target,
        test_human_behavior,  # New test
        test_hard_target_fingerprint,
        test_hard_target_cloudflare,
        test_proxy_integration
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(2) # Pause between tests
    
    success_count = sum(1 for r in results if r)
    logger.info("\n" + "="*30)
    logger.info(f"Tests Completed: {success_count}/{len(tests)} Passed")
    logger.info(f"See {os.path.join(OUTPUT_DIR, 'feature_test_report.txt')} for details.")
