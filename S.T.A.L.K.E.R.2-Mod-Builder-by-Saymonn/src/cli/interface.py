import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Any
from .menus import MenuSystem
from .prompts import UserPrompts

class CLIInterface:
    
    def __init__(self, app):
        self.app = app
        self.menu_system = MenuSystem()
        self.prompts = UserPrompts()
        self._extraction_completed = None
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _validate_extraction_completed(self) -> bool:
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
        self._extraction_completed = None
        self._validate_extraction_completed()
    
    def main_menu_loop(self):
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
                self.prompts.show_error("Invalid choice")
    
    def show_main_menu(self) -> str:
        options = ["Extract Game Files"]
        
        if self._validate_extraction_completed():
            options.append("Create New Modpack")
        
        options.extend([
            "Settings",
            "Check Game Version",
            "Exit"
        ])
        
        return self.menu_system.show_menu(
            "S.T.A.L.K.E.R. 2 Ultimate Modpack Builder by Saymonn",
            options
        )
    
    def extract_game_files(self):
        self.clear_screen()
        
        if self.prompts.confirm("Extract pakchunk0-Windows.pak? \n\nThis may take a while (5-15 minutes), depending on the speed of your CPU.\n~300,000 files / ~7GB data to extract). \n\nContinue?"):
            success = self.app.pak_manager.extract_base_pak()
            if success:
                self.app.config_manager.update_app_config({
                    'last_extraction': datetime.now().isoformat()
                })
                self.prompts.show_success("Extraction completed successfully!")
            else:
                self.prompts.show_error("Extraction failed!")
    
    def create_mod_workflow(self):
        self.clear_screen()
        
        # Показываем версию игры перед созданием мода
        self.show_game_version_banner()
        
        modules = self.select_modules()
        if not modules:
            print("No modules selected. Returning to main menu...")
            input("Press Enter to continue...")
            return
        
        configurations = {}
        for module in modules:
            config = self.configure_module(module)
            if config:
                configurations[module.name] = config
            else:
                print(f"Failed to configure {module.display_name}")
                input("Press Enter to continue...")
                return
        
        if configurations:
            mod_name = self.prompts.get_string("Enter modpack name (or press Enter for default): ")
            
            print(f"\nBuilding modpack with {len(configurations)} module(s)...")
            success = self.app.mod_builder.build_mod(configurations, mod_name)
            
            if success:
                print("Returning to main menu...")
            else:
                self.prompts.show_error("Modpack creation failed!")
        else:
            print("No valid configurations. Modpack creation cancelled.")
            input("Press Enter to continue...")
    
    def show_game_version_banner(self):
        """Показывает детальную информацию о версии игры перед созданием мода"""
        print("\n" + "=" * 60)
        print("    GAME VERSION ANALYSIS")
        print("=" * 60)
        
        version_info = self.analyze_game_version()
        
        print(f"Detected game version: {version_info['version']}")
        print(f"File format: {version_info['format']}")
        
        if version_info['is_modern']:
            print("✓ Using modern configuration (binary files detected)")
        else:
            print("⚠ Using legacy configuration (text files detected)")
        
        if version_info['warnings']:
            for warning in version_info['warnings']:
                print(f"  ⚠ {warning}")
        
        print("\n" + "-" * 60)
        print()
    
    def analyze_game_version(self) -> dict:
        """Анализирует версию игры по распакованным файлам"""
        result = {
            'version': 'unknown',
            'format': 'unknown',
            'is_modern': False,
            'warnings': []
        }
        
        config = self.app.config_manager.get_app_config()
        mod_base_path = config.get('mod_base_path', 'data')
        extract_path = Path(mod_base_path) / "data" / "extract"
        
        if not extract_path.exists():
            result['warnings'].append("No extracted files found")
            return result
        
        # Находим самую свежую распакованную папку
        extractions = []
        for item in extract_path.iterdir():
            if item.is_dir() and 'pakchunk' in item.name.lower():
                extractions.append(item)
        
        if not extractions:
            result['warnings'].append("No extraction folders found")
            return result
        
        latest = max(extractions, key=lambda p: p.stat().st_mtime)
        game_data = latest / "Stalker2" / "Content" / "GameLite" / "GameData"
        
        if not game_data.exists():
            result['warnings'].append(f"GameData folder not found in {latest.name}")
            return result
        
        # Проверяем форматы ключевых файлов
        weight_text = game_data / "ObjWeightParamsPrototypes.cfg"
        weight_bin = game_data / "ObjWeightParamsPrototypes.cfg.bin"
        effect_text = game_data / "ObjEffectMaxParamsPrototypes.cfg"
        effect_bin = game_data / "ObjEffectMaxParamsPrototypes.cfg.bin"
        core_vars = game_data / "CoreVariables.cfg"
        
        # Анализируем формат
        if weight_bin.exists() and effect_bin.exists():
            result['format'] = 'binary'
            result['is_modern'] = True
            result['version'] = '1.8.1+'
        elif weight_text.exists() and effect_text.exists():
            result['format'] = 'text'
            result['is_modern'] = False
            result['version'] = '1.5.2 - 1.7.x'
        else:
            result['format'] = 'mixed'
            result['version'] = 'mixed/unknown'
            if weight_bin.exists() and not effect_bin.exists():
                result['warnings'].append("Inconsistent file formats: WeightParams binary, EffectParams missing")
            elif effect_bin.exists() and not weight_bin.exists():
                result['warnings'].append("Inconsistent file formats: EffectParams binary, WeightParams missing")
        
        # Проверяем CoreVariables
        if core_vars.exists():
            try:
                with open(core_vars, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
                    if 'StaminaRegenStateCoefs' in content:
                        result['core_vars'] = 'modern'
                    else:
                        result['core_vars'] = 'legacy'
            except:
                result['warnings'].append("Could not read CoreVariables.cfg")
        else:
            result['warnings'].append("CoreVariables.cfg not found")
        
        return result
    
    def install_to_game(self, pak_file: Path):
        try:
            config = self.app.config_manager.get_app_config()
            game_path = Path(config.get('game_base_path', ''))
            
            if not game_path.exists():
                self.prompts.show_error("Game path not set!")
                return
            
            mods_dir = game_path / "Stalker2" / "Content" / "Paks" / "~mods"
            mods_dir.mkdir(parents=True, exist_ok=True)
            
            dest_file = mods_dir / pak_file.name
            
            if dest_file.exists():
                if not self.prompts.confirm(f"File {pak_file.name} already exists in game directory. Overwrite?"):
                    return
            
            import shutil
            shutil.copy2(pak_file, dest_file)
            
            self.prompts.show_success(f"Modpack installed to game directory: {dest_file}")
            
        except Exception as e:
            self.prompts.show_error(f"Failed to install mod: {e}")
    
    def select_modules(self) -> List[Any]:
        available_modules = self.app.module_loader.get_available_modules()
        
        if not available_modules:
            self.prompts.show_error("No modules available!")
            return []
        
        selected = []
        self.clear_screen()
        print("Module Selection")
        print("=" * 40)
        print("Select which modules to include in your modpack:\n")
        
        for module in available_modules:
            if self.prompts.confirm(f"Include {module.display_name}?"):
                selected.append(module)
        
        return selected
    
    def configure_module(self, module) -> Optional[dict]:
        self.clear_screen()
        print(f"Configuring: {module.display_name}")
        print("=" * 50)
        
        predefined = module.get_predefined_configs()
        
        if predefined:
            options = ["Custom Configuration\n"] + [cfg["name"] for cfg in predefined]
            choice = self.menu_system.show_menu(
                f"Select configuration for {module.display_name}",
                options
            )
            
            try:
                idx = int(choice) - 1
                if idx == 0:
                    return module.get_custom_config()
                elif 0 < idx <= len(predefined):
                    return predefined[idx - 1]['config']
            except (ValueError, IndexError):
                self.prompts.show_error("Invalid selection")
                return None
        else:
            return module.get_custom_config()
        
        return None
    
    def load_configuration(self):
        configs = self.app.config_manager.list_user_configs()
        
        if not configs:
            self.prompts.show_error("No saved configurations found!")
            return
        
        choice = self.menu_system.show_menu(
            "Select configuration to load",
            configs
        )
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(configs):
                config_name = configs[idx]
                config_data = self.app.config_manager.load_user_config(config_name)
                
                if config_data:
                    print(f"\nLoading configuration: {config_name}")
                    success = self.app.mod_builder.build_mod(config_data, f"from_{config_name}")
                    
                    if success:
                        print("Returning to main menu...")
                    else:
                        self.prompts.show_error("Failed to create modpack from configuration")
                else:
                    self.prompts.show_error("Failed to load configuration")
        except (ValueError, IndexError):
            self.prompts.show_error("Invalid selection")
    
    def settings_menu(self):
        while True:
            options = [
                "Change Game Path",
                "View Current Settings",
                "Clear Cache",
                "Refresh Extraction Status",
                "Back"
            ]
            
            choice = self.menu_system.show_menu("Settings", options)
            
            if choice == "1":
                self.app.game_manager.setup_game_path()
            elif choice == "2":
                self.show_current_settings()
            elif choice == "3":
                self.clear_cache()
            elif choice == "4":
                self._refresh_extraction_status()
                status = "Completed" if self._extraction_completed else "Not completed"
                self.prompts.show_success(f"Extraction status refreshed: {status}")
                input("\nPress Enter to continue...")
            elif choice == "5":
                break
    
    def check_game_version_detailed(self):
        """Подробная проверка версии игры"""
        self.clear_screen()
        print("=" * 60)
        print("    GAME VERSION DETECTION")
        print("=" * 60)
        
        version_info = self.analyze_game_version()
        
        print(f"\n📊 Detected version: {version_info['version']}")
        print(f"📁 File format: {version_info['format']}")
        print(f"🔧 Modern format: {'✅ Yes' if version_info['is_modern'] else '❌ No'}")
        
        if version_info['warnings']:
            print("\n⚠ Warnings:")
            for warning in version_info['warnings']:
                print(f"  • {warning}")
        
        print("\n" + "-" * 60)
        print("\nHow to interpret this:")
        print("  • 1.8.1+ = Modern version with binary files")
        print("  • 1.5.2-1.7.x = Older version with text files")
        print("  • mixed = Inconsistent file formats (may cause issues)")
        
        print("\nPress Enter to continue...")
        input()
    
    def show_current_settings(self):
        self.clear_screen()
        config = self.app.config_manager.get_app_config()
        extraction_status = "Completed" if self._validate_extraction_completed() else "Not completed"
        
        print("Current Settings")
        print("=" * 50)
        print(f"Game Path: {config.get('game_base_path', 'Not set')}")
        print(f"Modpack Base Path: {config.get('mod_base_path', 'Not set')}")
        print(f"Last Extraction: {config.get('last_extraction', 'Never')}")
        print(f"Extraction Status: {extraction_status}")
        
        if extraction_status == "Completed":
            latest_extraction = self.app.pak_manager.get_latest_extraction()
            if latest_extraction:
                print(f"Active Extraction Folder: {latest_extraction.name}")
                
                # Показываем версию игры
                version_info = self.analyze_game_version()
                print(f"Game Version: {version_info['version']}")
                print(f"File Format: {version_info['format']}")
                
                extract_dir = Path("data/extract")
                if extract_dir.exists():
                    all_extractions = []
                    for item in extract_dir.iterdir():
                        if item.is_dir() and 'pakchunk' in item.name.lower():
                            try:
                                mtime = item.stat().st_mtime
                                all_extractions.append((mtime, item))
                            except:
                                all_extractions.append((0, item))
                    
                    if len(all_extractions) > 1:
                        print(f"Total Extraction Folders: {len(all_extractions)}")
                        print("Available extractions (newest first):")
                        all_extractions.sort(key=lambda x: x[0], reverse=True)
                        for i, (mtime, path) in enumerate(all_extractions[:5]):
                            marker = " ← ACTIVE" if path == latest_extraction else ""
                            print(f"  {i+1}. {path.name}{marker}")
                        if len(all_extractions) > 5:
                            print(f"  ... and {len(all_extractions) - 5} more")
        
        input("\nPress Enter to continue...")
    
    def clear_cache(self):
        if self.prompts.confirm("Clear all cached data?"):
            self.prompts.show_success("Cache cleared!")
            self._refresh_extraction_status()