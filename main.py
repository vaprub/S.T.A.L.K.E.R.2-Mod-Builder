#!/usr/bin/env python3

"""
S.T.A.L.K.E.R. 2 Mod Builder by Saymonn
Main entry point for the application
Full version with internationalization support
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.i18n import i18n, _
from src.app import ModBuilderApp

def setup_logging():
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "mod_builder.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def print_welcome():
    """Prints welcome message in the current language"""
    welcome_text = _("Welcome to S.T.A.L.K.E.R. 2 Mod Builder!")
    
    print("\n╔" + "═" * 58 + "╗")
    print("║" + welcome_text.center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

def print_language_info():
    """Print current language information"""
    print("\n" + "─" * 60)
    print(_("🌐 Language Information:"))
    print("─" * 60)
    print(_("  Current language: {} ({})").format(
        i18n.get_language_name(),
        i18n.get_current_language()
    ))
    print("─" * 60)
    print()

def test_translations():
    """Test if translations are working"""
    logger = logging.getLogger(__name__)
    
    test_strings = [
        "Module Selection",
        "Settings",
        "Game Version Analysis",
        "Press Enter to continue..."
    ]
    
    logger.info(f"Testing translations for language: {i18n.get_current_language()}")
    for s in test_strings:
        translated = _(s)
        logger.debug(f"  '{s}' -> '{translated}'")
        if s == translated and i18n.get_current_language() != 'en':
            logger.warning(f"String not translated: '{s}'")

def check_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "logs",
        "config",
        "userconfig",
        "data/extract",
        "data/build/temp",
        "data/cache",
        "output/mods",
        "output/paks",
        "output/vortex",
        "locales"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("S.T.A.L.K.E.R. 2 Mod Builder starting...")
        logger.info("=" * 60)
        
        # Create directories
        check_directories()
        
        # Clear screen
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print welcome message
        print_welcome()
        
        # Print language info
        print_language_info()
        
        # Test translations
        test_translations()
        
        # Small pause
        import time
        time.sleep(2)
        
        # Initialize and run app
        logger.info("Initializing application...")
        print(_("\n🚀 Initializing application..."))
        
        app = ModBuilderApp()
        
        logger.info("Application initialized successfully")
        print(_("✅ Application ready!"))
        print(_("\nPress Enter to continue to main menu..."))
        input()
        
        app.run()
        
        logger.info("Application finished normally")
        print(_("\n✅ Application finished successfully!"))
        print(_("Press Enter to exit..."))
        input()
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        print(_("\n\n⚠ Application terminated by user."))
        print(_("Press Enter to exit..."))
        input()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(_("\n❌ Fatal error: {}").format(e))
        print(_("\nPress Enter to exit..."))
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()