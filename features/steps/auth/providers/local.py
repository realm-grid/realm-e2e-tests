"""
Local account authentication provider (username/password)
"""
import os
import sys
from typing import Optional, Dict

# Add parent auth directory to path
_auth_dir = os.path.dirname(os.path.dirname(__file__))
if _auth_dir not in sys.path:
    sys.path.insert(0, _auth_dir)

from base import BaseAuthProvider, AuthResult, AuthManager


class LocalAuthProvider(BaseAuthProvider):
    """Local username/password authentication provider"""
    
    PROVIDER_NAME = "local"
    
    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME
    
    def get_credentials(self) -> Dict[str, str]:
        return {
            "email": os.getenv("LOCAL_TEST_USER_EMAIL", "test@example.com"),
            "password": os.getenv("LOCAL_TEST_USER_PASSWORD", "")
        }
    
    def login(self, redirect_uri: Optional[str] = None) -> AuthResult:
        """Perform local account login"""
        redirect = redirect_uri or f"{self.functions_url}/api/health"
        login_url = f"{self.functions_url}/api/auth/login/local?post_login_redirect_uri={redirect}"
        
        captured_token = None
        def on_response(response):
            nonlocal captured_token
            token = self._extract_token_from_url(response.url)
            if token:
                captured_token = token
        
        self.page.on("response", on_response)
        
        try:
            self.page.goto(login_url, wait_until="networkidle")
            
            # Fill login form if present
            if self._is_login_form_present():
                self._complete_login_form()
            
            if not captured_token:
                captured_token = self._extract_token_from_url(self.page.url)
            
            if captured_token:
                result = self.validate_token(captured_token)
                result.redirect_url = self.page.url
                return result
            
            return AuthResult(
                success=False,
                error=f"No token received. Final URL: {self.page.url}"
            )
        finally:
            self.page.remove_listener("response", on_response)
    
    def _is_login_form_present(self) -> bool:
        """Check if login form is displayed"""
        try:
            return self.page.locator('input[name="email"], input[name="username"]').is_visible(timeout=3000)
        except:
            return False
    
    def _complete_login_form(self):
        """Fill and submit the login form"""
        creds = self.get_credentials()
        
        # Try email or username field
        email_field = self.page.locator('input[name="email"], input[name="username"]').first
        email_field.fill(creds["email"])
        
        # Fill password
        self.page.fill('input[name="password"], input[type="password"]', creds["password"])
        
        # Submit
        self.page.click('button[type="submit"], input[type="submit"]')


# Register provider
AuthManager.register(LocalAuthProvider)
