#!/usr/bin/env python3
"""
Инструмент для извлечения строк из исходников и создания .pot файла
"""
import os
import re
from pathlib import Path

def extract_strings_from_file(filepath: Path) -> set:
    """Извлекает все строки, обёрнутые в _() из файла"""
    strings = set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Ищем паттерны: _("...") и _('...')
        patterns = [
            r'_\(\s*"([^"\\]*(\\.[^"\\]*)*)"\s*\)',
            r"_\('\s*'([^'\\]*(\\.[^'\\]*)*)'\s*'\)",
            r'_\(\s*"""(.+?)"""\s*\)',
            r"_\(\s*'''(.+?)'''\s*\)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    strings.add(match[0])
                else:
                    strings.add(match)
    
    return strings

def generate_pot_file(output_path: Path):
    """Генерирует .pot файл со всеми строками"""
    source_dirs = ["src"]
    all_strings = set()
    
    for source_dir in source_dirs:
        for py_file in Path(source_dir).rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            strings = extract_strings_from_file(py_file)
            all_strings.update(strings)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('msgid ""\n')
        f.write('msgstr ""\n')
        f.write('"Content-Type: text/plain; charset=UTF-8\\n"\n')
        f.write('"Content-Transfer-Encoding: 8bit\\n"\n')
        f.write('"Project-Id-Version: STALKER 2 Mod Builder\\n"\n')
        f.write('"POT-Creation-Date: \\n"\n')
        f.write('"PO-Revision-Date: \\n"\n')
        f.write('"Last-Translator: \\n"\n')
        f.write('"Language-Team: \\n"\n')
        f.write('"MIME-Version: 1.0\\n"\n')
        f.write('"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n\n')
        
        for string in sorted(all_strings):
            f.write(f'msgid "{string}"\n')
            f.write('msgstr ""\n\n')
    
    print(f"✅ Generated {output_path} with {len(all_strings)} strings")

if __name__ == "__main__":
    generate_pot_file(Path("locales/messages.pot"))