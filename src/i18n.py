"""
Модуль интернационализации для S.T.A.L.K.E.R. 2 Mod Builder
Финальная версия с ручной загрузкой переводов в обход gettext
"""

import locale
import sys
import struct
from pathlib import Path
from typing import Dict, List, Optional

class I18N:
    """Класс для управления локализацией с ручной загрузкой переводов"""
    
    _instance = None
    _translations = {}  # Для совместимости с gettext
    _custom_translations = {}  # Наши собственные переводы
    _current_language = 'en'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Инициализация системы переводов"""
        self.locales_dir = Path("locales")
        self.locales_dir.mkdir(exist_ok=True)
        
        # Доступные языки
        self.available_languages = {
            'en': 'English',
            'ru': 'Русский',
            'uk': 'Українська',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'pl': 'Polski',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'it': 'Italiano',
            'cs': 'Čeština'
        }
        
        # Загружаем переводы вручную
        self._load_custom_translations()
        
        # Пробуем определить язык системы
        system_lang = self.detect_system_language()
        self.set_language(system_lang)
    
    def _load_custom_translations(self):
        """Загружает переводы напрямую из .po файла в обход gettext"""
        print("\n🔍 I18N: Загрузка переводов (ручной режим)...")
        
        # Загружаем русские переводы
        self._custom_translations['ru'] = self._parse_po_file('ru')
        
        # Для остальных языков пока пусто
        for lang in self.available_languages.keys():
            if lang != 'ru' and lang != 'en':
                self._custom_translations[lang] = {}
    
    def _parse_po_file(self, lang_code: str) -> Dict[str, str]:
        """Парсит .po файл и возвращает словарь переводов"""
        translations = {}
        
        po_path = self.locales_dir / lang_code / "LC_MESSAGES" / "messages.po"
        
        if not po_path.exists():
            print(f"  ⚠ Файл не найден: {po_path}")
            return translations
        
        print(f"  📖 Чтение {po_path}")
        
        try:
            with open(po_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Ищем все пары msgid/msgstr
            pattern = r'msgid "(.+?)"\nmsgstr "(.+?)"'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for msgid, msgstr in matches:
                if msgid and msgstr:
                    translations[msgid] = msgstr
            
            print(f"  ✅ Загружено {len(translations)} переводов для {lang_code}")
            
        except Exception as e:
            print(f"  ❌ Ошибка загрузки {lang_code}: {e}")
        
        return translations
    
    def set_language(self, language_code: str) -> bool:
        """Устанавливает язык интерфейса"""
        if language_code not in self.available_languages:
            language_code = 'en'
        
        self._current_language = language_code
        print(f"✅ I18N: Установлен язык {language_code}")
        return True
    
    def gettext(self, message: str) -> str:
        """Переводит сообщение на текущий язык"""
        # Для английского возвращаем как есть
        if self._current_language == 'en':
            return message
        
        # Для других языков ищем перевод
        translations = self._custom_translations.get(self._current_language, {})
        translated = translations.get(message, message)
        
        # Для отладки можно раскомментировать:
        # if translated != message:
        #     print(f"  ✓ '{message}' -> '{translated}'")
        # else:
        #     print(f"  ⚠ Не переведено: '{message}'")
        
        return translated
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Переводит сообщение с учётом plural forms"""
        # Простая реализация, для сложных случаев нужно доработать
        translation = self.gettext(singular if n == 1 else plural)
        return translation
    
    def get_current_language(self) -> str:
        """Возвращает текущий язык"""
        return self._current_language
    
    def get_language_name(self, language_code: str = None) -> str:
        """Возвращает название языка на его родном языке"""
        if language_code is None:
            language_code = self._current_language
        return self.available_languages.get(language_code, language_code)
    
    def detect_system_language(self) -> str:
        """Пытается определить язык системы"""
        try:
            if sys.platform == 'win32':
                # Windows
                import ctypes
                windll = ctypes.windll.kernel32
                locale_lang = windll.GetUserDefaultUILanguage()
                locale_map = {
                    1033: 'en', 1049: 'ru', 1058: 'uk', 1031: 'de',
                    1036: 'fr', 1034: 'es', 1045: 'pl', 2052: 'zh',
                    1041: 'ja', 1042: 'ko', 1040: 'it', 1029: 'cs',
                }
                detected = locale_map.get(locale_lang, 'en')
                print(f"  🖥️ Определен язык Windows: {detected}")
                return detected
            else:
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    detected = system_locale.split('_')[0]
                    print(f"  🖥️ Определен язык системы: {detected}")
                    if detected in self.available_languages:
                        return detected
        except Exception as e:
            print(f"  ⚠ Ошибка определения языка: {e}")
        return 'en'
    
    def get_available_languages_list(self) -> List[tuple]:
        """Возвращает список доступных языков для меню"""
        return [(code, name) for code, name in self.available_languages.items()]
    
    def reload_translations(self):
        """Перезагружает все переводы"""
        print("🔄 I18N: Перезагрузка переводов...")
        self._custom_translations.clear()
        self._load_custom_translations()


# Создаём глобальный экземпляр
i18n = I18N()
_ = i18n.gettext