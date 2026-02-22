import logging
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import statistics

logger = logging.getLogger(__name__)

class PakManager:
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.repak_path = Path("tools/repak/repak.exe")
        self.aes_key = "0x33A604DF49A07FFD4A4C919962161F5C35A134D37EFA98DB37A34F6450D7D386"
    
    def extract_base_pak(self) -> bool:
        """Extract the base game PAK file and detect game version"""
        config = self.config_manager.get_app_config()
        game_path = Path(config.get('game_base_path', ''))
        
        if not game_path.exists():
            logger.error("Game path not set")
            return False
        
        pak_file = game_path / "Stalker2" / "Content" / "Paks" / "pakchunk0-Windows.pak"
        
        if not pak_file.exists():
            logger.error(f"PAK file not found: {pak_file}")
            return False
        
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        extract_dir = Path("data/extract") / f"pakchunk0-Windows_{timestamp}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Extracting {pak_file} to {extract_dir}")
        print(f"\nExtracting game files...")
        print(f"File: pakchunk0-Windows.pak")
        print(f"Output: {extract_dir}")
        print()
        
        try:
            cmd = [
                str(self.repak_path),
                "--aes-key", self.aes_key,
                "unpack",
                str(pak_file),
                "--output", str(extract_dir)
            ]
            
            result = subprocess.run(cmd, text=True)
            
            print()
            
            if result.returncode == 0:
                logger.info("Extraction completed successfully")
                print("✓ Extraction completed successfully!")
                
                # Определяем версию игры максимально точно
                version_info = self.detect_game_version_precise(extract_dir)
                
                print(f"\n📊 GAME VERSION DETECTION RESULTS:")
                print(f"   Version: {version_info['version']}")
                print(f"   Confidence: {version_info['confidence']}%")
                print(f"   Methods used: {', '.join(version_info['methods_used'])}")
                print(f"   Modern format: {'✅ Yes' if version_info['is_modern'] else '❌ No'}")
                
                # Сохраняем всю информацию о версии
                update_data = {
                    'last_extraction': timestamp,
                    'last_extraction_path': str(extract_dir),
                    'game_version': version_info['version'],
                    'game_version_confidence': version_info['confidence'],
                    'game_version_details': version_info['details'],
                    'game_version_methods': version_info['methods_used'],
                    'game_is_modern': version_info['is_modern'],
                    'game_version_detected_at': datetime.now().isoformat()
                }
                
                # Добавляем отдельные поля для каждой версии для удобства
                if '1.8.1' in version_info['version']:
                    update_data['game_version_major'] = '1.8.1'
                elif '1.7' in version_info['version']:
                    update_data['game_version_major'] = '1.7.x'
                elif '1.6' in version_info['version']:
                    update_data['game_version_major'] = '1.6.x'
                elif '1.5' in version_info['version']:
                    update_data['game_version_major'] = '1.5.x'
                
                self.config_manager.update_app_config(update_data)
                
                return True
            else:
                logger.error(f"Extraction failed with return code: {result.returncode}")
                print(f"✗ Extraction failed!")
                return False
                
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            print(f"✗ Extraction error: {e}")
            return False
    
    def detect_game_version_precise(self, extract_dir: Path) -> Dict[str, Any]:
        """
        Точное определение версии игры множеством методов
        Возвращает словарь с версией и уровнем достоверности
        """
        result = {
            'version': 'unknown',
            'confidence': 0,
            'methods_used': [],
            'details': {},
            'is_modern': False
        }
        
        game_data = extract_dir / "Stalker2" / "Content" / "GameLite" / "GameData"
        if not game_data.exists():
            result['details']['error'] = "GameData folder not found"
            return result
        
        # МЕТОД 1: Анализ бинарных vs текстовых файлов (самый надежный)
        weight_text = game_data / "ObjWeightParamsPrototypes.cfg"
        weight_bin = game_data / "ObjWeightParamsPrototypes.cfg.bin"
        effect_text = game_data / "ObjEffectMaxParamsPrototypes.cfg"
        effect_bin = game_data / "ObjEffectMaxParamsPrototypes.cfg.bin"
        
        # Проверяем все возможные комбинации
        binary_count = 0
        text_count = 0
        
        if weight_bin.exists():
            binary_count += 1
            result['details']['weight_params'] = 'binary'
        elif weight_text.exists():
            text_count += 1
            result['details']['weight_params'] = 'text'
        
        if effect_bin.exists():
            binary_count += 1
            result['details']['effect_params'] = 'binary'
        elif effect_text.exists():
            text_count += 1
            result['details']['effect_params'] = 'text'
        
        # Анализируем CoreVariables
        core_vars = game_data / "CoreVariables.cfg"
        if core_vars.exists():
            result['details']['core_variables'] = 'text'
            text_count += 1
        elif (game_data / "CoreVariables.cfg.bin").exists():
            result['details']['core_variables'] = 'binary'
            binary_count += 1
        
        if binary_count >= 2 and text_count == 0:
            result['version'] = "1.8.1+"
            result['is_modern'] = True
            result['confidence'] = 95
            result['methods_used'].append("binary_files_detected")
        
        elif text_count >= 2 and binary_count == 0:
            result['version'] = "1.5.2 - 1.7.x"
            result['is_modern'] = False
            result['confidence'] = 90
            result['methods_used'].append("text_files_detected")
        
        # МЕТОД 2: Поиск в CoreVariables.cfg новых параметров
        if core_vars.exists():
            try:
                with open(core_vars, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(16384)
                    
                    # Проверяем наличие параметров из разных версий
                    version_indicators = {
                        '1.8.1': [
                            'StaminaRegenStateCoefs',
                            'GroundClamber',
                            'ClamberCostMultiplier',
                            'StaminaJumpCost',
                            'StaminaVaultCost'
                        ],
                        '1.7.x': [
                            'WeaponDurability',
                            'ArtifactBalance',
                            'EmissionFrequency'
                        ],
                        '1.6.x': [
                            'AimAssist',
                            'ControllerBalance',
                            'BloodsuckerInvisibility'
                        ],
                        '1.5.2': [
                            'MaxTotalWeight',
                            'InventoryPenalty',
                            'SprintStaminaCost'
                        ]
                    }
                    
                    found_indicators = {}
                    for version, indicators in version_indicators.items():
                        found = [ind for ind in indicators if ind in content]
                        if found:
                            found_indicators[version] = found
                            result['details'][f'indicators_{version}'] = found
                    
                    # Если нашли индикаторы и текущая уверенность низкая
                    if found_indicators and result['confidence'] < 80:
                        # Выбираем версию с наибольшим количеством совпадений
                        best_version = max(found_indicators.items(), key=lambda x: len(x[1]))
                        if len(best_version[1]) >= 2:
                            result['version'] = best_version[0]
                            result['confidence'] = 80
                            result['methods_used'].append("parameter_analysis")
                            # Обновляем is_modern на основе версии
                            result['is_modern'] = '1.8.1' in best_version[0]
            except Exception as e:
                result['details']['core_vars_error'] = str(e)
        
        # МЕТОД 3: Анализ версии в исполняемом файле игры (самый точный)
        try:
            config = self.config_manager.get_app_config()
            game_path = Path(config.get('game_base_path', ''))
            
            # Проверяем несколько возможных путей к exe
            possible_exe_paths = [
                game_path / "Stalker2" / "Binaries" / "Win64" / "Stalker2-Win64-Shipping.exe",
                game_path / "Stalker2.exe",
                game_path / "Binaries" / "Win64" / "Stalker2-Win64-Shipping.exe"
            ]
            
            for exe_path in possible_exe_paths:
                if exe_path.exists():
                    with open(exe_path, 'rb') as f:
                        exe_data = f.read(131072)  # 128KB
                        exe_str = exe_data.decode('utf-8', errors='ignore')
                        
                        # Ищем различные паттерны версии
                        version_patterns = [
                            (r'ProductVersion[\x00-\xFF]{0,20}(\d+\.\d+\.\d+(?:\.\d+)?)', 98),
                            (r'FileVersion[\x00-\xFF]{0,20}(\d+\.\d+\.\d+(?:\.\d+)?)', 97),
                            (r'(\d+\.\d+\.\d+\.\d+)', 95),
                            (r'Version[\x00-\xFF]{0,10}(\d+\.\d+\.\d+)', 90)
                        ]
                        
                        for pattern, confidence in version_patterns:
                            match = re.search(pattern, exe_str)
                            if match:
                                found_version = match.group(1)
                                # Проверяем, что это похоже на версию S.T.A.L.K.E.R. 2
                                if found_version.count('.') >= 2:
                                    # Если нашли более точную версию, обновляем
                                    if confidence > result['confidence']:
                                        result['version'] = found_version
                                        result['confidence'] = confidence
                                        result['methods_used'].append(f"exe_{pattern[1:10]}")
                                        # Обновляем is_modern на основе версии
                                        result['is_modern'] = found_version.startswith('1.8')
                                    break
                        break
        except Exception as e:
            result['details']['exe_error'] = str(e)
        
        # МЕТОД 4: Поиск в файлах манифеста
        try:
            manifest_files = list(game_data.rglob("*.manifest")) + list(game_data.rglob("*.version"))
            for mf in manifest_files[:5]:
                try:
                    with open(mf, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(8192)
                        version_match = re.search(r'(\d+\.\d+\.\d+(?:\.\d+)?)', content)
                        if version_match:
                            found_version = version_match.group(1)
                            # Если нашли версию и уверенность низкая или это более точная версия
                            if result['confidence'] < 85:
                                result['version'] = found_version
                                result['confidence'] = 85
                                result['methods_used'].append(f"manifest_{mf.name}")
                                result['is_modern'] = found_version.startswith('1.8')
                            break
                except:
                    pass
        except Exception as e:
            pass
        
        # МЕТОД 5: Анализ дат модификации файлов
        try:
            # Собираем даты модификации ключевых файлов
            mod_times = []
            for file in game_data.rglob("*"):
                if file.is_file() and file.stat().st_size > 10000:  # Только значимые файлы
                    mod_times.append(file.stat().st_mtime)
            
            if mod_times and result['confidence'] < 70:
                # Берем медианную дату
                median_time = statistics.median(mod_times)
                median_date = datetime.fromtimestamp(median_time)
                
                # Даты выхода версий (уточненные)
                release_dates = {
                    '1.5.2': datetime(2024, 10, 15),
                    '1.6.0': datetime(2024, 11, 1),
                    '1.7.0': datetime(2024, 11, 15),
                    '1.8.1': datetime(2024, 12, 1),
                }
                
                # Находим ближайшую дату релиза
                closest_version = min(release_dates.items(), 
                                     key=lambda x: abs((x[1] - median_date).days))
                days_diff = abs((closest_version[1] - median_date).days)
                
                if days_diff < 45:  # Если разница меньше 45 дней
                    result['version'] = closest_version[0]
                    result['confidence'] = 70
                    result['methods_used'].append("file_dates_analysis")
                    result['details']['median_file_date'] = median_date.isoformat()
                    result['details']['days_from_release'] = days_diff
                    result['is_modern'] = closest_version[0].startswith('1.8')
        except Exception as e:
            pass
        
        # МЕТОД 6: Проверка наличия специфических папок для версий
        try:
            # Папки, характерные для разных версий
            version_folders = {
                '1.8.1': [
                    "Quests/DLC_Quests",
                    "Zones/Icarus",
                    "Artifacts/LegendaryArtifacts"
                ],
                '1.7.x': [
                    "Zones/Yaniv",
                    "Quests/FactionQuests"
                ],
                '1.6.x': [
                    "Zones/Zaton",
                    "Quests/SideQuests"
                ]
            }
            
            for version, folders in version_folders.items():
                found_count = 0
                for folder in folders:
                    if (game_data / folder).exists():
                        found_count += 1
                
                if found_count >= 2 and result['confidence'] < 60:
                    result['version'] = version
                    result['confidence'] = 60
                    result['methods_used'].append(f"folder_structure_{version}")
                    result['is_modern'] = version.startswith('1.8')
                    result['details'][f'{version}_folders_found'] = found_count
        except Exception as e:
            pass
        
        # Финальная калибровка уверенности
        if result['confidence'] >= 90:
            # Уже очень уверены
            pass
        elif result['confidence'] >= 70:
            # Проверяем консистентность методов
            modern_indicators = sum([
                result['is_modern'],
                'binary_files_detected' in result['methods_used'],
                any('1.8' in m for m in result['methods_used']),
                any('1.8' in str(result.get('version', '')) for _ in [0])
            ])
            
            if modern_indicators >= 2:
                result['is_modern'] = True
                result['confidence'] = min(85, result['confidence'] + 10)
        
        return result
    
    def get_game_version(self) -> str:
        """Returns the detected game version from config"""
        config = self.config_manager.get_app_config()
        return config.get('game_version', 'unknown')
    
    def is_modern_game_version(self) -> bool:
        """Returns whether the game is modern (1.8.1+)"""
        config = self.config_manager.get_app_config()
        return config.get('game_is_modern', False)
    
    def get_game_version_info(self) -> Dict[str, Any]:
        """Returns all version information"""
        config = self.config_manager.get_app_config()
        return {
            'version': config.get('game_version', 'unknown'),
            'confidence': config.get('game_version_confidence', 0),
            'is_modern': config.get('game_is_modern', False),
            'methods': config.get('game_version_methods', []),
            'details': config.get('game_version_details', {}),
            'detected_at': config.get('game_version_detected_at', 'unknown')
        }
    
    def pack_mod(self, input_dir: Path, output_file: Path) -> bool:
        """Pack a mod directory into a .pak file"""
        logger.info(f"Packing {input_dir} to {output_file}")
        print(f"Packing mod: {output_file.name}")
        print()
        
        try:
            cmd = [
                str(self.repak_path),
                "pack",
                "--version", "V11",
                str(input_dir),
                str(output_file)
            ]
            
            result = subprocess.run(cmd, text=True)
            
            print()
            
            if result.returncode == 0:
                logger.info("Packing completed successfully")
                return True
            else:
                logger.error(f"Packing failed with return code: {result.returncode}")
                print(f"✗ Packing failed!")
                return False
                
        except Exception as e:
            logger.error(f"Packing error: {e}")
            print(f"✗ Packing error: {e}")
            return False
    
    def get_latest_extraction(self) -> Optional[Path]:
        """Get the path to the latest extraction folder"""
        config = self.config_manager.get_app_config()
        
        if 'last_extraction_path' in config:
            path = Path(config['last_extraction_path'])
            if path.exists():
                return path
        
        extract_dir = Path("data/extract")
        if extract_dir.exists():
            extractions = []
            for item in extract_dir.iterdir():
                if item.is_dir() and 'pakchunk' in item.name.lower():
                    try:
                        extractions.append((item.stat().st_mtime, item))
                    except:
                        extractions.append((0, item))
            
            if extractions:
                extractions.sort(key=lambda x: x[0], reverse=True)
                return extractions[0][1]
        
        return None