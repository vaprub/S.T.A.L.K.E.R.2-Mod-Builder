#!/usr/bin/env python3
"""
S.T.A.L.K.E.R. 2 Mod Builder - Translation Compiler
Full version - compiles .po files to .mo without external tools
"""

import os
import sys
import struct
from pathlib import Path

class POCompiler:
    """Class to compile .po files to .mo format"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.locales_dir = self.script_dir / "locales"
        
    def check_structure(self):
        """Check if locales directory exists"""
        if not self.locales_dir.exists():
            print(f"❌ Locales directory not found: {self.locales_dir}")
            return False
        return True
    
    def parse_po_file(self, po_path: Path) -> dict:
        """Parse .po file and return translations dictionary"""
        translations = {}
        current_msgid = None
        current_msgstr = None
        state = 'seek'
        
        with open(po_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.rstrip('\n')
            
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # Start of msgid
            if line.startswith('msgid "'):
                # Save previous pair
                if current_msgid is not None and current_msgstr is not None:
                    translations[current_msgid] = current_msgstr
                
                current_msgid = line[7:-1]
                current_msgstr = ""
                state = 'msgid'
                
            # Continuation of msgid
            elif state == 'msgid' and line.startswith('"'):
                current_msgid += line[1:-1]
                
            # Start of msgstr
            elif line.startswith('msgstr "'):
                current_msgstr = line[8:-1]
                state = 'msgstr'
                
            # Continuation of msgstr
            elif state == 'msgstr' and line.startswith('"'):
                current_msgstr += line[1:-1]
        
        # Save last pair
        if current_msgid is not None and current_msgstr is not None:
            translations[current_msgid] = current_msgstr
        
        return translations
    
    def create_mo_file(self, translations: dict, mo_path: Path) -> bool:
        """Create .mo file from translations dictionary"""
        # Sort items for stability
        items = sorted(translations.items(), key=lambda x: x[0])
        
        # Separate header (empty msgid)
        header = None
        strings = []
        for msgid, msgstr in items:
            if msgid == "":
                header = msgstr
            else:
                strings.append((msgid, msgstr))
        
        # Prepare byte strings
        orig_strings = []
        trans_strings = []
        for msgid, msgstr in strings:
            if msgid and msgstr:
                orig_strings.append(msgid.encode('utf-8') + b'\x00')
                trans_strings.append(msgstr.encode('utf-8') + b'\x00')
        
        num_strings = len(orig_strings)
        
        if num_strings == 0:
            print("  ⚠ No strings to translate!")
            return False
        
        # Calculate offsets
        magic = 0x950412de
        version = 0
        orig_table_offset = 28
        trans_table_offset = orig_table_offset + 8 * num_strings
        hash_table_offset = trans_table_offset + 8 * num_strings
        
        with open(mo_path, 'wb') as f:
            # Header
            f.write(struct.pack('<I', magic))
            f.write(struct.pack('<I', version))
            f.write(struct.pack('<I', num_strings))
            f.write(struct.pack('<I', orig_table_offset))
            f.write(struct.pack('<I', trans_table_offset))
            f.write(struct.pack('<I', hash_table_offset))
            f.write(struct.pack('<I', 0))  # hash table size
            
            # Original strings table
            offset = hash_table_offset
            for s in orig_strings:
                f.write(struct.pack('<I', len(s)))
                f.write(struct.pack('<I', offset))
                offset += len(s)
            
            # Translations table
            for s in trans_strings:
                f.write(struct.pack('<I', len(s)))
                f.write(struct.pack('<I', offset))
                offset += len(s)
            
            # Original strings data
            for s in orig_strings:
                f.write(s)
            
            # Translations data
            for s in trans_strings:
                f.write(s)
            
            # Header if exists
            if header:
                header_bytes = header.encode('utf-8') + b'\x00'
                f.write(header_bytes)
        
        return True
    
    def compile_language(self, lang_code: str) -> bool:
        """Compile translations for a specific language"""
        po_path = self.locales_dir / lang_code / "LC_MESSAGES" / "messages.po"
        mo_path = self.locales_dir / lang_code / "LC_MESSAGES" / "messages.mo"
        
        if not po_path.exists():
            print(f"❌ File not found: {po_path}")
            return False
        
        print(f"\n📄 Compiling {lang_code}...")
        
        # Parse .po file
        translations = self.parse_po_file(po_path)
        print(f"   Found {len(translations)} translations")
        
        # Create .mo file
        mo_path.parent.mkdir(parents=True, exist_ok=True)
        success = self.create_mo_file(translations, mo_path)
        
        if success:
            size = mo_path.stat().st_size
            print(f"   ✅ Created {mo_path} ({size} bytes)")
        else:
            print(f"   ❌ Failed to create {mo_path}")
        
        return success
    
    def compile_all(self):
        """Compile all found translations"""
        print("\n" + "=" * 60)
        print("🔧 S.T.A.L.K.E.R. 2 MOD BUILDER - TRANSLATION COMPILER")
        print("=" * 60)
        
        if not self.check_structure():
            return False
        
        # Find all languages with .po files
        languages = []
        for lang_dir in self.locales_dir.iterdir():
            if lang_dir.is_dir():
                po_file = lang_dir / "LC_MESSAGES" / "messages.po"
                if po_file.exists():
                    languages.append(lang_dir.name)
        
        if not languages:
            print("\n❌ No .po files found to compile")
            return False
        
        print(f"\n🔍 Found {len(languages)} languages to compile")
        
        # Compile each language
        success_count = 0
        for lang in languages:
            if self.compile_language(lang):
                success_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"✅ Successfully compiled: {success_count}/{len(languages)}")
        print("=" * 60)
        
        return success_count == len(languages)
    
    def show_status(self):
        """Show status of all translations"""
        print("\n" + "=" * 60)
        print("📊 TRANSLATIONS STATUS")
        print("=" * 60)
        
        if not self.check_structure():
            return
        
        for lang_dir in sorted(self.locales_dir.iterdir()):
            if not lang_dir.is_dir():
                continue
            
            po_file = lang_dir / "LC_MESSAGES" / "messages.po"
            mo_file = lang_dir / "LC_MESSAGES" / "messages.mo"
            
            if po_file.exists():
                # Count strings in .po file
                with open(po_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    msgid_count = content.count('msgid "')
                    msgstr_count = content.count('msgstr "') - 1
                
                mo_status = "✅" if mo_file.exists() else "❌"
                mo_size = mo_file.stat().st_size if mo_file.exists() else 0
                
                print(f"\n🌐 Language: {lang_dir.name}")
                print(f"   📄 PO: {po_file}")
                print(f"   📊 Strings: {msgid_count}")
                print(f"   ✏️ Translated: {msgstr_count}")
                print(f"   {mo_status} MO: {mo_size} bytes")

def main():
    """Main function"""
    compiler = POCompiler()
    
    if len(sys.argv) == 1:
        compiler.compile_all()
    elif sys.argv[1] == "status":
        compiler.show_status()
    elif sys.argv[1] == "compile":
        if len(sys.argv) > 2:
            compiler.compile_language(sys.argv[2])
        else:
            compiler.compile_all()
    elif sys.argv[1] == "help":
        print("\n" + "=" * 60)
        print("🔧 S.T.A.L.K.E.R. 2 MOD BUILDER - HELP")
        print("=" * 60)
        print("\nUsage:")
        print("  python tools/compile_po.py              # compile all languages")
        print("  python tools/compile_po.py compile      # compile all languages")
        print("  python tools/compile_po.py compile ru   # compile only Russian")
        print("  python tools/compile_po.py status       # show translations status")
        print("  python tools/compile_po.py help         # show this help")
        print()
    else:
        print("Unknown command. Use 'python tools/compile_po.py help'")

if __name__ == "__main__":
    main()