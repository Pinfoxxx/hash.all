import json
from pathlib import Path

from gui_v2.config import cfg


class TranslationManager:
    """Language change assistant"""

    def __init__(self):
        self.translations = {}
        self.lang_map = {"English": "en", "Русский": "ru"}
        self.load_language()

    def load_language(self):
        """Loads JSON file corresponding to the language"""
        lang_code = self.lang_map.get(cfg.data.LANGUAGE, "en")

        # Get locales path
        base_dir = Path(__file__).resolve().parent.parent
        locale_path = base_dir / "locales" / f"{lang_code}.json"

        try:
            if locale_path.exists():
                with open(locale_path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
            else:
                print(f"Error: Locale file not found: {locale_path}")
        except Exception as e:
            print(f"Critical error while loading locale: {e}")
            self.translations = {}

    def get_translation(self, key: str, default: str = "") -> str:
        """Return translation by key. If translation not exists, sends key or default."""
        return self.translations.get(key, default or key)


# Create an instance
translate = TranslationManager()
