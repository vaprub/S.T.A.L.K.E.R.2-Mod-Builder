import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Any
from .menus import MenuSystem
from .prompts import UserPrompts
from ..i18n import i18n, _

class CLIInterface:
    """Интерфейс командной строки для билдера"""
    
    def __init__(self, app):
        self.app = app
        self.menu_system = MenuSystem()
        self.prompts = UserPrompts()
        self._extraction_completed = None
    
    def clear_screen(self):
        """Очищает экран"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _validate_extraction_completed(self) -> bool:
        """Проверяет, завершена ли распаковка"""
        if self._extraction_completed is None:
            config = self.app.config_manager.get_app_config()
            mod_base_path = config.get('mod_base_path', 'data')
            extract_path = Path(mod_base_path) / "data" / "extract"
            
            if not extract_path.exists():
                self._extraction_completed = False
            else:
                self._extraction_completed = self._check_extraction_folder_size(extract_path)
        
        return self._extraction_completed
    
    def _check_extraction_folder_size(self, extract_path: Path) -> bool:
        """Проверяет размер папки распаковки"""
        try:
            for item in extract_path.iterdir():
                if item.is_dir():
                    folder_name = item.name.lower()
                    if 'pakchunk' in folder_name:
                        return True
            return False
        except Exception:
            return False
    
    def _refresh_extraction_status(self):
        """Обновляет статус распаковки"""
        self._extraction_completed = None
        self._validate_extraction_completed()
    
    def main_menu_loop(self):
        """Главный цикл меню"""
        self._refresh_extraction_status()
        
        while True:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.extract_game_files()
                self._refresh_extraction_status()
            elif choice == "2":
                if self._validate_extraction_completed():
                    self.create_mod_workflow()
                else:
                    self.settings_menu()
            elif choice == "3":
                if self._validate_extraction_completed():
                    self.settings_menu()
                else:
                    self.check_game_version_detailed()
            elif choice == "4":
                if self._validate_extraction_completed():
                    self.check_game_version_detailed()
                else:
                    break
            elif choice == "5":
                break
            else:
                self.prompts.show_error(_("Invalid choice"))
    
    def show_main_menu(self) -> str:
        """Показывает главное меню"""
        options = [_("Extract Game Files")]
        
        if self._validate_extraction_completed():
            options.append(_("Create New Modpack"))
        
        options.extend([
            _("Settings"),
            _("Check Game Version"),
            _("Exit")
        ])
        
        return self.menu_system.show_menu(
            _("S.T.A.L.K.E.R. 2 Ultimate Modpack Builder by Saymonn"),
            options
        )
    
    def extract_game_files(self):
        """Распаковывает файлы игры"""
        self.clear_screen()
        
        confirm_message = _(
            "Extract pakchunk0-Windows.pak? \n\n"
            "This may take a while (5-15 minutes), depending on the speed of your CPU.\n"
            "~300,000 files / ~7GB data to extract). \n\n"
            "Continue?"
        )
        
        if self.prompts.confirm(confirm_message):
            success = self.app.pak_manager.extract_base_pak()
            if success:
                self.app.config_manager.update_app_config({
                    'last_extraction': datetime.now().isoformat()
                })
                self.prompts.show_success(_("Extraction completed successfully!"))
            else:
                self.prompts.show_error(_("Extraction failed!"))
    
    def create_mod_workflow(self):
        """Процесс создания мода"""
        self.clear_screen()
        
        # Показываем версию игры перед созданием мода
        self.show_game_version_banner()
        
        modules = self.select_modules()
        if not modules:
            print(_("No modules selected. Returning to main menu..."))
            input(_("Press Enter to continue..."))
            return
        
        configurations = {}
        for module in modules:
            config = self.configure_module(module)
            if config:
                configurations[module.name] = config
            else:
                print(_("Failed to configure {}").format(module.display_name))
                input(_("Press Enter to continue..."))
                return
        
        if configurations:
            mod_name = self.prompts.get_string(
                _("Enter modpack name (or press Enter for default): ")
            )
            
            print(_("\nBuilding modpack with {} module(s)...").format(len(configurations)))
            success = self.app.mod_builder.build_mod(configurations, mod_name)
            
            if success:
                print(_("Returning to main menu..."))
            else:
                self.prompts.show_error(_("Modpack creation failed!"))
        else:
            print(_("No valid configurations. Modpack creation cancelled."))
            input(_("Press Enter to continue..."))
    
    def show_game_version_banner(self):
        """Показывает баннер с информацией о версии игры"""
        print("\n" + "=" * 60)
        print(_("    GAME VERSION ANALYSIS").center(60))
        print("=" * 60)
        
        version_info = self.analyze_game_version()
        
        print(_("Detected version: {}").format(version_info['version']))
        print(_("File format: {}").format(version_info['format']))
        
        if version_info['is_modern']:
            print(_("✓ Using modern configuration (binary files detected)"))
        else:
            print(_("⚠ Using legacy configuration (text files detected)"))
        
        if version_info['warnings']:
            for warning in version_info['warnings']:
                print(f"  ⚠ {warning}")
        
        print("\n" + "-" * 60)
        print()
    
    def analyze_game_version(self) -> dict:
        """Анализирует версию игры по распакованным файлам"""
        result = {
            'version': _('unknown'),
            'format': _('unknown'),
            'is_modern': False,
            'warnings': []
        }
        
        config = self.app.config_manager.get_app_config()
        mod_base_path = config.get('mod_base_path', 'data')
        extract_path = Path(mod_base_path) / "data" / "extract"
        
        if not extract_path.exists():
            result['warnings'].append(_("No extracted files found"))
            return result
        
        # Находим самую свежую распакованную папку
        extractions = []
        for item in extract_path.iterdir():
            if item.is_dir() and 'pakchunk' in item.name.lower():
                extractions.append(item)
        
        if not extractions:
            result['warnings'].append(_("No extraction folders found"))
            return result
        
        latest = max(extractions, key=lambda p: p.stat().st_mtime)
        game_data = latest / "Stalker2" / "Content" / "GameLite" / "GameData"
        
        if not game_data.exists():
            result['warnings'].append(
                _("GameData folder not found in {}").format(latest.name)
            )
            return result
        
        # Проверяем форматы ключевых файлов
        weight_text = game_data / "ObjWeightParamsPrototypes.cfg"
        weight_bin = game_data / "ObjWeightParamsPrototypes.cfg.bin"
        effect_text = game_data / "ObjEffectMaxParamsPrototypes.cfg"
        effect_bin = game_data / "ObjEffectMaxParamsPrototypes.cfg.bin"
        
        if weight_bin.exists() and effect_bin.exists():
            result['format'] = _('binary')
            result['is_modern'] = True
            result['version'] = '1.8.1+'
        elif weight_text.exists() and effect_text.exists():
            result['format'] = _('text')
            result['is_modern'] = False
            result['version'] = '1.5.2 - 1.7.x'
        else:
            result['format'] = _('mixed')
            result['version'] = _('mixed/unknown')
        
        return result
    
    def select_modules(self) -> List[Any]:
        """Выбор модулей для включения в мод"""
        available_modules = self.app.module_loader.get_available_modules()
        
        if not available_modules:
            self.prompts.show_error(_("No modules available!"))
            return []
        
        selected = []
        self.clear_screen()
        print(_("Module Selection"))
        print("=" * 40)
        print(_("Select which modules to include in your modpack:\n"))
        
        for module in available_modules:
            if self.prompts.confirm(_("Include {}?").format(module.display_name)):
                selected.append(module)
        
        return selected
    
    def configure_module(self, module) -> Optional[dict]:
        """Настройка конкретного модуля"""
        self.clear_screen()
        print(_("Configuring: {}").format(module.display_name))
        print("=" * 50)
        
        predefined = module.get_predefined_configs()
        
        if predefined:
            options = [_("Custom Configuration\n")] + [cfg["name"] for cfg in predefined]
            choice = self.menu_system.show_menu(
                _("Select configuration for {}").format(module.display_name),
                options
            )
            
            try:
                idx = int(choice) - 1
                if idx == 0:
                    return module.get_custom_config()
                elif 0 < idx <= len(predefined):
                    return predefined[idx - 1]['config']
            except (ValueError, IndexError):
                self.prompts.show_error(_("Invalid selection"))
                return None
        else:
            return module.get_custom_config()
        
        return None
    
    def check_game_version_detailed(self):
        """Подробная проверка версии игры"""
        self.clear_screen()
        print("=" * 60)
        print(_("    GAME VERSION DETECTION").center(60))
        print("=" * 60)
        
        version_info = self.analyze_game_version()
        
        print(_("\n📊 Detected version: {}").format(version_info['version']))
        print(_("📁 File format: {}").format(version_info['format']))
        print(_("🔧 Modern format: {}").format(
            _("✅ Yes") if version_info['is_modern'] else _("❌ No")
        ))
        
        if version_info['warnings']:
            print(_("\n⚠ Warnings:"))
            for warning in version_info['warnings']:
                print(f"  • {warning}")
        
        print("\n" + "-" * 60)
        print(_("\nHow to interpret this:"))
        print(_("  • 1.8.1+ = Modern version with binary files"))
        print(_("  • 1.5.2-1.7.x = Older version with text files"))
        print(_("  • mixed = Inconsistent file formats (may cause issues)"))
        
        print(_("\nPress Enter to continue..."))
        input()
    
    def language_menu(self):
        """Меню выбора языка"""
        self.clear_screen()
        print("=" * 60)
        print(_("    LANGUAGE SELECTION").center(60))
        print("=" * 60)
        print()
        
        # Получаем доступные языки
        languages = i18n.available_languages
        current = i18n.get_current_language()
        
        # Создаём список опций
        options = []
        lang_codes = []
        for code, name in languages.items():
            marker = " ✓" if code == current else ""
            options.append(f"{name}{marker}")
            lang_codes.append(code)
        
        options.append(_("Back"))
        
        choice = self.menu_system.show_menu(
            _("Select your language"),
            options
        )
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(lang_codes):
                selected_lang = lang_codes[idx]
                if i18n.set_language(selected_lang):
                    self.prompts.show_success(
                        _("Language changed to {}").format(languages[selected_lang])
                    )
                else:
                    self.prompts.show_error(_("Failed to change language"))
            elif idx == len(lang_codes):
                return  # Back
        except (ValueError, IndexError):
            self.prompts.show_error(_("Invalid selection"))
        
        input(_("Press Enter to continue..."))
    
    def settings_menu(self):
        """Меню настроек"""
        while True:
            options = [
                _("Change Game Path"),
                _("View Current Settings"),
                _("Clear Cache"),
                _("Refresh Extraction Status"),
                _("Language Settings"),
                _("Back")
            ]
            
            choice = self.menu_system.show_menu(_("Settings"), options)
            
            if choice == "1":
                self.app.game_manager.setup_game_path()
            elif choice == "2":
                self.show_current_settings()
            elif choice == "3":
                self.clear_cache()
            elif choice == "4":
                self._refresh_extraction_status()
                status = _("Completed") if self._extraction_completed else _("Not completed")
                self.prompts.show_success(f"{_('Extraction status refreshed')}: {status}")
                input(_("Press Enter to continue..."))
            elif choice == "5":
                self.language_menu()
            elif choice == "6":
                break
    
    def show_current_settings(self):
        """Показывает текущие настройки"""
        self.clear_screen()
        config = self.app.config_manager.get_app_config()
        extraction_status = _("Completed") if self._validate_extraction_completed() else _("Not completed")
        
        print(_("Current Settings"))
        print("=" * 50)
        print(_("Game Path: {}").format(config.get('game_base_path', _('Not set'))))
        print(_("Modpack Base Path: {}").format(config.get('mod_base_path', _('Not set'))))
        print(_("Last Extraction: {}").format(config.get('last_extraction', _('Never'))))
        print(_("Extraction Status: {}").format(extraction_status))
        print(_("Language: {} ({})").format(
            i18n.get_language_name(),
            i18n.get_current_language()
        ))
        
        if extraction_status == _("Completed"):
            latest_extraction = self.app.pak_manager.get_latest_extraction()
            if latest_extraction:
                print(_("Active Extraction Folder: {}").format(latest_extraction.name))
                
                version_info = self.analyze_game_version()
                print(_("Game Version: {}").format(version_info['version']))
                print(_("File Format: {}").format(version_info['format']))
        
        input(_("\nPress Enter to continue..."))
    
    def clear_cache(self):
        """Очищает кэш"""
        if self.prompts.confirm(_("Clear all cached data?")):
            import shutil
            cache_dirs = ["data/cache", "data/build/temp"]
            for cache_dir in cache_dirs:
                if Path(cache_dir).exists():
                    shutil.rmtree(cache_dir)
                    Path(cache_dir).mkdir(parents=True, exist_ok=True)
            self.prompts.show_success(_("Cache cleared!"))
            self._refresh_extraction_status()