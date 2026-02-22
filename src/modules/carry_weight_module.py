import json
import math
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_module import BaseModule

class CarryWeightModule(BaseModule):
    
    def __init__(self):
        super().__init__()
        self.display_name = "Carry Weight Modifier"
        self.config_file = Path("config/defaults/predefined_carry_weights_config.json")
        self.files = {
            'CoreVariables.cfg': 'CoreVariables.cfg',
            'ObjEffectMaxParamsPrototypes.cfg': 'ObjEffectMaxParamsPrototypes.cfg',
            'ObjWeightParamsPrototypes.cfg': 'ObjWeightParamsPrototypes.cfg'
        }
    
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        configs = []
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for name, config in data.get("configurations", {}).items():
                weight = config["ObjWeightParamsPrototypes.cfg"]["max_inventory_mass"]
                configs.append({
                    'name': f"{weight} kg" + (" (Vanilla)" if name == "vanilla" else ""),
                    'config': config,
                    'weight': weight
                })
        
        return sorted(configs, key=lambda x: x['weight'])
    
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        print("\nCustom Carry Weight Configuration")
        print("=" * 40)
        print("Enter weight between 81-10000 kg")
        
        try:
            weight = int(input("Max carry weight: ").strip())
            
            if not 81 <= weight <= 10000:
                print("Weight must be between 81 and 10000")
                return None
            
            return self._calculate_config(weight)
            
        except ValueError:
            print("Invalid input")
            return None
    
    def _calculate_config(self, max_weight: int) -> Dict[str, Any]:
        penalty = math.floor(max_weight * 0.88 / 5) * 5
        critical = round(max_weight * 0.96 / 5) * 5
        velocity_2 = round((penalty + critical) / 2)
        
        return {
            "CoreVariables.cfg": {
                "inventory_penalty_less_weight": float(penalty),
                "medium_effect_start_ui": penalty,
                "critical_effect_start_ui": critical
            },
            "ObjEffectMaxParamsPrototypes.cfg": {
                "penalty_less_weight_max": 99999,
                "additional_inventory_weight_max": 99999
            },
            "ObjWeightParamsPrototypes.cfg": {
                "max_inventory_mass": max_weight,
                "inventory_penalty_less_weight": penalty - 0.01,
                "thresholds": {
                    "no_effect": max_weight,
                    "velocity_change_3": critical,
                    "velocity_change_2": velocity_2,
                    "velocity_change_1": penalty
                }
            }
        }
    
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        try:
            game_data_path = output_path / "Stalker2/Content/GameLite/GameData"
            game_data_path.mkdir(parents=True, exist_ok=True)
            
            self._apply_core_variables(config["CoreVariables.cfg"], game_data_path)
            self._apply_effect_params(config["ObjEffectMaxParamsPrototypes.cfg"], game_data_path)
            self._apply_weight_params(config["ObjWeightParamsPrototypes.cfg"], game_data_path)
            
            return True
            
        except Exception as e:
            print(f"Error applying configuration: {e}")
            return False
    
    def _apply_core_variables(self, config: Dict[str, Any], output_path: Path):
        output_file = output_path / "CoreVariables.cfg"
        
        # Ищем оригинальный файл в распакованных данных
        source_file = self.find_file_in_extraction("CoreVariables.cfg")
        
        if not source_file:
            print("❌ ERROR: CoreVariables.cfg not found in extracted files!")
            print("   Please extract game files first.")
            return
        
        # Читаем оригинальный файл
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Обновляем только параметры веса
        content = re.sub(
            r'(InventoryPenaltyLessWeight\s*=\s*)\d+\.?\d*',
            f'\\g<1>{config["inventory_penalty_less_weight"]}',
            content
        )
        content = re.sub(
            r'(MediumEffectStartUI\s*=\s*)\d+',
            f'\\g<1>{config["medium_effect_start_ui"]}',
            content
        )
        content = re.sub(
            r'(CriticalEffectStartUI\s*=\s*)\d+',
            f'\\g<1>{config["critical_effect_start_ui"]}',
            content
        )
        
        # Сохраняем измененный файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Merged CoreVariables.cfg - updated weight parameters, preserved all other settings")
    
    def _apply_effect_params(self, config: Dict[str, Any], output_path: Path):
        output_file = output_path / "ObjEffectMaxParamsPrototypes.cfg"
        
        # Ищем оригинальный файл (может быть .cfg или .cfg.bin)
        source_file = self.find_file_in_extraction("ObjEffectMaxParamsPrototypes.cfg")
        if not source_file:
            source_file = self.find_file_in_extraction("ObjEffectMaxParamsPrototypes.cfg.bin")
        
        if not source_file:
            print("❌ ERROR: ObjEffectMaxParamsPrototypes.cfg[.bin] not found in extracted files!")
            return
        
        # Если это бинарный файл, создаем новый текстовый
        if source_file.suffix == '.bin':
            print("⚠ Original file is binary, creating new text config")
            self._create_effect_params_from_scratch(config, output_file)
            return
        
        # Читаем текстовый файл
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Обновляем параметры
        content = re.sub(
            r'(EffectSID\s*=\s*EEffectType::PenaltyLessWeight[\s\S]*?MaxValue\s*=\s*)\d+',
            f'\\g<1>{config["penalty_less_weight_max"]}',
            content
        )
        content = re.sub(
            r'(EffectSID\s*=\s*EEffectType::AdditionalInventoryWeight[\s\S]*?MaxValue\s*=\s*)\d+',
            f'\\g<1>{config["additional_inventory_weight_max"]}',
            content
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Merged ObjEffectMaxParamsPrototypes.cfg")
    
    def _create_effect_params_from_scratch(self, config: Dict[str, Any], output_file: Path):
        """Создает новый файл EffectParams если оригинал бинарный"""
        content = f"""[0] : struct.begin
   SID = Empty
struct.end

DefaultEffectMaxParamsSID : struct.begin {{refkey=[0]}}
   SID = DefaultEffectMaxParamsSID
   MaxEffectValues : struct.begin
      [0] : struct.begin
         EffectSID = EEffectType::ProtectionShock
         MaxValue = 90.f
      struct.end
      [1] : struct.begin
         EffectSID = EEffectType::PenaltyLessWeight
         MaxValue = {config['penalty_less_weight_max']}
      struct.end
      [2] : struct.begin
         EffectSID = EEffectType::RegenStamina
         MaxValue = 30.f
      struct.end
      [3] : struct.begin
         EffectSID = EEffectType::ProtectionStrike
         MaxValue = 4.5f
      struct.end
      [4] : struct.begin
         EffectSID = EEffectType::DegenBleeding
         MaxValue = 5
      struct.end
      [5] : struct.begin
         EffectSID = EEffectType::ProtectionBurn
         MaxValue = 90.f
      struct.end
      [6] : struct.begin
         EffectSID = EEffectType::ProtectionChemical
         MaxValue = 90.f
      struct.end
      [7] : struct.begin
         EffectSID = EEffectType::ProtectionPSY
         MaxValue = 90.f
      struct.end
      [8] : struct.begin
         EffectSID = EEffectType::ProtectionRadiation
         MaxValue = 85.f
      struct.end
      [9] : struct.begin
         EffectSID = EEffectType::AdditionalInventoryWeight
         MaxValue = {config['additional_inventory_weight_max']}
      struct.end
   struct.end
struct.end"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created ObjEffectMaxParamsPrototypes.cfg from template (original was binary)")
    
    def _apply_weight_params(self, config: Dict[str, Any], output_path: Path):
        output_file = output_path / "ObjWeightParamsPrototypes.cfg"
        
        # Ищем оригинальный файл (может быть .cfg или .cfg.bin)
        source_file = self.find_file_in_extraction("ObjWeightParamsPrototypes.cfg")
        if not source_file:
            source_file = self.find_file_in_extraction("ObjWeightParamsPrototypes.cfg.bin")
        
        if not source_file:
            print("❌ ERROR: ObjWeightParamsPrototypes.cfg[.bin] not found in extracted files!")
            return
        
        # Если это бинарный файл, создаем новый текстовый
        if source_file.suffix == '.bin':
            print("⚠ Original file is binary, creating new text config")
            self._create_weight_params_from_scratch(config, output_file)
            return
        
        # Читаем текстовый файл
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        max_weight = config["max_inventory_mass"]
        penalty = config["inventory_penalty_less_weight"]
        thresholds = config["thresholds"]
        
        # Обновляем параметры
        content = re.sub(
            r'(DefaultWeightParams.*?MaxInventoryMass\s*=\s*)\d+',
            f'\\g<1>{max_weight}',
            content,
            flags=re.DOTALL
        )
        content = re.sub(
            r'(DefaultWeightParams.*?InventoryPenaltyLessWeight\s*=\s*)\d+\.?\d*',
            f'\\g<1>{penalty}',
            content,
            flags=re.DOTALL
        )
        
        # Обновляем пороговые значения (более сложный regex)
        threshold_pattern = r'Threshold\s*=\s*\d+\.?\d*f?'
        thresholds_list = [
            f"Threshold = {thresholds['no_effect']}.f",
            f"Threshold = {thresholds['velocity_change_3']}.f",
            f"Threshold = {thresholds['velocity_change_2']}.f",
            f"Threshold = {thresholds['velocity_change_1']}.f"
        ]
        
        # Находим все Threshold и заменяем
        threshold_matches = list(re.finditer(threshold_pattern, content))
        if len(threshold_matches) >= 4:
            for i, match in enumerate(threshold_matches[:4]):
                content = content[:match.start()] + thresholds_list[i] + content[match.end():]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Merged ObjWeightParamsPrototypes.cfg")
    
    def _create_weight_params_from_scratch(self, config: Dict[str, Any], output_file: Path):
        """Создает новый файл WeightParams если оригинал бинарный"""
        max_weight = config["max_inventory_mass"]
        penalty = config["inventory_penalty_less_weight"]
        thresholds = config["thresholds"]
        
        content = f"""[0] : struct.begin
   SID = Empty
   MaxInventoryMass = 0.f
   InventoryPenaltyLessWeight = 0.f
struct.end

DefaultWeightParams : struct.begin {{refkey=[0]}}
   SID = DefaultWeightParams
   MaxInventoryMass = {max_weight}
   InventoryPenaltyLessWeight = {penalty}
   WeightEffectParams : struct.begin
      [0] : struct.begin
         Threshold = {thresholds["no_effect"]}.f
         EffectPrototypeSIDs : struct.begin
         struct.end
      struct.end
      [1] : struct.begin
         Threshold = {thresholds["velocity_change_3"]}.f
         EffectPrototypeSIDs : struct.begin
            [0] = OverweightMovementVelocityChange_3
         struct.end
      struct.end
      [2] : struct.begin
         Threshold = {thresholds["velocity_change_2"]}.f
         EffectPrototypeSIDs : struct.begin
            [0] = OverweightMovementVelocityChange_2
         struct.end
      struct.end
      [3] : struct.begin
         Threshold = {thresholds["velocity_change_1"]}.f
         EffectPrototypeSIDs : struct.begin
            [0] = OverweightMovementVelocityChange_1
         struct.end
      struct.end
   struct.end
struct.end"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created ObjWeightParamsPrototypes.cfg from template (original was binary)")
    
    def find_file_in_extraction(self, filename: str) -> Optional[Path]:
        """Find a file in the extracted game files"""
        if not hasattr(self, 'source_dir') or not self.source_dir or not self.source_dir.exists():
            return None
        
        for file_path in self.source_dir.rglob(filename):
            if file_path.is_file():
                print(f"Found {filename} at: {file_path}")
                return file_path
        
        return None