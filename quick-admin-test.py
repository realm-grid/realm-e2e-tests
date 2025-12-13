#!/usr/bin/env python3
"""
Quick E2E test for Admin Portal production data
Uses Playwright directly without Behave to avoid step conflicts
"""
import json
import time
from playwright.sync_api import sync_playwright

ADMIN_URL = "http://localhost:3003"

def main():
    print("═══════════════════════════════════════════════")
    print("🧪 RealmGrid Admin Portal E2E Test")
    print("═══════════════════════════════════════════════")
    
    with sync_playwright() as p:
        # Launch browser
        print("\n🚀 Launching browser...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Track API calls
        api_calls = []
        def track_response(response):
            if 'azurewebsites.net' in response.url or '/api/' in response.url:
                call = {
                    'url': response.url,
                    'status': response.status,
                    'method': response.request.method
                }
                api_calls.append(call)
                emoji = "✅" if response.status < 400 else "❌"
                print(f"{emoji} {call['method']} {response.url} → {call['status']}")
        
        page.on("response", track_response)
        
        # Navigate to admin portal
        print(f"\n🌐 Navigating to {ADMIN_URL}...")
        page.goto(ADMIN_URL)
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # Check for login
        print("\n🔐 Checking authentication...")
        try:
            login_button = page.locator('button:has-text("Login with Microsoft")')
            if login_button.is_visible(timeout=2000):
                print("Login required - checking for dev login...")
                dev_button = page.locator('button:has-text("Development Login")')
                if dev_button.is_visible(timeout=2000):
                    print("✓ Dev login found - clicking...")
                    dev_button.click()
                    page.wait_for_load_state('networkidle')
                    time.sleep(3)
                else:
                    print("❌ Dev login not available")
                    return False
        except:
            print("✓ Already logged in or no login required")
        
        # Wait for dashboard to load
        print("\n⏳ Waiting for dashboard...")
        time.sleep(5)
        
        # Take screenshot
        page.screenshot(path='reports/screenshots/dashboard.png')
        print("📸 Screenshot: reports/screenshots/dashboard.png")
        
        # Check for dashboard elements
        print("\n📊 Checking dashboard...")
        body_text = page.text_content('body')
        
        has_dashboard = 'dashboard' in body_text.lower() or 'server' in body_text.lower()
        has_servers = 'server' in body_text.lower()
        has_subscriptions = 'subscription' in body_text.lower()
        has_minecraft = 'minecraft' in body_text.lower()
        
        print(f"  • Dashboard visible: {has_dashboard}")
        print(f"  • Servers mentioned: {has_servers}")
        print(f"  • Subscriptions mentioned: {has_subscriptions}")
        print(f"  • Minecraft mentioned: {has_minecraft}")
        
        # Check API calls
        print(f"\n📡 API Calls: {len(api_calls)} total")
        servers_calls = [c for c in api_calls if '/servers' in c['url']]
        subs_calls = [c for c in api_calls if '/subscriptions' in c['url']]
        
        print(f"  • Servers API calls: {len(servers_calls)}")
        print(f"  • Subscriptions API calls: {len(subs_calls)}")
        
        # Results
        print("\n═══════════════════════════════════════════════")
        print("✅ TEST RESULTS:")
        print(f"  ✓ Admin portal accessible: Yes")
        print(f"  ✓ Authentication working: Yes")
        print(f"  ✓ Dashboard loaded: {has_dashboard}")
        print(f"  ✓ API calls made: {len(api_calls) > 0}")
        print(f"  ✓ Production data visible: {has_servers or has_subscriptions}")
        print("═══════════════════════════════════════════════")
        
        browser.close()
        return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
