"""Main application controller"""

import logging
from typing import Optional
from pathlib import Path

from .cli.interface import CLIInterface
from .core.game_manager import GameManager
from .core.pak_manager import PakManager
from .core.mod_builder import ModBuilder
from .config.config_manager import ConfigManager
from .modules.module_loader import ModuleLoader

logger = logging.getLogger(__name__)

class ModBuilderApp:
    """Main application controller"""
    
    def __init__(self):
        """Initialize the application"""
        self.config_manager = ConfigManager()
        self.game_manager = GameManager(self.config_manager)
        self.pak_manager = PakManager(self.config_manager)
        self.module_loader = ModuleLoader()
        self.mod_builder = ModBuilder(
            self.config_manager,
            self.pak_manager,
            self.module_loader
        )
        self.cli = CLIInterface(self)
        
        logger.info("S.T.A.L.K.E.R. 2 Ultimate Modpack Builder by Saymonn initialized")
    
    def run(self):
        """Run the main application"""
        # Initial setup
        if not self.setup():
            return
        
        # Main menu loop
        self.cli.main_menu_loop()
    
    def setup(self) -> bool:
        """Perform initial setup and validation"""
        logger.info("Starting application setup")
        
        # Check/setup game path
        if not self.game_manager.validate_game_path():
            if not self.game_manager.setup_game_path():
                logger.error("Failed to setup game path")
                return False
        
        # Initialize directories
        self._initialize_directories()
        
        # Load modules
        self.module_loader.discover_modules()
        
        logger.info("Setup completed successfully")
        return True
    
    def _initialize_directories(self):
        """Create necessary directories"""
        directories = [
            "config", "userconfig", "data/extract", "data/build/temp",
            "data/cache", "output/mods", "output/paks", "output/vortex", "logs", "assets"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)