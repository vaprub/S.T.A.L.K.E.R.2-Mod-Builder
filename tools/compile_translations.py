#!/usr/bin/env python3
"""
Компилирует .po файлы в .mo для всех языков
"""
import subprocess
from pathlib import Path

def compile_translations():
    locales_dir = Path("locales")
    
    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue
        
        po_file = lang_dir / "LC_MESSAGES" / "messages.po"
        mo_file = lang_dir / "LC_MESSAGES" / "messages.mo"
        
        if po_file.exists():
            try:
                # Используем msgfmt из gettext
                result = subprocess.run(
                    ["msgfmt", str(po_file), "-o", str(mo_file)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ Compiled {lang_dir.name}")
                else:
                    print(f"❌ Failed to compile {lang_dir.name}: {result.stderr}")
            except FileNotFoundError:
                # Если msgfmt не установлен, используем Python
                import msgfmt
                try:
                    msgfmt.make(str(po_file), str(mo_file))
                    print(f"✅ Compiled {lang_dir.name} (with Python)")
                except Exception as e:
                    print(f"❌ Failed to compile {lang_dir.name}: {e}")

if __name__ == "__main__":
    compile_translations()