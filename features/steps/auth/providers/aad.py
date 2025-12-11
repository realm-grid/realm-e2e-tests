"""
Azure AD (Entra ID) authentication provider
"""
import os
import sys
import time
from typing import Optional, Dict

# Add parent auth directory to path
_auth_dir = os.path.dirname(os.path.dirname(__file__))
if _auth_dir not in sys.path:
    sys.path.insert(0, _auth_dir)

from base import BaseAuthProvider, AuthResult, AuthManager


class AzureADProvider(BaseAuthProvider):
    """Azure AD SSO authentication provider"""
    
    PROVIDER_NAME = "aad"
    
    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME
    
    def get_credentials(self) -> Dict[str, str]:
        return {
            "email": os.getenv("SSO_TEST_USER_EMAIL", "test.sso.user@xevolve.io"),
            "password": os.getenv("SSO_TEST_USER_PASSWORD", "")
        }
    
    def login(self, redirect_uri: Optional[str] = None) -> AuthResult:
        """Perform Azure AD SSO login"""
        redirect = redirect_uri or getattr(self.context, "web_url", None) or f"{self.functions_url}/api/health"
        login_url = f"{self.functions_url}/api/auth/login/aad?post_login_redirect_uri={redirect}"
        
        # Capture token from redirects
        captured_token = None
        def on_response(response):
            nonlocal captured_token
            token = self._extract_token_from_url(response.url)
            if token:
                captured_token = token
        
        self.page.on("response", on_response)
        
        try:
            self.page.goto(login_url, wait_until="networkidle")
            
            # Handle Azure AD login if redirected
            if "login.microsoftonline.com" in self.page.url:
                self._complete_azure_login()
            
            # Wait for callback to complete (it returns a 302 redirect)
            # Give it time to follow redirects
            for _ in range(10):
                time.sleep(0.5)
                current_url = self.page.url
                # If we're no longer at the callback URL (redirected to final destination)
                if "auth/callback" not in current_url:
                    break
                # Check if we're still at callback - page might show error
                if "auth/callback" in current_url and "auth_token" not in current_url:
                    # Callback might have returned an error - check page content
                    pass
            
            # Get token from final URL if not captured
            if not captured_token:
                captured_token = self._extract_token_from_url(self.page.url)
            
            if captured_token:
                result = self.validate_token(captured_token)
                result.redirect_url = self.page.url
                return result
            
            # If still at callback URL, grab the page content for debugging
            page_content = ""
            if "auth/callback" in self.page.url:
                try:
                    page_content = self.page.content()[:1000]
                except:
                    pass
            
            error_msg = f"No token received. Final URL: {self.page.url}"
            if page_content:
                error_msg += f"\nPage content: {page_content}"
            
            return AuthResult(
                success=False,
                error=error_msg
            )
        finally:
            self.page.remove_listener("response", on_response)
    
    def _complete_azure_login(self):
        """Complete the Azure AD login form"""
        creds = self.get_credentials()
        
        # Enter email
        self.page.wait_for_selector('input[type="email"]', timeout=15000)
        self.page.fill('input[type="email"]', creds["email"])
        self.page.click('input[type="submit"]')
        
        # Enter password
        time.sleep(2)
        self.page.wait_for_selector('input[type="password"]', timeout=15000)
        self.page.fill('input[type="password"]', creds["password"])
        self.page.click('input[type="submit"]')
        
        time.sleep(3)
        self._handle_post_login_prompts()
        self._wait_for_redirect()
    
    def _handle_post_login_prompts(self):
        """Handle 'Stay signed in?' and consent prompts"""
        # Stay signed in prompt
        try:
            if self.page.locator('text="Stay signed in?"').is_visible(timeout=3000):
                self.page.click('input[value="No"]')
        except:
            pass
        
        # Consent prompt
        try:
            if self.page.locator('input[value="Accept"]').is_visible(timeout=3000):
                self.page.click('input[value="Accept"]')
        except:
            pass
    
    def _wait_for_redirect(self, max_seconds: int = 15):
        """Wait for redirect away from Azure AD"""
        for _ in range(max_seconds):
            time.sleep(1)
            if "login.microsoftonline.com" not in self.page.url:
                break


# Register provider
AuthManager.register(AzureADProvider)
