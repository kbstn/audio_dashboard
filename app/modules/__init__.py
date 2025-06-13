"""
Audio Processing Modules

This package contains all the processing modules for the audio dashboard.
"""

from typing import Dict, Type, List
from .base_module import BaseModule, MODULE_REGISTRY

# Import all modules here so they get registered
from . import about  # noqa: F401
from . import trim   # noqa: F401

# Export the module registry
MODULES = MODULE_REGISTRY

__all__ = ['BaseModule', 'MODULES']
