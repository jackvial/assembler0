"""Extension system for drex CLI."""

import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

import click


class DrexExtension(ABC):
    """Base class for all drex extensions."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Extension command name (e.g., 'test' for 'drex test')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Extension description for help text."""
        pass
    
    @abstractmethod
    def get_commands(self) -> click.Group:
        """Return Click command group for this extension."""
        pass
    
    def get_completion_script(self) -> Optional[str]:
        """Return bash completion script for this extension."""
        extension_dir = Path(__file__).parent
        completion_file = extension_dir / "completion.bash"
        
        if completion_file.exists():
            return completion_file.read_text()
        return None
    
    def initialize(self, config: dict = None):
        """Initialize extension with configuration."""
        self.config = config or {}


class ExtensionLoader:
    """Load extensions from drex_extensions folder."""
    
    def __init__(self):
        self.extensions = []
        self.extensions_path = self._find_extensions_folder()
    
    def _find_extensions_folder(self) -> Optional[Path]:
        """Find drex_extensions folder in repository root."""
        current = Path.cwd()
        
        # Walk up to find repository root
        while current != current.parent:
            # Check for drex_extensions folder
            extensions_path = current / "drex_extensions"
            if extensions_path.exists():
                return extensions_path
                
            # Check if this is the workspace root
            if (current / "pyproject.toml").exists():
                try:
                    with open(current / "pyproject.toml") as f:
                        content = f.read()
                        if "[tool.uv.workspace]" in content:
                            # This is the workspace root
                            extensions_path = current / "drex_extensions"
                            if extensions_path.exists():
                                return extensions_path
                            # Create it if it doesn't exist
                            extensions_path.mkdir(exist_ok=True)
                            return extensions_path
                except Exception:
                    pass
            current = current.parent
        
        return None
    
    def load_extensions(self) -> List[DrexExtension]:
        """Load all extensions from drex_extensions folder."""
        if not self.extensions_path:
            return []
        
        extensions = []
        
        for extension_dir in self.extensions_path.iterdir():
            if not extension_dir.is_dir():
                continue
            
            # Skip disabled extensions (prefixed with _)
            if extension_dir.name.startswith("_") or extension_dir.name.startswith("."):
                continue
            
            # Check if it's a proper package with pyproject.toml
            if not (extension_dir / "pyproject.toml").exists():
                continue
            
            try:
                extension = self._load_extension(extension_dir)
                if extension:
                    extensions.append(extension)
            except Exception as e:
                print(f"Warning: Failed to load extension {extension_dir.name}: {e}")
        
        return extensions
    
    def _load_extension(self, extension_path: Path) -> Optional[DrexExtension]:
        """Load a single extension from a directory."""
        # Add the extension's src directory to Python path
        src_path = extension_path / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Try to find the extension module
        extension_name = extension_path.name
        
        # Look for the extension.py file in the package
        module_name = extension_name.replace("-", "_")
        extension_file = src_path / module_name / "extension.py"
        
        if not extension_file.exists():
            # Try without src directory
            extension_file = extension_path / module_name / "extension.py"
            if not extension_file.exists():
                return None
        
        # Load the module
        spec = importlib.util.spec_from_file_location(
            f"drex_ext_{module_name}",
            extension_file
        )
        
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        # Find and instantiate the extension class
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, DrexExtension) and 
                attr != DrexExtension):
                return attr()
        
        return None