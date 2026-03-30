import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    
    def __init__(self):
        self.config_dir = Path("config")
        self.app_config_file = self.config_dir / "app_config.json"
        
        self.config_dir.mkdir(exist_ok=True)
        
        self.app_config = self._load_app_config()
    
    def _load_app_config(self) -> Dict[str, Any]:
        """Загружает конфиг, но НЕ сохраняет mod_base_path из файла — всегда берёт текущую папку"""
        config_data = {}
        
        if self.app_config_file.exists():
            try:
                with open(self.app_config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load app config: {e}")
        
        # Всегда переопределяем mod_base_path текущей рабочей папкой
        config_data['mod_base_path'] = str(Path.cwd())
        
        # Если версии нет — ставим по умолчанию
        if 'version' not in config_data:
            config_data['version'] = '2.0.0'
        
        return config_data
    
    def get_app_config(self) -> Dict[str, Any]:
        return self.app_config.copy()
    
    def update_app_config(self, updates: Dict[str, Any]):
        """Обновляет конфиг, но НЕ перезаписывает mod_base_path"""
        # Убираем mod_base_path из обновлений, если он там случайно попал
        updates.pop('mod_base_path', None)
        self.app_config.update(updates)
        self._save_app_config()
    
    def _save_app_config(self):
        try:
            with open(self.app_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_config, f, indent=2)
            logger.info("App config saved")
        except Exception as e:
            logger.error(f"Failed to save app config: {e}")