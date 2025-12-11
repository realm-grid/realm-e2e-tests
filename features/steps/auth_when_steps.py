"""
Authentication step definitions - When steps
"""
import os
import sys
import time
from behave import when

# Add steps directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from auth import AuthManager


@when('I request "{endpoint}" without authentication')
def step_request_without_auth(context, endpoint):
    """Make unauthenticated request"""
    url = f"{context.functions_url}{endpoint}"
    context.response = context.page.request.get(url)


@when('I request "{endpoint}" with my auth token')
def step_request_with_auth(context, endpoint):
    """Make authenticated request"""
    url = f"{context.functions_url}{endpoint}"
    context.response = context.page.request.get(
        url,
        headers={"Authorization": f"Bearer {context.auth_token}"}
    )


@when("I initiate SSO login with Azure AD")
def step_initiate_sso_login(context):
    """Perform full Azure AD SSO login flow"""
    provider = AuthManager.get_provider("aad", context)
    result = provider.login()
    context.login_result = result
    if result.success:
        context.auth_token = result.token
        context.auth_user = result.user


@when('I click the "Sign in with Microsoft" button')
def step_click_sso_button(context):
    """Click SSO login button or navigate to SSO endpoint"""
    selectors = [
        'text="Sign in with Microsoft"',
        'text="Login with Microsoft"',
        '[data-testid="sso-login"]',
        'a[href*="auth/login/aad"]',
    ]
    
    for selector in selectors:
        try:
            el = context.page.locator(selector)
            if el.is_visible(timeout=2000):
                el.click()
                return
        except:
            continue
    
    # Fallback: navigate directly
    redirect = context.admin_url or context.web_url
    url = f"{context.functions_url}/api/auth/login/aad?post_login_redirect_uri={redirect}"
    context.page.goto(url)


@when("I enter my SSO credentials")
def step_enter_sso_credentials(context):
    """Enter Azure AD credentials"""
    provider = AuthManager.get_provider("aad", context)
    creds = provider.get_credentials()
    
    context.page.wait_for_selector('input[type="email"]', timeout=15000)
    context.page.fill('input[type="email"]', creds["email"])
    context.page.click('input[type="submit"]')
    
    time.sleep(2)
    context.page.wait_for_selector('input[type="password"]', timeout=15000)
    context.page.fill('input[type="password"]', creds["password"])
    context.page.click('input[type="submit"]')


@when("I complete the Azure AD login flow")
def step_complete_sso_flow(context):
    """Handle post-login prompts and wait for redirect"""
    time.sleep(3)
    
    # Stay signed in prompt
    try:
        stay_signed_in = context.page.locator('text="Stay signed in?"')
        if stay_signed_in.is_visible(timeout=5000):
            no_button = context.page.locator('input[value="No"]')
            if no_button.is_visible():
                no_button.click()
            else:
                # Try alternative "No" button
                context.page.locator('#idBtn_Back').click()
    except:
        pass
    
    # Consent prompt
    try:
        accept_button = context.page.locator('input[value="Accept"]')
        if accept_button.is_visible(timeout=3000):
            accept_button.click()
    except:
        pass
    
    # Wait for redirect away from Azure AD
    for _ in range(20):
        time.sleep(1)
        current_url = context.page.url
        if "login.microsoftonline.com" not in current_url:
            break
    
    context.final_url = context.page.url


@when("I navigate to the profile page")
def step_navigate_profile(context):
    """Go to profile page"""
    url = context.web_url or context.admin_url
    context.page.goto(f"{url}/profile", wait_until="networkidle", timeout=30000)
    time.sleep(2)


@when("I navigate to the servers page")
def step_navigate_servers(context):
    """Go to servers page"""
    url = context.web_url or context.admin_url
    context.page.goto(f"{url}/servers", wait_until="networkidle", timeout=60000)
    time.sleep(2)


@when("I click on a server")
def step_click_server(context):
    """Click first server"""
    if not getattr(context, 'has_servers', False):
        context.scenario.skip("No servers available")
        return
    
    selectors = ['[data-testid="server-item"]', '.server-card', 'a[href*="/servers/"]']
    for selector in selectors:
        try:
            el = context.page.locator(selector).first
            if el.is_visible(timeout=2000):
                el.click()
                return
        except:
            continue


@when("I click the logout button")
def step_click_logout(context):
    """Click logout"""
    selectors = ['text="Logout"', 'text="Sign out"', '[data-testid="logout"]']
    
    for selector in selectors:
        try:
            el = context.page.locator(selector)
            if el.is_visible(timeout=2000):
                el.click()
                return
        except:
            continue
    
    # Fallback: direct logout
    redirect = context.admin_url or context.web_url
    context.page.goto(f"{context.functions_url}/api/auth/logout?post_login_redirect_uri={redirect}")
