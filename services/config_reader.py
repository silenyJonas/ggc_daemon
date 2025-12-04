# services/config_reader.py
import json


class ConfigReader:
    """Třída pro čtení vnořených hodnot z konfigurace."""

    def __init__(self, filepath="configuration.json"):
        self.data = self.load_config(filepath)

    def load_config(self, filepath):
        """Načte data z JSON souboru."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_value(self, key_path):
        """
        Vrátí hodnotu pro daný klíč ve formátu 'cesta.ke.klíči'.

        Args:
            key_path (str): Klíč ve formátu 'level1.level2.value'.

        Returns:
            Libovolná hodnota nalezená na dané cestě, nebo None,
            pokud klíč neexistuje.
        """
        keys = key_path.split('.')
        current_data = self.data

        for key in keys:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return None  # Klíč nebyl nalezen

        return current_data