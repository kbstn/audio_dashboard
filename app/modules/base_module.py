"""
Base module for all audio processing modules.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Type, ClassVar
from pydantic import BaseModel

# Global registry for all modules
MODULE_REGISTRY: Dict[str, Type['BaseModule']] = {}

def register_module(cls: Type['BaseModule']) -> Type['BaseModule']:
    """Decorator to register a module class."""
    if hasattr(cls, 'config'):
        MODULE_REGISTRY[cls.config.name] = cls
    return cls

# Type variable for module classes
T = TypeVar('T', bound='BaseModule')

class ModuleConfig(BaseModel):
    """Base configuration model for modules."""
    name: str
    description: str
    icon: str = "🎵"  # Default icon

@register_module
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
