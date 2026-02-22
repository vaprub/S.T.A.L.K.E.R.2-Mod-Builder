import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_module import BaseModule

class StaminaModule(BaseModule):
    
    def __init__(self):
        super().__init__()
        self.display_name = "Stamina Usage Modifier"
        self.config_file = Path("config/defaults/predefined_stamina_use_values.json")
    
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        configs = []
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for category, presets in data.items():
                for name, preset in presets.items():
                    config_data = {k: v for k, v in preset.items() if k != "description"}
                    configs.append({
                        'name': f"{name} - {preset['description']}",
                        'config': config_data
                    })
        
        return configs
    
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        print("\nCustom Stamina Configuration")
        print("=" * 40)
        print("Lower values = less stamina consumption")
        
        config = {}
        
        try:
            config['Sprint'] = self._get_float_input("Sprint (1.0-10.0): ", 1.0, 10.0)
            config['Jump'] = self._get_float_input("Jump (2.0-20.0): ", 2.0, 20.0)
            config['MeleeNormal'] = self._get_float_input("Melee Normal (2.0-20.0): ", 2.0, 20.0)
            config['MeleeStrong'] = self._get_float_input("Melee Strong (3.0-30.0): ", 3.0, 30.0)
            config['MeleeButstock'] = self._get_float_input("Melee Butstock (1.5-15.0): ", 1.5, 15.0)
            config['Vault'] = self._get_float_input("Vault (1.5-15.0): ", 1.5, 15.0)
            
            return config
            
        except ValueError:
            print("Invalid input")
            return None
    
    def _get_float_input(self, prompt: str, min_val: float, max_val: float) -> float:
        while True:
            try:
                value = float(input(prompt).strip())
                if min_val <= value <= max_val:
                    return value
                print(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        try:
            proto_path = output_path / "Stalker2/Content/GameLite/GameData/ObjPrototypes"
            proto_path.mkdir(parents=True, exist_ok=True)
            
            output_file = proto_path / "BetterStamina.cfg"
            
            content = f"""BetterStamina : struct.begin {{refurl=../ObjPrototypes.cfg;refkey=Player}}
   StaminaPerAction : struct.begin
      Sprint = {config['Sprint']}
      Jump = {config['Jump']}
      MeleeNormal = {config['MeleeNormal']}
      MeleeStrong = {config['MeleeStrong']}
      MeleeButstock = {config['MeleeButstock']}
      Vault = {config['Vault']}
   struct.end
struct.end"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error applying configuration: {e}")
            return False