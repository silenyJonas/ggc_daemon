import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab  # děděno z BaseTab pro logování

from managers.bulk_buy_item_manager import BulkBuyItemManager


class BulkBuyTab(BaseTab, ttk.Frame):
    """Záložka - Hromadný nákup (Bulk Buy)."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = BulkBuyItemManager()
        # --- Výchozí hodnoty ---
        self.is_running = False
        self.count = 10  # výchozí hodnota

        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""

        # --- Nastavení počtu ---
        count_frame = ttk.Frame(self)
        count_frame.pack(pady=10, anchor="w")
        ttk.Label(count_frame, text="Počet položek k nákupu (výsledný počet je x1000):").pack(side=tk.LEFT, padx=(0, 5))
        self.count_entry = ttk.Entry(count_frame, width=10)
        self.count_entry.insert(0, str(self.count))
        self.count_entry.pack(side=tk.LEFT)

        # --- Ovládací tlačítka Start / Stop ---
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15, anchor="center")
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_action)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_action)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    # --- Start / Stop ---
    def start_action(self):
        if self.is_running:
            self.log_message(status="info", message="Akce již běží!")
            return
        try:
            self.count = int(self.count_entry.get())
        except ValueError:
            self.log_message(status="error", message="Chyba: zadejte platné číslo pro počet položek.")
            return

        self.is_running = True
        self.log_message(status="info", message=f"Hromadný nákup spuštěn! Počet položek: {self.count}")
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop_action(self):
        if not self.is_running:
            self.log_message(status="info", message="Akce není spuštěna!")
            return
        self.is_running = False
        self.log_message(status="info", message="Akce zastavena.")

    def _run_loop(self):
        """Smyčka, která spouští funkci BulkBuyItemStart v manageru."""
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.log_message(status="info", message="Akce přerušena během odpočtu.")
                return
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        self.log_message(status="info", message="Hlavní akce spuštěna!")
        try:
            self.manager.BulkBuyItemStart(count=self.count)
        except Exception as e:
            self.log_message(status="error", message=f"Chyba při spuštění BulkBuyItemStart: {e}")

        self.is_running = False
        self.log_message(status="info", message="Akce dokončena.")
