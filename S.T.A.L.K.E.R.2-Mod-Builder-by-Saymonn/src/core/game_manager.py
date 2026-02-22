import logging
import json
import re
import ssl
from pathlib import Path
from urllib.request import urlopen, Request
from typing import Optional
import tkinter as tk
from tkinter import filedialog

logger = logging.getLogger(__name__)

class GameManager:
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.game_path: Optional[Path] = None
        self._load_game_path()
    
    def _load_game_path(self):
        config = self.config_manager.get_app_config()
        if 'game_base_path' in config:
            self.game_path = Path(config['game_base_path'])
    
    def validate_game_path(self) -> bool:
        if not self.game_path:
            return False
        
        # Проверяем несколько возможных путей к exe
        possible_paths = [
            self.game_path / "Stalker2" / "Binaries" / "Win64" / "Stalker2-Win64-Shipping.exe",
            self.game_path / "stalker2.exe",
            self.game_path / "Stalker2.exe",
            self.game_path / "Binaries" / "Win64" / "Stalker2-Win64-Shipping.exe"
        ]
        
        for path in possible_paths:
            if path.exists():
                return True
        
        return False
    
    def setup_game_path(self) -> bool:
        print()
        print("=" * 60)
        print("    GAME PATH SETUP REQUIRED")
        print("=" * 60)
        print()
        print("The application needs to locate your S.T.A.L.K.E.R. 2 installation.")
        print()
        print("You need to find and select this file:")
        print("  • Stalker2-Win64-Shipping.exe")
        print("    (located in Stalker2/Binaries/Win64/)")
        print()
        print("Common locations:")
        print("  • Steam: C:\\Program Files (x86)\\Steam\\steamapps\\common\\S.T.A.L.K.E.R. 2 Heart of Chornobyl\\")
        print("  • Epic: C:\\Program Files\\Epic Games\\S.T.A.L.K.E.R. 2 Heart of Chornobyl\\")
        print("  • GOG: C:\\GOG Games\\S.T.A.L.K.E.R. 2 Heart of Chornobyl\\")
        print()
        print("Press Enter to open file browser...")
        input()
        
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Select STALKER 2 Executable (Stalker2-Win64-Shipping.exe)",
            filetypes=[
                ("STALKER 2 Executable", "Stalker2-Win64-Shipping.exe"),
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ],
            initialdir="C:\\Program Files"
        )
        
        root.destroy()
        
        if file_path:
            exe_path = Path(file_path)
            
            # Находим корневую папку игры
            if "Binaries" in exe_path.parts:
                # Путь типа .../Stalker2/Binaries/Win64/exe
                self.game_path = exe_path.parents[3]
            else:
                # Просто папка с exe
                self.game_path = exe_path.parent
            
            self.config_manager.update_app_config({
                'game_base_path': str(self.game_path)
            })
            
            print()
            print(f"✓ Game path set successfully!")
            print(f"  Game directory: {self.game_path}")
            print()
            
            if not self.validate_game_path():
                print("⚠ Warning: Could not validate game installation.")
                print("  Make sure you selected the correct executable.")
            else:
                print("✓ Game installation validated successfully!")
            
            print()
            input("Press Enter to continue...")
            
            logger.info(f"Game path set to: {self.game_path}")
            return True
        else:
            print()
            print("✗ No file selected. Game path setup cancelled.")
            print("  You can set the game path later in Settings.")
            print()
            input("Press Enter to continue...")
            return False
    
    def get_pak_path(self) -> Path:
        """Returns path to the main game PAK file"""
        return self.game_path / "Stalker2" / "Content" / "Paks" / "pakchunk0-Windows.pak"
    
    def get_mods_directory(self) -> Path:
        """Returns path to the ~mods directory and creates it if needed"""
        mods_dir = self.game_path / "Stalker2" / "Content" / "Paks" / "~mods"
        mods_dir.mkdir(parents=True, exist_ok=True)
        return mods_dir
    
    def is_extraction_completed(self) -> bool:
        """Checks if extraction has been completed"""
        config = self.config_manager.get_app_config()
        mod_base_path = config.get('mod_base_path', 'data')
        extract_path = Path(mod_base_path) / "data" / "extract"
        
        if not extract_path.exists():
            return False
        
        return self._check_extraction_folder_size(extract_path)
    
    def _check_extraction_folder_size(self, extract_path: Path) -> bool:
        """Checks if extraction folder contains valid data"""
        try:
            for item in extract_path.iterdir():
                if item.is_dir():
                    folder_name = item.name.lower()
                    if 'pakchunk' in folder_name:
                        return True
            return False
        except Exception:
            return False
    
    def check_game_version(self) -> Optional[str]:
        """Checks game version from Steam news (legacy method)"""
        try:
            url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=1643320&count=30&maxlength=0"
            
            with urlopen(
                Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                timeout=12,
                context=ssl.create_default_context()
            ) as response:
                data = json.loads(response.read().decode("utf-8", "replace"))
                items = data["appnews"]["newsitems"]
            
            version_pattern = re.compile(
                r'(?:v(?:ersion)?|patch|hotfix|update)\s*(\d+(?:\.\d+){1,3})',
                re.IGNORECASE
            )
            
            for item in items:
                for text in (item.get("title", ""), item.get("contents", "")):
                    match = version_pattern.search(text)
                    if match:
                        return match.group(1)
            
            for item in items:
                title = item.get("title", "").strip()
                if title:
                    return title
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check game version: {e}")
            return None
    
    def detect_game_version_from_files(self, extract_dir: Optional[Path] = None) -> str:
        """
        Detects game version from extracted files
        More accurate than check_game_version()
        """
        if extract_dir is None:
            # Try to find latest extraction
            config = self.config_manager.get_app_config()
            mod_base_path = config.get('mod_base_path', 'data')
            extract_path = Path(mod_base_path) / "data" / "extract"
            
            if not extract_path.exists():
                return "unknown (no extraction)"
            
            # Find latest extraction folder
            extractions = []
            for item in extract_path.iterdir():
                if item.is_dir() and 'pakchunk' in item.name.lower():
                    extractions.append(item)
            
            if not extractions:
                return "unknown (no extraction folders)"
            
            extract_dir = max(extractions, key=lambda p: p.stat().st_mtime)
        
        game_data = extract_dir / "Stalker2" / "Content" / "GameLite" / "GameData"
        if not game_data.exists():
            return "unknown (no GameData)"
        
        # Check file formats
        weight_bin = game_data / "ObjWeightParamsPrototypes.cfg.bin"
        effect_bin = game_data / "ObjEffectMaxParamsPrototypes.cfg.bin"
        
        if weight_bin.exists() and effect_bin.exists():
            return "1.8.1+ (binary files detected)"
        
        # Check CoreVariables for version indicators
        core_vars = game_data / "CoreVariables.cfg"
        if core_vars.exists():
            try:
                with open(core_vars, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
                    if 'StaminaRegenStateCoefs' in content:
                        return "1.8.1+ (modern parameters)"
                    elif 'WeaponDurability' in content:
                        return "1.7.x"
            except:
                pass
        
        return "1.5.2 - 1.7.x (legacy)"