#!/usr/bin/env python3

"""
S.T.A.L.K.E.R. 2 Mod Builder by Saymonn
Main entry point for the application with internationalization support
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
            logging.FileHandler(log_dir / "mod_builder.log"),
            logging.StreamHandler()
        ]
    )

def print_welcome():
    """Prints welcome message in multiple languages"""
    welcome_messages = {
        'en': "Welcome to S.T.A.L.K.E.R. 2 Mod Builder!",
        'ru': "Добро пожаловать в S.T.A.L.K.E.R. 2 Mod Builder!",
        'uk': "Ласкаво просимо до S.T.A.L.K.E.R. 2 Mod Builder!",
        'de': "Willkommen beim S.T.A.L.K.E.R. 2 Mod Builder!",
        'fr': "Bienvenue dans S.T.A.L.K.E.R. 2 Mod Builder!",
        'es': "¡Bienvenido a S.T.A.L.K.E.R. 2 Mod Builder!",
        'pl': "Witamy w S.T.A.L.K.E.R. 2 Mod Builder!",
        'zh': "欢迎使用 S.T.A.L.K.E.R. 2 Mod Builder！",
        'ja': "S.T.A.L.K.E.R. 2 Mod Builderへようこそ！",
        'ko': "S.T.A.L.K.E.R. 2 Mod Builder에 오신 것을 환영합니다!",
    }
    
    current_lang = i18n.get_current_language()
    print("=" * 60)
    print(welcome_messages.get(current_lang, welcome_messages['en']).center(60))
    print("=" * 60)
    print()

def main():
    """Main entry point"""
    try:
        setup_logging()
        
        # Определяем язык системы и устанавливаем
        system_lang = i18n.detect_system_language()
        i18n.set_language(system_lang)
        
        print_welcome()
        
        print(_("Detected system language: {}").format(i18n.get_language_name()))
        print(_("Current interface language: {}").format(i18n.get_language_name()))
        print(_("You can change language in Settings -> Language Settings"))
        print()
        
        app = ModBuilderApp()
        app.run()
        
        print(_("\n✅ Application finished successfully!"))
        print(_("Press Enter to exit..."))
        input()
        
    except KeyboardInterrupt:
        print(_("\n\nApplication terminated by user."))
        input(_("Press Enter to exit..."))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(_("\n❌ Fatal error: {}").format(e))
        print(_("Press Enter to exit..."))
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()