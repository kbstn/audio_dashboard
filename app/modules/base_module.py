"""
Base module for all audio processing modules.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Type, ClassVar, TypeAlias
from pydantic import BaseModel

# Type definitions
ModuleType: TypeAlias = Type['BaseModule']

# Global registry for all modules
MODULE_REGISTRY: Dict[str, ModuleType] = {}

def register_module(cls: ModuleType) -> ModuleType:
    """
    Decorator to register a module class.
    
    Args:
        cls: The module class to register
        
    Returns:
        The same class, for use as a decorator
        
    Raises:
        ValueError: If the module is missing required configuration
    """
    if not hasattr(cls, 'config'):
        raise ValueError(f"Module class {cls.__name__} is missing required 'config' class variable")
    
    if not hasattr(cls.config, 'name') or not cls.config.name:
        raise ValueError(f"Module class {cls.__name__} config is missing required 'name' field")
    
    # Register the module
    MODULE_REGISTRY[cls.config.name] = cls
    return cls

# Type variable for module classes
T = TypeVar('T', bound='BaseModule')

# Make the register_module function available at the module level
__all__ = ['BaseModule', 'ModuleConfig', 'MODULE_REGISTRY', 'register_module']

class ModuleConfig(BaseModel):
    """Base configuration model for modules."""
    name: str
    description: str
    icon: str = "🎵"  # Default icon

class BaseModule(ABC):
    """
    Abstract base class for all audio processing modules.
    
    To create a new module, subclass this and implement the required methods.
    """
    config: ClassVar[ModuleConfig]
    
    def __init_subclass__(cls, **kwargs):
        """Initialize the subclass."""
        super().__init_subclass__(**kwargs)
    
    @abstractmethod
    def render_ui(self) -> None:
        """
        Render the module's user interface.
        
        This should use Streamlit functions to create the UI elements.
        """
        pass
    
    @abstractmethod
    def process(self, input_file: str) -> str:
        """
        Process the input file and return the path to the output file.
        
        Args:
            input_file: Path to the input file
            
        Returns:
            Path to the processed output file
        """
        pass
    
    def get_help(self) -> str:
        """
        Get help text for this module.
        
        Returns:
            Help text as a string
        """
        return self.config.description
