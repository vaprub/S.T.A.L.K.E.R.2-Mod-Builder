from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from .i18n import i18n, _

class BaseModule(ABC):
    """Базовый класс для всех модулей билдера"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.display_name = _(self.name.replace('Module', '').replace('_', ' '))
        self.source_dir = Path("to-mod-vanilla-files")
        self.output_dir = Path("modded-files")
        self.config_manager = None
        self._structure_cache = None
    
    def set_config_manager(self, config_manager):
        """Устанавливает config_manager для доступа к версии игры"""
        self.config_manager = config_manager
    
    def get_game_version(self) -> str:
        """Возвращает версию игры из конфига"""
        if self.config_manager:
            config = self.config_manager.get_app_config()
            return config.get('game_version', _('unknown'))
        return _('unknown')
    
    def is_modern_version(self) -> bool:
        """Проверяет, является ли версия игры современной (1.8.1+)"""
        version = self.get_game_version()
        return '1.8.1' in version or _('modern') in version.lower() or 'binary' in version.lower()
    
    def find_file_in_extraction(self, filename: str) -> Optional[Path]:
        """Ищет файл в распакованных данных игры"""
        if not self.source_dir or not self.source_dir.exists():
            return None
        
        for file_path in self.source_dir.rglob(filename):
            if file_path.is_file():
                return file_path
        
        return None
    
    def find_gamedata_path(self) -> Optional[Path]:
        """Находит путь к папке GameData в распакованных файлах"""
        if not self.source_dir or not self.source_dir.exists():
            return None
        
        for path in self.source_dir.rglob("GameData"):
            if path.is_dir():
                return path
        
        return None
    
    def analyze_game_structure(self) -> Dict[str, Any]:
        """Анализирует структуру распакованных файлов игры"""
        if self._structure_cache is not None:
            return self._structure_cache
        
        gamedata_path = self.find_gamedata_path()
        if not gamedata_path:
            self._structure_cache = {
                "status": "no_files",
                "game_version": self.get_game_version()
            }
            return self._structure_cache
        
        result = {
            "status": "ok",
            "gamedata_path": str(gamedata_path),
            "files": {},
            "has_cfg": False,
            "has_cfg_bin": False,
            "game_version": self.get_game_version(),
            "is_modern": self.is_modern_version()
        }
        
        # Список ключевых файлов для анализа
        key_files = [
            "CoreVariables.cfg",
            "ObjWeightParamsPrototypes.cfg",
            "ObjEffectMaxParamsPrototypes.cfg"
        ]
        
        for filename in key_files:
            file_info = self._analyze_file(gamedata_path, filename)
            if file_info:
                result["files"][filename] = file_info
                
                if file_info["exists"]:
                    if file_info["format"] == "text":
                        result["has_cfg"] = True
                    elif file_info["format"] == "binary":
                        result["has_cfg_bin"] = True
        
        self._structure_cache = result
        return result
    
    def _analyze_file(self, gamedata_path: Path, filename: str) -> Dict[str, Any]:
        """Анализирует конкретный файл"""
        result = {
            "filename": filename,
            "exists": False,
            "format": "unknown",
            "path": None,
            "size": 0
        }
        
        cfg_path = gamedata_path / filename
        if cfg_path.exists():
            result["exists"] = True
            result["format"] = "text"
            result["path"] = str(cfg_path)
            result["size"] = cfg_path.stat().st_size
            return result
        
        bin_path = gamedata_path / f"{filename}.bin"
        if bin_path.exists():
            result["exists"] = True
            result["format"] = "binary"
            result["path"] = str(bin_path)
            result["size"] = bin_path.stat().st_size
            return result
        
        return result
    
    def get_file_format(self, filename: str) -> str:
        """Возвращает формат конкретного файла ('text', 'binary', или 'unknown')"""
        structure = self.analyze_game_structure()
        if filename in structure.get("files", {}):
            return structure["files"][filename].get("format", "unknown")
        return "unknown"
    
    def should_create_minimal_config(self, filename: str) -> bool:
        """Определяет, нужно ли создавать минимальный конфиг для файла"""
        file_format = self.get_file_format(filename)
        # Для современных версий всегда создаём минимальные конфиги для бинарных файлов
        if self.is_modern_version() and file_format == "binary":
            return True
        # Для старых версий или если файл не найден
        return file_format in ["binary", "unknown"]
    
    @abstractmethod
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        """Возвращает список предопределенных конфигураций"""
        pass
    
    @abstractmethod
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        """Запрашивает у пользователя кастомную конфигурацию"""
        pass
    
    @abstractmethod
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        """Применяет конфигурацию к файлам"""
        pass
    
    def validate_source_files(self) -> bool:
        """Проверяет наличие исходных файлов"""
        return self.source_dir.exists()
    
    def log_info(self, message: str):
        """Логирует информационное сообщение с поддержкой перевода"""
        print(f"✓ {_(message)}")
    
    def log_warning(self, message: str):
        """Логирует предупреждение с поддержкой перевода"""
        print(f"⚠ {_(message)}")
    
    def log_error(self, message: str):
        """Логирует ошибку с поддержкой перевода"""
        print(f"❌ {_(message)}")