import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_module import BaseModule

class TraderDurabilityModule(BaseModule):
    
    def __init__(self):
        super().__init__()
        self.display_name = "Traders Buy Broken Stuff"
    
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'Accept All (0% minimum)', 'config': {'min_durability': 0.0}},
            {'name': 'Accept Damaged (25% minimum)', 'config': {'min_durability': 0.25}},
            {'name': 'Accept Used (50% minimum)', 'config': {'min_durability': 0.50}},
            {'name': 'Vanilla (70% minimum)', 'config': {'min_durability': 0.70}},
        ]
    
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        print("\nCustom Trader Durability Requirements")
        print("=" * 40)
        print("Set minimum item condition traders will accept")
        print("0% = Accept completely broken items")
        print("100% = Only accept pristine items")
        
        try:
            percentage = int(input("Minimum durability (0-100%): ").strip())
            
            if not 0 <= percentage <= 100:
                print("Percentage must be between 0 and 100")
                return None
            
            return {'min_durability': percentage / 100.0}
            
        except ValueError:
            print("Invalid input")
            return None
    
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        try:
            game_data_path = output_path / "Stalker2/Content/GameLite/GameData"
            game_data_path.mkdir(parents=True, exist_ok=True)
            
            source_file = self.find_file_in_extraction("TradePrototypes.cfg")
            if not source_file:
                print("TradePrototypes.cfg not found in extraction")
                return False
            
            output_file = game_data_path / "TradePrototypes.cfg"
            
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            min_durability = config['min_durability']
            formatted_value = self._format_durability_value(min_durability)
            
            def replace_trader_durability(match):
                trader_name = match.group(1)
                full_match = match.group(0)
                
                if trader_name == "Trader_Soviet_Rostok_TradePrototype":
                    return full_match
                
                modified = re.sub(
                    r'WeaponSellMinDurability\s*=\s*[\d.]+f?',
                    f'WeaponSellMinDurability = {formatted_value}',
                    full_match
                )
                
                modified = re.sub(
                    r'ArmorSellMinDurability\s*=\s*[\d.]+f?',
                    f'ArmorSellMinDurability = {formatted_value}',
                    modified
                )
                
                return modified
            
            trader_pattern = r'(\w+)\s*:\s*struct\.begin\s*\{refkey=\[0\]\}(.*?)struct\.end'
            content = re.sub(trader_pattern, replace_trader_durability, content, flags=re.DOTALL)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error applying configuration: {e}")
            return False
    
    def _format_durability_value(self, value: float) -> str:
        if value == int(value):
            return f"{value:.1f}f"
        else:
            formatted = f"{value:.2f}".rstrip('0')
            if formatted.endswith('.'):
                formatted += '0'
            return f"{formatted}f"