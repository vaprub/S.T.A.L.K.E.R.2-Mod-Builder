"""
Модуль интернационализации для S.T.A.L.K.E.R. 2 Mod Builder
Поддерживает множественные языки и автоматическое определение языка системы
"""

import gettext
import locale
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List

class I18N:
    """Класс для управления локализацией"""
    
    _instance = None
    _translations = {}
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
        
        # Загружаем переводы для всех доступных языков
        self._load_translations()
        
        # Устанавливаем язык по умолчанию (английский)
        self.set_language('en')
    
    def _load_translations(self):
        """Загружает все доступные переводы"""
        for lang in self.available_languages.keys():
            try:
                # Пытаемся загрузить переводы для языка
                translation = gettext.translation(
                    'messages',
                    localedir=str(self.locales_dir),
                    languages=[lang],
                    fallback=True
                )
                self._translations[lang] = translation
            except FileNotFoundError:
                # Если переводов нет, используем NullTranslations
                self._translations[lang] = gettext.NullTranslations()
            except Exception as e:
                print(f"Warning: Failed to load translations for {lang}: {e}")
                self._translations[lang] = gettext.NullTranslations()
    
    def set_language(self, language_code: str) -> bool:
        """Устанавливает язык интерфейса"""
        if language_code not in self.available_languages:
            language_code = 'en'  # Fallback to English
        
        if language_code in self._translations:
            self._current_language = language_code
            # Устанавливаем для текущего потока
            self._translations[language_code].install()
            return True
        return False
    
    def gettext(self, message: str) -> str:
        """Переводит сообщение на текущий язык"""
        try:
            return self._translations[self._current_language].gettext(message)
        except:
            return message
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Переводит сообщение с учётом plural forms"""
        try:
            return self._translations[self._current_language].ngettext(singular, plural, n)
        except:
            return singular if n == 1 else plural
    
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
            # Пробуем получить язык из системных настроек
            if sys.platform == 'win32':
                # Windows
                import ctypes
                windll = ctypes.windll.kernel32
                locale_lang = windll.GetUserDefaultUILanguage()
                # Преобразуем LCID в код языка
                locale_map = {
                    1033: 'en',  # English US
                    1049: 'ru',  # Russian
                    1058: 'uk',  # Ukrainian
                    1031: 'de',  # German
                    1036: 'fr',  # French
                    1034: 'es',  # Spanish
                    1045: 'pl',  # Polish
                    2052: 'zh',  # Chinese
                    1041: 'ja',  # Japanese
                    1042: 'ko',  # Korean
                    1040: 'it',  # Italian
                    1029: 'cs',  # Czech
                }
                return locale_map.get(locale_lang, 'en')
            else:
                # Linux/Mac
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    lang_code = system_locale.split('_')[0]
                    if lang_code in self.available_languages:
                        return lang_code
        except Exception as e:
            print(f"Warning: Failed to detect system language: {e}")
        
        return 'en'  # По умолчанию английский
    
    def get_available_languages_list(self) -> List[tuple]:
        """Возвращает список доступных языков для меню"""
        return [(code, name) for code, name in self.available_languages.items()]
    
    def reload_translations(self):
        """Перезагружает все переводы (полезно при добавлении новых языков)"""
        self._translations.clear()
        self._load_translations()
        self.set_language(self._current_language)


# Создаём глобальный экземпляр
i18n = I18N()
_ = i18n.gettext  # Алиас для удобства