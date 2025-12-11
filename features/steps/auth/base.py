"""
Base authentication classes and interfaces.
Extend BaseAuthProvider for new authentication providers.
"""
import os
import time
import json
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class AuthUser:
    """Authenticated user data"""
    id: str
    email: str
    name: str
    provider: str
    roles: List[str]
    raw_data: Dict[str, Any]


@dataclass  
class AuthResult:
    """Authentication result"""
    success: bool
    token: Optional[str] = None
    user: Optional[AuthUser] = None
    error: Optional[str] = None
    redirect_url: Optional[str] = None


class BaseAuthProvider(ABC):
    """Base class for authentication providers"""
    
    def __init__(self, context):
        self.context = context
        self.page = context.page
        self.functions_url = context.functions_url
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (e.g., 'aad', 'local', 'google')"""
        pass
    
    @abstractmethod
    def login(self, redirect_uri: Optional[str] = None) -> AuthResult:
        """Perform login and return auth result"""
        pass
    
    @abstractmethod
    def get_credentials(self) -> Dict[str, str]:
        """Get test credentials for this provider"""
        pass
    
    def logout(self, redirect_uri: Optional[str] = None) -> bool:
        """Logout user"""
        redirect = redirect_uri or f"{self.functions_url}/api/health"
        url = f"{self.functions_url}/api/auth/logout?post_login_redirect_uri={redirect}"
        self.page.goto(url)
        return True
    
    def validate_token(self, token: str) -> AuthResult:
        """Validate token via /auth/me endpoint"""
        response = self.page.request.get(
            f"{self.functions_url}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status != 200:
            return AuthResult(success=False, error=f"Token validation failed: {response.status}")
        
        data = response.json()
        user = self._parse_user_response(data)
        return AuthResult(success=True, token=token, user=user)
    
    def _parse_user_response(self, data: Any) -> Optional[AuthUser]:
        """Parse /auth/me response into AuthUser"""
        if isinstance(data, list) and len(data) > 0:
            # Easy Auth format
            info = data[0]
            claims = info.get("user_claims", [])
            return AuthUser(
                id=info.get("user_id", ""),
                email=self._get_claim(claims, "email", "preferred_username"),
                name=self._get_claim(claims, "name"),
                provider=info.get("provider_name", self.provider_name),
                roles=[c["val"] for c in claims if c.get("typ") == "role"],
                raw_data=info
            )
        return None
    
    def _get_claim(self, claims: List[Dict], *types: str) -> str:
        """Extract claim value by type"""
        for claim in claims:
            typ = claim.get("typ", "")
            for t in types:
                if t == typ or typ.endswith(f"/{t}"):
                    return claim.get("val", "")
        return ""
    
    def _extract_token_from_url(self, url: str) -> Optional[str]:
        """Extract auth token from URL (supports auth_token and accessToken)"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Try different token parameter names
        for param_name in ["accessToken", "auth_token", "access_token", "token"]:
            tokens = params.get(param_name, [])
            if tokens:
                return tokens[0]
        return None


class AuthManager:
    """Manages authentication across providers"""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, provider_class: type):
        """Register an auth provider"""
        instance = provider_class.__new__(provider_class)
        # Get provider name without full init
        name = getattr(provider_class, 'PROVIDER_NAME', None)
        if name:
            cls._providers[name] = provider_class
    
    @classmethod
    def get_provider(cls, name: str, context) -> BaseAuthProvider:
        """Get provider instance by name"""
        if name not in cls._providers:
            raise ValueError(f"Unknown auth provider: {name}")
        return cls._providers[name](context)
    
    @classmethod
    def available_providers(cls) -> List[str]:
        """List registered providers"""
        return list(cls._providers.keys())
