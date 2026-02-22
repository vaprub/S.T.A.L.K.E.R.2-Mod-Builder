import logging
from pathlib import Path
from typing import Dict, List, Optional
from importlib import import_module
import inspect

logger = logging.getLogger(__name__)

class ModuleLoader:
    
    def __init__(self):
        self.modules: Dict[str, object] = {}
        self.modules_dir = Path("src/modules")
    
    def discover_modules(self):
        """Discover and load all available modules"""
        if not self.modules_dir.exists():
            logger.warning(f"Modules directory not found: {self.modules_dir}")
            return
        
        for file_path in self.modules_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            if file_path.name == "base_module.py":
                continue
            
            module_name = file_path.stem
            self._load_module(module_name)
    
    def _load_module(self, module_name: str):
        """Load a specific module"""
        try:
            # Import the module
            module_path = f"src.modules.{module_name}"
            module = import_module(module_path)
            
            # Find module class (subclass of BaseModule)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'apply_configuration'):
                    if name != 'BaseModule':
                        instance = obj()
                        self.modules[module_name] = instance
                        logger.info(f"Loaded module: {module_name}")
                        break
                        
        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}")
    
    def get_module(self, name: str) -> Optional[object]:
        """Get a module by name"""
        return self.modules.get(name)
    
    def get_available_modules(self) -> List[object]:
        """Get list of all available modules"""
        return list(self.modules.values())