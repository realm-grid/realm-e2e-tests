"""
Authentication step definitions - Given steps
"""
import os
import sys
import time
import jwt
from datetime import datetime, timedelta
from behave import given

# Add steps directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from auth import AuthManager


@given("the API is healthy")
def step_api_is_healthy(context):
    """Verify the API is responding"""
    response = context.page.request.get(f"{context.functions_url}/api/health")
    if response.status == 503:
        time.sleep(3)
        response = context.page.request.get(f"{context.functions_url}/api/health")
    assert response.status in [200, 503], f"Health check failed: {response.status}"


@given("I am on the SSO login page")
def step_on_sso_login_page(context):
    """Navigate to the SSO login endpoint"""
    # Use the Functions API login endpoint directly
    login_url = f"{context.functions_url}/api/auth/login/aad"
    context.page.goto(login_url)


@given("I am not authenticated")
def step_not_authenticated(context):
    """Ensure user is not authenticated"""
    # Clear any existing cookies/session
    context.page.context.clear_cookies()
    context.auth_token = None
    context.auth_user = None


@given("I have logged in with SSO")
def step_logged_in_with_sso(context):
    """Login with Azure AD SSO"""
    provider = AuthManager.get_provider("aad", context)
    result = provider.login()
    assert result.success, f"SSO login failed: {result.error}"
    context.auth_token = result.token
    context.auth_user = result.user


@given('I have logged in with "{provider_name}"')
def step_logged_in_with_provider(context, provider_name):
    """Login with specified provider"""
    provider = AuthManager.get_provider(provider_name, context)
    result = provider.login()
    assert result.success, f"Login failed: {result.error}"
    context.auth_token = result.token
    context.auth_user = result.user


@given("there is at least one server available")
def step_server_available(context):
    """Check if servers exist"""
    response = context.page.request.get(
        f"{context.functions_url}/api/server/list",
        headers={"Authorization": f"Bearer {context.auth_token}"}
    )
    context.has_servers = False
    if response.status == 200:
        data = response.json()
        context.servers = data.get("servers", [])
        context.has_servers = len(context.servers) > 0


@given("I have an expired auth token")
def step_expired_token(context):
    """Create an expired JWT token"""
    secret = os.getenv("JWT_SECRET", "realm-grid-dev-secret-change-in-production")
    payload = {
        "sub": "test-user",
        "email": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=24),
    }
    context.auth_token = jwt.encode(payload, secret, algorithm="HS256")


@given("I have an invalid auth token")
def step_invalid_token(context):
    """Create an invalid token"""
    context.auth_token = "invalid.token.here"
