import logging
import shutil
import zipfile
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ModBuilder:
    
    def __init__(self, config_manager, pak_manager, module_loader):
        self.config_manager = config_manager
        self.pak_manager = pak_manager
        self.module_loader = module_loader
        self.game_manager = None
    
    def set_game_manager(self, game_manager):
        self.game_manager = game_manager
    
    def validate_prerequisites(self) -> bool:
        config = self.config_manager.get_app_config()
        mod_base_path = config.get('mod_base_path', 'data')
        extract_path = Path(mod_base_path) / "data" / "extract"
        
        if not extract_path.exists():
            logger.error("Extraction directory does not exist")
            return False
        
        if not self._check_extraction_folder_size(extract_path):
            logger.error("No valid extraction folder found")
            return False
        
        return True
    
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
    
    def _get_source_files_path(self) -> Path:
        pak_manager_latest = self.pak_manager.get_latest_extraction()
        if pak_manager_latest and pak_manager_latest.exists():
            return pak_manager_latest
        
        config = self.config_manager.get_app_config()
        mod_base_path = config.get('mod_base_path', 'data')
        extract_path = Path(mod_base_path) / "data" / "extract"
        
        if not extract_path.exists():
            raise Exception("No extraction folder found")
        
        extractions = []
        for item in extract_path.iterdir():
            if item.is_dir() and 'pakchunk' in item.name.lower():
                try:
                    extractions.append((item.stat().st_mtime, item))
                except:
                    extractions.append((0, item))
        
        if extractions:
            extractions.sort(key=lambda x: x[0], reverse=True)
            latest_path = extractions[0][1]
            print(f"Using extraction folder: {latest_path.name}")
            return latest_path
        
        raise Exception("No extraction folder found")
    
    def _analyze_game_version(self) -> dict:
        """Анализирует версию игры по распакованным файлам"""
        result = {
            'version': 'unknown',
            'format': 'unknown',
            'is_modern': False,
            'warnings': []
        }
        
        try:
            config = self.config_manager.get_app_config()
            mod_base_path = config.get('mod_base_path', 'data')
            extract_path = Path(mod_base_path) / "data" / "extract"
            
            if not extract_path.exists():
                result['warnings'].append("No extracted files found")
                return result
            
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
            
            weight_text = game_data / "ObjWeightParamsPrototypes.cfg"
            weight_bin = game_data / "ObjWeightParamsPrototypes.cfg.bin"
            effect_text = game_data / "ObjEffectMaxParamsPrototypes.cfg"
            effect_bin = game_data / "ObjEffectMaxParamsPrototypes.cfg.bin"
            
            if weight_bin.exists() and effect_bin.exists():
                result['format'] = 'binary'
                result['is_modern'] = True
                result['version'] = '1.8.1+'
            elif weight_text.exists() and effect_text.exists():
                result['format'] = 'text'
                result['is_modern'] = False
                result['version'] = '1.5.2 - 1.7.x'
            
        except Exception as e:
            result['warnings'].append(f"Error analyzing game version: {e}")
        
        return result
    
    def _show_version_banner(self):
        version_info = self._analyze_game_version()
        
        print("\n" + "=" * 60)
        print("    GAME VERSION ANALYSIS")
        print("=" * 60)
        print(f"📊 Detected version: {version_info['version']}")
        print(f"📁 File format: {version_info['format']}")
        print(f"🔧 Modern format: {'✅ Yes' if version_info['is_modern'] else '❌ No'}")
        
        if version_info['warnings']:
            print("\n⚠ Warnings:")
            for warning in version_info['warnings']:
                print(f"  • {warning}")
        
        print("=" * 60 + "\n")
        
        return version_info
    
    def _create_vortex_zip(self, pak_path: Path, mod_name: str, output_dir: Path) -> Optional[Path]:
        try:
            print("\n📦 Creating Vortex-compatible ZIP archive...")
            
            temp_dir = Path("data/temp/vortex_build")
            mod_structure = temp_dir / "Stalker2" / "Content" / "Paks" / "~mods"
            mod_structure.mkdir(parents=True, exist_ok=True)
            
            dest_pak = mod_structure / pak_path.name
            shutil.copy2(pak_path, dest_pak)
            
            vortex_dir = Path("output/vortex")
            vortex_dir.mkdir(parents=True, exist_ok=True)
            
            zip_filename = f"{mod_name}_Vortex.zip"
            zip_path = vortex_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
                        print(f"  📦 Added to ZIP: {arcname}")
            
            shutil.rmtree(temp_dir)
            
            zip_size = zip_path.stat().st_size
            zip_size_mb = zip_size / (1024 * 1024)
            
            print(f"✅ Vortex ZIP created: {zip_filename} ({zip_size_mb:.2f} MB)")
            print(f"   Location: {zip_path}")
            
            return zip_path
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create Vortex ZIP: {e}")
            logger.warning(f"Vortex ZIP creation failed: {e}")
            return None
    
    def build_mod(self, configurations: Dict[str, Any], mod_name: Optional[str] = None) -> bool:
        try:
            if not self.validate_prerequisites():
                logger.error("Prerequisites not met for mod building")
                print("ERROR: Game files must be extracted first!")
                return False
            
            version_info = self._show_version_banner()
            
            if not mod_name:
                timestamp = datetime.now().strftime("%d_%m_%Y__%H_%M_%S")
                mod_name = f"custom_multi_mod_{timestamp}"
            
            build_dir = Path("data/build/temp") / mod_name
            if build_dir.exists():
                shutil.rmtree(build_dir)
            build_dir.mkdir(parents=True, exist_ok=True)
            
            source_path = self._get_source_files_path()
            
            logger.info(f"Building mod: {mod_name}")
            print(f"Building mod: {mod_name}")
            
            conflicting_files = self._check_file_conflicts(configurations)
            if conflicting_files:
                print("⚠ File conflicts detected:")
                for file_name, modules in conflicting_files.items():
                    print(f"  {file_name} will be modified by: {', '.join(modules)}")
                print("  Modules will apply changes incrementally (later modules preserve earlier changes)")
                print()
            
            success_count = 0
            
            # 🔥 ИСПРАВЛЕНИЕ: Правильный поиск модулей
            all_modules = self.module_loader.get_available_modules()
            modules_by_name = {m.name: m for m in all_modules}
            modules_by_display = {m.display_name: m for m in all_modules}
            
            for module_key, config in configurations.items():
                # Пробуем найти модуль разными способами
                module = None
                
                # 1. По имени класса (module.name)
                if module_key in modules_by_name:
                    module = modules_by_name[module_key]
                    logger.info(f"Found module by class name: {module_key}")
                
                # 2. По отображаемому имени
                elif module_key in modules_by_display:
                    module = modules_by_display[module_key]
                    logger.info(f"Found module by display name: {module_key}")
                
                # 3. Поиск по всем модулям
                else:
                    for m in all_modules:
                        if m.name.lower().replace('module', '') == module_key.lower().replace('module', ''):
                            module = m
                            logger.info(f"Found module by fuzzy match: {m.name}")
                            break
                
                if module:
                    logger.info(f"Applying module: {module.name}")
                    print(f"Applying module: {module.display_name}")
                    
                    module.source_dir = source_path
                    
                    if module.apply_configuration(config, build_dir):
                        success_count += 1
                        print(f"✓ {module.display_name} applied successfully")
                    else:
                        logger.error(f"Failed to apply module: {module.name}")
                        print(f"✗ Failed to apply {module.display_name}")
                        return False
                else:
                    logger.error(f"Module not found for key: {module_key}")
                    print(f"✗ Module not found: {module_key}")
                    print(f"Available modules: {[m.display_name for m in all_modules]}")
                    return False
            
            if success_count == 0:
                logger.error("No modules were applied successfully")
                print("ERROR: No modules were applied successfully")
                return False
            
            paks_dir = Path("output/paks")
            paks_dir.mkdir(parents=True, exist_ok=True)
            
            output_pak = paks_dir / f"{mod_name}.pak"
            logger.info(f"Packing mod to: {output_pak}")
            print(f"Packing mod to: {output_pak}")
            print("Please wait...")
            
            pack_success = self.pak_manager.pack_mod(build_dir, output_pak)
            
            if pack_success:
                print("✓ Mod packed successfully!")
                
                vortex_zip = self._create_vortex_zip(output_pak, mod_name, Path("output/vortex"))
                
                mods_dir = Path("output/mods")
                mods_dir.mkdir(parents=True, exist_ok=True)
                
                mod_destination = mods_dir / mod_name
                
                if mod_destination.exists():
                    shutil.rmtree(mod_destination)
                
                shutil.copytree(build_dir, mod_destination)
                print(f"✓ Unpacked version created in: {mod_destination}")
                
                print()
                print("=" * 60)
                print("    CUSTOM MOD CREATED SUCCESSFULLY!")
                print("=" * 60)
                print(f"📦 Packed mod (.pak): {output_pak}")
                print(f"📂 Unpacked mod (folders): {mod_destination}")
                if vortex_zip:
                    print(f"🎮 Vortex ZIP: {vortex_zip}")
                
                if not version_info['is_modern'] and version_info['version'] != 'unknown':
                    print("\n⚠ NOTE: You are using an older game version (pre-1.8.1)")
                    print("  The mod should work, but some features may be different.")
                
                print()
                
                if self._ask_install_to_game():
                    self._install_to_game(output_pak)
                
                print()
                print("Press Enter to continue...")
                input()
                
                shutil.rmtree(build_dir)
                
                logger.info("Mod build completed successfully")
                return True
            else:
                logger.error("Failed to pack mod")
                print("ERROR: Failed to pack mod")
                print("Check the logs for more details.")
                print()
                print("Press Enter to continue...")
                input()
                return False
                
        except Exception as e:
            logger.error(f"Mod build error: {e}")
            print(f"ERROR: Mod build failed: {e}")
            return False
    
    def _ask_install_to_game(self) -> bool:
        while True:
            response = input("Install mod to game directory? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def _install_to_game(self, pak_file: Path) -> bool:
        try:
            config = self.config_manager.get_app_config()
            game_path = Path(config.get('game_base_path', ''))
            
            if not game_path.exists():
                print("ERROR: Game path not set!")
                return False
            
            mods_dir = game_path / "Stalker2" / "Content" / "Paks" / "~mods"
            mods_dir.mkdir(parents=True, exist_ok=True)
            
            dest_file = mods_dir / pak_file.name
            
            if dest_file.exists():
                while True:
                    response = input(f"File {pak_file.name} already exists in game directory. Overwrite? (y/n): ").strip().lower()
                    if response in ['y', 'yes']:
                        break
                    elif response in ['n', 'no']:
                        print("Installation cancelled.")
                        return False
                    else:
                        print("Please enter 'y' or 'n'")
            
            shutil.copy2(pak_file, dest_file)
            
            print(f"✓ Mod installed to game directory: {dest_file}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to install mod: {e}")
            return False
    
    def _check_file_conflicts(self, configurations: Dict[str, Any]) -> dict[str, list[str]]:
        file_usage = {}
        
        common_files = {
            'CarryWeightModule': ['CoreVariables.cfg'],
            'DayLengthModule': ['CoreVariables.cfg'],
            'StaminaModule': ['CoreVariables.cfg']
        }
        
        for module_name in configurations.keys():
            if module_name in common_files:
                for file_name in common_files[module_name]:
                    if file_name not in file_usage:
                        file_usage[file_name] = []
                    
                    module = self.module_loader.get_module(module_name)
                    if module:
                        file_usage[file_name].append(module.display_name)
        
        return {k: v for k, v in file_usage.items() if len(v) > 1}