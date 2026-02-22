import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_module import BaseModule

class DayLengthModule(BaseModule):
    
    def __init__(self):
        super().__init__()
        self.display_name = "Day Length Modifier"
        self.config_file = Path("config/defaults/predefined_day_lenght_values.json")
    
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        configs = []
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for name, config in data.get("configurations", {}).items():
                configs.append({
                    "name": f"{config['description']}\n{config['speed_info']}\n",
                    "config": {"coefficient": config["coefficient"]},
                    "speed_info": config["speed_info"]
                })
        
        return configs
    
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        print("\nCustom Day Length Configuration")
        print("=" * 40)
        print("Higher coefficient = faster time")
        print("24 = Vanilla (1 real minute = 2.5 game minutes)")
        print("1 = Real time (1:1)")
        
        try:
            coefficient = float(input("Time coefficient (0.5-100): ").strip())
            
            if not 0.5 <= coefficient <= 100:
                print("Coefficient must be between 0.5 and 100")
                return None
            
            return {'coefficient': coefficient}
            
        except ValueError:
            print("Invalid input")
            return None
    
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        try:
            game_data_path = output_path / "Stalker2/Content/GameLite/GameData"
            game_data_path.mkdir(parents=True, exist_ok=True)
            
            output_file = game_data_path / "CoreVariables.cfg"
            
            if output_file.exists():
                source_file = output_file
            else:
                source_file = self.find_file_in_extraction("CoreVariables.cfg")
                if not source_file:
                    print("CoreVariables.cfg not found in extraction")
                    return False
            
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            coefficient = config['coefficient']
            content = re.sub(
                r'(RealToGameTimeCoef\s*=\s*)\d+\.?\d*',
                rf'\g<1>{coefficient}',
                content
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error applying configuration: {e}")
            return False