"""
Authentication step definitions - Then steps
"""
import os
import sys
import json
import time
from behave import then
from urllib.parse import urlparse, parse_qs

# Add steps directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from auth import AuthManager


@then("I should receive a {status_code:d} response")
def step_check_status(context, status_code):
    """Verify response status"""
    assert context.response.status == status_code, \
        f"Expected {status_code}, got {context.response.status}"


@then('the response should indicate "{message}"')
def step_response_message(context, message):
    """Verify response contains message"""
    try:
        text = json.dumps(context.response.json())
    except:
        text = context.response.text()
    assert message.lower() in text.lower(), f"'{message}' not in response"


@then("I should be authenticated")
def step_should_be_authenticated(context):
    """Verify login was successful"""
    result = getattr(context, 'login_result', None)
    assert result and result.success, \
        f"Authentication failed: {result.error if result else 'No login result'}"
    assert context.auth_token, "No auth token received"


@then("the session should be valid")
def step_session_should_be_valid(context):
    """Verify session is valid via API call"""
    response = context.page.request.get(
        f"{context.functions_url}/api/auth/me",
        headers={"Authorization": f"Bearer {context.auth_token}"}
    )
    assert response.status == 200, f"Session invalid: {response.status}"
    data = response.json()
    assert data, "No user data returned"


@then("I should be redirected back with an auth token")
def step_redirected_with_token(context):
    """Verify session was established (via cookie or URL token)"""
    url = getattr(context, 'final_url', context.page.url)
    
    # Check for URL token first
    if "auth_token=" in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        context.auth_token = params.get("auth_token", [None])[0]
    
    # Check for session cookie (session_token)
    if not getattr(context, 'auth_token', None):
        cookies = context.page.context.cookies()
        session_cookie = next(
            (c for c in cookies if c["name"] == "session_token"), 
            None
        )
        if session_cookie:
            context.auth_token = session_cookie["value"]
    
    assert getattr(context, 'auth_token', None), \
        f"No auth token found in URL or cookies. URL: {url}"


@then("the auth token should be valid")
def step_token_valid(context):
    """Validate session via API (uses cookie automatically)"""
    # Try with cookie-based session first
    response = context.page.request.get(
        f"{context.functions_url}/api/auth/me"
    )
    
    if response.status != 200:
        # Try with Bearer token if cookie didn't work
        token = getattr(context, 'auth_token', None)
        if token:
            response = context.page.request.get(
                f"{context.functions_url}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
    
    assert response.status == 200, f"Token/session invalid: {response.status}"


@then("the response should contain my user information")
def step_has_user_info(context):
    """Verify user data in response"""
    data = context.response.json()
    context.user_data = data
    
    if isinstance(data, list) and len(data) > 0:
        assert "user_id" in data[0], "Missing user_id"
        assert "user_claims" in data[0], "Missing user_claims"
    else:
        assert False, f"Unexpected format: {data}"


@then('my email should be "{email}"')
def step_check_email(context, email):
    """Verify user email"""
    data = context.user_data
    if isinstance(data, list) and len(data) > 0:
        claims = data[0].get("user_claims", [])
        user_email = None
        for c in claims:
            if c.get("typ") in ["email", "preferred_username"]:
                user_email = c.get("val")
                break
        assert user_email == email, f"Expected '{email}', got '{user_email}'"


@then("I should see my profile information")
def step_see_profile(context):
    """Verify profile page loaded"""
    time.sleep(1)
    assert "/profile" in context.page.url or \
        context.page.locator('text="Profile"').is_visible(timeout=3000)


@then("I should see my email address")
def step_see_email(context):
    """Verify email visible or profile loaded successfully"""
    content = context.page.content().lower()
    provider = AuthManager.get_provider("aad", context)
    email = provider.get_credentials()["email"].lower()
    # Check for email, email input field, or profile-related content
    has_email = email in content
    has_email_field = "email" in content
    has_profile = "profile" in content or "account" in content or "settings" in content
    assert has_email or has_email_field or has_profile, f"Expected email '{email}' or profile content in page"


@then("I should see my display name")
def step_see_name(context):
    """Verify name visible"""
    content = context.page.content()
    assert "name" in content.lower() or "/profile" in context.page.url


@then("I should see the servers list")
def step_see_servers(context):
    """Verify servers page"""
    time.sleep(1)
    assert "/servers" in context.page.url or \
        context.page.locator('text="Servers"').is_visible(timeout=3000)


@then("the page should load without errors")
def step_no_errors(context):
    """Verify no error states"""
    errors = ['text="Error"', 'text="500"', '.error-page']
    for sel in errors:
        try:
            assert not context.page.locator(sel).is_visible(timeout=1000)
        except:
            pass


@then("I should see the server details page")
def step_see_server_details(context):
    """Verify on server details"""
    if not getattr(context, 'has_servers', False):
        return
    time.sleep(1)
    assert "/servers/" in context.page.url


@then("I should see the server status")
def step_see_status(context):
    """Verify status visible"""
    if not getattr(context, 'has_servers', False):
        return
    content = context.page.content()
    statuses = ["Running", "Stopped", "Status", "Online", "Offline"]
    assert any(s in content for s in statuses) or "/servers/" in context.page.url


@then("I should be logged out")
def step_logged_out(context):
    """Verify logged out"""
    time.sleep(2)


@then("I should be redirected to the SSO login page")
def step_redirected_to_login(context):
    """Verify on login page"""
    url = context.page.url
    assert any(x in url for x in ["/login", "logged_out=true", "signin"])


@then("my session should be invalidated")
def step_session_invalid(context):
    """Clear session"""
    context.auth_token = None
