"""
Behave environment configuration and hooks for features directory
"""
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def before_all(context):
    """Setup before all tests"""
    # Load configuration
    context.environment = os.getenv("ENVIRONMENT", "dev")
    context.admin_url = os.getenv("ADMIN_URL")
    context.web_url = os.getenv("WEB_URL")
    context.functions_url = os.getenv("FUNCTIONS_URL")
    
    # Test users
    context.test_user = {
        "email": os.getenv("TEST_USER_EMAIL"),
        "password": os.getenv("TEST_USER_PASSWORD")
    }
    context.admin_user = {
        "email": os.getenv("ADMIN_USER_EMAIL"),
        "password": os.getenv("ADMIN_USER_PASSWORD")
    }
    
    # Payment test data
    context.stripe_test_card = {
        "number": os.getenv("STRIPE_TEST_CARD"),
        "cvc": os.getenv("STRIPE_TEST_CVC"),
        "exp_month": os.getenv("STRIPE_TEST_EXP_MONTH"),
        "exp_year": os.getenv("STRIPE_TEST_EXP_YEAR")
    }
    
    # Browser settings
    context.headless = os.getenv("HEADLESS", "false").lower() == "true"
    context.slow_mo = int(os.getenv("SLOW_MO", "0"))
    context.browser_type = os.getenv("BROWSER", "chromium")

def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Start Playwright
    context.playwright = sync_playwright().start()
    
    # Launch browser
    if context.browser_type == "firefox":
        browser = context.playwright.firefox.launch(
            headless=context.headless,
            slow_mo=context.slow_mo
        )
    elif context.browser_type == "webkit":
        browser = context.playwright.webkit.launch(
            headless=context.headless,
            slow_mo=context.slow_mo
        )
    else:
        browser = context.playwright.chromium.launch(
            headless=context.headless,
            slow_mo=context.slow_mo
        )
    
    context.browser = browser
    context.page = browser.new_page()
    
    # Set viewport
    context.page.set_viewport_size({"width": 1920, "height": 1080})

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Take screenshot on failure
    if scenario.status == "failed":
        screenshot_dir = "reports/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = f"{screenshot_dir}/{scenario.name.replace(' ', '_')}.png"
        context.page.screenshot(path=screenshot_path)
    
    # Close browser
    context.page.close()
    context.browser.close()
    context.playwright.stop()

def after_all(context):
    """Cleanup after all tests"""
    pass
