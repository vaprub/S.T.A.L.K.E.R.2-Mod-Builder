import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_module import BaseModule

class WeaponDurabilityModule(BaseModule):
    
    def __init__(self):
        super().__init__()
        self.display_name = "Weapon Durability Modifier"
    
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        return [
            {'name': '2x More Durable', 'config': {'reduction_factor': 2.0}},
            {'name': '3x More Durable', 'config': {'reduction_factor': 3.0}},
            {'name': '5x More Durable', 'config': {'reduction_factor': 5.0}},
            {'name': '10x More Durable', 'config': {'reduction_factor': 10.0}},
        ]
    
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        print("\nCustom Weapon Durability Configuration")
        print("=" * 40)
        print("Higher factor = weapons degrade slower")
        print("2.0 = weapons last twice as long")
        
        try:
            factor = float(input("Durability factor (1.01-10.0): ").strip())
            
            if not 1.01 <= factor <= 10.0:
                print("Factor must be between 1.01 and 10.0")
                return None
            
            return {'reduction_factor': factor}
            
        except ValueError:
            print("Invalid input")
            return None
    
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        try:
            weapon_path = output_path / "Stalker2/Content/GameLite/GameData/WeaponData/CharacterWeaponSettingsPrototypes"
            weapon_path.mkdir(parents=True, exist_ok=True)
            
            source_file = self.find_file_in_extraction("PlayerWeaponSettingsPrototypes.cfg")
            if not source_file:
                print("PlayerWeaponSettingsPrototypes.cfg not found in extraction")
                return False
            
            output_file = weapon_path / "PlayerWeaponSettingsPrototypes.cfg"
            
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            reduction_factor = config['reduction_factor']
            
            def replace_durability(match):
                weapon_name = match.group(1)
                full_match = match.group(0)
                
                durability_match = re.search(r'DurabilityDamagePerShot\s*=\s*([\d.]+)f?', full_match)
                
                if durability_match:
                    original_value = float(durability_match.group(1))
                    new_value = round(original_value / reduction_factor, 2)
                    
                    modified = re.sub(
                        r'DurabilityDamagePerShot\s*=\s*[\d.]+f?',
                        f'DurabilityDamagePerShot = {new_value}',
                        full_match
                    )
                    return modified
                
                return full_match
            
            weapon_pattern = r'(\w+)\s*:\s*struct\.begin\s*(?:\{[^}]*\})?(.*?)struct\.end'
            content = re.sub(weapon_pattern, replace_durability, content, flags=re.DOTALL)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error applying configuration: {e}")
            return False