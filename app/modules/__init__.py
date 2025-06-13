"""
Audio Processing Modules

This package contains all the processing modules for the audio dashboard.
"""
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type, List, Any

# Import base module first to set up the registry
from .base_module import BaseModule, MODULE_REGISTRY, register_module

# Get the directory containing the modules
modules_dir = Path(__file__).parent

# Import all Python files in the modules directory (except __init__.py and base_module.py)
for finder, name, _ in pkgutil.iter_modules([str(modules_dir)]):
    if name not in ("__init__", "base_module"):
        try:
            print(f"Importing module: {name}")  # Debug print
            module = importlib.import_module(f".{name}", package="app.modules")
            # The @register_module decorator will handle registration
            print(f"Successfully imported module: {name}")  # Debug print
        except Exception as e:  # Catch all exceptions to see what's going wrong
            print(f"Warning: Could not import module {name}: {e}")
            import traceback
            traceback.print_exc()

# Export the module registry
MODULES = MODULE_REGISTRY

__all__ = ["BaseModule", "MODULES", "register_module"]
