import json
import time


class ConfigManager:
    """Třída pro správu konfigurace z JSON souboru."""

    def __init__(self, filepath="config.json"):
        self.filepath = filepath
        self.data = self.load_config()

    def load_config(self):

        """Načte data z JSON souboru."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Soubor {self.filepath} nebyl nalezen. Vytvářím prázdná data.")
            return {}
        except json.JSONDecodeError:
            print(f"Chyba při načítání JSON souboru {self.filepath}.")
            return {}

    def save_config(self):
        """Uloží data do JSON souboru."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            print("Konfigurace úspěšně uložena.")
        except Exception as e:
            print(f"Chyba při ukládání konfigurace: {e}")