#!/usr/bin/env python3
"""
SSO Authentication Test for Azure Functions
Tests the complete OAuth flow from login to callback to /auth/me
"""
import os
import sys
import json
import time
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect

# Test Configuration
FUNCTIONS_BASE_URL = "https://realm-dev-api-fa.azurewebsites.net/api"
TEST_USER_EMAIL = "test.sso.user@xevolve.io"
TEST_USER_PASSWORD = "uihfa#FAr214asd!"
SSO_CLIENT_ID = "524d8f43-6a4a-4117-b4fe-008906598d0b"
TENANT_ID = "34dd9821-1508-4858-974c-e5fd1493a58f"

def test_sso_authentication():
    """Test the complete SSO authentication flow"""
    print("\n" + "="*60)
    print("SSO AUTHENTICATION TEST")
    print("="*60)
    print(f"\nTarget: {FUNCTIONS_BASE_URL}")
    print(f"User: {TEST_USER_EMAIL}")
    print(f"SSO App: {SSO_CLIENT_ID}")
    print("="*60 + "\n")
    
    with sync_playwright() as p:
        # Launch browser (headless for CI, set to False for debugging)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable request/response logging
        auth_token = None
        
        def handle_response(response):
            nonlocal auth_token
            url = response.url
            if "auth_token=" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if "auth_token" in params:
                    auth_token = params["auth_token"][0]
                    print(f"✓ Captured auth_token from redirect")
        
        page.on("response", handle_response)
        
        try:
            # Step 1: Test health endpoint first
            print("Step 1: Testing health endpoint...")
            response = page.request.get(f"{FUNCTIONS_BASE_URL}/health")
            print(f"  Health: HTTP {response.status}")
            
            # Step 2: Test /auth/me without token (should return 401)
            print("\nStep 2: Testing /auth/me without token...")
            response = page.request.get(f"{FUNCTIONS_BASE_URL}/auth/me")
            print(f"  /auth/me (no token): HTTP {response.status}")
            if response.status == 401:
                print("  ✓ Correctly returns 401 for unauthenticated request")
            else:
                print(f"  ⚠ Expected 401, got {response.status}")
                print(f"  Response: {response.text()[:200]}")
            
            # Step 3: Initiate login flow
            print("\nStep 3: Initiating SSO login flow...")
            # Use function app URL as redirect so we don't need localhost running
            login_url = f"{FUNCTIONS_BASE_URL}/auth/login/aad?post_login_redirect_uri=https://realm-dev-api-fa.azurewebsites.net/api/health"
            print(f"  Login URL: {login_url}")
            
            page.goto(login_url, wait_until="networkidle")
            current_url = page.url
            print(f"  Redirected to: {current_url[:80]}...")
            
            # Should be on Microsoft login page
            if "login.microsoftonline.com" in current_url:
                print("  ✓ Redirected to Azure AD login page")
            else:
                print(f"  ⚠ Unexpected redirect: {current_url}")
            
            # Step 4: Enter credentials
            print("\nStep 4: Entering credentials...")
            
            # Wait for email input
            page.wait_for_selector('input[type="email"]', timeout=10000)
            page.fill('input[type="email"]', TEST_USER_EMAIL)
            print(f"  Entered email: {TEST_USER_EMAIL}")
            
            # Click Next
            page.click('input[type="submit"]')
            print("  Clicked Next")
            
            # Wait for password input (may take a moment)
            time.sleep(2)
            page.wait_for_selector('input[type="password"]', timeout=10000)
            page.fill('input[type="password"]', TEST_USER_PASSWORD)
            print("  Entered password")
            
            # Click Sign in
            page.click('input[type="submit"]')
            print("  Clicked Sign in")
            
            # Step 5: Handle "Stay signed in?" prompt if it appears
            print("\nStep 5: Handling post-login prompts...")
            time.sleep(3)
            
            # Check for "Stay signed in?" prompt
            try:
                stay_signed_in = page.locator('text="Stay signed in?"')
                if stay_signed_in.is_visible(timeout=3000):
                    print("  Found 'Stay signed in?' prompt")
                    # Click No
                    page.click('input[value="No"]')
                    print("  Clicked 'No'")
            except:
                print("  No 'Stay signed in?' prompt")
            
            # Check for consent prompt
            try:
                consent_btn = page.locator('input[value="Accept"]')
                if consent_btn.is_visible(timeout=3000):
                    print("  Found consent prompt")
                    consent_btn.click()
                    print("  Clicked 'Accept'")
            except:
                print("  No consent prompt")
            
            # Step 6: Wait for callback redirect
            print("\nStep 6: Waiting for callback redirect...")
            
            # Wait for the page to navigate away from login.microsoftonline.com
            max_wait = 15
            for i in range(max_wait):
                time.sleep(1)
                current_url = page.url
                print(f"  [{i+1}s] URL: {current_url[:80]}...")
                if "login.microsoftonline.com" not in current_url:
                    break
            
            final_url = page.url
            print(f"  Final URL: {final_url}")
            
            # Check if we got redirected back with a token
            if "auth_token=" in final_url:
                parsed = urlparse(final_url)
                params = parse_qs(parsed.query)
                auth_token = params.get("auth_token", [None])[0]
                print(f"  ✓ Got auth_token in URL!")
            elif "localhost" in final_url and auth_token:
                print(f"  ✓ Redirected to localhost with token")
            elif "error" in final_url.lower():
                print(f"  ✗ Error in redirect URL")
                print(f"  Full URL: {final_url}")
            else:
                print(f"  Current page content preview:")
                print(f"  {page.content()[:500]}...")
            
            # Step 7: Test /auth/me with token
            if auth_token:
                print(f"\nStep 7: Testing /auth/me with token...")
                print(f"  Token (first 50 chars): {auth_token[:50]}...")
                
                response = page.request.get(
                    f"{FUNCTIONS_BASE_URL}/auth/me",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                print(f"  /auth/me (with token): HTTP {response.status}")
                
                if response.status == 200:
                    user_data = response.json()
                    print(f"  ✓ SUCCESS! User authenticated")
                    print(f"  User data: {json.dumps(user_data, indent=2)}")
                else:
                    print(f"  ✗ Failed to get user info")
                    print(f"  Response: {response.text()[:500]}")
            else:
                print("\nStep 7: Skipped - No auth token captured")
                print("  Checking page for errors...")
                print(f"  Page URL: {page.url}")
                
                # Take a screenshot for debugging
                screenshot_path = "/home/falk/realm-grid/realm-e2e-tests/sso_debug.png"
                page.screenshot(path=screenshot_path)
                print(f"  Screenshot saved to: {screenshot_path}")
            
            # Summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)
            if auth_token:
                print("✓ SSO Authentication: PASSED")
            else:
                print("✗ SSO Authentication: FAILED - No token received")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            
            # Take screenshot on error
            screenshot_path = "/home/falk/realm-grid/realm-e2e-tests/sso_error.png"
            try:
                page.screenshot(path=screenshot_path)
                print(f"  Error screenshot saved to: {screenshot_path}")
            except:
                pass
            
            print(f"\n  Current URL: {page.url}")
            raise
        
        finally:
            browser.close()

def test_function_app_token_auth():
    """Test calling Function App with SPN token (service-to-service)"""
    print("\n" + "="*60)
    print("SPN TOKEN AUTHENTICATION TEST")
    print("="*60)
    
    import requests
    import os
    
    # Get token for the Function App using SPN credentials from environment
    tenant_id = os.getenv("AZURE_TENANT_ID", "34dd9821-1508-4858-974c-e5fd1493a58f")
    client_id = os.getenv("AZURE_CLIENT_ID", "4d33f320-724b-4bc4-944f-d9b22d18df2c")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    
    if not client_secret:
        raise ValueError("AZURE_CLIENT_SECRET environment variable is required")
    
    # The audience should be the SSO app's identifier URI
    scope = f"api://{SSO_CLIENT_ID}/.default"
    
    print(f"\nGetting token for: {scope}")
    print(f"Using SPN: {client_id}")
    
    # Get access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    
    response = requests.post(token_url, data=token_data)
    print(f"Token request: HTTP {response.status_code}")
    
    if response.status_code == 200:
        token_response = response.json()
        access_token = token_response.get("access_token")
        print(f"✓ Got access token (first 50 chars): {access_token[:50]}...")
        
        # Now call the Function App health endpoint with the token
        print(f"\nCalling Function App with SPN token...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        fa_response = requests.get(f"{FUNCTIONS_BASE_URL}/health", headers=headers)
        print(f"  /health: HTTP {fa_response.status_code}")
        
        if fa_response.status_code == 200:
            print("  ✓ Function App accepted SPN token")
        else:
            print(f"  Response: {fa_response.text[:500]}")
    else:
        print(f"✗ Failed to get token: {response.text}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    # Run SPN token test first (doesn't require browser)
    test_function_app_token_auth()
    
    # Then run the full SSO flow test
    test_sso_authentication()
