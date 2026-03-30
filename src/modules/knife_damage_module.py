import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_module import BaseModule, _

class KnifeDamageModule(BaseModule):
    """Модуль для увеличения урона ножа с возможностью игнорировать броню"""
    
    def __init__(self):
        super().__init__()
        self.display_name = _("Knife Damage Modifier")
    
    def get_predefined_configs(self) -> List[Dict[str, Any]]:
        return [
            {'name': _('2x Damage'), 'config': {'multiplier': 2.0}},
            {'name': _('3x Damage'), 'config': {'multiplier': 3.0}},
            {'name': _('5x Damage'), 'config': {'multiplier': 5.0}},
            {'name': _('10x Damage'), 'config': {'multiplier': 10.0}},
        ]
    
    def get_custom_config(self) -> Optional[Dict[str, Any]]:
        print("\n" + _("Custom Knife Damage Configuration"))
        print("=" * 40)
        print(_("Higher multiplier = more damage"))
        print(_("2.0 = double damage, 5.0 = five times damage"))
        print(_("Knife will ignore armor (useful for testing)"))
        
        try:
            multiplier = float(input(_("Damage multiplier (1.01-100.0): ")).strip())
            if not 1.01 <= multiplier <= 100.0:
                print(_("Multiplier must be between 1.01 and 100.0"))
                return None
            return {'multiplier': multiplier}
        except ValueError:
            print(_("Invalid input"))
            return None
    
    def apply_configuration(self, config: Dict[str, Any], output_path: Path) -> bool:
        try:
            game_data_path = output_path / "Stalker2/Content/GameLite/GameData"
            game_data_path.mkdir(parents=True, exist_ok=True)
            
            multiplier = config['multiplier']
            base_damage = 51.0  # из оригинального бинарного файла
            new_damage = base_damage * multiplier
            new_damage = round(new_damage, 2)
            
            print(_("Base damage: {}, multiplier: {}, new damage: {}").format(base_damage, multiplier, new_damage))
            print(_("Knife will ignore armor (ShouldIgnoreArmor = true)"))
            
            output_file = game_data_path / "MeleeWeaponPrototypes.cfg"
            
            # Полный текстовый файл на основе расшифрованного HEX, с изменёнными параметрами
            content = f"""﻿Empty : struct.begin
   SID = Empty
   DamageModifiers : struct.begin
   struct.end
   ImpulseModifiers : struct.begin
   struct.end
struct.end
Knife : struct.begin {{refkey=Empty}}
   SID = Knife
   
   HitDetectionDistance = 300.f
   HitDetectionAngle = 45.f
   HitDetectionRadius = 5.f
   
   Damage = {new_damage}.f
   ArmorDamage = 0.f
   ArmorPiercing = 1.f
   Bleeding = 50.f
   BleedingChanceIncrement = 90.f
   
   ShouldIgnoreArmor = true
   
   ImpulseStrength = 500.f
   ImpactPhysicalMaterialPrototypeSID = Knife
   LightAttackImpactSoundEvent = AkAudioEvent'/Game/_STALKER2/Audio/WwiseAudio/Events/Weapons/Melee/Knife_Impact/SFX_Knife_Hit_Weak.SFX_Knife_Hit_Weak'
   HeavyAttackImpactSoundEvent = AkAudioEvent'/Game/_STALKER2/Audio/WwiseAudio/Events/Weapons/Melee/Knife_Impact/SFX_Knife_Hit_Strong.SFX_Knife_Hit_Strong'
   CrosshairType = ECrosshairType::Point
   
   DamageModifiers : struct.begin
      HandOccupied = 1.0
      StrongAttack = 1.77
   struct.end
   
   ImpulseModifiers : struct.begin
      HandOccupied = 1.0
      StrongAttack = 1.0
   struct.end
struct.end
WeaponButt : struct.begin {{refkey=Knife}}
   SID = WeaponButt
   
   HitDetectionDistance = 300.f
   HitDetectionAngle = 45.f
   HitDetectionRadius = 5.f
   
   Damage = 90.f
   ArmorDamage = 0.f
   ArmorPiercing = 0.f
   Bleeding = 90.f
   BleedingChanceIncrement = 90.f
   ImpactPhysicalMaterialPrototypeSID = Empty
   
   LightAttackImpactSoundEvent = AkAudioEvent'/Game/_STALKER2/Audio/WwiseAudio/Events/Weapons/Melee_Attack/SFX_Melee_Attack.SFX_Melee_Attack'
   
   TargetEffects : struct.begin
      [*] : struct.begin
         EffectPrototypeSID = ButtStroke_CameraShake
         Chance = 1.f
      struct.end
   struct.end
   
   SourceEffects : struct.begin
      [*] : struct.begin
         EffectPrototypeSID = ButtStroke_Corrosion
         Chance = 1.f
      struct.end
   struct.end
struct.end
"""
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(_("✓ Created {} with new damage: {} and armor ignore enabled").format(output_file.name, new_damage))
            return True
            
        except Exception as e:
            print(_("Error applying knife damage configuration: {}").format(e))
            return False