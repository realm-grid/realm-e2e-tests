"""Auth providers package - import all providers to register them"""
import os
import sys

# Ensure this directory is in path
_dir = os.path.dirname(__file__)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from aad import AzureADProvider
from local import LocalAuthProvider

__all__ = ["AzureADProvider", "LocalAuthProvider"]
