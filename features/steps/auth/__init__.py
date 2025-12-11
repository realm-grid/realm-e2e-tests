"""Auth package - authentication testing framework"""
import os
import sys

# Ensure this directory is in path
_dir = os.path.dirname(__file__)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from base import BaseAuthProvider, AuthResult, AuthUser, AuthManager

# Import providers to register them
import providers

__all__ = ["BaseAuthProvider", "AuthResult", "AuthUser", "AuthManager"]
